#!/usr/bin/env python3

# FrameGenerator - A tool to generate a frame counter video that can
# be used for testing Nothing Phone (3) video to composition programms.
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

import os
import subprocess

from imagelib import *

# Customize if need be
OUTPUT_FOLDER = "frames"
VIDEO_OUTPUT_FILE = "output.mp4"
FPS = 60  # Frames per second
FRAMES = FPS * 10  # Total number of frames to generate

NUMBER_GLYPHS: dict[int, Image] = {
    0: Image(4, 5, [
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0
    ]),
    1: Image(4, 5, [
        0, 0, 0,  0, 0, 0,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  0, 0, 0,  255, 255, 255, 0, 0, 0,
        0, 0, 0,  0, 0, 0,  255, 255, 255, 0, 0, 0
    ]),
    2: Image(4, 5, [
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  0, 0, 0,
        255, 255, 255,  255, 255, 255,  255, 255, 255,  255, 255, 255
    ]),
    3: Image(4, 5, [
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0
    ]),
    4: Image(4, 5, [
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  255, 255, 255,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255
    ]),
    5: Image(4, 5, [
        255, 255, 255,  255, 255, 255,  255, 255, 255,  255, 255, 255,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  0, 0, 0,
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0
    ]),
    6: Image(4, 5, [
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  0, 0, 0,
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0
    ]),
    7: Image(4, 5, [
        255, 255, 255,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        0, 0, 0,  0, 0, 0,  0, 0, 0, 255, 255, 255,
        0, 0, 0,  0, 0, 0,  0, 0, 0, 255, 255, 255,
        0, 0, 0,  0, 0, 0,  0, 0, 0, 255, 255, 255,
        0, 0, 0,  0, 0, 0,  0, 0, 0, 255, 255, 255,
    ]),
    8: Image(4, 5, [
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0
    ]),
    9: Image(4, 5, [
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0,
        255, 255, 255,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  255, 255, 255,
        0, 0, 0,  0, 0, 0,  0, 0, 0,  255, 255, 255,
        0, 0, 0,  255, 255, 255,  255, 255, 255,  0, 0, 0
    ])
}

def main():
    WIDTH = 25
    HEIGHT = 25

    # Create the output folder if it does not exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    for frame_nr in range(FRAMES):
        # Create a new image for each frame
        image = Image(WIDTH, HEIGHT)

        # Extract digits from the frame index
        digits = [int(digit) for digit in str(frame_nr)]
        
        # Set the pixels for the current frame
        # Right align the glyphs in the center of the image
        digits.reverse()
        x = image.width - 1  # Start from the right edge of the image
        for j, digit in enumerate(digits):
            assert digit in NUMBER_GLYPHS, f"Digit {digit} not found in NUMBER_GLYPHS"
            
            glyph = NUMBER_GLYPHS[digit]            
            x -= glyph.width + 1  # Move left for the next glyph, leaving a space
            y = (image.height - glyph.height) // 2
            image.set_pixels_at(x, y, glyph)
        
        # Save the image as a PPM file
        filename = f"{OUTPUT_FOLDER}/frame_{frame_nr:03d}.ppm"
        image.save_as_ppm(filename)
    
    # Use ffmpeg to convert the PPM files to a video
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner",

        "-f", "lavfi",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", # Generate silent audio

        "-s", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FPS),
        "-i", f"{OUTPUT_FOLDER}/frame_%03d.ppm",

        "-vf", "scale=iw*2:ih*2", # Scale to double size. Avoids non divisible by 2 dimensions.
        "-sws_flags", "neighbor", # Make sure we use nearest neighbor scaling
        "-r", str(FPS),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "0", # Disable compression (lossless)
        "-c:a", "aac",
        "-shortest", # Stop encoding when the shortest input stream ends, the frames in this case
        VIDEO_OUTPUT_FILE
    ], check=True)

if __name__ == "__main__":
    main()