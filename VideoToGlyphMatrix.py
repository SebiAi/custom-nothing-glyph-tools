#!/usr/bin/env python3

# VideoToGlyphMatrix - A tool to convert a video file into the Glyph Tools
# intermediate file format called Nglyph. Can then be used with the
# "GlyphModder" script to create a valid composition for Nothing
# Phones with a Glyph Matrix.
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

from dataclasses import dataclass
from typing import TypedDict
import os
import argparse
import json
import logging

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
# |          Class Definitions         |
# |                                    |
# +------------------------------------+

class NGlyphData(TypedDict):
    VERSION: int
    PHONE_MODEL: str
    AUTHOR: list[str]
    CUSTOM1: str

class GenericVideoToPhone3NGlyphError(Exception):
    """Custom exception for VideoToPhone3NGlyph errors."""
    pass

class InvalidVideoFileError(GenericVideoToPhone3NGlyphError):
    """Custom exception for invalid video file errors."""
    pass

@dataclass
class DeviceInfo:
    """Data class to store device information."""
    model: str
    matrix_size: tuple[int, int]
    target_fps: float

# +------------------------------------+
# |                                    |
# |              Globals               |
# |                                    |
# +------------------------------------+

logger = logging.getLogger(__name__)

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
# Get the script name
SCRIPT_NAME = os.path.basename(__file__)

# Version of the script
SCRIPT_VERSION = "1.0.0"


PHONE_MODEL_INFO = {
    'PHONE3': DeviceInfo(model='PHONE3', matrix_size=(25, 25), target_fps=60.0),
    'PHONE4APRO': DeviceInfo(model='PHONE4APRO', matrix_size=(13, 13), target_fps=60.0)
}

