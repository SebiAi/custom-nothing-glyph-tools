#!/usr/bin/python3

import sys
import argparse
import os
import csv
import re
import zlib
from termcolor import cprint, colored
from enum import Enum

REGEX_PATTERN_TEXT = '^((?:[1-9]|1[0-1])|(?:#(?:[1-9]|[1-2]\d|3[0-3])))-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN|LOG))?$'

# +------------------------------------+
# |                                    |
# |         Global Constants           |
# |                                    |
# +------------------------------------+

# Enum definition for the global mode
## 'Compatibility': Compatibility mode for Phone (1) and Phone (2)
## 'Phone2': Phone (2) only mode (includes Glyph and Zone control)
GlobalMode = Enum('GlobalMode', ['Compatibility', 'Phone2'])

# Definition of the Glyphs for the Phone2 mode - defines the zones for each glyph and the index of the glyph
GlyphsPhone2: list[list[int]] = [
    [0], # GLYPH_CAMERA_TOP
    [1], # GLYPH_CAMERA_BOTTOM
    [2], # GLYPH_DIAGONAL
    range(3, 19), # GLYPH_BATTERY_TOP_RIGHT
    [19], # GLYPH_BATTERY_TOP_LEFT
    [20], # GLYPH_BATTERY_TOP_VERTICAL
    [21], # GLYPH_BATTERY_BOTTOM_LEFT
    [22], # GLYPH_BATTERY_BOTTOM_RIGHT
    [23], # GLYPH_BATTERY_BOTTOM_VERTICAL
    range(25, 33), # GLYPH_USB_LINE
    [24] # GLYPH_USB_DOT
]

# Map the 5 Glyphs to the 11 Glyphs
Glyphs5To11Mapping: list[list[int]] = [
    [0, 1], # GLYPH_CAMERA
    [2], # GLYPH_DIAGONAL
    [3, 4, 5, 6, 7, 8], # GLYPH_BATTERY
    [9], # GLYPH_USB_LINE
    [10] # GLYPH_USB_DOT
]

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def buildArgumentsParser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Transform Audacity Labels to Glyphs format.", epilog="audacity label format:\n  The text part of the exported Labels file is constructed like this: 'glyphId-lightLevelFrom[-lightLevelTo[-Mode]]'\n  AND must match this regex: '" + REGEX_PATTERN_TEXT + "', where the lightlevels are given in percent (0-100). When no mode is given 'LIN' will be used.\n\n  To convey the end of the audio file a final Label called 'END' MUST be pressent.\n\n  'LIN' - Linear\n  'EXP' - Exponential\n  'LOG' - Logarithmic\n  https://www.desmos.com/calculator/92ajzgfbat\n\n  Examples:\n    1-100\n    2-0-100-LIN\n    2-50-LIN\n\nCreated by: Sebastian Aigner (aka. SebiAi)")

    parser.add_argument('FILE', help="An absolute or relative path to the Label file.", type=str, nargs=1)
    parser.add_argument('--disableCompatibility', help="Force the Phone (2) mode if it is not automatically detected.", action='store_true')
    parser.add_argument('--watermark', help="An absolute or relative path to the watermark file. It will be embeded into the glypha file.", type=str, nargs=1)
    #parser.add_argument('-r', help="Try to reverse the Glyph format back into Audacity labels. You need to provide paths to the author and custom1 file.", type=str, nargs=1, metavar=('AUTHOR_FILE'))

    return parser

# Check the requirements
def checkRequirements():
    return


# Perform argument checks
def performChecks(args: dict):
    # Check if the file exists
    if not os.path.isfile(args['FILE'][0]):
        if args.get('r', False):
            # We are in reverse mode -> CUSTOM1 file must exist
            raise Exception(f"CUSTOM1 file does not exist: '{args['FILE'][0]}'")
        else:
            # We are in normal mode -> Audacity file must exist
            raise Exception(f"Audacity file does not exist: '{args['FILE'][0]}'")
    
    # Check if the watermark file exists
    if args.get('watermark', None) is not None:
        if not os.path.isfile(args['watermark'][0]):
            raise Exception(f"Watermark file does not exist: '{args['watermark'][0]}'")

    # Check if we need to write the metadata back
    if args.get('r', False):
        # Check if the file exists
        if not os.path.isfile(args['w'][0]):
            raise Exception(f"AUTHOR file does not exist: '{args['w'][0]}'")

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

def get_divisable_by(number: int, divisor: int) -> int:
    return number - (number % divisor)

