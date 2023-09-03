#!/usr/bin/python3

import base64
import sys
import subprocess
import argparse
import os
import zlib
import json
import csv
from termcolor import cprint, colored
from enum import Enum

base64_padding = '=='

# +------------------------------------+
# |                                    |
# |         Global Constants           |
# |                                    |
# +------------------------------------+

# Enum definition for the global mode
## 'Compatibility': Compatibility mode for Phone (1) and Phone (2)
## 'Phone2': Phone (2) only mode (includes Glyph and Zone control)
GlobalMode = Enum('GlobalMode', ['Compatibility', 'Phone2'])

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

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

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

# Print info message
def printInfo(message, start: str = ""):
    cprint(start + "INFO: " + message, color="cyan")

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def decode_base64(encoded_string: str) -> bytes:
    return base64.b64decode(encoded_string + base64_padding)

def encode_base64(bytes: bytes) -> str:
    return base64.b64encode(bytes).decode('utf-8').removesuffix(base64_padding)

def get_mode(data: bytes) -> GlobalMode:
    # Detect the mode by simply counting the commas (5 Glyphs = Compatibility, 33 Zones = Phone2)
    if data.splitlines()[0].count(b',') < 32:
        return GlobalMode.Compatibility
    else:
        return GlobalMode.Phone2

def ffmpeg_write_metadata(ffmpeg: str, file: str, tmp_file: str, metadata: dict[str, str]):
    # Beginning of the ffmpeg command
    ffmpeg_command = [ffmpeg, '-v', 'quiet', '-i', file]

    # Loop through the metadata and add it to the ffmpeg command
    for key_escaped, value_escaped in metadata.items():
        ffmpeg_command += ['-metadata:s:a:0', f'{key_escaped}={value_escaped}']
    
    # Add the end parameters to the ffmpeg command
    ffmpeg_command += ['-c', 'copy', '-y', '-fflags', '+bitexact', '-flags:v', '+bitexact', '-flags:a', '+bitexact', tmp_file]

    # If OS is Windows and the ffmpeg command is longer than 32764 characters, we need to save the metadata to a file and pass it to ffmpeg
    if os.name == 'nt' and len(' '.join(ffmpeg_command)) > 32764:
        # Print info
        printInfo("ffmpeg command is longer than 32764 characters which is the limit on Windows. Saving metadata to file and passing it to ffmpeg.")
        
        # Save the metadata to a file in tmp folder
        metadata_to_remove: list[str] = []
        metadata_file = 'FFMETADATAFILE'
        with open(metadata_file, 'w', newline='\n') as f:
            f.write(';FFMETADATA1')
            for key, value in metadata.items():
                if key == "":
                    continue
                if value == "":
                    # Add to the remove list (this will only be needed when we need to use the metadata file solution)
                    metadata_to_remove.append(key)
                # Escape '=', ';', '#', '\', '\n' in the key and value
                key_escaped = key.replace('\\', '\\\\').replace('=', '\\=').replace(';', '\\;').replace('#', '\\#').replace('\n', '\\\n')
                value_escaped = value.replace('\\', '\\\\').replace('=', '\\=').replace(';', '\\;').replace('#', '\\#').replace('\n', '\\\n')
                f.write(f'\n{key_escaped}={value_escaped}')
        
        # Build new ffmpeg command
        ffmpeg_command = [ffmpeg, '-v', 'quiet', '-i', file, '-i', metadata_file, '-c', 'copy', '-y', '-map_metadata', '1']
        for m in metadata_to_remove:
            # The tag gets removed if it is already present in the input file metadata (does not work with just the file pass method)
            ffmpeg_command += ['-metadata:s:a:0', f"{m}="]
        ffmpeg_command += ['-fflags', '+bitexact', '-flags:v', '+bitexact', '-flags:a', '+bitexact', tmp_file]

        # Run new ffmpeg command
        subprocess.run(ffmpeg_command)

        # Delete the metadata file
        os.remove(metadata_file)
    else:
        subprocess.run(ffmpeg_command)
    
    # Delete the old file - needed for Windows or else os.rename() will fail
    os.remove(file)

    # Copy back the file
    os.rename(tmp_file, file)


