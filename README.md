# GLYPH TOOLS

<p align="center">
This repo is intended to be a collection of tools and scripts to make it easy to create custom Nothing Glyph Compositions which in turn can be imported into the <i>Nothing Glyph Composer</i>.
</p>

https://github.com/SebiAi/custom-nothing-glyph-tools/assets/41116921/1852f2a6-1cf9-4c0e-9835-792bf1b09a58

***

# :pushpin: Disclaimer
> These scripts are provided as-is without any warranty. I and all other contributors are not responsible for any damage, misuse or other kind of physical or mental damage which results in the use of these scripts.
This repo is in no way shape or form affiliated with Nothing Technology Limited (NOTHING).

***

# :safety_vest: Need help?
If you need help feel free to reach out to me on Discord: @sebiai

***

# :construction: Compatibility
## OS
* Linux :white_check_mark:
* Windows :white_check_mark:
* Mac :question: - \[*To be tested - please reach out to me if you manage to get it working!*\]

I have only tested the scripts on Linux. Somebody else managed to do it on Windows. There *should* be nothing preventing them to run on MacOS.
## Phones
* Nothing Phone 1 :white_check_mark:
* Nothing Phone 2 :white_check_mark:

Works on both Nothing devices.

***

# :pencil2: Usage
## :memo: Requirements
* \[*Required*\] **[python3](https://www.python.org/downloads/)** - To run the scripts
* \[*Required*\] **[exiftool](https://exiftool.org/install.html)** - To read the metadata of the sound file (could be replaced by ffmpeg (ffprobe) - feel free to make a pull request)
* \[*Required*\] **[ffmpeg](https://ffmpeg.org/download.html)** - To write metadata to the sound file
* \[*Optional*\] **[Audacity](https://www.audacityteam.org/)** - Create custom compositions more easily with Labels

    :arrow_right: *exiftool and ffmpeg must be in PATH. There is currently no way to provide custom paths to these executables without editing the script.*

## :rocket: Setup
#### Clone the repo
```bash
git clone https://github.com/SebiAi/custom-nothing-glyph-tools.git
cd custom-nothing-glyph-tools
```

#### Install the necessary python dependencies
```bash
pip3 install -r requirements.txt
```
Sometimes it is also just `pip` instead of `pip3`.

## :sparkles: Making a custom Glyph composition
I would recommend using [Audacity](https://www.audacityteam.org/) to make your life easier. You can use it to cut your audio to the right length, layer effects on it, set Labels (which will come in handy later) and more.

### Cutting the sound
You can skip to [Creating the Glyph format with Audacity](#creating-the-glyph-format-with-audacity) if you already have the sound cut to the right length.

When exporting the sound I always used the *opus* codec because the Glyph Composer uses this format.
1) **Export audio:** Files -> Export -> Export Audio...
2) **Select the right codec in the dropdown:** Select Opus - default settings are fine
3) **Change the extension to *ogg* when naming your file!**
4) **Export**

### Creating the Glyph format with Audacity
To make our lives easier we can utilize Audacities Labels functionality and then use the Label data to generate our two needed csv files with the help of the [GlyphTranslater](./GlyphTranslater.py) - one for the *AUTHOR* tag (stores the light data) and the other for the *CUSTOM1* (stores data for the app to display) tag (for more info read the [technical details](#wrench-the-technical-details)).

I would recommend saving your Audacity project regularly.

#### Add the Labels track
1) **Open your audio with Audacity**
2) **Add the Labels track:** Tracks -> Add New -> Label Track

#### Creating and removing Labels
You can now add Labels by clicking on your desired location on the Label Track and pressing <kbd>CONTROL</kbd> + <kbd>b</kbd>. To remove one Label right-click on the Labels name and choose *Delete Label*. More info [here](https://manual.audacityteam.org/man/removing_labels_examples.html).

#### Naming format
Each Label should be named like this: `glyphId-lightLevelFrom[-lightLevelTo[-Mode]]`
* **glyphId**: 1 to 5 (Camera, Diagonal, Battery/Wireless Charger, USB Line, USB Dot)
* **lightLevelFrom** and **lightLevelTo**: In percent 0 to 100. When no *lightLevelTo* is provided *lightLevelFrom* will be used as the from and to value.
* **Mode**: Currently there are two modes supported:
    * LIN: Linear Interpolation (default)
    * EXP: Exponential Interpolation

The brackets (`[` and `]`) mean optional. Therefore do **NOT** include them in the Label name!

If you like regex patterns, the name of the Label should match this one (thanks [Joel05](https://github.com/SebiAi/custom-nothing-glyph-tools/issues/1)):
```regex
^([1-5])-(\d{1,2}|100)(?:-(\d{1,2}|100))?(?:-(EXP|LIN))?$
```

> **:warning: Important**

**At the end of the audio there MUST be a Label called *END*.** This is needed so the script knows how long the audio is. Also, make sure that there is enough space between your last Glyph lighting up and the *END* Label or else it might not get played - add silence at the end of the audio file if that happens and move the *END* Label accordingly.

Example 1:
```
0.031441	0.031441	2-0-100-LIN
0.074091	0.074091	2-100-0-LIN
0.198122	0.198122	3-0-100-LIN
0.242847	0.242847	3-100-0-LIN
0.296312	0.296312	END
```
In this example, the Mode `-LIN` is not necessary because it is the default but makes it more readable.

Example 2:
```
0.031441	0.031441	2-0-100
0.074091	0.074091	2-100-0
0.198122	0.198122	3-0-100
0.242847	0.242847	3-100-0
0.296312	0.296312	END
```
This is a minimalized version of *Example 1*.

Example 3:
```
0.031441	0.031441	2-100
0.074091	0.074091	3-100-0
0.198122	0.198122	4-0-100-EXP
0.296312	0.296312	END
```
Another example with one exponential interpolation (`-EXP`) and line one and two are minimalized. They expand to `2-100-100-LIN` and `3-100-0-LIN`.

#### Exporting Labels
1) **File -> Export -> Export Labels**

#### Converting Labels to Glyph format
Now that we have a Labels file we can use the [GlyphTranslater](./GlyphTranslater.py) to get our desired files like this:
```bash
python3 GlyphTranslater.py MyLabelFile.txt
```
Assuming your Label file was called `MyLabelFile.txt` it will spit out two files called `MyLabelFile.glypha` and `MyLabelFile.glyphc1` in your current working directory.

### Read and write the Glyph format data to an audio file
#### Read from an audio file
```bash
python3 GlyphModder.py MyGlyphCreation.ogg
```
Assuming your audio file was called `MyGlyphCreation.ogg` it will spit out two files called `MyGlyphCreation.glypha` and `MyGlyphCreation.glyphc1` in your current working directory.

#### Write to an audio file
When you have both your `.glypha` and `.glyphc1` files (via Audacity and the GlyphTranslater method or otherwise) you can write them to an audio file as metadata:
```bash
python3 GlyphModder.py -t MyCustomTitle -w MyLabelFile.glypha MyLabelFile.glyphc1 MyGlyphCreation.ogg
```
The `-t` argument is optional, this just sets the *TITLE* tag which, as far as I could see, is not used anywhere in the Glyph Composer right now.

> **:warning: Important**

**Regarding the `-w` option: The `.glypha` file must be passed before the `.glyphc1` file. The script will still comply but you can not play the file in the Glyph Composer!**

Congrats, you can now transfer the audio file to your Nothing phone and import it into the Glyph Composer app!

***

# Hardware limitations
* On the Phone (1) at least the Glyphs can't playback fast-changing light sequences. One user reported that this phenomenon disappeared when it was set as a ringtone or notification sound.

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
  
  The *AUTHOR* and *CUSTOM1* tags contain both *Base64* encoded and then *zlib compressed* data (Best Compression (no preset dictionary) - see [here](https://en.wikipedia.org/wiki/List_of_file_signatures)).
  
  ### TITLE
  Contains the title given in the Glyph composer. Weirdly enough the Glyph Composer does not use this tag when displaying the name of the composition - the filename is used instead.
  
  ### ALBUM
  Saves what "pack" was used when the composition was created. Can be changed without any effect on the audio or lights. It does display in the Glyph Composer.
  
  ### AUTHOR
  After decoding and decompressing it contains the Glyph light data in a csv like manner where in each line we have the 5 Glyphs separated and followed by a comma (`,`). Each line corresponds to 16ms. Each Glyph
  
  0) Camera
  1) Diagonal
  2) Battery/Wireless Charger
  3) USB Line
  4) USB Dot

  can have a light value from 0 to 4080 and it appears that the smallest step is 16. If the data is longer than the audio it will not be played.

  The new line consists of Carriage Return (CR) and Line Feed (LF): `\r\n`
  The data ends with a final new line `\r\n`.

  Most of the data is padded at the end with multiple "zero lines" (`0,0,0,0,0,`) even if the audio track has ended - therefore also the playback of the light show.
  
  This might be because of how the light data is stored in the app itself which are csv files for every audio clip which are combined.

  *Example:*
  ```csv
  0,0,4080,0,0,
  0,0,4080,0,2032,
  0,0,0,0,0,
  0,0,0,0,0,
  0,0,0,0,0,

  ```
  The *Battery/Wireless Charger* Glyph is fully on for 32ms and the *USB Dot* Glyph only for 16ms after 16ms at about 50% brightness.
  
  ### COMPOSER
  This is always `Spacewar Glyph Composer`. If this does not match the Glyph Composer will not import the file.
  
  ### CUSTOM1
  This is mainly data for the Glyph Composer so it can display the timeline when playing the file. After decoding and decompressing each dot in the app is defined by a timestamp (in ms and 16 ms steps) and a Glyph id (see [AUTHOR](#author)) separated by a dash (`-`). Between each dot is a comma (`,`) and at the end of the line also.
  
  There are no new lines in this file, all dots are after one another.
  It is possible to supply timestamps which are not dividable by 16 - this is not recommended as these points should match the data in the *ALBUM* tag. It is entirely possible to mismatch the *CUSTOM1* and *ALBUM* data.
</details>

***

# Pull requests
Pull requests are welcome (improvements, new scripts/tools).
