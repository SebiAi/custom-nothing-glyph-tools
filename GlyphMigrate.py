#!/usr/bin/env python3

# GlyphMigrate - A tool to migrate Label files to the newest format version.
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

import sys

# Check the python version
if sys.version_info < (3, 10):
    print("This script requires Python 3.10 or higher! Please upgrade your python version and try again.")
    sys.exit(1)

from collections.abc import Iterable
import os
import argparse
import csv
import re
import copy
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
SCRIPT_VERSION = "2.0.0"

# Default values for the arguments
DEFAULT_ARGS = {
    'output_path': { 'value': ['.'], 'description': 'The current working directory' },
}

LEGACY_COMPATIBILITY_MODE_TO_PHONE2_MAPPING: dict[int, list[int]]= {
    1: [1, 2],
    2: [3],
    3: [4, 5, 6, 7, 8, 9],
    4: [10],
    5: [11],
}

SUPPORTED_LABEL_VERSIONS = [0, 1]
V0_TO_V1_REPLACEMENTS: list[tuple[str, str]] = [# V0 also known as legacy
    ('#1-', '1-'),
    ('#2-', '2-'),
    ('#3-', '3-'),
    ('#4-', '4.1-'),
    ('#5-', '4.2-'),
    ('#6-', '4.3-'),
    ('#7-', '4.4-'),
    ('#8-', '4.5-'),
    ('#9-', '4.6-'),
    ('#10-', '4.7-'),
    ('#11-', '4.8-'),
    ('#12-', '4.9-'),
    ('#13-', '4.10-'),
    ('#14-', '4.11-'),
    ('#15-', '4.12-'),
    ('#16-', '4.13-'),
    ('#17-', '4.14-'),
    ('#18-', '4.15-'),
    ('#19-', '4.16-'),
    ('#20-', '5-'),
    ('#21-', '6-'),
    ('#22-', '7-'),
    ('#23-', '8-'),
    ('#24-', '9-'),
    ('#25-', '11-'),
    ('#26-', '10.8-'),
    ('#27-', '10.7-'),
    ('#28-', '10.6-'),
    ('#29-', '10.5-'),
    ('#30-', '10.4-'),
    ('#31-', '10.3-'),
    ('#32-', '10.2-'),
    ('#33-', '10.1-'),
]

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(add_help=False, description="A tool to migrate Label files to the newest format version.", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    # Add the arguments
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.') # help
    parser.add_argument('LABEL_PATH', help="A path to the Label file.", type=str, nargs=1) # LABEL_PATH
    parser.add_argument('-o', '--output-path', help=f"The path where the processed files will be dropped. Can be an absolute or relative path. - default: '{DEFAULT_ARGS['output_path']['value'][0]}' -> {DEFAULT_ARGS['output_path']['description']}", type=str, nargs=1, default=copy.deepcopy(DEFAULT_ARGS['output_path']['value']), dest='output_path') # output_path
    parser.add_argument('--version', action='version', help='Show the version number and exit.', version=SCRIPT_VERSION) # version

    return parser

# Check the requirements
def check_requirements():
    pass    

# Perform argument checks
def perform_checks(args: dict):
    # Check if the label file exists
    if 'LABEL_PATH' in args and not os.path.isfile(args['LABEL_PATH'][0]):
        raise Exception(f"Audio file does not exist: '{args['LABEL_PATH'][0]}'")
    
    # Check the file extension of the label file
    if 'LABEL_PATH' in args and os.path.splitext(args['LABEL_PATH'][0])[1].lower() != '.txt':
        raise Exception(f"Invalid file extension. The label file should have the extension '.txt'.")
    
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

class LabelFileReaderException(Exception):
    pass
class LabelFileReader:
    def __init__(self, label_file: Iterable[str]) -> None:
        self._csv_reader = csv.reader(label_file, delimiter='\t', strict=True, skipinitialspace=True)

    def line_num(self) -> int:
        return self._csv_reader.line_num
    
    def __iter__(self) -> 'LabelFileReader':
        return self

    def __next__(self) -> 'Label':
        row: list[str] = []
        
        # Skip empty lines
        while not row or row[0].strip() == '':
            try:
                row = next(self._csv_reader)
            except csv.Error as e:
                raise LabelFileReaderException(f"Invalid csv data while parsing Label row {self.line_num()}: {e}")

        # Check the row length
        if len(row) != 3:
            raise LabelFileReaderException(f"Invalid Label file format in line {self.line_num()}. The file should contain 3 columns, separated by a tabulator: 'Time Start', 'Time End' and 'Label Text'.")
        
        return Label(row, self.line_num())
class LabelType(Enum):
    NORMAL = 0
    VERSION = 1
    PHONE_MODEL = 2
    END = 99
class Label:
    INDEX_TIME_FROM: int = 0
    INDEX_TIME_TO: int = 1
    INDEX_TEXT_CONTENT: int = 2
    _REGEX_PATTERN_LABEL_VERSION = re.compile(r'^LABEL_VERSION=(\d+)$')
    _REGEX_PATTERN_LABEL_PHONE_MODEL = re.compile(r'^PHONE_MODEL=(\w+)$')

    def __init__(self, row: list[str], line_num: int) -> None:
        self.row: list[str] = row
        self.line_num: int = line_num
        self.type: LabelType = LabelType.NORMAL
        self.version: None | int = None
        self.phone_model_string: None | str = None

        if len(self.row) != 3:
            raise ValueError(f"Invalid Label row format. The row should contain 3 columns, separated by a tabulator: 'Time Start', 'Time End' and 'Label Text'.")

        match_version_label = re.match(Label._REGEX_PATTERN_LABEL_VERSION, self.row[2])
        match_phone_model_label = re.match(Label._REGEX_PATTERN_LABEL_PHONE_MODEL, self.row[2])

        if self.row[Label.INDEX_TEXT_CONTENT] == 'END':
            self.type = LabelType.END
        elif match_version_label:
            self.type = LabelType.VERSION
            self.version = int(match_version_label.group(1))
        elif match_phone_model_label:
            self.type = LabelType.PHONE_MODEL
            self.phone_model_string = match_phone_model_label.group(1)
    
    def __str__(self) -> str:
        return '\t'.join(self.row)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(row={self.row}, line_num={self.line_num}, type={self.type.name}, version={self.version}, phone_model_string={self.phone_model_string})"

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def migrate_labels(labels: list[Label], version: int) -> tuple[list[Label], int]:
    migration_steps: int = 0
    
    if version == 0:
        # Get the legacy phone model string
        phone_model = get_legacy_phone_model_string(version, labels)

        # Migrate the labels from version 0 to version 1
        for label in labels:
            match label.type:
                case LabelType.NORMAL:
                    for replacement in V0_TO_V1_REPLACEMENTS:
                        if replacement[0] in label.row[Label.INDEX_TEXT_CONTENT]:
                            label.row[Label.INDEX_TEXT_CONTENT] = label.row[Label.INDEX_TEXT_CONTENT].replace(replacement[0], replacement[1], 1)
                            migration_steps += 1
                            continue
                # Do nothing for other labels - we do not have a version label and end labels do not need to be changed
                case LabelType.VERSION: pass
                case LabelType.PHONE_MODEL: pass
                case LabelType.END: pass
                case _:
                    raise NotImplementedError(f"[Development Error] Please report this to the developer: Could not upgrade the data from v0 to v1. Got {label.type}, expected LabelType.NORMAL, LabelType.VERSION, LabelType.PHONE_MODEL or LabelType.END.")
        
        # Add the version label
        labels.insert(0, Label(['0.000000', '0.000000', 'LABEL_VERSION=1'], 0)) # Set the line number to 0 for all added labels
        migration_steps += 1
        # Add the phone model label
        labels.insert(1, Label(['0.000000', '0.000000', f'PHONE_MODEL={phone_model}'], 0)) # Set the line number to 0 for all added labels
        migration_steps += 1
        
        version = 1
    
    #if version == 1:
        # Migrate the labels from version 1 to version 2
        # for label in labels:
        #     match label.type:
        #         case LabelType.VERSION:
        #             label.row[Label.INDEX_TEXT_CONTENT] = 'LABEL_VERSION=2'
        #         case LabelType.NORMAL:
        #             pass # Replace with upgrade process
        #         case LabelType.PHONE_MODEL:
        #             pass # Replace with upgrade process
        #         case LabelType.END:
        #             pass # Replace with upgrade process
        #         case _:
        #             raise NotImplementedError(f"[Development Error] Please report this to the developer: Could not upgrade the data from v1 to v2. Got {label.type}, expected LabelType.NORMAL, LabelType.VERSION, LabelType.PHONE_MODEL or LabelType.END.")
        # version = 1
    
    max_version: int = max(SUPPORTED_LABEL_VERSIONS)
    if version != max_version:
        raise NotImplementedError(f"[Development Error] Could not upgrade the data to the latest format version. Got {version}, expected {max_version}.")
        
    return (labels, migration_steps)

def get_legacy_phone_model_string(label_version: int, labels: list[Label]) -> str:
    assert label_version == 0, "This function is only for legacy label files (v0)."

    for label in labels:
        if label.type != LabelType.NORMAL:
            continue
        
        # Get the text
        text: str = label.row[Label.INDEX_TEXT_CONTENT]

        # Check if the text contains a hash
        if '#' in text:
            return 'PHONE2'
        
        # Get the glyphId - which does not have a hash because we checked that before
        try:
            glyphId: int = int(text.split('-', 1)[0])
        except ValueError:
            raise ValueError(f"Invalid label text. Could not parse the glyphId from the label text '{text}' in line {label.line_num}.")

        if glyphId > 5:
            return 'PHONE2'
    
    return 'PHONE1'

def is_legacy_compatiblity_mode(label_version: int, labels: list[Label]) -> bool:
    if label_version != 0:
        return False
    
    return get_legacy_phone_model_string(label_version, labels) == 'PHONE1'

def convert_labels_to_phone2(labels: list[Label]) -> tuple[list[Label], int]:
    converted_labels: list[Label] = []
    conversion_steps: int = 0
    for label in labels:
        # Skip non normal labels
        if label.type != LabelType.NORMAL:
            converted_labels.append(label)
            continue

        # Get the glyphId - should not fail because we checked that before in is_legacy_compatiblity_mode()
        label_text_split: list[str] = label.row[Label.INDEX_TEXT_CONTENT].split('-', 1)
        glyph_id: int = int(label_text_split[0])

        try:
            new_glyph_ids: list[int] = LEGACY_COMPATIBILITY_MODE_TO_PHONE2_MAPPING[glyph_id]
        except KeyError:
            raise KeyError(f"Invalid label text. Could not find the mapping for the glyphId '{glyph_id}' in line {label.line_num}.")
        
        # Create the new labels
        for i, new_glyph_id in enumerate(new_glyph_ids):
            conversion_steps += 1
            new_label: Label = copy.deepcopy(label)
            new_label.row[Label.INDEX_TEXT_CONTENT] = f"{new_glyph_id}-{label_text_split[1]}"
            if i > 0:
                new_label.line_num = 0 # Set to 0 for all added labels
            converted_labels.append(new_label)    

    return (converted_labels, conversion_steps)



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
        print_info(f"Using GlyphMigrate version v{SCRIPT_VERSION}")

    # Parse the arguments
    args = build_arguments_parser().parse_args()
    print_debug(f"args: {args}")

    # Expand the paths
    args.LABEL_PATH[0] = os.path.abspath(args.LABEL_PATH[0])
    args.output_path[0] = os.path.abspath(args.output_path[0])
    print_debug(f"expanded args: {args}")

    # Check the requirements
    check_requirements()

    # Perform all the checks
    try:
        perform_checks(args.__dict__)
    except Exception as e:
        print_critical_error(e)
    
    print_debug("")

    # Read the label file
    with open(args.LABEL_PATH[0], newline='') as label_file:
        try:
            labels: list[Label] = list(LabelFileReader(label_file))
        except LabelFileReaderException as e:
            print_critical_error(e)
    
    # Debug print the labels
    print_debug("Read labels:")
    for label in labels:
        print_debug(f"{label!r}")
    print_debug("")

    # Check if this is a label file (basic)
    if len([x for x in labels if x.type == LabelType.END]) == 0:
        print_critical_error("This does not seem to be a label file. Please use a valid label file.")

    # Check the amount of version labels
    version_labels: list[Label] = [x for x in labels if x.type == LabelType.VERSION]
    print_debug(f"Version labels: {version_labels}")
    if len(version_labels) > 1:
        print_critical_error("There are more than one version labels in the file. Please use a valid label file.")

    label_version: int = version_labels[0].version if version_labels else 0
    print_debug(f"Label version: v{label_version}")

    # Check if the label version is supported
    if label_version not in SUPPORTED_LABEL_VERSIONS:
        print_critical_error(f"The label version v{label_version} is not supported by this tool (supported versions: {', '.join('v' + SUPPORTED_LABEL_VERSIONS)}). Please upgrade the script or use a different label file.")

    # Check if we need to migrate the labels
    if label_version != max(SUPPORTED_LABEL_VERSIONS):
        # Handle legacy compatibility mode by asking the user for the device
        try:
            ilcm: bool = is_legacy_compatiblity_mode(label_version, labels)
        except ValueError as e:
            print_critical_error(e)
        if ilcm:
            while (True):
                # Ask for what device the labels should be migrated
                print_info("The label file seems to be in legacy compatibility mode.", start="\n")
                device: str = input(colored("\tPlease select the device you wish to convert the composition to ['1' for Phone1 or '2' for Phone2]: ", color="cyan", attrs=["bold"]))
                device = device.strip().lower()

                if device in ['phone1', '1']:
                    print_info(f"No conversion needed. 0 conversion steps were conducted.")
                    break
                elif device in ['phone2', '2']:
                    print_info("Converting the labels to the Nothing Phone (2).")
                    labels, conversion_steps = convert_labels_to_phone2(labels)
                    if conversion_steps == 1:
                        print_info(f"Conversion successful! {conversion_steps} conversion step was conducted.")
                    else:
                        print_info(f"Conversion successful! {conversion_steps} conversion steps were conducted.")
                    break
                
                print_warning("Invalid device selection. Please select either 'Phone1' or 'Phone2' by typing it in.")
            
            # Debug print the labels
            print_debug("Converted labels:")
            for label in labels:
                print_debug(f"{label!r}")
            print_debug("")

        # Migrate the label file
        if label_version == 0: print_info(f"Migrating the legacy label file (v{label_version}) to the newest supported version (v{max(SUPPORTED_LABEL_VERSIONS)})", start="\n")
        else: print_info(f"Migrating the label file from v{label_version} to the newest supported version (v{max(SUPPORTED_LABEL_VERSIONS)})")
        migrated_labels, migration_steps = migrate_labels(copy.deepcopy(labels), label_version)
        print_debug(f"Migration steps: {migration_steps}")
        
        # Debug print the migrated labels
        print_debug("\nMigrated labels:")
        for label in migrated_labels:
            print_debug(f"{label!r}")
        print_debug("")

        if migration_steps == 1:
            print_info(f"Migration successful! {migration_steps} migration step was conducted.")
        else:
            print_info(f"Migration successful! {migration_steps} migration steps were conducted.")

        # Build the new filename
        label_file_ext_split = os.path.splitext(os.path.basename(args.LABEL_PATH[0]))
        new_label_file_path = os.path.join(args.output_path[0], label_file_ext_split[0] + '_migrated' + label_file_ext_split[1])
        
        # Write the migrated labels to the new file
        print_info(f"Writing the migrated label file to '{new_label_file_path}'")
        with open(new_label_file_path, 'w', newline='') as new_label_file:
            for label in migrated_labels:
                new_label_file.write(f"{label}\n")
    else:
        print_info(f"The label file is already on the newest version (v{max(SUPPORTED_LABEL_VERSIONS)}). No migration needed.")
        print_info(f"No file has been written!")

    cprint("Done!", color="green", attrs=["bold"])
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")
    # except Exception as e:
    #     printCriticalError(e)