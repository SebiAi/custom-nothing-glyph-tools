#!/usr/bin/python3

import mido
import csv
from termcolor import cprint
import argparse
import sys
import os

# +------------------------------------+
# |                                    |
# |           Bioler Plate             |
# |                                    |
# +------------------------------------+

# Build the arguments parser
def buildArgumentsParser() -> argparse.ArgumentParser:
    # Parse the arguments with argparse (https://docs.python.org/3/library/argparse.html)
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Transform MIDI files to Audacity Labels.", epilog="MIDI format:\n  Use notes 60 to 70 for normal glyphs and 80 to 112 for zones.\n  The velocity of the note is the percentage of the light intensity (100% is 127).\n  The channel is used to define the mode (0 = LIN, 1 = EXP, 2 = LOG).")

    parser.add_argument('FILE', help="An absolute or relative path to the file.", type=str, nargs=1)

    return parser

# Check the requirements
def checkRequirements():
    return


# Perform argument checks
def performChecks(args: dict):
    # Check if the file exists
    if not os.path.isfile(args['FILE'][0]):
        raise Exception(f"MIDI file does not exist: '{args['FILE'][0]}'")

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
# |             Constants              |
# |                                    |
# +------------------------------------+

TIME_PRECISION_EXPONENT: int = 6
TIME_PRECISION: int = pow(10, TIME_PRECISION_EXPONENT)

# +------------------------------------+
# |                                    |
# |             Functions              |
# |                                    |
# +------------------------------------+

def isNoteValid(note: int) -> bool:
    # From 60 to 70 (Normal Glyph - 11) and from 80 to 112 (Zones - 33)
    return note >= 60 and note <= 70 or note >= 80 and note <= 112

def getModeFromChannel(channel: int) -> str:
    match channel:
        case 1:
            return "EXP"
        case 2:
            return "LOG"
        case _:
            if channel > 2:
                printError(f"Channel '{channel}' should be 0 to 2! Using default mode 'LIN'...")
            return "LIN"

def appendGlyph(glyphList: list, fromTime: int, toTime: int, isZone: bool, note: int, lightFrom: int, lightTo: int, mode: str) -> None:
    glyphList.append({
        "from": fromTime / TIME_PRECISION,
        "to": toTime / TIME_PRECISION,
        "label": f"{'#' if isZone else ''}{note - 79 if isZone else note - 59}-{lightFrom}-{lightTo}-{mode}"
    })

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

    # Perform all the checks
    try:
        performChecks(args.__dict__)
    except Exception as e:
        printCriticalError(str(e))
    


    # Load MIDI file
    mid = mido.MidiFile(args.FILE[0])

    # Print midi infos
    print(f"Ticks per beat: {mid.ticks_per_beat}")
    print(f"Number of tracks: {len(mid.tracks)}")
    print(f"Audio lenght: {round(mid.length, 3)}s\n")

    # Limit to one track for now
    if len(mid.tracks) > 1:
        printCriticalError("Only one track is supported for now!")

    # Print MIDI messages
    globalTime: int = 0
    noteOnCache: dict = {}
    outputList: list[dict] = []
    for msg in mid:
        # Add time to global time
        globalTime += int(msg.time * TIME_PRECISION)

        # Do not process meta messages
        if msg.is_meta:
            continue

        if msg.type == 'note_on' and msg.velocity > 0: # note_on with velocity of 0 is equivalent to note_off
            note: int = msg.note
            percent: int = int(msg.velocity / 127 * 100)
            assert(percent >= 0 and percent <= 100)
            mode: str = getModeFromChannel(msg.channel)

            # Check if Glyph is valid
            if not isNoteValid(note):
                printWarning(f"Note '{note}' is not valid at {globalTime / TIME_PRECISION}s (ON)! Ignoring...")
                continue
            
            # Check if Glyph is already in cache
            if note in noteOnCache:
                printWarning(f"Note '{note}' starting at {globalTime / TIME_PRECISION}s is already on! Stopping previous Glyph and starting new one...")
                # Add Glyph to output list
                appendGlyph(outputList, noteOnCache[note]['time'], globalTime, noteOnCache[note]['isZone'], note, noteOnCache[note]['lightPercent'], noteOnCache[note]['lightPercent'], noteOnCache[note][mode])
                # Delete Glyph from cache
                del noteOnCache[note]
            
            # Add note to cache
            noteOnCache[note] = {'time': globalTime, 'lightPercent': percent, 'mode': mode, 'isZone': note >= 80}
            

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            note: int = msg.note
            percent: int = int(msg.velocity / 127 * 100)
            assert(percent >= 0 and percent <= 100)

            # Check if Glyph is valid
            if not isNoteValid(note):
                printWarning(f"Note '{note}' is not valid at {globalTime / TIME_PRECISION}s (OFF)! Ignoring...")
                continue

            # Check if Glyph is already in cache
            if note in noteOnCache:
                # Add Glyph to output list
                appendGlyph(outputList, noteOnCache[note]['time'], globalTime, noteOnCache[note]['isZone'], note, noteOnCache[note]['lightPercent'], percent, noteOnCache[note]['mode'])
                
                # Remove Glyph from cache
                del noteOnCache[note]
            else:
                printError(f"Received 'Note Off' command at {globalTime / TIME_PRECISION}s for note '{note}' without 'Note On'! Skipping...")
                continue

        else:
            printWarning(f"Message '{msg.type}' not supported! Skipping...")

    # Check if the cache is empty
    if len(noteOnCache) > 0:
        printWarning(f"End of MIDI file reached. {len(noteOnCache)} Glyphs are still active! Stopping them...")
        for note in noteOnCache:
            appendGlyph(outputList, noteOnCache[note]['time'], globalTime, noteOnCache[note]['isZone'], note, noteOnCache[note]['lightPercent'], noteOnCache[note]['lightPercent'], noteOnCache[note]['mode'])

    # Add 'END' Label
    outputList.append({
        "from": globalTime / TIME_PRECISION,
        "to": globalTime / TIME_PRECISION,
        "label": "END"
    })

    # Sort output list by 'from' key
    outputList.sort(key=lambda x: x["from"])

    # Get the filename without extension of the input file
    filename = os.path.splitext(os.path.basename(args.FILE[0]))[0]

    # Write output list to CSV file
    with open(f"{filename}.txt", 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in outputList:
            csvwriter.writerow([("{:." + str(TIME_PRECISION_EXPONENT) + "f}").format(row["from"]), ("{:." + str(TIME_PRECISION_EXPONENT) + "f}").format(row["to"]), row["label"]])

    cprint("Done!", color="green", attrs=["bold"])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        printCriticalError("Interrupted by user.", 130)
    # except Exception as e:
    #     printCriticalError(str(e))