# Get the length of the watermark data
def watermark_get_length(watermarkData: bytes) -> int:
    to = watermarkData.find(b',', 5)
    if to == -1:
        printCriticalError("Watermark length could not be found. Please check the file.")
    return int(watermarkData[5:to])

# Returns the decoded watermark
def decode_watermark(watermarkData: bytes) -> str:
    if watermarkData.find(b'4081') == -1 or len(watermarkData) == 0:
        raise ValueError("Watermark not found in the data.")

    # Get the length of the watermark
    length = watermark_get_length(watermarkData)
    
    # Read the watermark as csv
    csvReader = csv.reader(watermarkData.decode('utf-8').splitlines(), delimiter=',', strict=True)
    # Flatten the list, remove empty strings convert to int, trim to the length of the watermark and convert to bytes
    data = bytes([int(x) for y in csvReader for x in y if x != ''][2:length + 2])

    return zlib.decompress(data).decode('utf-8')

# Returns the watermark (if present, else None) and the author data from the data
def split_watermark_from_author(data: bytes) -> (bytes, bytes):
    # Check if we don't have a watermark or the data is empty
    if data.find(b'4081') == -1 or len(data) == 0:
        return (None, data)
    
    startIndex = data.rfind(b'4081')
    watermarkData = data[startIndex:]
    authorData = data[:startIndex]

    return (watermarkData, authorData)

# Returns the watermark (if present, else None) and the author data from the file
def read_author_file(file: str) -> (bytes, bytes):
    with open(file, 'rb') as f:
        data = f.read()

    # Find the last occurence of the watermark marker
    watermarkData, authorData = split_watermark_from_author(data)

    if watermarkData == None:
        return (None, authorData)

    # Get number of columns
    if get_mode(data) == GlobalMode.Compatibility:
        columns = 5
    else:
        columns = 33

    # Get number of rows of the watermark
    watermarkRows = int(watermark_get_length(watermarkData) / columns) + 1
    if len(watermarkData.splitlines()) < watermarkRows:
        printCriticalError("Watermark length is longer than the file. Please check the file.")

    return (watermarkData, authorData)

