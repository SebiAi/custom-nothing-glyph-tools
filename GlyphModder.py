#!/usr/bin/python3

import base64
import sys
import subprocess
import argparse
import os
import zlib
import json
from termcolor import cprint

base64_padding = '=='

# Build the arguments parser
def buildArgumentsParser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(description="Read or write the Glyph metadata from the Nothing Glyph Composer.", epilog="Created by: Sebastian Aigner (aka. SebiAi)")

    parser.add_argument('FILE', help="The file to read from or write to.", type=str, nargs=1)
    parser.add_argument('-w', help="Write the metadata back from the files instead of reading. - You need to provide the file with the author data first, then the file with the custom1 data.", type=str, nargs=2, metavar=('AUTHOR_FILE', 'CUSTOM1_FILE'))
    parser.add_argument('-t', help="What title to write into the metadata. (default: 'MyCustomSong')", default=['MyCustomSong'], type=str, nargs=1, metavar=('TITLE'))
    parser.add_argument('--ffmpeg', help="Path to ffmpeg executable. (default: 'ffmpeg' - looks in PATH)", default=['ffmpeg'], type=str, nargs=1, metavar=('FFMPEG_PATH'))
    parser.add_argument('--ffprobe', help="Path to ffprobe executable. (default: 'ffprobe' - looks in PATH)", default=['ffprobe'], type=str, nargs=1, metavar=('FFPROBE_PATH'))

    return parser

