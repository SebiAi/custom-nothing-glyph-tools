#!/usr/bin/env python3

# GlyphModder - A tool to read/write glyph data from/to ringtones or notification sounds for Nothing devices.
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

# TODO: Make it possible to read files from stdin but make sure only one file is read from stdin: https://docs.python.org/3/library/fileinput.html
# TODO: Maybe create an interactive mode where the user can select the files and the output path if no arguments are given. Then also "pause" the console at the end so the user can see the output.

import sys

# Check the python version
if sys.version_info < (3, 10):
    print("This script requires Python 3.10 or higher! Please upgrade your python version and try again.")
    sys.exit(1)

import os
import argparse
import subprocess
import json
import csv
import re
import zlib
import copy
import math
import base64
from binascii import Error as BinasciiError
import shutil
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
    from cryptography.fernet import InvalidToken as FernetInvalidToken
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
SCRIPT_VERSION = "2.2.0"
SCRIPT_VERSION_MAJOR = SCRIPT_VERSION.split('.', 1)[0]

TIME_STEP_MS = 16.666

# Default values for the arguments
DEFAULT_ARGS = {
    'title': { 'value': ['MyCustomSong'], 'description': '' },
    'ffmpeg_path': { 'value': ['ffmpeg'], 'description': 'Tries to find ffmpeg on your system (PATH)' },
    'ffprobe_path': { 'value': ['ffprobe'], 'description': 'Tries to find ffprobe on your system (PATH)' },
    'output_path': { 'value': ['.'], 'description': 'The current working directory' }
}

# Enums
class Cols(Enum):
    FIVE_ZONE = 0
    FIFTEEN_ZONE = 1
    ELEVEN_ZONE = 2 # Unused
    THIRTY_THREE_ZONE = 3
    THREE_ZONE = 4 # Unused
    TWENTY_SIX_ZONE = 5
    THIRTY_SIX_ZONE = 6
    SIX_TWENTY_FIVE_ZONE = 7
class PhoneModel(Enum):
    PHONE1 = 0
    PHONE2 = 1
    PHONE2A = 2
    PHONE3A = 3
    PHONE3 = 4

# Cols lookup tables
STRING_TO_COLS: dict[Cols, str] = {
    Cols.FIVE_ZONE: '5cols',
    Cols.FIFTEEN_ZONE: '5cols',
    Cols.THIRTY_THREE_ZONE: '33cols',
    Cols.TWENTY_SIX_ZONE: '26cols',
    Cols.THIRTY_SIX_ZONE: '36cols',
    Cols.SIX_TWENTY_FIVE_ZONE: '625cols',
}
N_COLUMNS_TO_COLS = {
    5: Cols.FIVE_ZONE,
    15: Cols.FIFTEEN_ZONE,
    33: Cols.THIRTY_THREE_ZONE,
    26: Cols.TWENTY_SIX_ZONE,
    36: Cols.THIRTY_SIX_ZONE,
    625: Cols.SIX_TWENTY_FIVE_ZONE,
}

