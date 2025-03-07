#!/usr/bin/env python3

# GlyphTranslator - A tool to convert Audacity Labels to Glyphs format for Nothing devices.
# Copyright (C) 2024  Sebastian Aigner (aka. SebiAi)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# TODO: [NOW] Make it possible to read files from stdin but make sure only one file is read from stdin: https://docs.python.org/3/library/fileinput.html
# TODO: Make it possible to write the nglyph file to stdout (check with sys.stdout.isatty() if the output is a terminal or a pipe)
# TODO: Maybe create an interactive mode where the user can select the files and the output path if no arguments are given. Then also "pause" the console at the end so the user can see the output.

import sys

# Check the python version
if sys.version_info < (3, 10):
    print("This script requires Python 3.10 or higher! Please upgrade your python version and try again.")
    sys.exit(1)

import os
import argparse
import csv
import re
import zlib
import copy
import math
import base64
import json
from enum import Enum
try:
    from termcolor import cprint, colored
except ImportError:
    print("IMPORT ERROR: termcolor is not installed. Please install it with 'pip install -U termcolor' and try again.")
    sys.exit(1)
try:
    from colorama import just_fix_windows_console
except ImportError:
    print("IMPORT ERROR: colorama is not installed. Please install it with 'pip install -U colorama' and try again.")
    sys.exit(1)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("IMPORT ERROR: cryptography is not installed. Please install it with 'pip install -U cryptography' and try again.")
    sys.exit(1)


# +------------------------------------+
# |                                    |
# |              Globals               |
# |                                    |
# +------------------------------------+

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
# Get the script name
SCRIPT_NAME = os.path.basename(__file__)

# Version of the script
SCRIPT_VERSION = "2.1.0"

# Default values for the arguments
DEFAULT_ARGS = { 'output_path': { 'value': ['.'], 'description': 'The current working directory' } }

# Regex patterns for the Label text
REGEX_PATTERN_LABEL_TEXT_PHONE1 = r'^([1-5])(?:\.((?:(?<![1-24-5]\.)[1-4])|(?:(?<![1-35]\.)[1-8])))?-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN|LOG))?$'
REGEX_PATTERN_LABEL_TEXT_PHONE2 = r'^([1-9]|1[0-1])(?:\.((?:(?<![0-35-9]\.)[1-9]|1[0-6])|(?:(?<![1-9]\.)[1-8])))?-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN|LOG))?$'
REGEX_PATTERN_LABEL_TEXT_PHONE2A = r'^([1-3])(?:(?<![23])\.([1-9]|1\d|2[0-4]))?-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN|LOG))?$'
REGEX_PATTERN_LABEL_TEXT_PHONE3A = r'^([1-3])(?:\.((?:(?<=1\.)(?:[1-9]|1\d|20))|(?:(?<=2\.)(?:[1-9]|1[0-1]))|(?:(?<=3\.)[1-5])))?-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN|LOG))?$'

# Enums
class Cols(Enum):
    FIVE_ZONE = 0
    FIFTEEN_ZONE = 1
    ELEVEN_ZONE = 2
    THIRTY_THREE_ZONE = 3
    THREE_ZONE_2A = 4
    TWENTY_SIX_ZONE = 5
    THREE_ZONE_3A = 6
    THIRTY_SIX_ZONE = 7
class PhoneModel(Enum):
    PHONE1 = 0
    PHONE2 = 1
    PHONE2A = 2
    PHONE3A = 3

# -- Lookup tables to convert our numbering system to the array indexes --
PHONE1_5COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL: list[list[int]] = [
    [0], # 1 to CAMERA_GLYPH
    [1], # 2 to DIAGONAL_GLYPH
    [2], # 3 to BATTERY_GLYPH
    [3], # 4 to USB_LINE_GLYPH
    [4], # 5 to USB_DOT_GLYPH
]
PHONE1_5COL_GLYPH_INDEX_TO_ARRAY_INDEXES_15COL: list[list[int]] = [
    [0], # 1 to CAMERA_GLYPH
    [1], # 2 to DIAGONAL_GLYPH
    range(2, 6), # 3 to BATTERY_GLYPH
    range(7, 15), # 4 to USB_LINE_GLYPH
    [6], # 5 to USB_DOT_GLYPH
]
# We need this because our numbering is different than the array indexes in the AUTHOR data for the 15Col mode
PHONE1_15COL_GLYPH_ZONE_INDEX_TO_ARRAY_INDEXES_15COL: list[list[int]] = [
    [0], # 1 to CAMERA_GLYPH
    [1], # 2 to DIAGONAL_GLYPH
    [4], # 3 to BATTERY_TOP_RIGHT_ZONE
    [5], # 4 to BATTERY_TOP_LEFT_ZONE
    [2], # 5 to BATTERY_BOTTOM_LEFT_ZONE
    [3], # 6 to BATTERY_BOTTOM_RIGHT_ZONE
    [14], # 7 to USB_LINE_ZONE8 (top of the line)
    [13], # 8 to USB_LINE_ZONE7
    [12], # 9 to USB_LINE_ZONE6
    [11], # 10 to USB_LINE_ZONE5
    [10], # 11 to USB_LINE_ZONE4
    [9], # 12 to USB_LINE_ZONE3
    [8], # 13 to USB_LINE_ZONE2
    [7], # 14 to USB_LINE_ZONE1
    [6], # 15 to USB_DOT_GLYPH
]

# Used for creating the CUSTOM1 data
PHONE2_11COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL: list[list[int]] = [
    [0], # 1 from CAMERA_TOP_GLYPH to CAMERA_GLYPH
    [0], # 2 from CAMERA_BOTTOM_GLYPH to CAMERA_GLYPH
    [1], # 3 from DIAGONAL_GLYPH to DIAGONAL_GLYPH
    [2], # 4 from BATTERY_TOP_RIGHT_GLYPH to BATTERY_GLYPH
    [2], # 5 from BATTERY_TOP_LEFT_GLYPH to BATTERY_GLYPH
    [2], # 6 from BATTERY_TOP_VERTICAL_GLYPH to BATTERY_GLYPH
    [2], # 7 from BATTERY_BOTTOM_LEFT_GLYPH to BATTERY_GLYPH
    [2], # 8 from BATTERY_BOTTOM_RIGHT_GLYPH to BATTERY_GLYPH
    [2], # 9 from BATTERY_BOTTOM_VERTICAL_GLYPH to BATTERY_GLYPH
    [3], # 10 from USB_LINE_GLYPH to USB_LINE_GLYPH
    [4], # 11 from USB_DOT_GLYPH to USB_DOT_GLYPH
]

