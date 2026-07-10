#!/usr/bin/env python3

# JsonToGlyphMatrix - A tool to convert Glyph Museum JSON animations into the 
# Glyph Tools intermediate file format called Nglyph.
# Copyright (C) 2026 Asher Edwards and Gemini 3.5 Flash

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

@dataclass
class DeviceInfo:
    """Data class to store device information."""
    model: str
    matrix_size: tuple[int, int]
    target_fps: float
    visible_leds: list[int]

# +------------------------------------+
# |                                    |
# |              Globals               |
# |                                    |
# +------------------------------------+

logger = logging.getLogger(__name__)

# Version of the script
SCRIPT_VERSION = "1.0.0"

# LED mappings from docs/9_Technical Details.md
# PHONE4APRO (Phone 4a Pro): 13x13 grid, 137 visible LEDs
PHONE4APRO_VISIBLE_LEDS = []
for start, end in [
    (4, 8),
    (15, 23),
    (27, 37),
    (40, 50),
    (52, 116),
    (118, 128),
    (131, 141),
    (145, 153),
    (160, 164)
]:
    PHONE4APRO_VISIBLE_LEDS.extend(range(start, end + 1))

# PHONE3 (Phone 3): 25x25 grid, 489 visible LEDs
PHONE3_VISIBLE_LEDS = []
for start, end in [
    (9, 15),
    (32, 42),
    (55, 69),
    (79, 95),
    (103, 121),
    (127, 147),
    (152, 172),
    (176, 198),
    (201, 223),
    (225, 399),
    (401, 423),
    (426, 448),
    (452, 472),
    (477, 497),
    (503, 521),
    (529, 545),
    (555, 569),
    (582, 592),
    (609, 615)
]:
    PHONE3_VISIBLE_LEDS.extend(range(start, end + 1))

PHONE_MODEL_INFO = {
    'PHONE3': DeviceInfo(model='PHONE3', matrix_size=(25, 25), target_fps=60.0, visible_leds=PHONE3_VISIBLE_LEDS),
    'PHONE4APRO': DeviceInfo(model='PHONE4APRO', matrix_size=(13, 13), target_fps=60.0, visible_leds=PHONE4APRO_VISIBLE_LEDS)
}

# +------------------------------------+
# |                                    |
# |           Boiler Plate             |
# |                                    |
# +------------------------------------+

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
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(ColoredFormatter())

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    just_fix_windows_console()

def print_critical_error(message: str, exitCode: int = 1, start: str = ""):
    logger.error(message, extra={"start": start})
    sys.exit(exitCode)

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def map_visible_to_matrix(visible_vals: list[float], device: DeviceInfo) -> list[int]:
    """Map sequential visible LED values to physical matrix layout."""
    total_pixels = device.matrix_size[0] * device.matrix_size[1]
    matrix = [0] * total_pixels
    
    for i, val in enumerate(visible_vals):
        if i < len(device.visible_leds):
            # Scale 0-255 to 0-4095 using truncation to match NumPy/OpenCV default cast
            scaled = int(val * 4095.0 / 255.0)
            scaled = max(0, min(4095, scaled))
            matrix[device.visible_leds[i]] = scaled
            
    return matrix

def matrix_to_csv_string(matrix: list[int]) -> str:
    """Convert matrix list to comma separated string with trailing comma."""
    return ",".join(map(str, matrix)) + ","

def interpolate_frames(frames: list[dict], target_fps: float, interpolation_mode: str) -> list[list[float]]:
    """Interpolate frames to the target FPS.
    
    Returns a list of frames, where each frame is a list of pixel values (0-255 floats).
    """
    num_input_frames = len(frames)
    if num_input_frames == 0:
        return []

    # Calculate input frame durations
    durations = [f.get('d', 100) for f in frames]
    
    # Time-based interpolation
    # Compute timeline boundaries
    times = [0.0]
    for d in durations:
        times.append(times[-1] + d)
        
    total_duration = times[-1]
    
    total_output_frames = max(1, int(total_duration / 1000.0 * target_fps))
        
    logger.info(f"Time-based interpolation: total_duration={total_duration:.1f}ms, target_fps={target_fps}, total_output_frames={total_output_frames}")
    
    output_pixel_data = []
    for j in range(total_output_frames):
        t_out = j * (1000.0 / target_fps)
        
        # Find interval
        k = 0
        while k < num_input_frames - 1 and t_out >= times[k+1]:
            k += 1
            
        p_curr = frames[k]['p']
        
        if interpolation_mode == 'nearest' or k >= num_input_frames - 1:
            output_pixel_data.append(list(p_curr))
        else:
            # Linear interpolation
            t_curr = times[k]
            t_next = times[k+1]
            p_next = frames[k+1]['p']
            
            # Make sure we don't divide by zero
            denom = t_next - t_curr
            fraction = (t_out - t_curr) / denom if denom > 0 else 0.0
            fraction = max(0.0, min(1.0, fraction))
            
            p_interp = []
            # Ensure we align lists correctly
            for val_curr, val_next in zip(p_curr, p_next):
                p_interp.append(val_curr + fraction * (val_next - val_curr))
            output_pixel_data.append(p_interp)
            
    return output_pixel_data

# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

def main() -> int:
    setup_logger()
    
    parser = argparse.ArgumentParser(
        description="Convert Glyph Museum JSON files to custom Nothing Glyph Tools NGLYPH files.",
        epilog="Created for Nothing community tools."
    )
    parser.add_argument("JSON_PATH", help="Path to the Glyph Museum JSON file.", type=str)
    parser.add_argument("-o", "--output", help="Path to write the output .nglyph file.", type=str)
    parser.add_argument("-m", "--model", help="Target phone model. If omitted, auto-detected from JSON data.", type=str, choices=list(PHONE_MODEL_INFO.keys()))
    parser.add_argument("-i", "--interpolation", help="Interpolation mode (linear or nearest). Default: linear.", type=str, choices=["linear", "nearest"], default="linear")
    parser.add_argument("--fps", help="Target frame rate (default: 60.0).", type=float, default=60.0)
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    
    args = parser.parse_args()
    
    json_path = os.path.abspath(args.JSON_PATH)
    if not os.path.isfile(json_path):
        print_critical_error(f"Input JSON file does not exist: '{json_path}'")
        
    logger.info(f"Reading Glyph Museum JSON: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print_critical_error(f"Failed to parse JSON file: {e}")
        
    if 'frames' not in data or not isinstance(data['frames'], list) or len(data['frames']) == 0:
        print_critical_error("Invalid Glyph Museum JSON: 'frames' list is missing or empty.")
        
    # Auto-detect model if not specified
    first_frame_p = data['frames'][0].get('p', [])
    num_pixels = len(first_frame_p)
    logger.info(f"First frame contains {num_pixels} pixel values.")
    
    model = args.model
    if not model:
        if num_pixels <= 169:
            model = 'PHONE4APRO'
            logger.info("Auto-detected model: PHONE4APRO (Phone 4a Pro)")
        else:
            model = 'PHONE3'
            logger.info("Auto-detected model: PHONE3 (Phone 3)")
            
    device_info = PHONE_MODEL_INFO[model]
    
    # Check if number of pixels is enough for the visible LEDs
    needed_visible = len(device_info.visible_leds)
    if num_pixels < needed_visible:
        logger.warning(f"Frame has {num_pixels} pixels, but {model} has {needed_visible} visible LEDs. Padding with zeros.")
        for frame in data['frames']:
            if 'p' in frame:
                frame['p'] = list(frame['p']) + [0] * (needed_visible - len(frame['p']))
                
    # Perform interpolation
    logger.info(f"Interpolating frames (mode={args.interpolation})...")
    interpolated_pixel_frames = interpolate_frames(
        data['frames'],
        target_fps=args.fps,
        interpolation_mode=args.interpolation
    )
    
    # Map and format frames
    author_data = []
    for frame_idx, pixel_frame in enumerate(interpolated_pixel_frames):
        matrix = map_visible_to_matrix(pixel_frame, device_info)
        csv_str = matrix_to_csv_string(matrix)
        author_data.append(csv_str)
        
    # Determine output file path
    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        output_path = os.path.join(os.path.dirname(json_path), f"{base_name}.nglyph")
        
    output_path = os.path.abspath(output_path)
    logger.info(f"Writing NGLYPH file: {output_path}")
    
    nglyph_data: NGlyphData = {
        'VERSION': 1,
        'PHONE_MODEL': device_info.model,
        'AUTHOR': author_data,
        'CUSTOM1': ''
    }
    
    try:
        with open(output_path, 'w', newline='\r\n', encoding='utf-8') as f:
            json.dump(nglyph_data, f, indent=4)
        cprint("Done successfully!", color="green", attrs=["bold"])
    except Exception as e:
        print_critical_error(f"Failed to write output file: {e}")
        
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_critical_error("Interrupted by user.", 130, start="\n")
