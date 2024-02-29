#!/usr/bin/env python3

# This script is inspired by @nocturnalsushi on the Nothing Discord, and upgraded by @sebiai

import sys

# Check the python version
if sys.version_info < (3, 10):
    print("This script requires Python 3.10 or higher! Please upgrade your python version and try again.")
    sys.exit(1)

import os
import argparse
import csv
import copy
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

# Default values for the arguments
DEFAULT_ARGS = { 'files': [''], 'output': ['./combined.glypha'] }

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(description="Merge multiple glypha files (append each line). The first file will be the base where all the other files will be appended to line by line. Can be used to create a 15 Zone composition for the Phone (1) out of three compatibility glypha files. For tutorial: https://www.youtube.com/watch?v=WAkBL5NOaEY", epilog="Created by: Sebastian Aigner (aka. SebiAi)")
    
    # Add the arguments
    parser.add_argument('files', help="The files to merge. The first file will be first, the second one second and so on. Can be multiple files separated by a space. Remember: Put quotes arround the path if it contains spaces!", type=str, nargs='+', metavar="FILES") # files
    parser.add_argument('-o', '--output', help=f"A path to a file to write the output to. Can be an absolute or relative path to the file. - default: '{DEFAULT_ARGS['output'][0]}'", type=str, nargs=1, default=copy.deepcopy(DEFAULT_ARGS['output']), dest='output') # output
    
    return parser

# Check the requirements
def check_requirements():
    pass

# Perform argument checks
def perform_checks(args: dict):
    # Check if the files list is empty
    if not args.get('files', False):
        raise Exception(f"No files given. See '{SCRIPT_NAME} --help' for more information.")

    # Check if we have at least two files
    if len(args['files']) < 2:
        raise Exception(f"Trying to merge only one file does not really make sense, eh? Try providing at least two O_o. See '{SCRIPT_NAME} --help' for more information.")
    
    # Check if all the files exist and have the right extension
    for file in args['files']:
        if not os.path.isfile(file):
            raise Exception(f"File '{file}' does not exist.")
        if not file.endswith(".glypha"):
            raise Exception(f"File '{file}' is not a glypha file.")
    
    # Check if the directory structure of the output file exists
    if not os.path.isdir(os.path.dirname(args['output'][0])):
        raise Exception(f"Can't write the output file there! The directory structure does not exist: '{os.path.dirname(args['output'][0])}'")
    
    # Check if the output file is a directory
    if os.path.isdir(args['output'][0]):
        raise Exception(f"Output file '{args['output'][0]}' is a directory. Please specify a file name!")

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

# Exception for the GlyphaFile class
class GlyphaFileException(Exception):
    pass

# Class for the glypha file
class GlyphaFile:
    def __init__(self, file: str):
        self.file = file
        self.content: list[list[str]] = []
        self.columns: int = 0

        # Open the file and read the content
        with open(file, newline='', encoding='utf-8') as f:
            try:
                reader = csv.reader(f, delimiter=',', strict=True)
                # Read the content and remove all empty elements and all empty lines
                self.content = [[e for e in line if e.strip()] for line in list(reader) if ''.join(line).strip()]
            except csv.Error as e:
                raise GlyphaFileException(f"File '{file}' is not a valid csv file.")
        
        # Throw an error if the file is empty
        if not self.content:
            raise GlyphaFileException(f"File '{file}' is empty.")

        # Get the number of columns
        self.columns = len(self.content[0])

        # Check if the number of columns is the same for all lines
        for line in self.content:
            if len(line) != self.columns:
                raise GlyphaFileException(f"File '{file}' has different number of columns in some lines.")

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+



# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

def main() -> int:
    # Fix the windows console - needed for correct color output
    just_fix_windows_console()

    # Parse the arguments
    args = build_arguments_parser().parse_args()
    print_debug(f"args: {args}")

    # Check the requirements
    check_requirements()

    # Expand the output path
    args.output[0] = os.path.abspath(args.output[0])

    # Perform all the checks
    try:
        perform_checks(args.__dict__)
    except Exception as e:
        print_critical_error(e)
    
    # Get the files
    print_info(f"Reading the {len(args.files)} file(s)...")
    try:
        glypha_files = [GlyphaFile(file) for file in args.files]
    except GlyphaFileException as e:
        print_critical_error(e)
    
    # Get the largest number of lines
    max_lines = max([len(file.content) for file in glypha_files])

    # Loop through all the lines
    print_info(f"Combining the file(s)...")
    output: list[list[str]] = []
    for i in range(max_lines):
        line: list[str] = []
        for file in glypha_files:
            try:
                line += file.content[i]
            except IndexError:
                line += ['0' for _ in range(file.columns)]
        output.append(line)
    
    # Check if the output file already exists
    print_info(f"Writing output...")
    if os.path.isfile(args.output[0]):
        print_warning(f"Output file '{args.output[0]}' already exists. Do you want to overwrite it? (y/N): ", end="")
        if input().strip().lower() != "y":
            print_critical_error("Aborted by user.", 0)

    # Write the output to a file
    print_info(f"The output file will be written to: '{args.output[0]}'")
    with open(args.output[0], "w", newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter=',', lineterminator=',\r\n', strict=True).writerows(output)
    
    cprint("Done!", color="green", attrs=["bold"])
    
    return 0

    


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")
    # except Exception as e:
    #     printCriticalError(e)