PHONE2_5COL_GLYPH_INDEX_TO_ARRAY_INDEXES_11COL: list[list[int]] = [
    range(0, 2), # 1 to CAMERA_GLYPH
    [2], # 2 to DIAGONAL_GLYPH
    range(3, 9), # 3 to BATTERY_GLYPH
    [9], # 4 to USB_LINE_GLYPH
    [10], # 5 to USB_DOT_GLYPH
]
PHONE2_11COL_GLYPH_INDEX_TO_ARRAY_INDEXES_33COL: list[list[int]] = [
    [0], # 1 to CAMERA_TOP_GLYPH
    [1], # 2 to CAMERA_BOTTOM_GLYPH
    [2], # 3 to DIAGONAL_GLYPH
    range(3, 19), # 4 to BATTERY_TOP_RIGHT_GLYPH
    [19], # 5 to BATTERY_TOP_LEFT_GLYPH
    [20], # 6 to BATTERY_TOP_VERTICAL_GLYPH
    [21], # 7 to BATTERY_BOTTOM_LEFT_GLYPH
    [22], # 8 to BATTERY_BOTTOM_RIGHT_GLYPH
    [23], # 9 to BATTERY_BOTTOM_VERTICAL_GLYPH
    range(25, 33), # 10 to USB_LINE_GLYPH
    [24], # 11 to USB_DOT_GLYPH
]
# We need this because our numbering is different than the array indexes in the AUTHOR data for the 33Col mode
PHONE2_33_COL_GLYPH_ZONE_INDEX_TO_ARRAY_INDEXES_33COL: list[list[int]] = [
    [0], # 1 to CAMERA_TOP_GLYPH
    [1], # 2 to CAMERA_BOTTOM_GLYPH
    [2], # 3 to DIAGONAL_GLYPH
    [3], # 4 to BATTERY_TOP_RIGHT_ZONE1 (right side)
    [4], # 5 to BATTERY_TOP_RIGHT_ZONE2
    [5], # 6 to BATTERY_TOP_RIGHT_ZONE3
    [6], # 7 to BATTERY_TOP_RIGHT_ZONE4
    [7], # 8 to BATTERY_TOP_RIGHT_ZONE5
    [8], # 9 to BATTERY_TOP_RIGHT_ZONE6
    [9], # 10 to BATTERY_TOP_RIGHT_ZONE7
    [10], # 11 to BATTERY_TOP_RIGHT_ZONE8
    [11], # 12 to BATTERY_TOP_RIGHT_ZONE9
    [12], # 13 to BATTERY_TOP_RIGHT_ZONE10
    [13], # 14 to BATTERY_TOP_RIGHT_ZONE11
    [14], # 15 to BATTERY_TOP_RIGHT_ZONE12
    [15], # 16 to BATTERY_TOP_RIGHT_ZONE13
    [16], # 17 to BATTERY_TOP_RIGHT_ZONE14
    [17], # 18 to BATTERY_TOP_RIGHT_ZONE15
    [18], # 19 to BATTERY_TOP_RIGHT_ZONE16
    [19], # 20 to BATTERY_TOP_LEFT_GLYPH
    [20], # 21 to BATTERY_TOP_VERTICAL_GLYPH
    [21], # 22 to BATTERY_BOTTOM_LEFT_GLYPH
    [22], # 23 to BATTERY_BOTTOM_RIGHT_GLYPH
    [23], # 24 to BATTERY_BOTTOM_VERTICAL_GLYPH
    [32], # 25 to USB_LINE_ZONE8 (top of the line)
    [31], # 26 to USB_LINE_ZONE7
    [30], # 27 to USB_LINE_ZONE6
    [29], # 28 to USB_LINE_ZONE5
    [28], # 29 to USB_LINE_ZONE4
    [27], # 30 to USB_LINE_ZONE3
    [26], # 31 to USB_LINE_ZONE2
    [25], # 32 to USB_LINE_ZONE1
    [24], # 33 to USB_DOT_GLYPH
]

# Used for creating the CUSTOM1 data - custom mapping by SebiAi (not official)
PHONE2A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL: list[list[int]] = [
    [0],
    [1],
    [2],
]
PHONE2A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_26COL: list[list[int]] = [
    range(0, 24), # 1 to TOP_LEFT_GLYPH
    [24], # 2 to MIDDLE_RIGHT_GLYPH
    [25], # 3 to BOTTOM_LEFT_GLYPH
]
# We need this because our numbering is different than the array indexes in the AUTHOR data for the 26Col mode
PHONE2A_26COL_GLYPH_INDEX_TO_ARRAY_INDEXES_26COL: list[list[int]] = [
    [23], # 1 to TOP_LEFT_ZONE24 (right top side)
    [22], # 2 to TOP_LEFT_ZONE23
    [21], # 3 to TOP_LEFT_ZONE22
    [20], # 4 to TOP_LEFT_ZONE21
    [19], # 5 to TOP_LEFT_ZONE20
    [18], # 6 to TOP_LEFT_ZONE19
    [17], # 7 to TOP_LEFT_ZONE18
    [16], # 8 to TOP_LEFT_ZONE17
    [15], # 9 to TOP_LEFT_ZONE16
    [14], # 10 to TOP_LEFT_ZONE15
    [13], # 11 to TOP_LEFT_ZONE14
    [12], # 12 to TOP_LEFT_ZONE13
    [11], # 13 to TOP_LEFT_ZONE12
    [10], # 14 to TOP_LEFT_ZONE11
    [9], # 15 to TOP_LEFT_ZONE10
    [8], # 16 to TOP_LEFT_ZONE9
    [7], # 17 to TOP_LEFT_ZONE8
    [6], # 18 to TOP_LEFT_ZONE7
    [5], # 19 to TOP_LEFT_ZONE6
    [4], # 20 to TOP_LEFT_ZONE5
    [3], # 21 to TOP_LEFT_ZONE4
    [2], # 22 to TOP_LEFT_ZONE3
    [1], # 23 to TOP_LEFT_ZONE2
    [0], # 24 to TOP_LEFT_ZONE1
    [24], # 25 to MIDDLE_RIGHT_GLYPH
    [25], # 26 to BOTTOM_LEFT_GLYPH
]

