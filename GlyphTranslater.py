#!/usr/bin/python3

import sys
import argparse
import os
import csv
import re
from termcolor import cprint

REGEX_PATTERN_TEXT = '^([1-5])-(\d{1,3})(?:-(\d{1,3}))?(?:-(EXP|LIN))?$'

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def buildArgumentsParser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Transform Audacity Labels to Glyphs format.", epilog="audacity label format:\n  The text part of the exported Labels file is constructed like this: 'glyphId-lightLevelFrom[-lightLevelTo[-Mode]]'\n  AND must match this regex: '" + REGEX_PATTERN_TEXT + "', where the lightlevels are given in percent (0-100). When no mode is given 'LIN' will be used.\n\n  To convey the end of the audio file a final Label called 'END' MUST be pressent.\n\n  'LIN' - Linear\n  'EXP' - Exponential\n\n  Examples:\n    1-100\n    2-0-100-LIN\n    2-50-LIN\n\nCreated by: Sebastian Aigner (aka. SebiAi)")

    parser.add_argument('FILE', help="An absolute or relative path to the file.", type=str, nargs=1)
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

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def get_divisable_by(number: int, divisor: int) -> int:
    return number - (number % divisor)

def audacity_to_glyphs(file: str):
    # Constants for the csv file
    FROM = 0
    TO = 1
    TEXT = 2

    # Constants for the text interpretation
    TEXT_GLYPH = 0
    TEXT_FROMLIGHTLV = 1
    TEXT_TOLIGHTLV = 2
    TEXT_MODE = 3

    # Parse input csv file
    labels: list[dict[str, Any]] = []
    endLabel: dict[str, Any] = None
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', strict=True, skipinitialspace=True)
        for i, row in enumerate(reader):
            # Check if we have more lines after the end
            if endLabel:
                printWarning(f"There is more data after the 'END' label in row {i}. This data will be ignored.")
                break

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
                #print(f"Row {i + 1}: {fromTime} - {toTime} ({deltaTime}) | {text} -> END")
                endLabel = {"from": fromTime, "to": toTime, "delta": deltaTime}
                continue

            # Get the values from the text
            result = re.match(REGEX_PATTERN_TEXT, text)
            if result is None:
                if '[' in text or ']' in text:
                    printWarning(f"Row {i + 1} text is invalid - seems like you have brackets in your Label name => remove them!. Skipping.")
                else:
                    printWarning(f"Row {i + 1} text is invalid. Skipping.")
                continue

            glyph = int(result.group(1))
            fromLightLV = min(int(result.group(2)), 100)
            toLightLV = min(int(result.group(3)), 100) if result.group(3) is not None else fromLightLV
            mode = result.group(4) if result.group(4) is not None else "LIN"
            
            # Debug print all the values
            #print(f"Row {i + 1}: {fromTime} - {toTime} ({deltaTime}) | {text} -> {glyph} {fromLightLV} {toLightLV} {mode}")

            # Add the Label to the list
            labels.append({"from": fromTime, "to": toTime, "delta": deltaTime, "glyph": glyph, "fromLV": fromLightLV, "toLV": toLightLV, "mode": mode})
    
    # Check if we found the end
    if not endLabel:
        printCriticalError(f"No 'END' label found. Please set a Label at the end of the audio file with the name 'END'.")

    # Check if we have any labels
    if len(labels) == 0:
        printCriticalError(f"No Labels found.")
    
    # Check if the labels are sorted
    if not all(labels[i]["from"] <= labels[i + 1]["from"] for i in range(len(labels) - 1)):
        printCriticalError(f"Labels are not sorted by time.")
    
    # Get the filename without extension of the input file
    filename = os.path.splitext(os.path.basename(file))[0]

    # Define the stepsizes in ms
    TIME_STEP_SIZE = 16
    LIGHT_STEP_SIZE = 16
    MAX_LIGHT_LV = 4080

    # Calculate the number of lines in the AUTHOR file + 5 extra lines for margin
    numLines = int(get_divisable_by(int(endLabel['to'] + TIME_STEP_SIZE), TIME_STEP_SIZE) / TIME_STEP_SIZE + 5)

    # Prepare and prefill the author data
    author_data: list[list[int]] = [[0 for x in range(5)] for y in range(numLines)]

    # Generate AUTHOR data and write the CUSTOM1 file
    with open(f"{filename}.glyphc1", "w") as custom1File:
        for i, label in enumerate(labels):
            # Get values
            fromTime: int = get_divisable_by(round(label['from']), TIME_STEP_SIZE)
            toTime: int = get_divisable_by(round(label['to']), TIME_STEP_SIZE)
            deltaTime: int = max(0, int((toTime - fromTime) / TIME_STEP_SIZE) - 1)
            glyph: int = int(label['glyph'] - 1)
            fromLightLV: int = max(1, get_divisable_by(round(label['fromLV'] * MAX_LIGHT_LV / 100.0), LIGHT_STEP_SIZE))
            toLightLV: int = max(1, get_divisable_by(round(label['toLV'] * MAX_LIGHT_LV / 100.0), LIGHT_STEP_SIZE))
            mode: str = str(label['mode'])

            # Debug print all the values
            #print(f"Entry {i + 1}: {fromTime} - {toTime} ({deltaTime}) | {glyph} {fromLightLV} {toLightLV} {mode}")

            # CUSTOM1 (time in ms-glyph,)
            custom1File.write(f"{fromTime}-{glyph},")

            # AUTHOR
            #for j, row in enumerate(range(int(fromTime / 16), int(toTime / 16) + 1)):
            tmp = range(int(fromTime / 16), int(toTime / 16) + 1)
            tmp1 = range(0, deltaTime + 1)
            for j, row in enumerate(range(int(fromTime / 16), int(fromTime / 16) + deltaTime + 1)):
                # Calculate the light level depending on the mode
                if mode == "LIN": # Linear
                    lightLV = get_divisable_by(round(fromLightLV + ((toLightLV - fromLightLV) / max(1, deltaTime)) * j), LIGHT_STEP_SIZE)
                elif mode == "EXP": # Exponential
                    lightLV = get_divisable_by(round(fromLightLV * ((toLightLV / fromLightLV) ** (j / max(1, deltaTime)))), LIGHT_STEP_SIZE)
                
                # Assert
                assert lightLV >= 0 and lightLV <= MAX_LIGHT_LV, f"Light level {lightLV} is out of range [0, {MAX_LIGHT_LV}]"

                # Write the light level to the author data
                author_data[row][glyph] = lightLV
    
    # Write the AUTHOR file
    with open(f"{filename}.glypha", "w", newline='') as custom1File:
        csv.writer(custom1File, delimiter=',', lineterminator=',\r\n', strict=True).writerows(author_data)


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
    audacity_to_glyphs(args.FILE[0])

    cprint("Done!", color="green", attrs=["bold"])

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        printCriticalError("Interrupted by user.", 130)
    # except Exception as e:
    #     printCriticalError(str(e))
