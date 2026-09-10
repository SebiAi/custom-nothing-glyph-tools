#!/usr/bin/env python3

# VideoToGlyphMatrix - A tool to convert select glyph data formats into
# the Glyph Tools intermediate file format called Nglyph. Can then
# be used with the "GlyphModder" script to create a valid composition
# for Nothing Phones.
# Idea by "little ica apologist" (@lagartoeldelagartosdelrey on Discord)
# Copyright (C) 2026  Sebastian Aigner (aka. SebiAi)
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

from abc import ABC, abstractmethod
import argparse
from bisect import bisect_right
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
import io
import json
import logging
import math
from pathlib import Path
import re
import sys
from typing import IO, Any, TypedDict, BinaryIO, Optional, NotRequired, cast
from contextlib import contextmanager
from collections.abc import Generator
import tempfile
import shutil

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
    import jsonschema
except ImportError:
    print("IMPORT ERROR: jsonschema is not installed. Please install it with 'pip install -U jsonschema' and try again.")
    sys.exit(1)

# +------------------------------------+
# |                                    |
# |          Class Definitions         |
# |                                    |
# +------------------------------------+


class GenericConversionError(Exception):
    """Custom exception for conversion errors."""
    pass
class UnsupportedFormatError(GenericConversionError):
    """Exception raised when the input format is not supported."""
    pass
class PhoneModelNotSupportedError(GenericConversionError):
    """Exception raised when the target phone model is not supported."""
    pass
class ConversionError(GenericConversionError):
    """Exception raised during conversion when an error occurs."""
    pass

class PhoneModel(Enum):
    PHONE3 = "Phone (3)"
    PHONE4APRO = "Phone (4a) Pro"

@dataclass
class DeviceInfo:
    """Data class to store device information."""
    model: PhoneModel
    supported_zones: list[int]
    target_fps: float


ReadableData = str | bytes | IO[Any]

class NGlyphDictData(TypedDict):
    """Dictionary definition for NGlyph data"""
    VERSION: int
    PHONE_MODEL: str
    AUTHOR: list[str]
    CUSTOM1: list[str]

@dataclass
class NGlyphData:
    """Data class for NGlyph data"""
    PHONE_MODEL: str
    AUTHOR: list[str]
    CUSTOM1: list[str]
    VERSION: int = 1

    def to_dict(self) -> NGlyphDictData:
        """Convert NGlyphData to a dictionary format."""
        return NGlyphDictData(
            VERSION=self.VERSION,
            PHONE_MODEL=self.PHONE_MODEL,
            AUTHOR=self.AUTHOR,
            CUSTOM1=self.CUSTOM1
        )


