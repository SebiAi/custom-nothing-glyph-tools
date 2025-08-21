#!/usr/bin/env python3

# VideoToPhone3NGlyph - A tool to convert a video file into the Glyph Tools
# intermediate file format called Nglyph. Can then be used with the
# "GlyphModder" script to create a valid composition for Nothing Phone (3).
# Copyright (C) 2025  Sebastian Aigner (aka. SebiAi)
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

import os
import argparse
import json

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
    import cv2
except ImportError:
    print("IMPORT ERROR: OpenCV is not installed. Please install it with 'pip install -U opencv-python-headless' and try again.")
    sys.exit(1)
try:
    import numpy as np
except ImportError:
    print("IMPORT ERROR: numpy is not installed. Please install it with 'pip install -U numpy' and try again.")
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
SCRIPT_VERSION = "1.0.0"

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(add_help=False, description="A tool to convert a video file into the Glyph Tools intermediate file format called Nglyph. Can then be used with the \"GlyphModder\" script to create a valid composition for Nothing Phone (3).", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    # Add the arguments
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.') # help
    parser.add_argument('VIDEO_PATH', help="A path to the video file.", type=str, nargs=1) # VIDEO_PATH
    parser.add_argument('--version', action='version', help='Show the version number and exit.', version=SCRIPT_VERSION) # version

    return parser

# Check the requirements
def check_requirements():
    pass

# Perform argument checks
def perform_checks(args: dict):
    # Check if the video file exists
    if 'VIDEO_PATH' in args and not os.path.isfile(args['VIDEO_PATH'][0]):
        raise Exception(f"Video file does not exist: '{args['VIDEO_PATH'][0]}'")

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

class GenericVideoToPhone3NGlyphError(Exception):
    """Custom exception for VideoToPhone3NGlyph errors."""
    pass

class InvalidVideoFileError(GenericVideoToPhone3NGlyphError):
    """Custom exception for invalid video file errors."""
    pass

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def frame_to_nglyph_csv(frame: np.ndarray) -> str:
    """Convert a video frame to grayscale CSV string.

    Args:
        frame (np.ndarray): The video frame to convert.

    Returns:
        str: The converted CSV string where each pixel value is scaled to 0-4095.
    """

    grayscale_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(grayscale_image, (25, 25), interpolation=cv2.INTER_NEAREST)
    assert resized_image.shape == (25, 25), f"Image must be 25x25 pixels, was {resized_image.shape}."

    flattened = resized_image.flatten("C")
    csv_data = np.interp(flattened, (0, 255), (0, 4095)).astype(np.uint16)  # Scale the values to 0-4095
    return ','.join(csv_data.astype(str))  # Convert to string and join with commas

def process_video(video_path: str) -> list[str]:
    nglyph_author_data: list[str] = []

    video_capture = cv2.VideoCapture(video_path)
    try: 
        if not video_capture.isOpened():
            raise InvalidVideoFileError(f"Could not open video file: {video_path}")

        success, frame = video_capture.read()
        while success:
            #cv2.imwrite(f"frames/frame_{len(nglyph_author_data)}.png", frame)
            csv_str = frame_to_nglyph_csv(frame) + ","
            nglyph_author_data.append(csv_str)
            success, frame = video_capture.read()

    finally:
        video_capture.release()

    return nglyph_author_data


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

    # Expand the paths
    args.VIDEO_PATH[0] = os.path.abspath(args.VIDEO_PATH[0])
    print_debug(f"expanded args: {args}")

    # Check the requirements
    check_requirements()

    # Perform all the checks
    try:
        perform_checks(args.__dict__)
    except Exception as e:
        print_critical_error(e)
    
    print_debug("")

    # Process the video
    print_info(f"Processing video: {args.VIDEO_PATH[0]}")
    author_data = process_video(args.VIDEO_PATH[0])

    # Get the file paths
    base_filename = os.path.splitext(os.path.basename(args.VIDEO_PATH[0]))[0]
    nglyph_file_path = os.path.join(os.path.abspath("."), base_filename + ".nglyph")
    print_info(f"Writing NGlyph file to '{nglyph_file_path}'")
    nglyph_data = {
        'VERSION': 1,
        'PHONE_MODEL': 'PHONE3',
        'AUTHOR': author_data,
        'CUSTOM1': ''
    }
    with open(nglyph_file_path, 'w', newline='\r\n', encoding='utf-8') as f:
        json.dump(nglyph_data, f, indent=4)
    
    cprint("Done!", color="green", attrs=["bold"])

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")
    # except Exception as e:
    #     printCriticalError(e)