PHONE_MODEL_ARGUMENT = 'PHONE_MODEL'
VIDEO_PATH_ARGUMENT = 'VIDEO_PATH'

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(add_help=False, description="A tool to convert a video file into the Glyph Tools intermediate file format called Nglyph. Can then be used with the \"GlyphModder\" script to create a valid composition for Nothing Phones with a Glyph Matrix.", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    # Add the arguments
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.') # help
    parser.add_argument(PHONE_MODEL_ARGUMENT, help="The phone model to target.", type=str, nargs=1, choices=list(PHONE_MODEL_INFO.keys()))
    parser.add_argument(VIDEO_PATH_ARGUMENT, help="A path to the video file.", type=str, nargs=1)
    parser.add_argument('--version', action='version', help='Show the version number and exit.', version=SCRIPT_VERSION) # version

    return parser

# Check the requirements
def check_requirements():
    pass

# Perform argument checks
def perform_checks(args: dict[str, list[str]]):
    # Check if the video file exists
    if VIDEO_PATH_ARGUMENT in args and not os.path.isfile(args[VIDEO_PATH_ARGUMENT][0]):
        raise Exception(f"Video file does not exist: '{args[VIDEO_PATH_ARGUMENT][0]}'")

class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        start = getattr(record, "start", "")
        message = record.getMessage()
        match record.levelno:
            case logging.DEBUG:
                return colored(f"{start}DEBUG: {message}", color="grey")
            case logging.INFO:
                return colored(f"{start}INFO: {message}", color="cyan")
            case logging.WARNING:
                return colored(f"{start}WARNING: {message}", color="yellow", attrs=["bold"])
            case logging.ERROR | logging.CRITICAL:
                return colored(f"{start}ERROR: {message}", color="red", attrs=["bold"])
            case _: pass
        return f"{start}{message}"

def setup_logger():
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(ColoredFormatter())
    # Only pass messages below ERROR to stdout
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(ColoredFormatter())

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    # Fix the windows console - needed for correct color output
    just_fix_windows_console()

# Print critical error message and exit
def print_critical_error(message: str, exitCode: int = 1, start: str = "", **args):
    logger.error(message, extra={"start": start})
    #raise Exception(message)
    sys.exit(exitCode)

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def frame_to_nglyph_csv(frame: np.ndarray, resize_size: tuple[int, int]) -> str:
    """Convert a video frame to grayscale CSV string.

    Args:
        frame (np.ndarray): The video frame to convert.
        resize_size (tuple[int, int]): The size to resize the frame to - if need be.

    Returns:
        str: The converted CSV string where each pixel value is scaled to 0-4095.
    """

    grayscale_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(grayscale_image, resize_size, interpolation=cv2.INTER_NEAREST)
    assert resized_image.shape == resize_size, f"Image must be {resize_size[0]}x{resize_size[1]} pixels, was {resized_image.shape}."

    flattened = resized_image.flatten("C")
    csv_data = np.interp(flattened, (0, 255), (0, 4095)).astype(np.uint16)  # Scale the values to 0-4095
    return ','.join(csv_data.astype(str))  # Convert to string and join with commas

def _process_video_precise(video_capture: cv2.VideoCapture, target_device: DeviceInfo, total_output_frames: int) -> list[str]:
    nglyph_author_data: list[str] = []

    last_progress_update = 0.0
    for current_frame_index in range(total_output_frames):
        logger.debug(f"Processing frame {current_frame_index}/{total_output_frames}")
        success, frame = video_capture.read()  # Read the next frame from the video
        if not success:
            logger.warning(f"Could not read frame from input video for NGlyph frame {current_frame_index}/{total_output_frames}. Stopping video processing.")
            break

        #cv2.imwrite(f"frames/frame_{len(nglyph_author_data)}.png", frame)
        csv_str = f"{frame_to_nglyph_csv(frame, target_device.matrix_size)},"
        nglyph_author_data.append(csv_str)

        progress = current_frame_index / total_output_frames * 100
        if progress - last_progress_update >= 5.0:  # Update progress every 5%
            logger.info(f"Progress: {int(progress)}%")
            last_progress_update = progress

    return nglyph_author_data

def _process_video_interpolated(video_capture: cv2.VideoCapture, target_device: DeviceInfo, video_fps: float, total_output_frames: int) -> list[str]:
    nglyph_author_data: list[str] = []
    
    last_progress_update = 0.0
    last_target_frame_index = -1
    for current_frame_index in range(total_output_frames):
        target_time_s = (current_frame_index / target_device.target_fps)
        target_frame_index = int(target_time_s * video_fps)

        if last_target_frame_index == target_frame_index:
            logger.debug(f"Using cached frame for frame index {current_frame_index} (target frame index {target_frame_index}).")
            nglyph_author_data.append(nglyph_author_data[-1])  # Append the last frame's CSV string again, because it is the same as the target frame index
            continue  # We can skip the decoding and just use the cached frame, because it is the same as the target frame index
        
        # greater equal because we only can decode the target frame after grabbing it
        while target_frame_index >= int(video_capture.get(cv2.CAP_PROP_POS_FRAMES)):
            success = video_capture.grab()  # Grab the next frame without decoding it, to move the video forward
            if not success:
                logger.warning(f"Could not grab frame at {target_time_s * 1000:.2f} ms (frame {target_frame_index}/{int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))}) from input video for NGlyph frame {current_frame_index}/{total_output_frames}. Stopping video processing.")
                return nglyph_author_data
        
        logger.debug(f"Processing frame {current_frame_index}/{total_output_frames} at {target_time_s * 1000:.2f} ms => frame index {target_frame_index} of the input video.")
        success, frame = video_capture.retrieve()  # Retrieve the grabbed frame and decode it
        if not success:
            logger.warning(f"Could not decode frame at {target_time_s * 1000:.2f} ms (frame {target_frame_index}/{int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))}) from input video for NGlyph frame {current_frame_index}/{total_output_frames}. Stopping video processing.")
            break

        #cv2.imwrite(f"frames/frame_{len(nglyph_author_data)}.png", frame)
        csv_str = f"{frame_to_nglyph_csv(frame, target_device.matrix_size)},"
        nglyph_author_data.append(csv_str)
        last_target_frame_index = target_frame_index

        progress = current_frame_index / total_output_frames * 100
        if progress - last_progress_update >= 5.0:  # Update progress every 5%
            logger.info(f"Progress: {int(progress)}%")
            last_progress_update = progress
    
    return nglyph_author_data

def process_video(video_path: str, target_device: DeviceInfo) -> list[str]:
    video_capture = cv2.VideoCapture(video_path)
    try: 
        if not video_capture.isOpened():
            raise InvalidVideoFileError(f"Could not open video file: {video_path}")

        fps_match = True
        video_fps = video_capture.get(cv2.CAP_PROP_FPS)
        if video_fps != target_device.target_fps:
            fps_match = False
            logger.warning(f"{target_device.model} expects a video with {target_device.target_fps} FPS, but the input video has {video_fps} FPS. Make sure the video you are using has a constant {target_device.target_fps} FPS. Using basic interpolation...")

        video_length_ms = (int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) / video_fps) * 1000
        total_output_frames = int(video_length_ms / 1000 * target_device.target_fps)
        logger.debug(f"fps={video_fps}")
        logger.debug(f"video_length_ms={video_length_ms}")
        logger.debug(f"frames_in_output={total_output_frames}")

        if fps_match:
            return _process_video_precise(video_capture, target_device, total_output_frames)
        else:
            return _process_video_interpolated(video_capture, target_device, video_fps, total_output_frames)
    finally:
        video_capture.release()


# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

def main() -> int:
    setup_logger()

    # Parse the arguments
    args = build_arguments_parser().parse_args()
    logger.debug(f"args: {args}")

    # Get arguments
    video_path = os.path.abspath(str(args.__dict__[VIDEO_PATH_ARGUMENT][0]))
    phone_model_str = str(args.__dict__[PHONE_MODEL_ARGUMENT][0])
    logger.debug(f"video_path={video_path!r}")
    logger.debug(f"phone_model_str={phone_model_str!r}")

    # Check the requirements
    check_requirements()

    # Perform all the checks
    try:
        perform_checks(args.__dict__)
    except Exception as e:
        print_critical_error(str(e))
    
    logger.debug("")

    # Get the device info
    device_info = PHONE_MODEL_INFO[phone_model_str]
    logger.debug(f"device_info={device_info!r}")

    # Process the video
    logger.info(f"Processing video: {video_path}")
    author_data = process_video(video_path, device_info)

    # Get the file paths
    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    nglyph_file_path = os.path.join(os.path.abspath("."), base_filename + ".nglyph")
    logger.info(f"Writing NGlyph file to '{nglyph_file_path}'")
    nglyph_data: NGlyphData = {
        'VERSION': 1,
        'PHONE_MODEL': device_info.model,
        'AUTHOR': author_data,
        'CUSTOM1': ''
    }
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