# Used for creating the CUSTOM1 data - custom mapping by SebiAi (not official)
PHONE3A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL: list[list[int]] = [
    [0],
    [1],
    [2],
]
PHONE3A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_36COL: list[list[int]] = [
    range(0, 20), # 1 to TOP_LEFT_GLYPH
    range(20, 31), # 2 to MIDDLE_RIGHT_GLYPH
    range(31, 36), # 3 to BOTTOM_LEFT_GLYPH
]
# We need this because our numbering is different than the array indexes in the AUTHOR data for the 36Col mode
PHONE3A_36COL_GLYPH_INDEX_TO_ARRAY_INDEXES_36COL: list[list[int]] = [
    [0], # 1 to TOP_LEFT_ZONE1 (left bottom side)
    [1], # 2 to TOP_LEFT_ZONE2
    [2], # 3 to TOP_LEFT_ZONE3
    [3], # 4 to TOP_LEFT_ZONE4
    [4], # 5 to TOP_LEFT_ZONE5
    [5], # 6 to TOP_LEFT_ZONE6
    [6], # 7 to TOP_LEFT_ZONE7
    [7], # 8 to TOP_LEFT_ZONE8
    [8], # 9 to TOP_LEFT_ZONE9
    [9], # 10 to TOP_LEFT_ZONE10
    [10], # 11 to TOP_LEFT_ZONE11
    [11], # 12 to TOP_LEFT_ZONE12
    [12], # 13 to TOP_LEFT_ZONE13
    [13], # 14 to TOP_LEFT_ZONE14
    [14], # 15 to TOP_LEFT_ZONE15
    [15], # 16 to TOP_LEFT_ZON16
    [16], # 17 to TOP_LEFT_ZONE17
    [17], # 18 to TOP_LEFT_ZONE18
    [18], # 19 to TOP_LEFT_ZONE19
    [19], # 20 to TOP_LEFT_ZONE20
    [20], # 21 to MIDDLE_RIGHT_ZONE1 (top side)
    [21], # 22 to MIDDLE_RIGHT_ZONE2
    [22], # 23 to MIDDLE_RIGHT_ZONE3
    [23], # 24 to MIDDLE_RIGHT_ZONE4
    [24], # 25 to MIDDLE_RIGHT_ZONE5
    [25], # 26 to MIDDLE_RIGHT_ZONE6
    [26], # 27 to MIDDLE_RIGHT_ZONE7
    [27], # 28 to MIDDLE_RIGHT_ZONE8
    [28], # 29 to MIDDLE_RIGHT_ZONE9
    [29], # 30 to MIDDLE_RIGHT_ZONE10
    [30], # 31 to MIDDLE_RIGHT_ZONE11
    [31], # 32 to BOTTOM_LEFT_GLYPH (right bottom side)
    [32], # 33 to BOTTOM_LEFT_GLYPH
    [33], # 34 to BOTTOM_LEFT_GLYPH
    [34], # 35 to BOTTOM_LEFT_GLYPH
    [35], # 36 to BOTTOM_LEFT_GLYPH
]

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, add_help=False, description="Transform Audacity Labels to Glyphs format.", epilog="Audacity Label format:\n  The text part of the exported Labels file is constructed like this: 'glyphId-lightLevelFrom[-lightLevelTo[-interpolationMode]]'\n  Please consult the documentation for more info on the individual parts (glyphId, lightLevelFrom, lightLevelTo, interpolationMode).\n\n  Examples:\n    1-100\n    2-0-100\n    2-50-100-EXP\n    3.1-100-0-LOG\n\nCreated by: Sebastian Aigner (aka. SebiAi)")
    
    # Add the arguments
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.') # help
    parser.add_argument('FILE', help="An absolute or relative path to the Label file.", type=str, nargs=1) # FILE
    parser.add_argument('--watermark', help="An absolute or relative path to the watermark file. It will be embeded into the nglyph file.", type=str, nargs=1) # watermark
    parser.add_argument('-o', '--output-path', help=f"The path where the processed files will be dropped. Can be an absolute or relative path. - default: '{DEFAULT_ARGS['output_path']['value'][0]}' -> {DEFAULT_ARGS['output_path']['description']}", type=str, nargs=1, default=copy.deepcopy(DEFAULT_ARGS['output_path']['value']), dest='output_path') # output_path
    parser.add_argument('--version', action='version', help='Show the version number and exit.', version=SCRIPT_VERSION) # version
    
    return parser

# Check the requirements
def check_requirements():
    pass

# Perform argument checks
def perform_checks(args: dict):
    # Check if the file exists
    if not os.path.isfile(args['FILE'][0]):
        raise Exception(f"Label file does not exist: '{args['FILE'][0]}'")
    # Check if the file has the right extension
    if not args['FILE'][0].endswith(".txt"):
        raise Exception(f"File '{os.path.basename(args['FILE'][0])}' is not a Label file.")
    
    # Check if the watermark file exists and has the right extension
    if args.get('watermark', None) is not None:
        if not os.path.isfile(args['watermark'][0]):
            raise Exception(f"Watermark file does not exist: '{args['watermark'][0]}'")
        if not args['watermark'][0].endswith(".txt"):
            raise Exception(f"The watermark file should be a txt file which contains your watermark!")
    
    # Check if the output directory structure exists
    if not os.path.isdir(args['output_path'][0]):
        raise Exception(f"Can't write the output files there! The directory structure does not exist: '{args['output_path'][0]}'")