# Check the requirements
def checkRequirements(ffmpeg: str, ffprobe: str, write: bool):
    if write:
        try:
            # Check if ffmpeg is installed - write metadata
            if subprocess.run([ffmpeg, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                printCriticalError(f"ffmpeg could not be found. ({ffmpeg})")
        except FileNotFoundError:
            printCriticalError(f"ffmpeg could not be found. ({ffmpeg})")
    else:
        try:
            # Check if ffprobe is installed - read metadata
            if subprocess.run([ffprobe, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                printCriticalError(f"ffprobe could not be found. ({ffprobe})")
        except FileNotFoundError:
            printCriticalError(f"ffprobe could not be found. ({ffprobe})")


# Perform argument checks
def performChecks(args: dict):
    # Check if the file exists
    if not os.path.isfile(args['FILE'][0]):
        raise Exception(f"File does not exist: '{args['FILE'][0]}'")

    # Check if we need to write the metadata back
    if args.get('w', False):
        # Check if the file exists
        if not os.path.isfile(args['w'][0]):
            raise Exception(f"AUTHOR file does not exist: '{args['w'][0]}'")
        if not os.path.isfile(args['w'][1]):
            raise Exception(f"CUSTOM1 file does not exist: '{args['w'][1]}'")

# Print critical error message and exit
def printCriticalError(message: str, exitCode: int = 1):
    printError(message)
    #raise Exception(message)
    sys.exit(exitCode)

# Print error message
def printError(message, start: str = ""):
    cprint(start + "ERROR: " + message, color="red", attrs=["bold"], file=sys.stderr)

# Print warning message
def printWarning(message, start: str = ""):
    cprint(start + "WARNING: " + message, color="yellow", attrs=["bold"])

def decode_base64(encoded_string: str) -> bytes:
    return base64.b64decode(encoded_string + base64_padding)

def encode_base64(bytes: bytes) -> str:
    return base64.b64encode(bytes).decode('utf-8').removesuffix(base64_padding)

def write_metadata(file: str, author_file: str, custom1_file: str, custom_title: str, ffmpeg: str):
    with open(author_file, 'rb') as f:
        author = f.read()
    with open(custom1_file, 'rb') as f:
        custom1 = f.read()

    if author == "" or custom1 == "":
        printCriticalError("AUTHOR or CUSTOM1 metadata is empty. Please check the files.")
    
    # Print the metadata
    print("Author: ", author)
    print("Custom1:", custom1)

    # Compress the strings with zlib
    compressed_author = zlib.compress(author, zlib.Z_BEST_COMPRESSION)
    compressed_custom1 = zlib.compress(custom1, zlib.Z_BEST_COMPRESSION)

    # Print the metadata
    print("\nCompressed Author: ", compressed_author)
    print("Compressed Custom1:", compressed_custom1)

    # Encode
    encoded_author = encode_base64(compressed_author)
    encoded_custom1 = encode_base64(compressed_custom1)

    # New line every 76 characters (76 character is the new line character)
    encoded_author = '\n'.join(encoded_author[i:i+76] for i in range(0, len(encoded_author), 76))
    encoded_custom1 = '\n'.join(encoded_custom1[i:i+76] for i in range(0, len(encoded_custom1), 76))

    # Print the metadata
    print("\nBase 64 Author:  " + encoded_author)
    print("Base 64 Custom1: " + encoded_custom1)

    # Tmp file name
    tmp_file = os.path.splitext(os.path.basename(file))[0] + '_new.ogg'

    # Write the metadata back to the file
    subprocess.run([ffmpeg, '-hide_banner', '-i', file, '-metadata:s:a:0', 'TITLE=' + custom_title, '-metadata:s:a:0', 'ALBUM=CUSTOM', '-metadata:s:a:0', 'AUTHOR=' + encoded_author, '-metadata:s:a:0', 'COMPOSER=Spacewar Glyph Composer', '-metadata:s:a:0', 'CUSTOM1=' + encoded_custom1, '-c', 'copy', '-y', tmp_file])

    # Delete the old file - needed for Windows or else os.rename() will fail
    os.remove(file)

    # Copy back the file
    os.rename(tmp_file, file)

def read_metadata(file: str, ffprobe: str):
    # Get the metadata from the file with ffmpeg (first audio stream only)
    ffprobe_json = json.loads(subprocess.check_output([ffprobe, '-v', 'quiet', '-of', 'json', '-show_streams', '-select_streams', 'a:0', file]).decode('utf-8'))

    try:
        author = str(ffprobe_json['streams'][0]['tags']['AUTHOR'])
        custom1 = str(ffprobe_json['streams'][0]['tags']['CUSTOM1'])
    except KeyError:
        printCriticalError("AUTHOR or CUSTOM1 metadata is missing. Please check the file.")

    if author == "" or custom1 == "":
        printCriticalError("AUTHOR or CUSTOM1 metadata is empty. Please check the file.")

    # Print the metadata
    print("Base 64 Author:  " + author)
    print("Base 64 Custom1: " + custom1)

    # Decode
    decoded_author = decode_base64(author)
    decoded_custom1 = decode_base64(custom1)

    # Get the filename from the input
    filename = os.path.splitext(os.path.basename(sys.argv[1]))[0]

    # Print the metadata
    print("\nDecoded Author: ", decoded_author)
    print("Decoded Custom1:", decoded_custom1)
    
    # Decompress the decoded strings with zlib
    decompressed_author = zlib.decompress(decoded_author)
    decompressed_custom1 = zlib.decompress(decoded_custom1)

    # Print the metadata
    print("\nDecompressed Author: ", decompressed_author)
    print("Decompressed Custom1:", decompressed_custom1)

    # Write the decoded and decompressed strings to a file
    with open(f"{filename}.glypha", 'wb') as f:
        f.write(decompressed_author)
    with open(f"{filename}.glyphc1", 'wb') as f:
        f.write(decompressed_custom1)


# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

# Parse the arguments
args = buildArgumentsParser().parse_args()

# Check the requirements
checkRequirements(args.ffmpeg[0], args.ffprobe[0], bool(args.w))

# Perform all the checks before downloading the video
try:
    performChecks(args.__dict__)
except Exception as e:
    printCriticalError(str(e))

if args.w:
    # Write the metadata back to the file
    write_metadata(args.FILE[0], args.w[0], args.w[1], args.t[0], args.ffmpeg[0])
else:
    # Read the metadata from the file
    read_metadata(args.FILE[0], args.ffprobe[0])

cprint("Done!", color="green", attrs=["bold"])