def write_metadata(file: str, author_file: str, custom1_file: str, custom_title: str, ffmpeg: str):
    watermark, author = read_author_file(author_file)
    with open(custom1_file, 'rb') as f:
        custom1 = f.read()

    if author == "" or custom1 == "":
        printCriticalError("AUTHOR or CUSTOM1 metadata is empty. Please check the files.")

    if watermark:
        try:
            decodedWatermark = decode_watermark(watermark)
        except:
            printCriticalError("Watermark decoding failed. Please check the file.")
        
        # Print the watermark
        printInfo("Watermark by creator detected - always give credit to the creator!")
        print(decodedWatermark + '\n')

    # Compress the strings with zlib
    compressed_author = zlib.compress(author, zlib.Z_BEST_COMPRESSION)
    compressed_custom1 = zlib.compress(custom1, zlib.Z_BEST_COMPRESSION)

    # Encode
    encoded_author = encode_base64(compressed_author)
    encoded_custom1 = encode_base64(compressed_custom1)

    # New line every 76 characters (76 character is the new line character)
    encoded_author = '\n'.join(encoded_author[i:i+76] for i in range(0, len(encoded_author), 76))
    encoded_custom1 = '\n'.join(encoded_custom1[i:i+76] for i in range(0, len(encoded_custom1), 76))

    # Tmp file name
    split_file = os.path.splitext(file)
    tmp_file = split_file[0] + '_new' + split_file[1]

    # Set the metadata
    ffmpegMetadata = {'TITLE': custom_title, 'ALBUM': 'CUSTOM', 'AUTHOR': encoded_author, 'COMPOSER': 'Spacewar Glyph Composer', 'CUSTOM1': encoded_custom1, 'CUSTOM2': '', 'GLYPHER_WATERMARK': ''}
    if get_mode(author) == GlobalMode.Compatibility:
        # Write the metadata back to the file (5 Glyphs)
        printInfo(f"Auto detected Phone (1) and Phone (2) compatibility mode.")
    else:
        # Write the metadata back to the file (33 Zones)
        printInfo(f"Auto detected Phone (2) mode.")
        ffmpegMetadata['COMPOSER'] = 'Pong Glyph Composer'
        ffmpegMetadata['CUSTOM2'] = '33cols'
    
    # Add the watermark if present
    if watermark != None:
        ffmpegMetadata['GLYPHER_WATERMARK'] = decodedWatermark

    # Write the metadata back to the file
    ffmpeg_write_metadata(ffmpeg, file, tmp_file, ffmpegMetadata)

    # Print number of bytes written
    print(f"Wrote {colored(len(bytearray(encoded_author, 'utf-8')), attrs=['bold'])} bytes of AUTHOR metadata")
    print(f"Wrote {colored(len(bytearray(encoded_custom1, 'utf-8')), attrs=['bold'])} bytes of CUSTOM1 metadata")

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

    # Get watermark if present
    try:
        watermark = str(ffprobe_json['streams'][0]['tags']['GLYPHER_WATERMARK'])
        printInfo("Watermark by creator detected - always give credit to the creator!")
        print(watermark + '\n')
    except KeyError:
        watermark = None

    # Print number of bytes read
    print(f"Read {colored(len(bytearray(author, 'utf-8')), attrs=['bold'])} bytes of AUTHOR metadata")
    print(f"Read {colored(len(bytearray(custom1, 'utf-8')), attrs=['bold'])} bytes of CUSTOM1 metadata")

    # Decode
    decoded_author = decode_base64(author)
    decoded_custom1 = decode_base64(custom1)

    # Get the filename from the input
    filename = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    
    # Decompress the decoded strings with zlib
    decompressed_author = zlib.decompress(decoded_author)
    decompressed_custom1 = zlib.decompress(decoded_custom1)
    
    # Check if there is a watermark in the author data
    watermarkDataSplit, decompressed_author = split_watermark_from_author(decompressed_author)
    if watermarkDataSplit != None:
        try:
            watermarkAuthor = decode_watermark(watermarkDataSplit)
        except:
            printCriticalError("Watermark decoding failed. Please check the file.")
        printInfo("Watermark by creator detected in author data - always give credit to the creator!")
        print(watermarkAuthor + '\n')
    
    # Get watermark data (combine if we have two watermarks)
    nColumns = 5 if get_mode(decompressed_author) == GlobalMode.Compatibility else 33
    if watermark and watermarkDataSplit:
        printInfo("Combining watermarks...")
        watermarkData = encode_watermark(f"{watermark}\n\n{watermarkAuthor}", nColumns)
    elif watermark:
        watermarkData = encode_watermark(watermark, nColumns)
    elif watermarkDataSplit:
        watermarkData = encode_watermark(watermarkAuthor, nColumns)
    else:
        watermarkData = None

    # Write the decoded and decompressed strings to a file
    with open(f"{filename}.glypha", 'wb') as f:
        f.write(decompressed_author)
        if not decompressed_author.endswith(b'\r\n'):
            f.write(b'\r\n')

    if watermarkData:
        with open(f"{filename}.glypha", "a", newline='') as authorFile:
            csv.writer(authorFile, delimiter=',', lineterminator=',\r\n', strict=True).writerows(watermarkData)

    with open(f"{filename}.glyphc1", 'wb') as f:
        f.write(decompressed_custom1)

# Encode the watermark to the AUTHOR format
def encode_watermark(watermark: str, numColumns: int) -> list[list[int]]:
    watermark: bytes = zlib.compress(bytes(watermark, 'utf-8'), zlib.Z_BEST_COMPRESSION)
    
    output: list[list[int]] = [[0 for x in range(numColumns)]]
    # Add header
    output[0][0] = 4081
    output[0][1] = len(watermark)
    # Process the watermark
    for i, byte in enumerate(watermark):
        # Offset i by 2 because of the header
        i += 2
        # Calculate the row and column
        row = int(i / numColumns)
        column = i % numColumns
        # Check if we need a new row
        if len(output) <= row:
            output.append([0 for x in range(numColumns)])
        # Write the byte
        output[row][column] = byte
    
    # Return the output
    return output

# +------------------------------------+
# |                                    |
# |             Main Code              |
# |                                    |
# +------------------------------------+

def main() -> int:
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

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        printCriticalError("Interrupted by user.", 130)
    # except Exception as e:
    #     printCriticalError(str(e))