# Print critical error message and exit
def print_critical_error(message: str, exitCode: int = 1, start: str = "", **args):
    print_error(message, start, **args)
    #raise Exception(message)
    sys.exit(exitCode)

# Print error message
def print_error(message, start: str = "", **args):
    cprint(str(start) + "ERROR: " + str(message), color="red", attrs=["bold"], file=sys.stderr, flush=True, **args)

# Print warning message
def print_warning(message, start: str = "", **args):
    cprint(str(start) + "WARNING: " + str(message), color="yellow", attrs=["bold"], flush=True, **args)

# Print info message
def print_info(message, start: str = "", **args):
    cprint(str(start) + "INFO: " + str(message), color="cyan", flush=True, **args)

# Print debug message
def print_debug(message, start: str = "", **args):
    #cprint(str(start) + "DEBUG: " + str(message), color="grey", flush=True, **args)
    pass

# +------------------------------------+
# |                                    |
# |          Class Definitions         |
# |                                    |
# +------------------------------------+

class LabelFile:
    # Constants
    _TIME_STEP_MS = 16.666
    _MAX_LIGHT_LEVEL = 4095
    _SUPPORTED_LABEL_VERSIONS = [1]
    _SUPPORTED_PHONE_MODELS = list(map(lambda x: x.name, PhoneModel))

    # Exception for the LabelFile class
    class LabelFileException(Exception):
        pass

    def __iter__(self):
        return iter(self.labels)
    def __getitem__(self, index: int) -> 'LabelFile.Label':
        return self.labels[index]
    
    # String representation
    def __str__(self) -> str:
        return f"LabelFile('{self.file}', {len(self.labels)} Labels: {self.labels[:3] + ['...'] if len(self.labels) > 3 else self.labels})"
    def __repr__(self) -> str:
        return self.__str__()
    
    # Constructor
    def __init__(self, file_path: str) -> None:
        self.file: str = file_path
        self.labels: list[LabelFile.Label] = []
        self.contains_zone_labels: bool = False
        self.columns_model: Cols = Cols.FIVE_ZONE
        self.label_version: int = 0
        self.phone_model: PhoneModel = self._determine_phone_model(file_path) # This is before the version check. This whole script is kind of a cluster f*ck.

        # Get the regex for the phone model
        match self.phone_model:
            case PhoneModel.PHONE1:
                regex = re.compile(REGEX_PATTERN_LABEL_TEXT_PHONE1)
            case PhoneModel.PHONE2:
                regex = re.compile(REGEX_PATTERN_LABEL_TEXT_PHONE2)
            case PhoneModel.PHONE2A:
                regex = re.compile(REGEX_PATTERN_LABEL_TEXT_PHONE2A)
            case PhoneModel.PHONE3A:
                regex = re.compile(REGEX_PATTERN_LABEL_TEXT_PHONE3A)
            case _:
                raise ValueError(f"[Programming Error] Missing phone model in switch case: '{self.phone_model}'. Please report this error to the developer.")

        # Open the file and read the content
        found_end_label: bool = False
        encountered_error: bool = False
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t', strict=True, skipinitialspace=True) # TODO: Catch the csv.Error and print a better error message
            for row in reader:
                # Skip empty lines
                if len(row) == 0 or row[0].strip() == "":
                    continue

                # Check if the row has the right amount of columns
                if len(row) != 3:
                    raise LabelFile.LabelFileException(f"Invalid Label file format in line {reader.line_num}. The file should contain 3 columns: 'Time Start', 'Time End' and 'Label Text'.")
                
                # Add the Label to the list
                try:
                    self.labels.append(LabelFile.Label.from_list(row, reader.line_num))
                except:
                    raise LabelFile.LabelFileException(f"Parsing type error in line {reader.line_num}. Please check the Label file for errors.")

                # Check if the last Label is the END Label
                if self.labels[-1].is_end_label:
                    found_end_label = True
                else:
                    # Do not parse version or phone model labels
                    if not self.labels[-1].is_version_label and not self.labels[-1].is_phone_model_label:
                        # Parse the text of the label
                        try:
                            self.labels[-1].extract_text_values(regex)
                        except LabelFile.LabelFileException as e:
                            encountered_error = True
                            print_error(e)
        
        # Check if the end Label is present
        if not found_end_label:
            encountered_error = True
            print_error("No 'END' Label found. Please set a Label at the end of the audio file with the name 'END'.")
        
        # Check if we encountered an error while parsing the text values
        if encountered_error:
            raise LabelFile.LabelFileException("Encountered errors while parsing the Label text values. Please resolve the errors above. Make sure that you used the right phone model.")
        
        # Check if the Labels are sorted by time
        if not all(self.labels[i].time_from_ms <= self.labels[i+1].time_from_ms for i in range(len(self.labels)-1)):
            # Inform the user
            print_info("The Labels are not sorted by time. Sorting them now...")
            # Sort the Labels by time
            self.labels.sort(key=lambda x: x.time_from_ms)

        # Check if there are more than one END Label
        end_labels = [label for label in self.labels if label.is_end_label]
        if len(end_labels) > 1:
            raise LabelFile.LabelFileException("More than one 'END' Label found. Please set only one Label at the end of the audio file with the name 'END'.")
        
        # Get the Label version
        self.label_version = self._get_label_version()

        # Check if another Label is present after the END Label by checking the to_time
        beyond_end_label_labels = [label for label in self.labels if label.time_to_ms > end_labels[0].time_to_ms and not label.is_end_label]
        if beyond_end_label_labels:
            raise LabelFile.LabelFileException(f"There is a Label after the 'END' Label. Please set the 'END' Label at the end of the audio file and move the other Labels before it (offending line(s): {','.join([str(label.line_num) for label in beyond_end_label_labels])}).")

        # Find the columns model
        self.contains_zone_labels = any(label.is_zone_label for label in self.labels)
        match self.phone_model:
            case PhoneModel.PHONE1:
                self.columns_model = Cols.FIFTEEN_ZONE if self.contains_zone_labels else Cols.FIVE_ZONE
            case PhoneModel.PHONE2:
                self.columns_model = Cols.THIRTY_THREE_ZONE if self.contains_zone_labels else Cols.ELEVEN_ZONE
            case PhoneModel.PHONE2A:
                self.columns_model = Cols.TWENTY_SIX_ZONE if self.contains_zone_labels else Cols.THREE_ZONE_2A
            case PhoneModel.PHONE3A:
                self.columns_model = Cols.THIRTY_SIX_ZONE if self.contains_zone_labels else Cols.THREE_ZONE_3A
            case _:
                raise ValueError(f"[Programming Error] Missing phone model in switch case: '{self.phone_model}'. Please report this error to the developer.")

    def _determine_phone_model(self, file_path: str) -> PhoneModel:
        phone_model: PhoneModel | None = None

        # Open the file and read the content
        with open(file_path, newline='', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'PHONE_MODEL=(\w+)', line) #  There is another re in the Label class
                if m is not None:
                    # Check if we already found a phone model label
                    if phone_model is not None:
                        raise LabelFile.LabelFileException("More than one 'PHONE_MODEL' Label found. Please set only one Label with the name 'PHONE_MODEL=<model>'.")
                    # We found a phone model label => Use it
                    phone_model_string: str = m.group(1)
                    if phone_model_string not in LabelFile._SUPPORTED_PHONE_MODELS:
                        raise LabelFile.LabelFileException(f"This phone model '{phone_model_string}' is not supported in this version of this script (Supported phone models: {', '.join(self._SUPPORTED_PHONE_MODELS)}). Please update the script or use a different file.")
                    phone_model = PhoneModel[phone_model_string]
        
        # Return the phone model if found
        if phone_model is not None:
            return phone_model
        
        # No phone model label found
        raise LabelFile.LabelFileException(f"No 'PHONE_MODEL' Label found. Please set a Label with the name 'PHONE_MODEL=<model>', where '<model>' must be replaced with the appropriate phone model (Supported phone models: {', '.join(self._SUPPORTED_PHONE_MODELS)}). Refer to the documentation for more information.")

    def _get_label_version(self) -> int:        
        # Check if there are more than one VERSION Label
        version_labels = [label for label in self.labels if label.is_version_label]
        if len(version_labels) > 1:
            raise LabelFile.LabelFileException("More than one 'LABEL_VERSION' Label found. Please set only one Label with the name 'LABEL_VERSION=<version>'.")
        if len(version_labels) == 0:
            raise LabelFile.LabelFileException(f"No 'LABEL_VERSION' Label found. Please set a Label with the name 'LABEL_VERSION=<version>', where '<version>' must be replaced with the appropriate version number (Supported versions: {', '.join(map(str, self._SUPPORTED_LABEL_VERSIONS))}). Refer to the documentation for more information.")

        # Get the version number and check if it is supported
        label_version_match = re.match(LabelFile.Label._REGEX_PATTERN_LABEL_VERSION, version_labels[0].text)
        label_version = int(label_version_match.group(1))
        if label_version not in LabelFile._SUPPORTED_LABEL_VERSIONS:
            max_version = max(LabelFile._SUPPORTED_LABEL_VERSIONS)
            if label_version > max_version:
                raise LabelFile.LabelFileException(f"This Label version '{label_version}' is not supported in this version of this script (Supported versions: {', '.join(map(str, self._SUPPORTED_LABEL_VERSIONS))}). Please update the script or use a different file.")
            else:
                raise LabelFile.LabelFileException(f"This Label version '{label_version}' is not supported in this version of this script (Supported versions: {', '.join(map(str, self._SUPPORTED_LABEL_VERSIONS))}). Please check the documentation on how to migrate the Label file to a newer version.")
        
        return label_version

    def get_nglyph_data(self) -> tuple[list[str], list[str]]:
        # Get the END Label
        end_label: LabelFile.Label = next(label for label in self.labels if label.is_end_label)

        # Calculate the number of lines for the AUTHOR data
        author_lines = math.ceil(end_label.time_to_ms / LabelFile._TIME_STEP_MS)

        # Prepare the AUTHOR and CUSTOM1 data so we can index into it
        author_data: list[list[int]] = [[0 for x in range(get_numer_of_columns_from_columns_model(self.columns_model))] for y in range(author_lines)]
        custom1_data: list[str] = []

        for label in self.labels:
            # Check if the label is the END, LABEL_VERSION or PHONE_MODEL label
            if label.is_end_label or label.is_version_label or label.is_phone_model_label:
                continue

            # Get the parsed label
            parsed_label = label.to_parsed_label(self.columns_model)

            # Set the AUTHOR data
            overwrites: int = 0
            steps = list(range(round(parsed_label.rastered_time_from_ms/LabelFile._TIME_STEP_MS), round(parsed_label.rastered_time_to_ms/LabelFile._TIME_STEP_MS)))
            for i, row in enumerate(steps, 1 if parsed_label.absolute_light_level_from <= parsed_label.absolute_light_level_to else 0):
                # Calculate the light level depending on the light mode
                match parsed_label.light_mode:
                    case "LIN":
                        light_level = round(parsed_label.absolute_light_level_from + ((parsed_label.absolute_light_level_to - parsed_label.absolute_light_level_from) / len(steps)) * i)
                    case "EXP":
                        light_level = round(max(parsed_label.absolute_light_level_from, 1) * ((max(parsed_label.absolute_light_level_to, 1) / max(parsed_label.absolute_light_level_from, 1)) ** (i / len(steps))))
                    case "LOG":
                        light_level = round(-max(parsed_label.absolute_light_level_to, 1) * (max(parsed_label.absolute_light_level_to, 1)/max(parsed_label.absolute_light_level_from, 1))**(-i/len(steps)) + parsed_label.absolute_light_level_from + parsed_label.absolute_light_level_to)
                    case _:
                        raise ValueError(f"[Programming Error] Missing light mode in switch case: '{parsed_label.light_mode}'. Please report this error to the developer.")
                
                
                for index in parsed_label.array_indexes:
                    # Check if there is already a value present
                    if author_data[row][index] != 0:
                        overwrites += 1
                    # Write the light level to the AUTHOR data
                    author_data[row][index] = light_level
            
            # Inform the user if there were any overwrites
            if overwrites > 0:
                print_warning(f"Overwrote {overwrites} values in the AUTHOR data for label '{label.text}' in line {label.line_num}.")

            # Set the CUSTOM1 data
            custom1_data.append(f"{round(label.time_from_ms)}-{parsed_label.custom_5col_id}")


        return ([f"{','.join([str(e) for e in line])}," for line in author_data], custom1_data)
    
    # Class for the Label
    class Label:
        # Private constants
        _TIME_FROM = 0
        _TIME_TO = 1
        _TEXT_CONTENT = 2
        _REGEX_PATTERN_LABEL_VERSION = r'^LABEL_VERSION=(\d+)$'
        _REGEX_PATTERN_LABEL_PHONE_MODEL = re.compile(r'^PHONE_MODEL=(\w+)$') # There is another re in _determine_phone_model()

        # String representation
        def __str__(self) -> str:
            return f"Label(time_from: {self.time_from_ms}ms, time_to: {self.time_to_ms}ms, time_delta: {self.time_delta_ms}ms, text: '{self.text}', is_end_label: {self.is_end_label}, line_num:{self.line_num})"        
        def __repr__(self) -> str:
            return self.__str__()

        # Constructor
        def __init__(self, time_from: float, time_to: float, text: str, line_num: int) -> None:
            self.time_from_ms: float = round(time_from * 1000, 3)
            self.time_to_ms: float = round(time_to * 1000, 3)
            self.time_delta_ms: float = round(self.time_to_ms - self.time_from_ms, 3)
            self.text: str = text.strip()
            self.is_end_label: bool = self.text == "END"
            self.is_version_label: bool = re.match(LabelFile.Label._REGEX_PATTERN_LABEL_VERSION, self.text) is not None
            self.is_phone_model_label: bool = re.match(LabelFile.Label._REGEX_PATTERN_LABEL_PHONE_MODEL, self.text) is not None
            self.line_num: int = line_num

            # Values that get populated after extracting the text values
            self.glyph_index: int = 0
            self.zone_index: int = 0
            self.relative_light_level_from: int = 0
            self.relative_light_level_to: int = 0
            self.light_mode: str = "LIN"
            self.is_zone_label: bool = False

        # Create Label from a list
        @staticmethod
        def from_list(list: list[str], line_num: int) -> 'LabelFile.Label':
            if len(list) != 3:
                raise ValueError("The list must contain 3 elements.")
            
            time_from = float(list[LabelFile.Label._TIME_FROM].replace(',', '.'))
            time_to = float(list[LabelFile.Label._TIME_TO].replace(',', '.'))
            text = list[LabelFile.Label._TEXT_CONTENT]

            return LabelFile.Label(time_from, time_to, text, line_num)
        
        def extract_text_values(self, regex: re.Pattern[str]) -> None:
            # Check if the text matches the regex
            result = regex.match(self.text)
            if result is None:
                if '#' in self.text:
                    raise LabelFile.LabelFileException(f"Invalid Label text '{self.text}' in line {self.line_num}. It seems like you are using the outdated Label syntax. Please refere to the documentation on how to migrate your Label file to the new syntax.")
                else:
                    raise LabelFile.LabelFileException(f"Invalid Label text '{self.text}' in line {self.line_num}. Please refer to the documentation on how to name the Labels.")

            # Get the values from the match
            try:
                glyph_index = int(result.group(1))
                zone_index = int(result.group(2)) if result.group(2) is not None else 0
                relative_light_level_from = int(result.group(3))
                relative_light_level_to = int(result.group(4)) if result.group(4) is not None else relative_light_level_from
                light_mode = result.group(5) if result.group(5) is not None else "LIN"
            except:
                raise LabelFile.LabelFileException(f"Parsing type error in Label text '{self.text}' in line {self.line_num}. Please check the Label file for errors.")
            
            self.glyph_index = glyph_index
            self.zone_index = zone_index
            self.relative_light_level_from = relative_light_level_from
            self.relative_light_level_to = relative_light_level_to
            self.light_mode = light_mode
            self.is_zone_label = zone_index != 0

        def to_parsed_label(self, columns_model: Cols) -> 'LabelFile.ParsedLabel':
            parsed_label = LabelFile.ParsedLabel()
            # Round the time values to the nearest multiple of the time step
            parsed_label.rastered_time_from_ms = get_nearest_divisable_by(self.time_from_ms, LabelFile._TIME_STEP_MS)
            parsed_label.rastered_time_to_ms = get_nearest_divisable_by(self.time_to_ms, LabelFile._TIME_STEP_MS)
            parsed_label.rastered_time_delta_ms = parsed_label.rastered_time_to_ms - parsed_label.rastered_time_from_ms

            # If the time delta is zero, set it to the time step
            if parsed_label.rastered_time_delta_ms == 0:
                parsed_label.rastered_time_to_ms += LabelFile._TIME_STEP_MS
                parsed_label.rastered_time_delta_ms = LabelFile._TIME_STEP_MS

            # Get the array indexes for the glyph/zone
            parsed_label.array_indexes = get_glyph_array_indexes(self.glyph_index, self.zone_index, columns_model)
            parsed_label.custom_5col_id = get_custom_5col_id(self.glyph_index, columns_model)

            # Calculate the absolute light levels
            parsed_label.absolute_light_level_from = round(self.relative_light_level_from * LabelFile._MAX_LIGHT_LEVEL / 100.0)
            parsed_label.absolute_light_level_to = round(self.relative_light_level_to * LabelFile._MAX_LIGHT_LEVEL / 100.0)
            
            # Copy the light mode and zone label flag
            parsed_label.light_mode = self.light_mode
            parsed_label.is_zone_label = self.is_zone_label

            return parsed_label
    
    class ParsedLabel:
        # Constructor
        def __init__(self) -> None:
            self.rastered_time_from_ms: float = 0
            self.rastered_time_to_ms: float = 0
            self.rastered_time_delta_ms: float = 0
            self.array_indexes: list[int] = []
            self.custom_5col_id: int = 0
            self.absolute_light_level_from: int = 0
            self.absolute_light_level_to: int = 0
            self.light_mode: str = "LIN"
            self.is_zone_label: bool = False