# Device codename lookup table (used for the composer tag)
DEVICE_CODENAME = {
    Cols.FIVE_ZONE: 'Spacewar',
    Cols.FIFTEEN_ZONE: 'Spacewar',
    Cols.THIRTY_THREE_ZONE: 'Pong',
    Cols.TWENTY_SIX_ZONE: 'Pacman',
    Cols.THIRTY_SIX_ZONE: 'Asteroids',
    Cols.SIX_TWENTY_FIVE_ZONE: 'Metroid',
}
STRING_COLS_TO_PHONE_MODEL = {
    '5cols': PhoneModel.PHONE1,
    '33cols': PhoneModel.PHONE2,
    '26cols': PhoneModel.PHONE2A,
    '36cols': PhoneModel.PHONE3A,
    '625cols': PhoneModel.PHONE3,
}

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(add_help=False, description="Read or write the Glyph metadata from or to ringtones/notification sounds for Nothing devices.", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    # General arguments
    global_argument_group = parser.add_argument_group(title='Global arguments', description="These arguments are used by all subcommands.")
    global_argument_group.add_argument('-o', '--output-path', help=f"The path where the processed files will be dropped. Can be an absolute or relative path. - default: '{DEFAULT_ARGS['output_path']['value'][0]}' -> {DEFAULT_ARGS['output_path']['description']}", type=str, nargs=1, default=copy.deepcopy(DEFAULT_ARGS['output_path']['value']), dest='output_path') # output_path
    global_argument_group.add_argument('--ffmpeg', help=f"Path to ffmpeg executable. - default: '{DEFAULT_ARGS['ffmpeg_path']['value'][0]}' -> {DEFAULT_ARGS['ffmpeg_path']['description']}", default=copy.deepcopy(DEFAULT_ARGS['ffmpeg_path']['value']), type=str, nargs=1, dest='ffmpeg_path') # ffmpeg_path
    global_argument_group.add_argument('--ffprobe', help=f"Path to ffprobe executable. - default: '{DEFAULT_ARGS['ffprobe_path']['value'][0]}' -> {DEFAULT_ARGS['ffprobe_path']['description']}", default=copy.deepcopy(DEFAULT_ARGS['ffprobe_path']['value']), type=str, nargs=1, dest='ffprobe_path') # ffprobe_path
    global_argument_group.add_argument('--disable-ff-v-check', help="WARNING: Only do this if you know what you are doing! Disable the version check for ffmpeg AND ffprobe.", action='store_true', dest='disable_ff_v_check') # disable_ff_v_check
    global_argument_group.add_argument('--version', action='version', help='Show the version number and exit.', version=SCRIPT_VERSION) # version
    global_argument_group.add_argument('-h', '--help', action='help', help='Show this help message and exit.')

    # Copy the parser for the subcommands - prevents the subcommands from inheriting themselves
    parent_parser = copy.deepcopy(parser)

    # Subcommands
    subparsers = parser.add_subparsers(title='Subcommands', help=f'Get additional help by entering "{SCRIPT_NAME} [subcommand] -h"', required=True, dest='subcommand') # subcommand

    # Write subcommand
    write_parser = subparsers.add_parser('write', aliases=['w'], help='Write metadata to the audio file.', parents=[parent_parser], add_help=False)
    write_argument_group = write_parser.add_argument_group(title='Write arguments', description="These arguments are used by the 'write' subcommand.")
    write_argument_group.add_argument('NGLYPH_PATH', help="A path to the nglyph file to write from.", type=str, nargs=1) # NGLYPH_PATH
    write_argument_group.add_argument('AUDIO_PATH', help="A path to the audio file to write to.", type=str, nargs=1) # AUDIO_PATH
    write_argument_group.add_argument('-t', help=f"What title to write into the metadata. - default: '{DEFAULT_ARGS['title']['value'][0]}'", default=copy.deepcopy(DEFAULT_ARGS['title']['value']), type=str, nargs=1, metavar=('TITLE'), dest='title') # title
    write_argument_group.add_argument('--auto-fix-audio', help="Do not ask for confirmation and automatically fix the audio file if the codec or extension is wrong.", action='store_true', dest='auto_fix_audio') # auto_fix_audio

    # Read subcommand
    read_parser = subparsers.add_parser('read', aliases=['r'], help='Read metadata from the audio file.', parents=[parent_parser], add_help=False)
    read_argument_group = read_parser.add_argument_group(title='Read arguments', description="These arguments are used by the 'read' subcommand.")
    read_argument_group.add_argument('AUDIO_PATH', help="A path to the audio file to read from.", type=str, nargs=1) # AUDIO_PATH

    return parser

# Check the requirements
def check_requirements(ffmpeg: str, ffprobe: str, write: bool, disable_ff_v_check: bool):
    if write:
        try:
            # Check if ffmpeg is installed - write metadata
            ffmpeg_result = subprocess.run([ffmpeg, "-version"],  capture_output=True, text=True)
            if ffmpeg_result.returncode != 0:
                raise FileNotFoundError
        except FileNotFoundError:
            print_critical_error(f"ffmpeg could not be found. ({ffmpeg})")
        
        if not disable_ff_v_check:
            # Check if the ffmpeg version is at least 4.4.0 or newer than 2021-04-08
            ffmpeg_version = re.search(r'ffmpeg version n?(\d+)\.(\d+)(?:\.(\d+))?', ffmpeg_result.stdout)
            ffmpeg_date = re.search(r'ffmpeg version (\d{4})-(\d{2})-(\d{2})|ffmpeg version N-\d+-\w+-(\d{4})(\d{2})(\d{2})', ffmpeg_result.stdout)

            # Check if we have a match
            if (ffmpeg_version is None) and (ffmpeg_date is None):
                print_critical_error(f"Could not check that the ffmpeg version is above 4.4.0 or newer than 2021-04-08! It you are sure that it is, you can disable this check by passing '--disable-ff-v-check' to the script. See '{SCRIPT_NAME} --help' for more info.")
            
            # Debug print the groups of the match
            print_debug(f"ffmpeg_version groups: {ffmpeg_version.groups() if ffmpeg_version is not None else None}")
            print_debug(f"ffmpeg_date groups: {ffmpeg_date.groups() if ffmpeg_date is not None else None}\n")

            # Map the version to an int tuple
            ffmpeg_version = tuple(map(lambda x: int(x) if x is not None else 0, ffmpeg_version.groups())) if ffmpeg_version is not None else None
            ffmpeg_date = tuple(int(x) for x in ffmpeg_date.groups() if x is not None) if ffmpeg_date is not None else None

            print_debug(f"ffmpeg_version: {ffmpeg_version}")
            print_debug(f"ffmpeg_date: {ffmpeg_date}\n")

            if ((ffmpeg_version is not None) and (ffmpeg_version < (4, 4, 0))) or ((ffmpeg_date is not None) and (ffmpeg_date < (2021, 4, 8))):
                print_critical_error(f"ffmpeg version is too old! (got: {ffmpeg_version if ffmpeg_version is not None else ffmpeg_date}, expected: 4.4.0 or higher or newer than 2021-04-08)")



    # We need ffprobe for both reading and writing (reading: get the metadata, writing: check the audio codec)
    try:
        # Check if ffprobe is installed - read metadata
        ffprobe_result = subprocess.run([ffprobe, "-version"],  capture_output=True, text=True)
        if ffprobe_result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        print_critical_error(f"ffprobe could not be found. ({ffprobe})")
    
    if not disable_ff_v_check:
        # Check if the ffprobe version is at least 4.4.0 or newer than 2021-04-08
        ffprobe_version = re.search(r'ffprobe version n?(\d+)\.(\d+)(?:\.(\d+))?', ffprobe_result.stdout)
        ffprobe_date = re.search(r'ffprobe version (\d{4})-(\d{2})-(\d{2})|ffprobe version N-\d+-\w+-(\d{4})(\d{2})(\d{2})', ffprobe_result.stdout)

        # Check if we have a match
        if (ffprobe_version is None) and (ffprobe_date is None):
            print_critical_error(f"Could not check that the ffprobe version is above 4.4.0 or newer than 2021-04-08! It you are sure that it is, you can disable this check by passing '--disable-ff-v-check' to the script. See '{SCRIPT_NAME} --help' for more info.")
        
        # Debug print the groups of the match
        print_debug(f"ffprobe_version groups: {ffprobe_version.groups() if ffprobe_version is not None else None}")
        print_debug(f"ffprobe_date groups: {ffprobe_date.groups() if ffprobe_date is not None else None}\n")

        # Map the version to an int tuple
        ffprobe_version = tuple(map(lambda x: int(x) if x is not None else 0, ffprobe_version.groups())) if ffprobe_version is not None else None
        ffprobe_date = tuple(int(x) for x in ffprobe_date.groups() if x is not None) if ffprobe_date is not None else None

        print_debug(f"ffprobe_version: {ffprobe_version}")
        print_debug(f"ffprobe_date: {ffprobe_date}\n")

        if ((ffprobe_version is not None) and (ffprobe_version < (4, 4, 0))) or ((ffprobe_date is not None) and (ffprobe_date < (2021, 4, 8))):
            print_critical_error(f"ffprobe version is too old! (got: {ffprobe_version if ffprobe_version is not None else ffprobe_date}, expected: 4.4.0 or higher or newer than 2021-04-08)")
    else:
        # Print a warning if the ff_v_check is disabled
        print_warning("The version check for ffmpeg and ffprobe is disabled!")
    

# Perform argument checks
def perform_checks(args: dict, write: bool):
    # Check if the file exists
    if not os.path.isfile(args['AUDIO_PATH'][0]):
        raise Exception(f"Audio file does not exist: '{args['AUDIO_PATH'][0]}'")

    # Check if we need to write metadata
    if write:
        # Check if the file exists
        if not os.path.isfile(args['NGLYPH_PATH'][0]):
            raise Exception(f"The nglyph file does not exist: '{args['NGLYPH_PATH'][0]}'")
    
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

# Class for the nglyph file
class NGlyphFile:
    # Constants
    SUPPORTED_FORMAT_VERSIONS = [1] # Will most of the time only contain one element, but we can add more if we want to support multiple versions

    # Exception for the NGlyphFile class
    class NGlyphFileException(Exception):
        pass
    
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.format_version: int = 0
        self.raw_data: bytes = b''
        self.data: dict[str, ] = {}

        self.phone_model: PhoneModel = PhoneModel.PHONE1
        self.author: AuthorData | None = None
        self.custom1: Custom1Data | None = None
        self.watermark: Watermark | None = None
        self.legacy: bool = False

        # Check the file extension
        if os.path.splitext(file_path)[1] != '.nglyph':
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - Wrong extension. If you have a glypha and glyphc1 file then please consult the documentation on how to migrate your composition to the new format.")
        
        # Open the file and read the content
        with open(file_path, 'rb') as f:
            self.raw_data = f.read()
        
        # Parse json
        try:
            self.data = json.loads(self.raw_data)
        except json.JSONDecodeError as e:
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - Could not parse the json data.")

        # Check the format version
        try:
            self.format_version = int(self.data['VERSION'])
        except (KeyError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No valid VERSION found.")
        print_debug(f"format_version: {self.format_version}")
        if self.format_version not in NGlyphFile.SUPPORTED_FORMAT_VERSIONS:
            max_version = max(NGlyphFile.SUPPORTED_FORMAT_VERSIONS)
            if self.format_version > max_version:
                raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not supported in this version of this script. Please update the script or use a different file.")
            else:
                raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not supported in this version of this script. Please check the documentation on how to migrate the file to a newer version.")
                
        
        # Get the phone model
        try:
            self.phone_model = PhoneModel[str(self.data['PHONE_MODEL'])]
        except (KeyError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No or invalid PHONE_MODEL found.")

        # Get the author data
        author: list[str] = []
        try:
            author = list(self.data['AUTHOR'])
        except (KeyError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No valid AUTHOR data found.")
        try:
            self.author = AuthorData(author)
        except AuthorData.AuthorDataException as e:
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - {e}.")
        
        # Get the custom1 data
        custom1: list[str] = []
        try:
            custom1 = list(self.data['CUSTOM1'])
        except (KeyError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No valid CUSTOM1 data found.")
        try:
            self.custom1 = Custom1Data(custom1)
        except Custom1Data.Custom1DataException as e:
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - {e}.")

        # Check if it is a legacy composition (pre 1.4.0 with desync issues)
        if self.data.get('LEGACY', None) is not None:
            try:
                if type(self.data['LEGACY']) is not bool:
                    raise ValueError("Not a boolean")
                self.legacy = bool(self.data['LEGACY'])
            except (KeyError, ValueError):
                raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No valid LEGACY data found.")

        # Stop if there is no watermark
        if self.data.get('WATERMARK', None) is None:
            return
        
        # Get the watermark
        watermark: list[str] = []
        try:
            watermark = list(self.data['WATERMARK'])
        except (KeyError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No valid WATERMARK data found.")
        watermark_str = '\n'.join(watermark)

        # Get the salt
        salt_str: str = ""
        try:
            salt_str = str(self.data['SALT'])
        except (KeyError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - No valid SALT data found.")
        salt: bytes = b''
        try:
            salt = base64.b64decode(salt_str, validate=True)
        except (BinasciiError, ValueError):
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - SALT data is not valid.")
        
        # Create the watermark
        try:
            self.watermark = Watermark(watermark_str, salt)
        except Watermark.WatermarkException:
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - SALT length is not valid.")

        # Decrypt the author data
        try:
            self.author.decrypt(self.watermark.to_key())
        except AuthorData.AuthorDataException as e:
            raise NGlyphFile.NGlyphFileException(f"File '{file_path}' is not a valid nglyph file - {e}.")

class AuthorData:
    # Exception for the AuthorData class
    class AuthorDataException(Exception):
        pass

    def __init__(self, data: list[str]):
        self.raw_data: bytes = b''
        self.data: list[list[int]] = []
        self.columns: int = 0
        self.columns_mode: Cols = Cols.FIFTEEN_ZONE

        # Get data and raw_data
        self._parse_author_data(data)

        # Throw an error if the data is empty
        if not self.data:
            raise AuthorData.AuthorDataException("AUTHOR data is empty")

        # Get the number of columns
        self.columns = len(self.data[0])

        # Check if the number of columns is the same for all lines
        for line in self.data:
            if len(line) != self.columns:
                raise AuthorData.AuthorDataException("AUTHOR data has different number of columns in some lines")
        
        # Get the columns mode
        try:
            self.columns_mode = N_COLUMNS_TO_COLS[self.columns]
        except KeyError:
            raise AuthorData.AuthorDataException("AUTHOR data has an invalid number of columns ({self.author_columns})")
    
    def _parse_author_data(self, data: list[str]):
        # Get data and raw_data
        self.raw_data = ('\r\n'.join(data) + '\r\n').encode('utf-8')
        try:
            reader = csv.reader(data, delimiter=',', strict=True)
            # Read the content and remove all empty elements and all empty lines
            self.data = [[int(e) for e in line if e.strip()] for line in list(reader) if ''.join(line).strip()]
        except (csv.Error, ValueError):
            raise AuthorData.AuthorDataException("AUTHOR data is not valid")

    def decrypt(self, key: bytes) -> None:
        f = Fernet(key)
        author_len = self.data[0][0]
        compressed_token = bytes([e for line in self.data for e in line][1:author_len+1]) # If author_len is invalid it does not throw an error here
        data: list[str] = []
        try:
            data = zlib.decompress(f.decrypt(zlib.decompress(compressed_token))).decode('utf-8').splitlines()
        except (zlib.error, FernetInvalidToken, UnicodeDecodeError):
            raise AuthorData.AuthorDataException("AUTHOR decryption failed")
        
        # Get data and raw_data
        self._parse_author_data(data)
    
    def encrypt(self, key: bytes) -> None:
        f = Fernet(key)
        compressed_token = zlib.compress(f.encrypt(zlib.compress('\r\n'.join([f"{','.join([str(e) for e in line])}," for line in self.data]).encode('utf-8'), zlib.Z_BEST_COMPRESSION)), zlib.Z_BEST_COMPRESSION)
        encrypt_author_data: list[list[int]] = [[0 for n_column in range(self.columns)] for n_row in range(math.ceil((len(compressed_token) + 1) / self.columns))]
        encrypt_author_data[0][0] = len(compressed_token)
        for i, byte in enumerate(compressed_token, 1):
            encrypt_author_data[i // self.columns][i % self.columns] = byte
        self._parse_author_data([f"{','.join([str(e) for e in line])}," for line in encrypt_author_data])

class Custom1Data:
    # Exception for the Custom1Data class
    class Custom1DataException(Exception):
        pass

    def __init__(self, data: list[str]):
        self.raw_data: bytes = b''
        self.data: list[list[int]] = []
        self.COLUMNS: int = 2

        # Get data and raw_data
        self.raw_data = (','.join(data) + ',').encode('utf-8')
        try:
            reader = csv.reader(data, delimiter=',', strict=True)
            # Read the content and remove all empty elements and all empty lines
            self.data = [[int(e) for e in line[0].split('-') if e.strip()] for line in list(reader) if line[0].strip()]
        except (csv.Error, ValueError):
            raise Custom1Data.Custom1DataException(f"CUSTOM1 data is not valid")

        # Check if the number of columns is the same for all lines
        for line in self.data:
            if len(line) != self.COLUMNS:
                raise Custom1Data.Custom1DataException("CUSTOM1 data has an invalid format")

class Watermark:
    # Exception for the Watermark class
    class WatermarkException(Exception):
        pass

    def __init__(self, watermark: str, salt: bytes = os.urandom(16)) -> None:
        self.content = watermark.replace('\r\n', '\n').replace('\r', '\n')
        self.salt = salt

        if len(self.salt) != 16:
            raise Watermark.WatermarkException("The salt has to be 16 bytes long.")
    
    def to_key(self) -> bytes:
        # Get the key for the watermark
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.content.encode('utf-8')))
        return key

class FFmpeg:
    # Exception for the FFmpeg class
    class FFmpegError(Exception):
        pass

    def __init__(self, ffmpeg_path: str, ffprobe_path: str):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.ffmpeg_base_command = [self.ffmpeg_path, '-v', 'error']
        self.ffprobe_base_command = [self.ffprobe_path, '-v', 'error', '-of', 'json']
    
    def write_metadata_to_audio_file(self, input_audio: str, output_file: str, metadata: dict[str, str]) -> None:
        # Construct the ffmetadata file content
        ffmetadata_content = ';FFMETADATA1\n' + '\n'.join([f"{self._escape_ffmetadata(key)}={self._escape_ffmetadata(value)}" for key, value in metadata.items()]) + '\n'
        
        # Construct the command
        ffmpeg_command = self.ffmpeg_base_command + ['-i', input_audio, '-i', '-', '-y']
        
        # Clear all the metadata we want to write - we want to keep the rest
        # Mapping the metadata from the input file does only merge the metadata, but we want to overwrite it
        for key in metadata.keys():
            ffmpeg_command += ['-metadata:s:a:0', f"{key}="]

        # Add the metadata
        ffmpeg_command += ['-map_metadata', '1', '-c:a', 'copy',
                          '-fflags', '+bitexact', '-flags:v', '+bitexact', '-flags:a', '+bitexact',
                          output_file]
        
        # Run the command and handle the result
        print_debug(f"ffmpeg_command: {ffmpeg_command}")
        result = subprocess.run(ffmpeg_command, input=ffmetadata_content.encode('utf-8'), capture_output=True, text=False) # This somehow fucks up on windows in text mode...
        if result.returncode != 0:
            raise FFmpeg.FFmpegError(f"Failed to write the metadata to the audio file: {result.stderr.decode('utf-8')}")
        
    def _escape_ffmetadata(self, content: str) -> str:
        # Special characters need to be escaped with a backslash ('\', '=', ';', '#', '\n')
        return content.replace('\\', '\\\\').replace('=', '\\=').replace(';', '\\;').replace('#', '\\#').replace('\n', '\\\n')

class AudioFile:
    # Exception for the AudioFile class
    class AudioFileError(Exception):
        pass

    def __init__(self, audio_path: str, ffmpeg: FFmpeg):
        self.audio_path = audio_path
        
        # Construct the ffprobe command
        ffprobe_command = ffmpeg.ffprobe_base_command + ['-show_streams', '-select_streams', 'a', audio_path]
        
        # Run the command and handle the result
        result = subprocess.run(ffprobe_command, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise AudioFile.AudioFileError(f"Failed to get the audio file metadata: {result.stderr}")
        
        # Parse the output as json
        try:
            self.metadata = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise AudioFile.AudioFileError(f"Failed to parse the ffprobe output: {e}")
        
        # Check if we have a stream
        if len(self.metadata['streams']) == 0:
            raise AudioFile.AudioFileError("The file has no audio streams. Did you pass in the right file?")

        # Check if we have more than one stream
        if len(self.metadata['streams']) > 1:
            print_warning("The file has more than one audio stream. Using the first one.", start="\t")
        
        # Check if the codec type is audio (Should never happen because we only return audio streams from ffprobe => assert)
        assert self.metadata['streams'][0]['codec_type'] == 'audio', "[Development Error] This file does not contain an audio stream. What happened here?"
    
    # Fix the audio codec. Returns the new path to the audio file.
    def fix_audio_codec(self, ffmpeg: FFmpeg, new_audio_path: str) -> str:
        assert new_audio_path != self.audio_path, "[Development Error] The new audio path is the same as the old one. What happened here?"

        ffmpeg_command = ffmpeg.ffmpeg_base_command + ['-y', '-i', self.audio_path, '-strict', '-2', '-c:a', 'opus', '-map_metadata', '0:s:a:0', '-fflags', '+bitexact', '-flags:v', '+bitexact', '-flags:a', '+bitexact', new_audio_path]

        result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise AudioFile.AudioFileError(f"Failed to fix the audio codec: {result.stderr}")

        self.audio_path = new_audio_path
        return new_audio_path

    # Fix the audio extension. Returns the new path to the audio file.
    def fix_audio_extension(self, new_audio_path: str) -> str:
        assert new_audio_path != self.audio_path, "[Development Error] The new audio path is the same as the old one. What happened here?"

        try:
            shutil.copy(self.audio_path, new_audio_path)
        except Exception as e:
            raise AudioFile.AudioFileError(f"Could not automatically fix the file extension. Please consult the documentation on how to fix it and try again: {e}")
        
        self.audio_path = new_audio_path
        return new_audio_path

    def get_audio_codec(self) -> str:
        return self.metadata['streams'][0]['codec_name']
    
    def get_tags(self) -> dict[str, str]:
        try:
            return self.metadata['streams'][0]['tags']
        except KeyError:
            return {}
    
    def get_audio_duration_ms(self) -> float:
        return float(self.metadata['streams'][0]['duration']) * 1000

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def decode_base64(data: str) -> bytes:
    # Remove all padding
    data_no_padding = data.rstrip('=')
    # Calculate the padding length (append '=' until the length is a multiple of 4)
    padding_length = (4 - (len(data_no_padding) % 4)) if (len(data_no_padding) % 4 != 0) else 0
    return base64.b64decode(data_no_padding + '=' * padding_length, validate=True)

def encode_base64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8').removesuffix('==').removesuffix('=')

def read_metadata_from_audio_file(audio_file: AudioFile, output_path: str, ffmpeg: FFmpeg) -> None:
    # Check the audio codec and print a warning if it is not opus
    audio_file_codec = audio_file.get_audio_codec()
    if audio_file_codec != "opus":
        print_warning(f"The audio file has the wrong codec (got: {audio_file_codec}, expected: opus). Please consult the documentation on how to fix it.", start="\t")
    # Check the audio extension and print a warning if it is not ogg
    audio_file_extension = os.path.splitext(audio_file.audio_path)[1]
    if audio_file_extension != '.ogg':
        print_warning(f"The audio file has the wrong extension (got: {audio_file_extension}, expected: .ogg). Please consult the documentation on how to fix it.", start="\t")
    
    # Get the tags
    tags = audio_file.get_tags()
    author_compressed_base64 = tags.get('AUTHOR', None)
    custom1_compressed_base64 = tags.get('CUSTOM1', None)
    custom2 = tags.get('CUSTOM2', STRING_TO_COLS[Cols.FIVE_ZONE]) # Default to 5 Column mode because the pre 1.4.0 compositions do not have this tag
    composer = tags.get('COMPOSER', None)
    watermark_str = tags.get('GLYPHER_WATERMARK', None)
    watermark = Watermark(watermark_str.removeprefix('\n')) if watermark_str is not None else None
    album = tags.get('ALBUM', None)

    # Check if the tags are present
    if author_compressed_base64 is None or custom1_compressed_base64 is None or custom2 is None or composer is None or album is None:
        print_critical_error("This is not a valid composition because the audio file does not contain the required metadata.", start="\t")

    # Check if we have a pre 1.4.0 composition
    is_legacy = False
    if not composer.startswith('v1-'):
        print_warning("This is an \"old\" composition. Depending on the length of it and if it was made with the old Glyph Tools (pre v1 Glyph Format), it might desync when playing it back on device or in the GlyphVisualizer!", start="\t")
        is_legacy = True

    # Legacy checks for other creation tools - 'v1-Glyphify' is fine
    if album == 'Glyphify':
        print_warning("This looks like an \"old\" Glyphify composition. Depending on the length of it, it might desync when playing it back on device or in the GlyphVisualizer!", start="\t")
        is_legacy = True
    ## https://github.com/Krishnagopal-Sinha/better-nothing-glyph-composer
    if album == 'custom':
        print_warning("This looks like an \"old\" better-nothing-glyph-composer composition. Depending on the length of it, it might desync when playing it back on device or in the GlyphVisualizer!", start="\t")
        is_legacy = True
    
    # Check if the custom2 tag is valid
    if custom2 not in STRING_COLS_TO_PHONE_MODEL.keys():
        print_critical_error(f"The custom2 tag is not valid ({custom2}). Is this a new phone?.", start="\t")

    # Remove the newlines from the base64 strings
    author_compressed_base64_debug = author_compressed_base64.replace('\n','\\n')
    custom1_compressed_base64_debug = custom1_compressed_base64.replace('\n','\\n')
    print_debug(f"author_compressed_base64: {author_compressed_base64_debug}", start="\t")
    print_debug(f"custom1_compressed_base64: {custom1_compressed_base64_debug}", start="\t")
    print_debug("", start="\t")
    author_compressed_base64 = author_compressed_base64.replace('\n','')
    custom1_compressed_base64 = custom1_compressed_base64.replace('\n','')
    print_debug(f"author_compressed_base64_lineless: {author_compressed_base64}", start="\t")
    print_debug(f"custom1_compressed_base64_lineless: {custom1_compressed_base64}", start="\t")


    # Print the number of bytes which have been read
    print(f"\tRead {colored(len(bytearray(author_compressed_base64, 'utf-8')), attrs=['bold'])} bytes of AUTHOR metadata")
    print(f"\tRead {colored(len(bytearray(custom1_compressed_base64, 'utf-8')), attrs=['bold'])} bytes of CUSTOM1 metadata")

    # Decode the base64 data
    try:
        author_compressed = decode_base64(author_compressed_base64)
        custom1_compressed = decode_base64(custom1_compressed_base64)
    except BinasciiError as e:
        print_critical_error(f"Failed to decode the base64 data. Is this a valid composition?: {e}", start="\t")
    print_debug(f"author_compressed: {author_compressed.hex()}", start="\t")
    print_debug(f"custom1_compressed: {custom1_compressed.hex()}", start="\t")

    # Decompress the data
    try:
        author_raw = zlib.decompress(author_compressed)
        custom1_raw = zlib.decompress(custom1_compressed)
    except zlib.error as e:
        print_critical_error(f"Failed to decompress the data. Is this a valid composition?: {e}", start="\t")

    # Get author data
    try:
        author = AuthorData(author_raw.decode('utf-8').splitlines())
    except (AuthorData.AuthorDataException, UnicodeDecodeError) as e:
        print_critical_error(f"Failed to parse the AUTHOR data. Is this a valid composition?: {e}", start="\t")
    
    # Get custom1 data
    try:
        custom1 = Custom1Data([e for e in custom1_raw.decode('utf-8').split(',') if e])
    except Custom1Data.Custom1DataException as e:
        print_critical_error(f"Failed to parse the CUSTOM1 data. Is this a valid composition?: {e}", start="\t")

    # Create the nglyph file
    nglyph_data = {
        'VERSION': 1,
        'PHONE_MODEL': STRING_COLS_TO_PHONE_MODEL[custom2].name,
        'AUTHOR': [],
        'CUSTOM1': [f"{'-'.join([str(e) for e in line])}" for line in custom1.data],
    }
    if watermark is not None:
        # If there is a new line at the end of the file splitlines() will not make an extra empty line => add one if needed
        nglyph_data['WATERMARK'] = watermark.content.splitlines() + ([''] if watermark.content.endswith('\n') else [])
        nglyph_data['SALT'] = base64.b64encode(watermark.salt).decode('utf-8')

        # Encrypt the author data
        author.encrypt(watermark.to_key())
    nglyph_data['AUTHOR'] = [f"{','.join([str(e) for e in line])}," for line in author.data]

    # Add legacy option if needed - was made pre 1.4.0 and might desync
    if is_legacy:
        nglyph_data['LEGACY'] = True

    # Get the filenames
    base_filename = os.path.splitext(os.path.basename(audio_file.audio_path))[0]
    nglyph_file_path = os.path.join(output_path, base_filename + ".nglyph")
    
    # Print info
    print_info(f"Writing the nglyph file to '{nglyph_file_path}'")
    
    # Write the nglyph file
    with open(nglyph_file_path, 'w', newline='\r\n', encoding='utf-8') as f:
        json.dump(nglyph_data, f, indent=4)


def write_metadata_to_audio_file(audio_file: AudioFile, nglyph_file: NGlyphFile, output_path: str, title: str, ffmpeg: FFmpeg, auto_fix_audio: bool) -> None:
    # Check if the audio file has the right codec and ask the user if we should fix it
    audio_file_codec = audio_file.get_audio_codec()
    audio_file_extension = os.path.splitext(audio_file.audio_path)[1]
    audio_file_path_fixed = os.path.splitext(audio_file.audio_path)[0] + "_fixed.ogg"
    if audio_file_codec != "opus":
        if auto_fix_audio:
            print_warning(f"The audio file has the wrong codec (got: {audio_file_codec}, expected: opus). Automatically fixing it.", start="\t")
        else:
            print_warning(f"The audio file has the wrong codec (got: {audio_file_codec}, expected: opus). Do you want to fix it? (Recommended) (Y/n): ", start="\t", end='')
            answer = input().lower()
            if answer == "n":
                print_critical_error("The audio file has the wrong codec. Please consult the documentation on how to fix it and try again.", start="\t")
        try:
            audio_file.fix_audio_codec(ffmpeg, audio_file_path_fixed)
        except AudioFile.AudioFileError as e:
            print_critical_error(e, start="\t")
    # Check if the audio file has the right extension and ask the user if we should fix it
    elif audio_file_extension != '.ogg':
        if auto_fix_audio:
            print_warning(f"The audio file has the wrong extension (got: {audio_file_extension}, expected: .ogg). Automatically fixing it.", start="\t")
        else:
            print_warning(f"The audio file has the wrong extension (got: {audio_file_extension}, expected: .ogg). Do you want to fix it? (Recommended) (Y/n): ", start="\t", end='')
            answer = input().lower()
            if answer == "n":
                print_critical_error("The audio file has the wrong extension. Please consult the documentation on how to fix it and try again.", start="\t")
        
        # Copy the file to the new path
        try:
            audio_file.fix_audio_extension(audio_file_path_fixed)
        except AudioFile.AudioFileError as e:
            print_critical_error(e, start="\t")

    # Check if the AUTHOR data has enough lines to play the whole song
    required_n_lines = math.ceil(audio_file.get_audio_duration_ms() / TIME_STEP_MS)
    if required_n_lines > len(nglyph_file.author.data):
        # Check if we are off by one line
        if required_n_lines - 1 == len(nglyph_file.author.data):
            # Add a new empty line to the author data
            nglyph_file.author.data.append([0 for _ in range(nglyph_file.author.columns)])
        else:
            # Print the error
            print_critical_error(f"The AUTHOR data does not have enough lines to play the whole song. Did you really place the 'END' Label at the end of the audio in Audacity? (Got: {len(nglyph_file.author.data)}, Expected: {required_n_lines})", start="\t")


    # Print the watermark
    if nglyph_file.watermark is not None:
        print_info("Watermark by creator detected - always give credit to the creator!", start="\t")
        print('\t' + nglyph_file.watermark.content.replace('\n', '\n\t') + '\n')
        

    # Compress the data
    author_compressed = zlib.compress(nglyph_file.author.raw_data, zlib.Z_BEST_COMPRESSION)
    custom1_compressed = zlib.compress(nglyph_file.custom1.raw_data, zlib.Z_BEST_COMPRESSION)

    # Encode the compressed data as base64
    author_compressed_base64 = encode_base64(author_compressed)
    custom1_compressed_base64 = encode_base64(custom1_compressed)

    # Add new lines to the base64 string every 76th character
    author_compressed_base64 = '\n'.join([author_compressed_base64[i:i+76] for i in range(0, len(author_compressed_base64), 76)]) + '\n'
    custom1_compressed_base64 = '\n'.join([custom1_compressed_base64[i:i+76] for i in range(0, len(custom1_compressed_base64), 76)]) + '\n'

    # Build the new filename
    audio_file_ext_split = os.path.splitext(os.path.basename(audio_file.audio_path))
    new_audio_file_path = os.path.join(output_path, audio_file_ext_split[0] + '_composed' + audio_file_ext_split[1])

    # Get the CUSTOM2 tag by reverse lookup STRING_TO_COLS to get the string from the enum
    custom2 = STRING_TO_COLS.get(nglyph_file.author.columns_mode, None)
    assert custom2 is not None, "[Development Error] Could not find the custom2 tag."

    # Construct the metadata
    metadata = {
        'TITLE': title,
        'ALBUM': f"Glyph Tools v{SCRIPT_VERSION_MAJOR}",
        'AUTHOR': author_compressed_base64,
        'COMPOSER': f"v1-{DEVICE_CODENAME[nglyph_file.author.columns_mode]} Glyph Composer",
        'CUSTOM1': custom1_compressed_base64,
        'CUSTOM2': custom2,
    }
    if nglyph_file.watermark is not None:
        metadata['GLYPHER_WATERMARK'] = '\n' + nglyph_file.watermark.content
    print_debug(f"metadata: {metadata}", start="\t")

    # Print info
    print_info(f"Writing the composition to '{new_audio_file_path}'", start="\t")

    # Write the metadata to the audio file
    try:
        ffmpeg.write_metadata_to_audio_file(audio_file.audio_path, new_audio_file_path, metadata)
    except FFmpeg.FFmpegError as e:
        print_critical_error(e, start="\t")

    # Print the number of bytes which have been written
    print(f"\tWrote {colored(len(bytearray(author_compressed_base64, 'utf-8')), attrs=['bold'])} bytes of AUTHOR metadata")
    print(f"\tWrote {colored(len(bytearray(custom1_compressed_base64, 'utf-8')), attrs=['bold'])} bytes of CUSTOM1 metadata")    


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
        print_info(f"Using GlyphModder version v{SCRIPT_VERSION}")

    # Parse the arguments
    args = build_arguments_parser().parse_args()
    print_debug(f"args: {args}")

    # Check if we read or write the metadata
    write: bool = False
    if args.subcommand == "write" or args.subcommand == "w":
        write = True
    elif args.subcommand == "read" or args.subcommand == "r":
        write = False
    else:
        print_critical_error(f"[Development Error] Invalid subcommand: '{args.subcommand}'", 2)
    print_debug(f"write: {write}")

    # Expand the paths
    args.AUDIO_PATH[0] = os.path.abspath(args.AUDIO_PATH[0])
    if write:
        args.NGLYPH_PATH[0] = os.path.abspath(args.NGLYPH_PATH[0])
    if args.ffmpeg_path[0] != DEFAULT_ARGS['ffmpeg_path']['value'][0]:
        args.ffmpeg_path[0] = os.path.abspath(args.ffmpeg_path[0])
    if args.ffprobe_path[0] != DEFAULT_ARGS['ffprobe_path']['value'][0]:
        args.ffprobe_path[0] = os.path.abspath(args.ffprobe_path[0])
    args.output_path[0] = os.path.abspath(args.output_path[0])
    print_debug(f"expanded args: {args}")

    # Check the requirements
    check_requirements(args.ffmpeg_path[0], args.ffprobe_path[0], write, args.disable_ff_v_check)

    # Perform all the checks
    try:
        perform_checks(args.__dict__, write)
    except Exception as e:
        print_critical_error(e)
    
    print_debug("")

    # Create ffmpeg object
    ffmpeg = FFmpeg(args.ffmpeg_path[0], args.ffprobe_path[0])

    # Create the audio file object
    try:
        audio_file = AudioFile(args.AUDIO_PATH[0], ffmpeg)
    except AudioFile.AudioFileError as e:
        print_critical_error(e)

    if write:
        # Create a nglyph object
        try:
            nglyph_file = NGlyphFile(args.NGLYPH_PATH[0])
        except NGlyphFile.NGlyphFileException as e:
            print_critical_error(e)

        # Print legacy warning
        if nglyph_file.legacy:
            print_warning("This is an \"old\" composition. Depending on the length of it, it might desync when playing it back on device or in the GlyphVisualizer!")

        print_info("Writing metadata to the audio file...")
        write_metadata_to_audio_file(audio_file, nglyph_file, args.output_path[0], args.title[0], ffmpeg, args.auto_fix_audio)
    else:
        print_info("Reading metadata from the audio file...")
        read_metadata_from_audio_file(audio_file, args.output_path[0], ffmpeg)


    cprint("Done!", color="green", attrs=["bold"])
    return 0



if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")
    # except Exception as e:
    #     printCriticalError(e)
