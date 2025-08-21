#!/usr/bin/env python3

# NGlyphToFrames - A tool to convert Nothing Phone (3) light data in an NGlyph file to an image sequence.
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

import argparse
import json
import os

from imagelib import *

# Output folder for the extracted frames
OUTPUT_FOLDER = "nglyphframes"

def main():
    parser = argparse.ArgumentParser(add_help=False, description="A tool to convert Nothing Phone (3) light data in an NGlyph file to an image sequence.", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    parser.add_argument('NGLYPH_PATH', help="A path to the nglyph file to read the light data from.", type=str, nargs=1) # NGLYPH_PATH

    args = parser.parse_args()

    # Expand to an absolute path
    args.NGLYPH_PATH[0] = os.path.abspath(args.NGLYPH_PATH[0])
    print(f"Reading nglyph from: \"{args.NGLYPH_PATH[0]}\"")

    # Check if the file exists
    if not os.path.isfile(args.NGLYPH_PATH[0]):
        raise Exception(f"The nglyph file does not exist: '{args.NGLYPH_PATH[0]}'")
    
    # Create the output folder if it does not exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    # Read the nglyph file
    with open(args.NGLYPH_PATH[0], "r") as f:
        nglyph: dict[str, any] = json.load(f)
    
    assert 'VERSION' in nglyph and int(nglyph['VERSION']) == 1, "Only nglyph version 1 is supported."
    assert 'PHONE_MODEL' in nglyph and nglyph['PHONE_MODEL'] == "PHONE3", "Only Nothing Phone (3) is supported."
    assert 'WATERMARK' not in nglyph, "NGlyph files protected by a watermark are not supported."
    assert 'AUTHOR' in nglyph and isinstance(nglyph['AUTHOR'], list) and all(isinstance(frame, str) for frame in nglyph['AUTHOR']), "The nglyph file does not contain valid frame data."

    frame_data = nglyph['AUTHOR']
    print(f"Found {len(frame_data)} frames in the nglyph file.")

    for frame_nr, frame in enumerate(frame_data):
        print(f"Processing frame {frame_nr + 1}/{len(frame_data)}...")
        
        frame_ints = [int(x.strip()) for x in frame.strip().split(",") if x.strip() != '']
        assert len(frame_ints) == 25*25, "Each frame must contain exactly 25x25=625 pixel values."
        assert all(0 <= x <= 4095 for x in frame_ints), "Each pixel value must be between 0 and 4095."
        mapped_ints = list(map(lambda x: x >> 4, frame_ints))  # Map to 0-255 range by bitshift (divide by 16)

        pixel_data = [gray_value for gray_value in mapped_ints for _ in range(3)]  # Convert to RGB format

        Image(25, 25, pixel_data).save_as_ppm(os.path.join(OUTPUT_FOLDER, f"frame_{frame_nr:03d}.ppm"))

    print("Done!")

if __name__ == "__main__":
    main()