class WatermarkFile:
    # Exception for the WatermarkFile class
    class WatermarkFileException(Exception):
        pass

    def __init__(self, file: str) -> None:
        self.file: str = file
        self.content: str = ""
        self._salt: bytes = os.urandom(16)
        print_debug(f"[Watermark] salt: {self._salt.hex()}")

        # Open the file and read the content - make sure we get '\n' as newline by setting newline=None
        try:
            with open(file, newline=None, encoding='utf-8') as f:
                self.content = f.read()
        except Exception as e:
            raise WatermarkFile.WatermarkFileException(f"Error while reading the watermark file: {e}")

    def to_key(self) -> bytes:
        # Get the key for the watermark
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.content.encode('utf-8')))
        return key
    
    
        
# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def get_numer_of_columns_from_columns_model(columns_model: Cols) -> int:
    match columns_model:
        case Cols.FIVE_ZONE:
            return 5
        case Cols.FIFTEEN_ZONE:
            return 15
        case Cols.ELEVEN_ZONE | Cols.THIRTY_THREE_ZONE:
            # There only exists 33 columns mode for the AUTHOR data,
            # the 11 columns mode is a convenience mode for the 33 columns mode
            return 33
        case Cols.THREE_ZONE_2A | Cols.TWENTY_SIX_ZONE:
            # There only exists 26 columns mode for the AUTHOR data,
            # the 3 columns mode is a convenience mode for the 26 columns mode
            return 26
        case Cols.THREE_ZONE_3A | Cols.THIRTY_SIX_ZONE:
            # There only exists 36 columns mode for the AUTHOR data,
            # the 3 columns mode is a convenience mode for the 36 columns mode
            return 36
        case _:
            raise ValueError(f"[Programming Error] Missing columns model in switch case: '{columns_model}'. Please report this error to the developer.")