class AToNGlyphConverter(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the converter. Should be implemented by subclasses."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a brief description of the converter. Should be implemented by subclasses."""
        pass

    @abstractmethod
    def can_convert_to(self, input_data: ReadableData) -> list[DeviceInfo]:
        """Determine if the converter can handle the given input data.

        Args:
            input_data (ReadableData): The input data to check for compatibility.

        Returns:
            list[DeviceInfo]: A list of supported devices depending on the input data.
            If empty, the converter cannot handle the input data.
        """
        pass 

    def convert(self, input_data: ReadableData, to_device: DeviceInfo, duration: Optional[timedelta], offset: Optional[timedelta]) -> NGlyphData:
        """Convert the input data to NGlyph format.

        Args:
            input_data (ReadableData): The input data to convert.
            to_device (DeviceInfo): The target device.
            duration (Optional[timedelta]): The target duration for the converted animation. If None,
                the original duration will be kept.
            offset (Optional[timedelta]): The positive offset into the source animation. If None,
                the animation starts at time 0.

        Raises:
            UnsupportedFormatError: Raised if the input data format is not supported.
            PhoneModelNotSupportedError: Raised if the target phone model is not supported.

        Returns:
            NGlyphData: The converted NGlyph data.
        """
        supported_devices = self.can_convert_to(input_data)
        if isinstance(input_data, io.IOBase):
            input_data.seek(0) # Reset file pointer after checking compatibility

        if not supported_devices:
            raise UnsupportedFormatError("Input data format is not supported by this converter.")

        if to_device not in supported_devices:
            raise PhoneModelNotSupportedError("Target phone model is not supported.")

        converted_data = self._convert(input_data, to_device, duration, offset)

        assert converted_data.PHONE_MODEL == to_device.model.name, "[Development Error] Converted data's phone model does not match the target device's model."
        assert any([frame.endswith(',') for frame in converted_data.AUTHOR]), "[Development Error] At least one frame in the AUTHOR field does not end with a comma."
        assert self._has_2d_list_consistent_length([frame.removesuffix(',').split() for frame in converted_data.AUTHOR]), "[Development Error] Converted data's AUTHOR field does not have a consistent frame length."

        return converted_data

    @abstractmethod
    def _convert(self, input_data: ReadableData, to_device: DeviceInfo, duration: Optional[timedelta], offset: Optional[timedelta]) -> NGlyphData:
        """Internal method to perform the actual conversion. Should be implemented by subclasses.
        Will be called by the public convert method after checking for compatibility and if the 
        target device is supported.

        Args:
            input_data (ReadableData):  The input data to convert.
            to_device (DeviceInfo): The target device.
            duration (Optional[timedelta]): The target duration for the converted animation. If None,
                the original duration should be kept. If shorter than the original duration, the
                animation should be cut off. If longer, the animation should be looped to fill the duration.
            offset (Optional[timedelta]): The positive offset into the source animation. If None,
                the animation starts at time 0.

        Raises:
            ConversionError: Raised if an error occurs during conversion.

        Returns:
            NGlyphData: The converted NGlyph data.
        """
        pass

    @staticmethod
    def _has_2d_list_consistent_length(list_2d: list[list[Any]]) -> bool:
        """Helper to determine if a 2 dimensional list has the same number of elements
        in each list.

        Args:
            list_2d (list[list[Any]]): The list to check.

        Returns:
            bool: True if all inner lists have the same length or if the outer list is empty, False otherwise.
        """
        if len(list_2d) == 0:
            return True

        expected_length = len(list_2d[0])
        if any(len(l) != expected_length for l in list_2d):
            return False
        return True
    
    @staticmethod
    def _to_author(frames: list[list[int]]) -> list[str]:
        """Helper to properly convert frames to the author data.

        Args:
            frames (list[list[int]]): 2D list aka. frames.

        Returns:
            list[str]: The author data.
        """
        return [','.join(str(x) for x in data)+',' for data in frames]
    
    @staticmethod
    def _build_author_data_from_frames(frames: list[list[int]], frame_durations_s: list[float], total_frame_count: int, target_fps: float, offset_s: float = 0.0) -> list[list[int]]:
        """Helper to generate all the author data from an animation (frames, frame durations) and
        the how many frames should be generated based on the target fps and duration.
        Will loop the animation if the total duration is longer than the animation duration, or cut it off if
        it is shorter.

        Args:
            frames (list[list[int]]): The individual frames of the animation to use. Should have
                the right zone count and value range for the target device already.
            frame_durations_s (list[float]): How long each frame of the animation should be shown,
                in seconds.
            total_frame_count (int): How many frames should be generated in total.
            target_fps (float): The target frames per second for the animation.
            offset_s (float): The offset in seconds for the animation.

        Returns:
            list[list[int]]: The generated author data.
        """
        if not frames or\
            not frame_durations_s or\
            total_frame_count <= 0 or\
            target_fps <= 0 or\
            len(frames) != len(frame_durations_s):
            return []

        frame_end_times_s: list[float] = []
        running_time_s = 0.0
        for duration_s in frame_durations_s:
            running_time_s += duration_s
            frame_end_times_s.append(running_time_s)
        logger.debug(f'frame_end_times_s={frame_end_times_s}')

        animation_duration_s = frame_end_times_s[-1] if frame_end_times_s else 0.0
        logger.debug(f'animation_duration_s={animation_duration_s}')

        # Sample frames for each target frame based on the target fps and duration.
        logger.debug(f'Current Frame Index | Total Animation Time (s) | Animation Time (s) | Frame Index Used')
        author_data: list[list[int]] = []
        for current_frame_index in range(total_frame_count):
            total_animation_time_s = current_frame_index / target_fps
            animation_time_s = (total_animation_time_s + offset_s) % animation_duration_s
            frame_index = bisect_right(frame_end_times_s, animation_time_s)
            if frame_index >= len(frames):
                frame_index = len(frames) - 1
            logger.debug(f'{current_frame_index:>6} {total_animation_time_s:>10.4f} {animation_time_s:>10.4f} {frame_index:>6}')
            author_data.append(frames[frame_index])
        
        return author_data
    
    @staticmethod
    def _input_to_json(input_data: ReadableData, schema: Optional[dict[str, Any]]) -> Optional[Any]:
        """Convert the input to a JSON object with optional schema validation.

        Args:
            input_data (ReadableData): The input data to convert.
            schema (Optional[dict[str, Any]]): The JSON schema to validate against.
                If None, no validation will be performed.

        Returns:
            Optional[Any]: The converted JSON object, or None if conversion or validation fails.
        """
        try:
            if isinstance(input_data, (str, bytes)):
                data = json.loads(input_data)
            elif isinstance(input_data, io.IOBase):
                data = json.load(input_data)
            else:
                return None
        except:
            return None

        if schema:
            try:
                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.ValidationError as e:
                logger.debug(f"JSON schema validation failed: {e}")
                return None
        
        return data

# +------------------------------------+
# |                                    |
# |         Converter Classes          |
# |                                    |
# +------------------------------------+

class PauwmaGlyphMuseumConverter(AToNGlyphConverter):
    # If there is only one frame, no duration is given => Assume one frame if no duration is given, otherwise stretch.
    # If there are multiple frames, a duration is given for each frame.
    JSON_SCHEMA: dict[str, Any] = {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","required":["v","frames"],"properties":{"v":{"type":"number"},"frames":{"type":"array","minItems":1,"items":{"type":"object","properties":{"d":{"type":"number","exclusiveMinimum":0},"p":{"type":"array","items":{"type":"number","minimum":0,"maximum":255}}}},"if":{"maxItems":1},"then":{"items":{"required":["p"],"properties":{"d":False}}},"else":{"items":{"required":["d","p"]}}}}}

    DEVICE_MODEL_TO_COMPRESSED_ZONE_COUNT = {
        PhoneModel.PHONE3: 489,
        PhoneModel.PHONE4APRO: 137
    }

    V_TO_DEVICE_MODEL = {
        1: PhoneModel.PHONE3,
        4: PhoneModel.PHONE4APRO
    }
    
    class _Frame(TypedDict):
        d: NotRequired[int]
        p: list[int]
    
    class _Root(TypedDict):
        v: int
        frames: list['PauwmaGlyphMuseumConverter._Frame']

    def get_name(self) -> str:
        return "Pauwma's Glyph Museum JSON Export Converter"
    
    def get_description(self) -> str:
        return "JSON export format from Pauwma's Glyph Museum app"

    def _get_root(self, input_data: ReadableData) -> Optional['PauwmaGlyphMuseumConverter._Root']:
        return self._input_to_json(input_data, self.JSON_SCHEMA)

    def can_convert_to(self, input_data: ReadableData) -> list[DeviceInfo]:
        devices: list[DeviceInfo] = []
        
        root = self._get_root(input_data)
        if root is None:
            logger.debug(f"[{self.__class__.__name__}] Input data is not valid JSON or does not conform to the expected schema.")
            return devices

        frames = root["frames"]
        if not frames:
            logger.debug(f"[{self.__class__.__name__}] No frames found in the input data.")
            return devices

        if not self._has_2d_list_consistent_length([frame['p'] for frame in frames]):
            logger.debug(f"[{self.__class__.__name__}] Inconsistent frame lengths found in the input data.")
            return devices

        if declared_device_model := self.V_TO_DEVICE_MODEL.get(root["v"], None):
            zone_count = len(frames[0]["p"])
            if zone_count != self.DEVICE_MODEL_TO_COMPRESSED_ZONE_COUNT[declared_device_model]:
                logger.debug(f"[{self.__class__.__name__}] Format declared device model {declared_device_model} does not match the expected zone count. Got {zone_count} zones, expected {self.DEVICE_MODEL_TO_COMPRESSED_ZONE_COUNT[declared_device_model]} zones.")
                return devices
            devices.append(PHONE_MODEL_INFO[declared_device_model])
        else:
            logger.warning(f"[{self.__class__.__name__}] Device identifier 'v' unknown ({root['v']})! Script needs an update to support the new device!")

        return devices

    def _inflate_matrix_frame(self, frame: list[int], device: DeviceInfo) -> list[int]:
        """Inflate a single frame to have the right amount of zones for the device,
        and right number range."""

        # Shifting the value range from 0-255 to 0-4080 by bitshifting. Note that the 
        # max value documented with Glyph Tools is 4095.

        match device.model:
            case PhoneModel.PHONE3:
                # For the Phone (3), we need to inflate the 489 zones to 625
                full_frame = [0] * 9 + [x<<4 for x in frame[0:7]] + [0] * 9 # 9, 7, 9
                full_frame += [0] * 7 + [x<<4 for x in frame[7:18]] + [0] * 7 # 7, 11, 7
                full_frame += [0] * 5 + [x<<4 for x in frame[18:33]] + [0] * 5 # 5, 15, 5
                full_frame += [0] * 4 + [x<<4 for x in frame[33:50]] + [0] * 4 # 4, 17, 4
                full_frame += [0] * 3 + [x<<4 for x in frame[50:69]] + [0] * 3 # 3, 19, 3
                full_frame += [0] * 2 + [x<<4 for x in frame[69:90]] + [0] * 2 # 2, 21, 2
                full_frame += [0] * 2 + [x<<4 for x in frame[90:111]] + [0] * 2 # 2, 21, 2
                full_frame += [0] * 1 + [x<<4 for x in frame[111:134]] + [0] * 1 # 1, 23, 1
                full_frame += [0] * 1 + [x<<4 for x in frame[134:157]] + [0] * 1 # 1, 23, 1
                full_frame += [x<<4 for x in frame[157:332]] # 7 full rows => 25 * 7 = 175
                full_frame += [0] * 1 + [x<<4 for x in frame[332:355]] + [0] * 1 # 1, 23, 1
                full_frame += [0] * 1 + [x<<4 for x in frame[355:378]] + [0] * 1 # 1, 23, 1
                full_frame += [0] * 2 + [x<<4 for x in frame[378:399]] + [0] * 2 # 2, 21, 2
                full_frame += [0] * 2 + [x<<4 for x in frame[399:420]] + [0] * 2 # 2, 21, 2
                full_frame += [0] * 3 + [x<<4 for x in frame[420:439]] + [0] * 3 # 3, 19, 3
                full_frame += [0] * 4 + [x<<4 for x in frame[439:456]] + [0] * 4 # 4, 17, 4
                full_frame += [0] * 5 + [x<<4 for x in frame[456:471]] + [0] * 5 # 5, 15, 5
                full_frame += [0] * 7 + [x<<4 for x in frame[471:482]] + [0] * 7 # 7, 11, 7
                full_frame += [0] * 9 + [x<<4 for x in frame[482:489]] + [0] * 9 # 9, 7, 9

                assert len(full_frame) == 625, f"[Development Error] Inflated frame length does not match expected length for Phone (3). Expected: 625, Actual: {len(full_frame)}"
            case PhoneModel.PHONE4APRO:
                # For the Phone (4A Pro), we need to inflate the 137 zones to 169
                full_frame = [0] * 4 + [x<<4 for x in frame[0:5]] + [0] * 4 # 4, 5, 4
                full_frame += [0] * 2 + [x<<4 for x in frame[5:14]] + [0] * 2 # 2, 9, 2
                full_frame += [0] * 1 + [x<<4 for x in frame[14:25]] + [0] * 1 # 1, 11, 1
                full_frame += [0] * 1 + [x<<4 for x in frame[25:36]] + [0] * 1 # 1, 11, 1
                full_frame += [x<<4 for x in frame[36:101]] # 5 full rows => 13 * 5 = 65
                full_frame += [0] * 1 + [x<<4 for x in frame[101:112]] + [0] * 1 # 1, 11, 1
                full_frame += [0] * 1 + [x<<4 for x in frame[112:123]] + [0] * 1 # 1, 11, 1
                full_frame += [0] * 2 + [x<<4 for x in frame[123:132]] + [0] * 2 # 2, 9, 2
                full_frame += [0] * 4 + [x<<4 for x in frame[132:137]] + [0] * 4 # 4, 5, 4

                assert len(full_frame) == 169, f"[Development Error] Inflated frame length does not match expected length for Phone (4A Pro). Expected: 169, Actual: {len(full_frame)}"

        return full_frame

    def _convert(self, input_data: ReadableData, to_device: DeviceInfo, duration: Optional[timedelta], offset: Optional[timedelta]) -> NGlyphData:
        root = self._get_root(input_data)
        assert root is not None, "[Development Error] The input data should have already been validated in the can_convert_to method. This should never happen."

        frame_durations_s = [
            (frame["d"] / 1000) if 'd' in frame else (1 / to_device.target_fps)
            for frame in root["frames"]
        ]
        animation_duration_s = sum(frame_durations_s)
        logger.debug(f'[{self.__class__.__name__}] frame_durations_s={frame_durations_s}')
        logger.debug(f'[{self.__class__.__name__}] animation_duration_s={animation_duration_s}')

        inflated_frames = [self._inflate_matrix_frame(frame["p"], to_device) for frame in root["frames"]]
        logger.debug(f'[{self.__class__.__name__}] animation frame count: {len(inflated_frames)}')

        frame_count = math.ceil(duration.total_seconds() * to_device.target_fps) if duration else \
            math.ceil(animation_duration_s * to_device.target_fps)
        logger.debug(f'[{self.__class__.__name__}] frame_count={frame_count}')

        offset_s = offset.total_seconds() if offset else 0.0
        author_data = self._build_author_data_from_frames(inflated_frames, frame_durations_s, frame_count, to_device.target_fps, offset_s)

        return NGlyphData(
            PHONE_MODEL=to_device.model.name,
            AUTHOR=self._to_author(author_data),
            CUSTOM1=[]
        )

# +------------------------------------+
# |                                    |
# |              Globals               |
# |                                    |
# +------------------------------------+

logger = logging.getLogger(__name__)

# Get the script directory
SCRIPT_DIR = Path(__file__).resolve().parent
# Get the script name
SCRIPT_NAME = Path(__file__).name

# Version of the script
SCRIPT_VERSION = "1.0.0"


PHONE_MODEL_INFO = {
    PhoneModel.PHONE3: DeviceInfo(model=PhoneModel.PHONE3, supported_zones=[625], target_fps=60.0),
    PhoneModel.PHONE4APRO: DeviceInfo(model=PhoneModel.PHONE4APRO, supported_zones=[169], target_fps=60.0)
}

INPUT_FILE_ARGUMENT = 'INPUT_FILE'
DURATION_ARGUMENT = 'DURATION'
OFFSET_ARGUMENT = 'OFFSET'

CONVERTERS: list[AToNGlyphConverter] = [
    PauwmaGlyphMuseumConverter()
]

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# https://docs.python.org/3/library/argparse.html#action
class ListConvertersAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, **kwargs): # type: ignore
        #nargs = 0 is important to not expect any arguments for this flag
        super().__init__(option_strings, dest, nargs=nargs, **kwargs) # type: ignore
    
    def __call__(self, parser, namespace, values, option_string=None): # type: ignore
        print("Available converters:")
        for converter in CONVERTERS:
            print(f"[*] {converter.get_name()} - {converter.get_description()}")
        parser.exit()

# https://docs.python.org/3/library/argparse.html#type
def parse_duration(value: str) -> timedelta:
    """
    Custom argparse type to parse SS:ms.
    """
    # 1. Enforce the exact format using regex
    match = re.match(r'^(\d+)(?:\:(\d{1,3}))?$', value)
    if not match:
        raise argparse.ArgumentTypeError(f"'{value}' for a duration is invalid. Must be in <seconds>[:<milliseconds>] format, where seconds is a non-negative integer and milliseconds is an optional non-negative integer between 0 and 999.")
    
    secs = int(match.group(1))
    ms = int(match.group(2)) if match.group(2) else 0

    td = timedelta(seconds=secs, milliseconds=ms)
    if td.total_seconds() <= 0:
        raise ValueError(f"'{value}' for a duration is invalid. Duration must be greater than 0.")

    return td

def parse_offset(value: str) -> timedelta:
    """
    Custom argparse type to parse SS:ms for a positive offset.
    """
    match = re.match(r'^(\d+)(?:\:(\d{1,3}))?$', value)
    if not match:
        raise argparse.ArgumentTypeError(f"'{value}' for an offset is invalid. Must be in <seconds>[:<milliseconds>] format, where seconds is a non-negative integer and milliseconds is an optional non-negative integer between 0 and 999.")

    secs = int(match.group(1))
    ms = int(match.group(2)) if match.group(2) else 0

    td = timedelta(seconds=secs, milliseconds=ms)
    if td.total_seconds() < 0:
        raise ValueError(f"'{value}' for an offset is invalid. Offset must be greater or equal to 0.")

    return td

# Build the arguments parser
def build_arguments_parser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(add_help=False, description="A tool to convert select glyph data formats into the Glyph Tools intermediate file format called Nglyph. Can then be used with the \"GlyphModder\" script to create a valid composition for Nothing Phones.", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    # Add the arguments
    # Note: Using nargs=1 creates a list with a single item instead of a single value => Don't use
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.') # help
    parser.add_argument(INPUT_FILE_ARGUMENT, help="A path to the input file or '-' to read from stdin.", type=Path)
    parser.add_argument('-d', '--duration', dest=DURATION_ARGUMENT, type=parse_duration, help='Target duration formatted as <seconds>[:<milliseconds>]. Providing no duration will keep the original duration of the animation. If the provided duration is longer than the original animation, the animation will be looped to fill the duration. If it is shorter, the animation will be cut off.')
    parser.add_argument('--offset', dest=OFFSET_ARGUMENT, type=parse_offset, help='Positive offset formatted as <seconds>[:<milliseconds>]. The converted animation will start at this offset into the source animation.')
    parser.add_argument('--list-converters', action=ListConvertersAction, help='List all available converters and exit.') # list converters
    parser.add_argument('--version', action='version', help='Show the version number and exit.', version=SCRIPT_VERSION) # version

    return parser

# Check the requirements
def check_requirements():
    pass

# Perform argument checks
def perform_checks(args: dict[str, list[str]]):
    assert INPUT_FILE_ARGUMENT in args, "Input file argument is missing."

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
    # Change logger level here to DEBUG if needed.
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
def print_critical_error(message: str, exitCode: int = 1, start: str = ""):
    logger.error(message, extra={"start": start})
    #raise Exception(message)
    sys.exit(exitCode)

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

class InputOpenError(Exception):
    pass
@contextmanager
def open_seekable_binary_input(path: Path) -> Generator[tuple[BinaryIO, bool], None, None]:
    """Yields an open binary stream or sys.stdin.buffer, safely.
    This allows buffered reading for large files.

    Args:
        path (Path): The path to open. If the path is '-' stdin will be returned.

    Throws:
        InputOpenError: When an exception is thrown when opening the file or when stdin is not a tty.

    Yields:
        tuple[BinaryIO, bool]: The open binary stream and if the binary stream is sys.stdin.buffer.
    """
    is_stdin = path.name == '-'
    if is_stdin:
        if sys.stdin.isatty():
            raise InputOpenError("No input provided to stdin.")

        # Cache up to 10 MB of stdin in memory. If stdin is larger a temporary file is created.
        # This allows seeking.
        # "w+b" stands for writing and reading in binary mode
        with tempfile.SpooledTemporaryFile(max_size=10*1024*1024, mode="w+b") as spooled:
            try:
                # Catch file creation errors or disk full errors...
                shutil.copyfileobj(sys.stdin.buffer, spooled)
                spooled.seek(0)
            except OSError as e:
                raise InputOpenError(f"Cannot process piped file: {e.strerror}") from e
            # typing.cast needed to make Pylance happy
            yield (cast(BinaryIO, spooled), is_stdin)
        return

    try:
        f = path.open('rb')
    except OSError as e:
        raise InputOpenError(f"Cannot open {path.as_posix()!r}: {e.strerror}") from e
    try:
        yield (f, is_stdin)
    finally:
        f.close()

def convert_and_save(input_data: ReadableData, converter: AToNGlyphConverter, device: DeviceInfo, duration: Optional[timedelta], offset: Optional[timedelta], absolute_output_file_path: Path):
    try:
        converted_data = converter.convert(input_data, device, duration, offset)
    except UnsupportedFormatError as e:
        print_critical_error(f"Conversion failed: {str(e)}")
        return # Just for Pylance - print_critical_error will exit
    except PhoneModelNotSupportedError as e:
        print_critical_error(f"Conversion failed: {str(e)}")
        return # Just for Pylance - print_critical_error will exit
    except ConversionError as e:
        print_critical_error(f"An error occurred during conversion: {str(e)}")
        return # Just for Pylance - print_critical_error will exit

    try:
        absolute_output_file_path.write_text(json.dumps(converted_data.to_dict(), indent=4), encoding='utf-8', newline='\r\n')
    except Exception as e:
        print_critical_error(f"Failed to save the converted data: {str(e)}")

def offer_choice(options: list[str], prompt: str = "Please choose an option:") -> int:
    """Offer a list of options to the user and return the index of the chosen option."""
    while True:
        logger.info(prompt)
        for i, option in enumerate(options):
            print(f"  [{i + 1}] {option}")
        choice = input("Enter the number of your choice: ")
        if choice.isdigit():
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(options):
                return choice_index
        logger.warning("Invalid choice. Please try again.")

def get_available_converters_for_file(file: BinaryIO) -> list[tuple[int, list[DeviceInfo]]]:
    available_converter: list[tuple[int, list[DeviceInfo]]] = []
    for i, converter in enumerate(CONVERTERS):
        device_info = converter.can_convert_to(file)
        if device_info:
            logger.debug(f"Converter '{converter.__class__.__name__}' can convert the input data for the following device(s): {', '.join([d.model.value for d in device_info])}")
            available_converter.append((i, device_info))
        file.seek(0)  # Reset file pointer for the next converter
    
    return available_converter

# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

def main() -> int:
    setup_logger()

    args = build_arguments_parser().parse_args()
    logger.debug(f"args: {args}")

    # Perform all the checks
    try:
        perform_checks(args.__dict__)
    except Exception as e:
        print_critical_error(str(e))

    check_requirements()

    # Get arguments
    relative_input_file_path: Path = args.__dict__[INPUT_FILE_ARGUMENT]
    absolute_input_file_path = relative_input_file_path.resolve().absolute()
    duration: Optional[timedelta] = args.__dict__.get(DURATION_ARGUMENT, None)
    offset: Optional[timedelta] = args.__dict__.get(OFFSET_ARGUMENT, None)

    logger.debug("")

    try:
        with open_seekable_binary_input(relative_input_file_path) as (f, is_stdin):
            available_converter = get_available_converters_for_file(f)
            
            if not available_converter:
                logger.info("No available converters found for the input data. Input format is not supported.")
                return 0
            
            if len(available_converter) == 1:
                converter_index = 0
                logger.info(f"One available converter found: '{CONVERTERS[available_converter[converter_index][0]].get_name()}'. Automatically selecting it.")
            else:
                converter_options = [CONVERTERS[i].get_name() + " - " + CONVERTERS[i].get_description() for i, _ in available_converter]
                converter_index = offer_choice(converter_options, prompt="Multiple converters found for the input data. Please choose the most fitting converter:")
            
            selected_converter_index, supported_devices = available_converter[converter_index]
            logger.info(f"Selected converter: '{CONVERTERS[selected_converter_index].get_name()}'")

            if len(supported_devices) == 1:
                device_index = 0
                logger.info(f"One supported device for the input data: {supported_devices[device_index].model.value}. Automatically selecting it.")
            else:
                device_options = [device.model.value for device in supported_devices]
                device_index = offer_choice(device_options, prompt="Multiple supported devices found for the input data. Please choose the target device you want to convert for:")
            
            selected_device = supported_devices[device_index]
            logger.info(f"Selected target device: {selected_device.model.value}")

            if is_stdin:
                absolute_output_file_path = Path("output.nglyph").resolve().absolute()
                logger.warning(f"Input is from standard input. The output file will be saved as: '{absolute_output_file_path.as_posix()}'")
            else:
                base_filename = absolute_input_file_path.stem
                absolute_output_file_path = Path(base_filename + ".nglyph").resolve().absolute()
                logger.info(f"Output file will be saved as: '{absolute_output_file_path.as_posix()}'")
            convert_and_save(f, CONVERTERS[selected_converter_index], selected_device, duration, offset, absolute_output_file_path)
    except InputOpenError as e:
        # When opening the input file fails
        print_critical_error(str(e))

    cprint("Done!", color="green", attrs=["bold"])
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")