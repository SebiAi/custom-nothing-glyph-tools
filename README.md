# GLYPH TOOLS

<p align="center">
This repo is intended to be a collection of self contained tools and scripts to make it easy to create custom Nothing Glyph Compositions which in turn can be imported into the <i>Nothing Glyph Composer</i>.
</p>

https://github.com/SebiAi/custom-nothing-glyph-tools/assets/41116921/1852f2a6-1cf9-4c0e-9835-792bf1b09a58

***

# :clapper: Simple tutorial Video
https://www.youtube.com/watch?v=YlJBqQxSgWA

***

# :pushpin: Disclaimer
> These scripts are provided as-is without any warranty. I and all other contributors are not responsible for any damage, misuse or other kind of physical or mental damage which results in the use of these scripts.
This repo is in no way shape or form affiliated with Nothing Technology Limited (NOTHING).

***

# :safety_vest: Need help?
If you need help look at the [Troubleshooting](#interrobang-troubleshooting) chapter. If this does not help either feel free to reach out to me on Discord: @sebiai

***

# :construction: Compatibility
## OS
* Linux :white_check_mark:
* Windows :white_check_mark:
* Mac :white_check_mark:

I have only tested the scripts on Linux. Multiple people managed to do it on Windows and MacOS.
## Phones
* Nothing Phone (1) :white_check_mark:
* Nothing Phone (2) :white_check_mark:

Works on both Nothing devices. Supports all 33 Zones on Phone (2).

***

# :pencil2: Usage
## :memo: Requirements
* \[*Required*\] [**python3**](https://www.python.org/downloads/) - To run the scripts
* \[*Required*\] [**ffmpeg**](https://ffmpeg.org/download.html) - To write metadata to the sound file
* \[*Required*\] [**ffprobe**](https://ffmpeg.org/download.html) - To read metadata from the sound file (should be included in almost every ffmpeg install)
* \[*Optional*\] [**Audacity&reg;**](https://www.audacityteam.org/) - Create custom compositions more easily with Labels

    :arrow_right: If *ffmpeg* or *ffprobe* are not in PATH they can be passed to the script with the `--ffmpeg` and `--ffprobe` arguments.

    :arrow_right: If you are on ***Windows*** you can use (double click) the [Install-Dependencies.bat](./Install-Dependencies.bat) script to install all requirements.

## :rocket: Setup
#### Clone the repo
```bash
git clone https://github.com/SebiAi/custom-nothing-glyph-tools.git
cd custom-nothing-glyph-tools
```
If you don't feel comfortable using git then you can also [download an archive file here](https://github.com/SebiAi/custom-nothing-glyph-tools/archive/refs/heads/main.zip).

#### Install the necessary python dependencies
```bash
pip3 install -r requirements.txt
```
Sometimes it is also just `pip` instead of `pip3`.

## :sparkles: Making a custom Glyph composition
I would recommend using [Audacity&reg;](https://www.audacityteam.org/) to make your life easier. You can use it to cut your audio to the right length, layer effects on it, set Labels (which will come in handy later) and more.

### Cutting the sound
You can skip to [Creating the Glyph format with Audacity&reg;](#creating-the-glyph-format-with-audacity) if you already have the sound cut to the right length and the right codec (`opus`).

When exporting the sound always use the *opus* codec:
1) **Export audio:** Files -> Export -> Export Audio...
2) **Select the right codec in the dropdown:** Select Opus - default settings are fine
3) **Change the extension to *ogg* when naming your file!**
4) **Export**

### Creating the Glyph format with Audacity&reg;
To make our lives easier we can utilize Audacity&reg;'s Labels functionality and then use the Label data to generate our two needed csv files with the help of the [GlyphTranslator](./GlyphTranslator.py) - one for the *AUTHOR* tag (stores the light data) and the other for the *CUSTOM1* (stores data for the app to display) tag (for more info read the [technical details](#wrench-the-technical-details)).

I would recommend saving your Audacity&reg; project regularly.

You can also use the [MidiToLabel](./MidiToLabel.py) script to transform MIDI files to Audacity Labels. Use the `--help` command on the script to learn more.

#### Add the Labels track
1) **Open your audio with Audacity&reg;**
2) **Add the Labels track:** Tracks -> Add New -> Label Track (you can add multiple tracks)

#### Working with Labels
You can now add Labels by clicking on your desired location on the Label Track and pressing <kbd>CONTROL</kbd> + <kbd>b</kbd>. To remove one Label right-click on the Labels name and choose *Delete Label*. More info on how to work with them see [here](https://manual.audacityteam.org/man/label_tracks.html).

#### Naming format
Each Label should be named like this: `[#]glyphId-lightLevelFrom[-lightLevelTo[-Mode]]`
* **#** *(Optional)*: Just the `#` symbol to indicate that you want to address one of the 33 individual Zones on Phone (2).
* **glyphId**: See [glyphId](#glyphid) below.
* **lightLevelFrom**: In percent 0 to 100.
* **lightLevelTo** *(Optional)*: In percent 0 to 100. The default is *lightLevelFrom*.
* **Mode** *(Optional)*: Currently there are three modes supported ([Desmos Graphs](https://www.desmos.com/calculator/92ajzgfbat)):
    * LIN: Linear Interpolation (default)
    * EXP: Exponential Interpolation
    * LOG: Logarithmic Interpolation

The brackets (`[` and `]`) mean optional. Therefore do **NOT** include them in the Label name!

If you like regex patterns, the name of the Label should match this one (thanks [Joel05](https://github.com/SebiAi/custom-nothing-glyph-tools/issues/1)):
```regex
^((?:[1-9]|1[0-1])|(?:#(?:[1-9]|[1-2]\d|3[0-3])))-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN|LOG))?$
```

> **:warning: Important**

**At the end of the audio there MUST be a non ranged Label called *END*.** This is needed so the script knows how long the audio is. Also, make sure that there is enough space between your last Glyph lighting up and the *END* Label or else it might not get played - add silence at the end of the audio file if that happens and move the *END* Label accordingly.

##### glyphId
Depending on which Phone you want to make the composition for there are two modes that I have called the *Compatibility* or *Phone2* mode:
![Mode decision chart](./assets/Mode%20decision%20chart.png)

After you've made your decision continue to the respective section:
* [Compatibility mode](#compatibility-mode)
* [Phone2 mode](#phone2-mode)

###### Compatibility mode
* You can **NOT** use the `#` symbol in front which is used to control one of the 33 Zones of Phone (2).
* The `glyphId` can only be 1 to 5 which correspond to the individual Glyphs:

| glyphId | Glyph    |
|:-------:|:---------|
|    1    | Camera   |
|    2    | Diagonal |
|    3    | Battery  |
|    4    | USB Line |
|    5    | USB Dot  |

<img src="assets/Glyph%20Ids%20Compatibility%20mode.png" alt="Glyph Ids Compatibility mode" width="25%"/>

Example c1:
```
0.000000	1.000000	2-0-100-LIN
1.000000	2.000000	2-100-0-LIN
2.000000	3.000000	3-0-100-LIN
3.000000	4.000000	3-100-0-LIN
5.000000	5.000000	END
```
In this example, the Mode `-LIN` is not necessary because it is the default but makes it more readable.

Example c2:
```
0.000000	1.000000	2-0-100
1.000000	2.000000	2-100-0
2.000000	3.000000	3-0-100
3.000000	4.000000	3-100-0
5.000000	5.000000	END
```
This is a minimalized version of *Example c1*.

Example c3:
```
0.000000	0.500000	2-100
0.000000	1.000000	3-100-0
0.500000	1.500000	4-0-100-EXP
2.000000	2.000000	END
```
Another example with one exponential interpolation (`-EXP`) and line one and two are minimalized. They expand to `2-100-100-LIN` and `3-100-0-LIN`.

Please continue at the [Exporting Labels](#exporting-labels) section.

###### Phone2 mode
The `glyphId` can only be 1 to 11 which correspond to the individual Glyphs:

| glyphId | Glyph                                |
|:-------:|:-------------------------------------|
|    1    | Camera top                           |
|    2    | Camera bottom                        |
|    3    | Diagonal                             |
|    4    | Battery top right                    |
|    5    | Battery top left                     |
|    6    | Battery top vertical (left side)     |
|    7    | Battery bottom left                  |
|    8    | Battery bottom right                 |
|    9    | Battery bottom vertical (right side) |
|    10   | USB Line                             |
|    11   | USB Dot                              |

<img src="assets/Glyph%20Ids%20Phone2%20mode.png" alt="Glyph Ids Phone2 mode" width="25%"/>

Do **NOT** prepend the `#` symbol! This is for addressing each individual Zone - see below.

If you want even more control you can control each individual Zone with the Zone ids:
| Index | Glyph                                | Direction          |
|:-----:|:-------------------------------------|:-------------------|
|   1   | Camera top                           | -                  |
|   2   | Camera bottom                        | -                  |
|   3   | Diagonal                             | -                  |
|  4-19 | Battery top right                    | From right to left |
|   20  | Battery top left                     | -                  |
|   21  | Battery top vertical (left side)     | -                  |
|   22  | Battery bottom left                  | -                  |
|   23  | Battery bottom right                 | -                  |
|   24  | Battery bottom vertical (right side) | -                  |
|   25  | USB Dot                              | -                  |
| 26-33 | USB Line                             | From bottom to top |

<img src="assets/Glyph%20Ids%20Phone2%20mode%20-%20Zones.png" alt="Glyph Ids Phone2 mode - Zones" width="25%"/>

Example p1:
```
1.000000	2.000000	1-100
2.500000	3.500000	2-100
4.000000	5.000000	3-100
5.500000	6.500000	4-100
7.000000	8.000000	5-100
8.500000	9.500000	6-100
10.000000	11.000000	7-100
11.500000	12.500000	8-100
13.000000	14.000000	9-100
14.500000	15.500000	10-100
16.000000	17.000000	11-100
18.000000	18.000000	END
```
Go through each of the 11 Glyphs where each Glyph is on for 1s and with 0.5s delay in between.

Example p2:
```
1.000000	2.000000	#1-100
2.500000	3.500000	#2-100
4.000000	5.000000	#3-100
5.500000	6.500000	#4-100
7.000000	8.000000	#5-100
8.500000	9.500000	#6-100
10.000000	11.000000	#7-100
11.500000	12.500000	#8-100
13.000000	14.000000	#9-100
14.500000	15.500000	#10-100
16.000000	17.000000	#11-100
17.500000	18.500000	#12-100
19.000000	20.000000	#13-100
20.500000	21.500000	#14-100
22.000000	23.000000	#15-100
23.500000	24.500000	#16-100
25.000000	26.000000	#17-100
26.500000	27.500000	#18-100
28.000000	29.000000	#19-100
29.500000	30.500000	#20-100
31.000000	32.000000	#21-100
32.500000	33.500000	#22-100
34.000000	35.000000	#23-100
35.500000	36.500000	#24-100
37.000000	38.000000	#25-100
38.500000	39.500000	#26-100
40.000000	41.000000	#27-100
41.500000	42.500000	#28-100
43.000000	44.000000	#29-100
44.500000	45.500000	#30-100
46.000000	47.000000	#31-100
47.500000	48.500000	#32-100
49.000000	50.000000	#33-100
51.000000	51.000000	END
```
Same as *Example p1* except for lighting up all the Glpyhs we control the individual Zones.

Looking at the examples of the *Compatibility* mode can also help.

Please continue at the [Exporting Labels](#exporting-labels) section.

#### Exporting Labels
1) **File -> Export -> Export Labels**

#### Converting Labels to Glyph format
Now that we have a Labels file we can use the [GlyphTranslator](./GlyphTranslator.py) to get our desired files like this:
```bash
python3 GlyphTranslator.py MyLabelFile.txt
```
You can also add a watermark by writing your watermark to a text file and passing it to the script like this: `--watermark MyWatermarkFile.txt`

Assuming your Label file was called `MyLabelFile.txt` it will spit out two files called `MyLabelFile.glypha` and `MyLabelFile.glyphc1` in your current working directory.

> **:warning: Attention**

If you see this message in the output:
```
INFO: Auto detected Phone (1) and Phone (2) compatibility mode.
INFO: If you intended to use the Glyphs 1-5 on the Nothing Phone (2) use the '--disableCompatibility' parameter. More info with '--help' or in the README.
```
act according to this:
* You are using ***Compatibility*** mode: Do NOT follow the advice - this is intended behaviour.
* You are using ***Phone2*** mode: Please add the `--disableCompatibility` parameter to the command to use the right Glyphs.

### Read and write the Glyph format data to an audio file
#### Write to an audio file
When you have both your `.glypha` and `.glyphc1` files (via Audacity&reg; and the GlyphTranslator method or otherwise) you can write them to an audio file as metadata:
```bash
python3 GlyphModder.py -t MyCustomTitle -w MyLabelFile.glypha MyLabelFile.glyphc1 MyGlyphCreation.ogg
```
The `-t` argument is optional, this just sets the *TITLE* tag which, as far as I could see, is not used anywhere in the Glyph Composer right now.

You can provide the path to *ffmpeg* with the `--ffmpeg` argument if it can not be found in PATH.

> **:warning: Important**

**Regarding the `-w` option: The `.glypha` file must be passed before the `.glyphc1` file. The script will still comply but you can not play the file in the Glyph Composer!**

Congrats, you can now transfer the audio file to your Nothing phone and import it into the Glyph Composer app!

#### Read from an audio file
This is used when you want to modify a composition but you don't have the Audacity&reg;/Label file.

```bash
python3 GlyphModder.py MyGlyphCreation.ogg
```
Assuming your audio file was called `MyGlyphCreation.ogg` it will spit out two files called `MyGlyphCreation.glypha` and `MyGlyphCreation.glyphc1` in your current working directory.

You can provide the path to *ffprobe* with the `--ffprobe` argument if it can not be found in PATH.

It is almost impossible to convert the `.glypha` and `.glyphc1` files back to an Audacity&reg; Label file therefore you would need to edit both files manually. More info on that is in the [The technical details](#wrench-the-technical-details) section.

***

# Hardware limitations
* The Glyphs can't playback fast-changing light sequences. One user reported that this phenomenon disappeared when it was set as a ringtone or notification sound. When doing this there is a small chance that the audio and the light sequence get desynced over time. The only solution until now is to don't make fast light sequences.
* In some unknown cases the light sequence gets desynced from the audio when set as a ringtone or notification sound. If you know more feel free to reach out.

***

# :interrobang: Troubleshooting
## ModuleNotFoundError: No module named 'termcolor'
You did not properly install the requirements. Try executing
```bash
python3 -m pip install -r requirements.txt
```

## I can't find the modified audio file after using GlyphModder
The file was modified in place, no other files were generated.

If you want to confirm that the metadata was written correctly see [Glyph Composer does not import my file](#glyph-composer-does-not-import-my-file).

## File is not supported on this device
If you get this error message:
```
Import failed. File is not supported on this device.
```
You are trying to import a Phone (2) exclusive (*Phone2* mode) composition on a Phone (1).

If you created this composition please only use `glyphId`s that are compatible with your device. See [glyphId](#glyphid).

## File is not created by Composer
If you get this error message:
```
Import failed. File is not created by Composer.
```
* Avoid using a third party file explorer app to import the audio file and use Android's built in instead. Apps like Solid Explorer may try to modify the file and the import will fail.
* You are trying to import an audio file with no metadata. See [No or missing metadata](#no-or-missing-metadata).

## Glyph Composer does not import my file
Make sure that the file has the right codec and that the metadata is present:
```bash
ffprobe MyGlyphCreation.ogg
```
It should spit out something like this:
```
Input #0, ogg, from 'MyGlyphCreation.ogg':
  Duration: 00:00:10.01, start: 0.000000, bitrate: 146 kb/s
  Stream #0:0: Audio: opus, 48000 Hz, stereo, fltp
    Metadata:
      encoder         : Lavf58.76.100
      TITLE           : MyCustomSong
      ALBUM           : CUSTOM
      AUTHOR          : eNrtxqENAAAIAzBPwieI/X8dhg+wTU0zOV1xd3d3d3d3d3d3d3d3d/f3F8ocpN8=
      COMPOSER        : Spacewar Glyph Composer
      CUSTOM1         : eNoljVsKAEEIwy60A+r4qPe/2E7pj8FAiZ340vvYh8S7HjBiPB7ivUQ1ZexS3owkUJxlDGWOUZZf
                      : yqrmrs24awVahVFhVIAKUAEqrAqrwg8LSR98
```
Important are:
* Audio: **opus**
* The extension `.ogg`
* The presence of the metadata tags TITLE, ALBUM, AUTHOR, COMPOSITOR and CUSTOM1 (the order is irrelevant) - Optionally the CUSTOM2 tag if the composition is for Phone (2).

### Wrong codec
You have two options:
* Reexport with Audacity&reg; (see [Cutting the sound](#cutting-the-sound))
* Convert with ffmpeg (replace `MyGlyphCreation.ogg` with your audio): `ffmpeg -i MyGlyphCreation.ogg -strict -2 -c:a opus -map_metadata 0:s:a:0 output.ogg`

### Wrong extension
See [Wrong codec](#wrong-codec)

### No or missing metadata
Did you run the [GlyphModder](./GlyphModder.py) correctly? See [Write to an audio file](#write-to-an-audio-file).

## No glyphs light up
See [Glyph Composer does not import my file](#glyph-composer-does-not-import-my-file).

## I can import my audio but my glyphs don't light up
When you use the linear, exponential or logarithmic mode make sure that your Labels cover a range like this left Label:
![Audacity ranged Labels example](./assets/audacity_ranged_labels_example.png)

You can make the right Label ranged if you drag on the left or right part of it.

## Some of my glyphs don't light up
See [I can import my audio but my glyphs don't light up](#i-can-import-my-audio-but-my-glyphs-dont-light-up).

## The Glyphs are not alligned or desync with the audio
See [Hardware limitations](#hardware-limitations)

***

# :wrench: The technical details
<details>
  <summary>Click to expand</summary>

  **This is just a written up more technical view on this whole system.**

  ## Audio
  The audio seems disconnected from the lighting - seems like it only determines the final length of the composition. The maximum you can produce in the app is 10s but it can be longer when making it custom.
  
  ## Metadata
  There are the following tags in the ogg file (order irrelevant):
  * TITLE
  * ALBUM
  * AUTHOR
  * COMPOSER
  * CUSTOM1
  * CUSTOM2
  
  The *AUTHOR* and *CUSTOM1* tags contain both *Base64* encoded and then *zlib compressed* data (Best Compression (no preset dictionary) - see [here](https://en.wikipedia.org/wiki/List_of_file_signatures)).
  
  ### TITLE
  Contains the title given in the Glyph composer. Weirdly enough the Glyph Composer does not use this tag when displaying the name of the composition - the filename is used instead.
  
  ### ALBUM
  Saves what sound pack was used when the composition was created. Can be changed without any effect on the audio or lights (could affect the preview in the *Glyph Composer*). It does display in the *Glyph Composer*.
  
  ### AUTHOR
  After decoding and decompressing it contains the Glyph light data in a csv like manner where in each line we have the *5 Glyphs*/*33 Zones* separated and followed by a comma (`,`). Each line corresponds to 16ms.
  
  Depending on if the [*CUSTOM2*](#custom2) tag is set to `33cols` we have, what I will call, the *Compatibility* or *Phone2* mode:
  * Not set => *Compatibility* mode - 5 columns
  * Set => *Phone2* mode - 33 columms (**Nothing Phone (2) exclusive**)
  
  #### Indexes for the Glyphs
  Depending on the mode we have different indexes in the csv for the Glyphs:
  ##### *Compatibility* mode indexes
  | Index | Glyph    |
  |:-----:|:---------|
  |   0   | Camera   |
  |   1   | Diagonal |
  |   2   | Battery  |
  |   3   | USB Line |
  |   4   | USB Dot  |

  ##### *Phone2* mode indexes
  | Index | Glyph                                | Direction          |
  |:-----:|:-------------------------------------|:-------------------|
  |   0   | Camera top                           | -                  |
  |   1   | Camera bottom                        | -                  |
  |   2   | Diagonal                             | -                  |
  |  3-18 | Battery top right                    | From right to left |
  |   19  | Battery top left                     | -                  |
  |   20  | Battery top vertical (left side)     | -                  |
  |   21  | Battery bottom left                  | -                  |
  |   22  | Battery bottom right                 | -                  |
  |   23  | Battery bottom vertical (right side) | -                  |
  |   24  | USB Dot                              | -                  |
  | 25-32 | USB Line                             | From bottom to top |

  Each Glyph can have a light value from 0 to 4080 and it appears that the smallest step is 1. If the data is longer than the audio it will not be played.

  The new line consists of Carriage Return (CR) and Line Feed (LF): `\r\n`
  The data ends with a final new line `\r\n`.

  Most of the data is padded at the end with multiple "zero lines" (`0,0,0,0,0,`) even if the audio track has ended - therefore also the playback of the light show.
  
  This might be because of how the light data is stored in the app itself which are csv files for every audio clip which are combined.

  *Example 5 Glyphs (Compatibility mode):*
  ```csv
  0,0,4080,0,0,
  0,0,4080,0,2032,
  0,0,0,0,0,
  0,0,0,0,0,
  0,0,0,0,0,

  ```
  The *Battery* Glyph is fully on for 32ms and the *USB Dot* Glyph is only on for 16ms after 16ms (after the start) at about 50% brightness.

  *Example 33 Zones (Phone2 mode):*
  ```csv
  0,0,0,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,0,0,2709,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,0,0,1791,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,919,919,919,919,919,919,919,919,919,919,919,919,919,919,919,919,0,0,919,0,0,0,0,0,0,0,0,0,0,0,
  0,0,0,245,245,245,245,245,245,245,245,245,245,245,245,245,245,245,245,0,0,245,0,0,0,0,0,0,0,0,0,0,0,

  ```
  
  ### COMPOSER
  This depends on what device the composition was created on:
  * Phone (1): `Spacewar Glyph Composer`
  * Phone (2): `Pong Glyph Composer`

  If this does not match the Glyph Composer will not import the file.

  It ***is*** totally possible to import a Phone (2) composition **IF** the *CUSTOM2* tag is **NOT** set, which infers that no *33 Zone* sound pack was used.
  
  ### CUSTOM1
  This is mainly data for the Glyph Composer so it can display the timeline when playing the file. After decoding and decompressing each dot in the app is defined by a timestamp (in ms and 1 ms steps) and a Glyph id (see [AUTHOR](#author)) separated by a dash (`-`). Between each dot is a comma (`,`) and at the end of the line also.
  
  There are no new lines in this file, all dots are after one another.
  It is entirely possible to mismatch the *CUSTOM1* and *ALBUM* data (could affect the preview in the *Glyph Composer*).

  Keep in mind that the *Glyph Composer* only has 5 Buttons (therefore 5 dot locations) which means that complex custom light animations which address Zones individually can not be properly displayed in the *Glyph Composer*.

  ### CUSTOM2
  This indicates if the saved data in the *AUTHOR* tag uses the *33 Zone* addressing (*Phone2* mode) instead of the *5 Glyphs* (*Compatibility* mode) addressing.

  This tag will only be present if the composition was made on a Nothing Phone (2) and with a *33 Zone* sound pack (e.g.: Swedish House Mafia) therefore this composition can only be played back on a Nothing Phone (2).

  If it is present it ALWAYS has the value `33cols`.

  It *can* be manually imported on a Nothing Phone (1) by moving the audio file to `Ringtones/Compositions` but the phone will interpret the lighting data in the *Compatibility* mode (see [*Author*](#author) tag).
</details>

***

# Pull requests
Pull requests are welcome (improvements, new scripts/tools).