def get_glyph_array_indexes(glyph_index: int, zone_index: int, columns_model: Cols) -> list[int]:
    # Offset the glyph_index and zone_index
    glyph_index -= 1
    zone_index -= 1

    # Offset is needed because we use the dot index system
    # E.g.: Phone1 has in 15Col mode 4 zones in the BATTERY_GLYPH (glyph_index of 3).
    #       So we need to offset the array index by 4 to get the right zone if the glyph_index is greater than 3.
    offset: int = 0

    match columns_model:
        case Cols.FIVE_ZONE:
            # No zone_index in 5Col mode therefore we use the 5col mode to keep upwards compatibility
            return PHONE1_5COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL[glyph_index]
        case Cols.FIFTEEN_ZONE:
            # Offset the array index if the glyph_index is greater than (3 - 1) (BATTERY_GLYPH has 4 zones in 15Col mode => 3 + 1)
            offset += 3 if glyph_index > 2 else 0
            # Offset the array index if the glyph_index is greater than (4 - 1) (USB_LINE_GLYPH has 8 zones in 15Col mode => 7 + 1)
            offset += 7 if glyph_index > 3 else 0

            if zone_index == -1:
                # No zone_index provided => we need to address the whole glyph
                return PHONE1_5COL_GLYPH_INDEX_TO_ARRAY_INDEXES_15COL[glyph_index]
            else:
                # Only address the zone
                return PHONE1_15COL_GLYPH_ZONE_INDEX_TO_ARRAY_INDEXES_15COL[glyph_index + zone_index + offset]
        case Cols.ELEVEN_ZONE:
            # No zone_index in 11Col mode
            return PHONE2_11COL_GLYPH_INDEX_TO_ARRAY_INDEXES_33COL[glyph_index]
        case Cols.THIRTY_THREE_ZONE:
            # Offset the array index if the glyph_index is greater than (4 - 1) (BATTERY_TOP_RIGHT_GLYPH has 16 zones in 33Col mode => 15 + 1)
            offset += 15 if glyph_index > 3 else 0
            # Offset the array index if the glyph_index is greater than (10 - 1) (USB_LINE_GLYPH has 8 zones in 33Col mode => 7 + 1)
            offset += 7 if glyph_index > 9 else 0

            if zone_index == -1:
                # No zone_index provided => we need to address the whole glyph
                return PHONE2_11COL_GLYPH_INDEX_TO_ARRAY_INDEXES_33COL[glyph_index]
            else:
                # Only address the zone
                return PHONE2_33_COL_GLYPH_ZONE_INDEX_TO_ARRAY_INDEXES_33COL[glyph_index + zone_index + offset]
        case Cols.THREE_ZONE_2A:
            # No zone_index in 3Col mode
            return PHONE2A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_26COL[glyph_index]
        case Cols.TWENTY_SIX_ZONE:
            # Offset the array index if the glyph_index is greater than (1 - 1) (TOP_LEFT_GLYPH has 24 zones in 26Col mode => 23 + 1)
            offset += 23 if glyph_index > 0 else 0

            if zone_index == -1:
                # No zone_index provided => we need to address the whole glyph
                return PHONE2A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_26COL[glyph_index]
            else:
                # Only address the zone
                return PHONE2A_26COL_GLYPH_INDEX_TO_ARRAY_INDEXES_26COL[glyph_index + zone_index + offset]
        case Cols.THREE_ZONE_3A:
            # No zone_index in 3Col mode
            return PHONE3A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_36COL[glyph_index]
        case Cols.THIRTY_SIX_ZONE:
            # Offset the array index if the glyph_index is greater than (1 - 1) (TOP_LEFT_GLYPH has 20 zones in 36Col mode => 19 + 1)
            offset += 19 if glyph_index > 0 else 0
            # Offset the array index if the glyph_index is greater than (2 - 1) (MIDDLE_RIGHT_GLYPH has 11 zones in 36Col mode => 10 + 1)
            offset += 10 if glyph_index > 1 else 0

            if zone_index == -1:
                # No zone_index provided => we need to address the whole glyph
                return PHONE3A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_36COL[glyph_index]
            else:
                # Only address the zone
                return PHONE3A_36COL_GLYPH_INDEX_TO_ARRAY_INDEXES_36COL[glyph_index + zone_index + offset]
        case _:
            raise ValueError(f"[Programming Error] Missing columns model in switch case: '{columns_model}'. Please report this error to the developer.")