def audacity_to_glyphs(file: str, disableCompatibility: bool = False, watermarkPath: str = None):
    # Constants for the csv file
    FROM = 0
    TO = 1
    TEXT = 2

    # Parse input csv file
    labels: list[dict[str, Any]] = []
    endLabel: dict[str, Any] = None
    endLabels: list[dict[str, Any]] = []
    globalModeState: GlobalMode = GlobalMode['Compatibility']
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', strict=True, skipinitialspace=True)
        for i, row in enumerate(reader):
            # Check if the row is valid
            if len(row) != 3:
                printWarning(f"Row {i + 1} is invalid. Skipping.")
                continue

            # Get all three values
            try:
                fromTime = float(row[FROM]) * 1000
                toTime = float(row[TO]) * 1000
                deltaTime = toTime - fromTime
                text = row[TEXT].strip()
            except:
                printWarning(f"Row {i + 1} could not be parsed. Skipping.")
                continue
            
            # Check if the text matches "END" to indicate the end of the audio file
            if text == "END":
                endLabels.append({"from": fromTime, "to": toTime, "delta": deltaTime, "line": i + 1})
                continue

            # Get the values from the text
            result = re.match(REGEX_PATTERN_TEXT, text)
            if result is None:
                if '[' in text or ']' in text:
                    printWarning(f"Row {i + 1} text is invalid - seems like you have brackets in your Label name => remove them!. Skipping.")
                else:
                    printWarning(f"Row {i + 1} text is invalid. Skipping.")
                continue

            glyph_str = result.group(1)
            isZone: bool = False
            # Update the global mode state
            if glyph_str.startswith('#'):
                isZone = True
                glyph_str = glyph_str[1:]
                globalModeState = GlobalMode['Phone2']

            id = int(glyph_str)
            # Update the global mode state
            if id > 5:
                globalModeState = GlobalMode['Phone2']

            # Determine the light levels and mode
            fromLightLV = int(result.group(2))
            toLightLV = int(result.group(3)) if result.group(3) is not None else fromLightLV
            mode = result.group(4) if result.group(4) is not None else "LIN"

            # Add the Label to the list
            labels.append({"from": fromTime, "to": toTime, "delta": deltaTime, "id": id, "fromLV": fromLightLV, "toLV": toLightLV, "mode": mode, "isZone": isZone, "line": i + 1})
    
    # Check if we found the end
    if len(endLabels) == 0:
        printCriticalError(f"No 'END' label found. Please set a Label at the end of the audio file with the name 'END'.")

    # Check if we have any labels
    if len(labels) == 0:
        printCriticalError(f"No Labels found.")
    
    # Check if the labels are sorted
    if not all(labels[i]["from"] <= labels[i + 1]["from"] for i in range(len(labels) - 1)):
        # Inform user
        printInfo(f"Labels are not sorted by time. This is perfectly normal when using multiple Label tracks. Sorting them now.")
        # Sort the labels
        labels.sort(key=lambda x: x["from"])
    
    # Sort the end labels and get the last one
    endLabels.sort(key=lambda x: x["to"])
    endLabel = endLabels[-1]
    if len(endLabels) > 1:
        printInfo(f"Found {len(endLabels)} 'END' labels. Using the last one in row {endLabel['line']}.")
    
    # Remove all labels that are after the END label
    oldLabelSize = len(labels)
    labels = [label for label in labels if label["to"] < endLabel["to"]]
    if len(labels) != oldLabelSize:
        printWarning(f"Removed {oldLabelSize - len(labels)} labels that were after the 'END' label.")
    
    # Inform the user about the global mode state
    if disableCompatibility:
        globalModeState = GlobalMode['Phone2']
        printInfo(f"Using forced Phone (2) mode.")
    else:
        if globalModeState == GlobalMode['Compatibility']:
            printInfo(f"Auto detected Phone (1) and Phone (2) compatibility mode.")
            printInfo(f"If you intended to use the Glyphs 1-5 on the Nothing Phone (2) use the '--disableCompatibility' parameter. More info with '--help' or in the README.")
        else:
            printInfo(f"Auto detected Phone (2) mode.")

    # Get the filename without extension of the input file
    filename = os.path.splitext(os.path.basename(file))[0]

    # Define the stepsizes in ms
    TIME_STEP_SIZE = 16
    MAX_LIGHT_LV = 4080

    # Calculate the number of lines in the AUTHOR file + 5 extra lines for margin
    numLines = int(get_divisable_by(int(endLabel['to'] + TIME_STEP_SIZE), TIME_STEP_SIZE) / TIME_STEP_SIZE + 5)

    # Prepare and prefill the author data depending on the global mode state
    author_data: list[list[int]] = [[0 for x in range(5)] for y in range(numLines)] if globalModeState == GlobalMode['Compatibility'] else [[0 for x in range(33)] for y in range(numLines)]

    # Generate AUTHOR data and write the CUSTOM1 file
    with open(f"{filename}.glyphc1", "w") as authorFile:
        for i, label in enumerate(labels):
            # Get values
            fromTime: int = get_divisable_by(round(label['from']), TIME_STEP_SIZE)
            toTime: int = get_divisable_by(round(label['to']), TIME_STEP_SIZE)
            deltaTime: int = max(0, int((toTime - fromTime) / TIME_STEP_SIZE) - 1)
            id: int = int(label['id'] - 1)
            fromLightLV: int = max(1, round(label['fromLV'] * MAX_LIGHT_LV / 100.0))
            toLightLV: int = max(1, round(label['toLV'] * MAX_LIGHT_LV / 100.0))
            mode: str = str(label['mode'])
            isZone: bool = bool(label['isZone'])

            # Debug print all the values
            #print(f"Entry {i + 1}: {fromTime} - {toTime} ({deltaTime}) | {glyph} {fromLightLV} {toLightLV} {mode}")

            # Get the glyph index
            ## Return the index of the first occurence of 'glyph' in the GlyphsPhone2 list[list[int]]
            #| globalModeState | isZone || glyphIndex                                     |
            #|-----------------|--------||------------------------------------------------|
            #| Compatibility   | False  || use id                                         |
            #| Compatibility   | True   || INVALID                                        |
            #| Phone2          | False  || use id                                         |
            #| Phone2          | True   || search for id in GlyphsPhone2 and return index |
            glyphIndex = next((i for i, glyphSet in enumerate(GlyphsPhone2) if id in glyphSet)) if isZone else id

            # Get the columns we need to write to
            #| globalModeState | isZone || columns                            |
            #|-----------------|--------||------------------------------------|
            #| Compatibility   | False  || use id                             |
            #| Compatibility   | True   || INVALID                            |
            #| Phone2          | False  || get list with id from GlyphsPhone2 |
            #| Phone2          | True   || use id                             |
            columns = GlyphsPhone2[glyphIndex] if globalModeState == GlobalMode['Phone2'] and not isZone else [id]

            # CUSTOM1 (time in ms-glyph,)
            ## Map the 11 Glyphs to the 5 Glyphs and write the time and the glyph index
            authorFile.write(f"{fromTime}-{next((i for i, glyphMapping in enumerate(Glyphs5To11Mapping) if glyphIndex in glyphMapping))},")

            # AUTHOR
            overwrites = 0
            for j, row in enumerate(range(int(fromTime / TIME_STEP_SIZE), int(fromTime / TIME_STEP_SIZE) + deltaTime + 1)):
                # Calculate the light level depending on the mode
                if mode == "LIN": # Linear
                    lightLV = round(fromLightLV + ((toLightLV - fromLightLV) / max(1, deltaTime)) * j)
                elif mode == "EXP": # Exponential
                    lightLV = round(fromLightLV * ((toLightLV / fromLightLV) ** (j / max(1, deltaTime))))
                elif mode == "LOG": # Logarithmic
                    lightLV = round(-toLightLV*(toLightLV/fromLightLV)**(-j/max(1, deltaTime)) + fromLightLV + toLightLV)
                
                # Assert
                assert lightLV >= 0 and lightLV <= MAX_LIGHT_LV, f"Light level {lightLV} is out of range [0, {MAX_LIGHT_LV}]"

                for column in columns:
                    # Check if there is already a value present
                    if author_data[row][column] != 0:
                        overwrites += 1
                    # Write the light level to the author data
                    author_data[row][column] = lightLV
            
            # Print warning if there were overwrites
            if overwrites > 0:
                if isZone:
                    printWarning(f"Row {label['line']} overwrote {overwrites} value(s) for zone {columns[0] + 1}.")
                else:
                    printWarning(f"Row {label['line']} overwrote {overwrites} value(s) for glyph {glyphIndex + 1}.")
    
    # Get the watermark data
    if watermarkPath:
        watermarkData = encode_watermark_from_file(watermarkPath, len(author_data[0]))

    # Write the AUTHOR file
    with open(f"{filename}.glypha", "w", newline='') as authorFile:
        csvWriter = csv.writer(authorFile, delimiter=',', lineterminator=',\r\n', strict=True)
        csvWriter.writerows(author_data)
        if watermarkPath:
            csvWriter.writerows(watermarkData)
            printInfo("Embeded watermark into the glypha file.", start="\n")

# Encode the watermark to the AUTHOR format from a file
def encode_watermark_from_file(watermarkPath: str, numColumns: int) -> list[list[int]]:
    # Read the watermark file
    with open(watermarkPath, "rb") as watermarkFile:
        watermark: bytes = zlib.compress(watermarkFile.read(), zlib.Z_BEST_COMPRESSION)
    
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
    checkRequirements()

    # Perform all the checks before downloading the video
    try:
        performChecks(args.__dict__)
    except Exception as e:
        printCriticalError(str(e))

    # Normal mode - convert Audacity Labels to Glyphs format
    audacity_to_glyphs(args.FILE[0], args.disableCompatibility, args.watermark[0] if args.watermark is not None else None)

    cprint("Done!", color="green", attrs=["bold"])

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        printCriticalError("Interrupted by user.", 130)
    # except Exception as e:
    #     printCriticalError(str(e))