def get_custom_5col_id(glyph_index: int, columns_model: Cols) -> int:
    # Offset the glyph_index
    glyph_index -= 1

    match columns_model:
        case Cols.FIVE_ZONE | Cols.FIFTEEN_ZONE:
            return PHONE1_5COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL[glyph_index][0]
        case Cols.ELEVEN_ZONE | Cols.THIRTY_THREE_ZONE:
            return PHONE2_11COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL[glyph_index][0]
        case Cols.THREE_ZONE_2A | Cols.TWENTY_SIX_ZONE:
            return PHONE2A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL[glyph_index][0]
        case Cols.THREE_ZONE_3A | Cols.THIRTY_SIX_ZONE:
            return PHONE3A_3COL_GLYPH_INDEX_TO_ARRAY_INDEXES_5COL[glyph_index][0]
        case _:
            raise ValueError(f"[Programming Error] Missing columns model in switch case: '{columns_model}'. Please report this error to the developer.")


def get_nearest_divisable_by(number: float, divisor: float) -> float:
    # Return the nearest number that is divisable by the divisor
    return round(number / divisor) * divisor

def encrypt_author_data(key: bytes, author_data: list[str], columns_model: Cols) -> list[str]:
    # Get the number of columns
    num_columns = get_numer_of_columns_from_columns_model(columns_model)
    
    # Create encryption object
    f = Fernet(key)

    # Concat the data and compress it
    byte_data = '\r\n'.join(author_data).encode('utf-8')
    data = zlib.compress(byte_data, zlib.Z_BEST_COMPRESSION)
    token = zlib.compress(f.encrypt(data), zlib.Z_BEST_COMPRESSION)

    print_debug(f"length before encryption: {len(data)}")
    print_debug(f"length after encryption: {len(token)}")

    # Prepend the length of the token
    encrypt_author_data: list[list[int]] = [[0 for n_column in range(num_columns)] for n_row in range(math.ceil((len(token) + 1) / num_columns))]
    encrypt_author_data[0][0] = len(token)

    # Add the token
    for i, byte in enumerate(token, 1):
        encrypt_author_data[i // num_columns][i % num_columns] = byte


    return [f"{','.join([str(e) for e in line])}," for line in encrypt_author_data]
    

# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

def main() -> int:
    # Fix the windows console - needed for correct color output
    just_fix_windows_console()

    # Print version only if the --version argument is not present
    if "--version" not in sys.argv:
        print_info(f"Using GlyphTranslator version v{SCRIPT_VERSION}")

    # Parse the arguments
    args = build_arguments_parser().parse_args()
    print_debug(f"args: {args}")

    # Check the requirements
    check_requirements()

    # Expand the paths
    args.FILE[0] = os.path.abspath(args.FILE[0])
    if args.watermark is not None:
        args.watermark[0] = os.path.abspath(args.watermark[0])
    args.output_path[0] = os.path.abspath(args.output_path[0])
    print_debug(f"expanded args: {args}")

    # Perform all the checks
    try:
        perform_checks(args.__dict__)
    except Exception as e:
        print_critical_error(e)
    
    print_debug("")

    # Read the Label file
    try:
        label_file = LabelFile(args.FILE[0])
    except LabelFile.LabelFileException as e:
        print_critical_error(e)
    
    # Inform the user
    print_info(f"Processed {len(label_file.labels)} Labels.")
    print_info(f"Using phone model: {label_file.phone_model.name}, columns model: {label_file.columns_model.name}")

    # Create the nglyph data
    nglyph_data = {
        'VERSION': 1,
        'PHONE_MODEL': label_file.phone_model.name,
    }

    # Process the Labels
    try:
        nglyph_data['AUTHOR'], nglyph_data['CUSTOM1'] = label_file.get_nglyph_data()
    except LabelFile.LabelFileException as e:
        print_critical_error(e)
    
    # Get the watermark file data
    if args.watermark is not None:
        print_info(f"Processing watermark from file '{args.watermark[0]}'...")
        try:
            watermark_file = WatermarkFile(args.watermark[0])
        except WatermarkFile.WatermarkFileException as e:
            print_critical_error(e)
        
        # If there is a new line at the end of the file splitlines() will not make an extra empty line => add one if needed
        nglyph_data['WATERMARK'] = watermark_file.content.splitlines() + ([''] if watermark_file.content.endswith('\n') else [])
        nglyph_data['SALT'] = base64.b64encode(watermark_file._salt).decode('utf-8')

        # Get the key
        watermark_key = watermark_file.to_key()
        nglyph_data['AUTHOR'] = encrypt_author_data(watermark_key, nglyph_data['AUTHOR'], label_file.columns_model)

    # Get the file paths
    base_filename = os.path.splitext(os.path.basename(args.FILE[0]))[0]
    nglyph_file_path = os.path.join(args.output_path[0], base_filename + ".nglyph")

    # Print info
    print_info(f"Writing the nglyph file to '{nglyph_file_path}'")

    # Write the nglyph file
    with open(nglyph_file_path, 'w', newline='\r\n', encoding='utf-8') as f:
        json.dump(nglyph_data, f, indent=4)

    cprint("Done!", color="green", attrs=["bold"])

    return 0



if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")
    # except Exception as e:
    #     printCriticalError(e)
