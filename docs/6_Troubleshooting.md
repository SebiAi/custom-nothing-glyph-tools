# :interrobang: Troubleshooting
## File is not supported on this device
If you get this error message:
```
Import failed. File is not supported on this device.
```
* You are trying to import a composition made for a different phone.  
If you created this composition please make sure you used the right phone-model string in the [\[GlyphTranslator\]](./1_Terminology.md#glyphtranslator) command.
* You are trying to import an older Phone (1) [\[composition\]](./1_Terminology.md#compositioncompositions) **on a Phone (2)**. You can try [this](https://github.com/SebiAi/custom-nothing-glyph-tools/discussions/25) as a workaround.
> [!CAUTION]
> This workaround only works for Phone (1) [\[compositions\]](./1_Terminology.md#compositioncompositions) that strictly use the whole *5 [\[Glyphs\]](./1_Terminology.md#glyphs)* aka. not using the 4 [\[Zones\]](./1_Terminology.md#zones) in the *Battery Glyph* and the 8 [\[Zones\]](./1_Terminology.md#zones) in the *USB Line Glyph*.
>
> There is currently no simple way to discern *5 [\[Zones\]](./1_Terminology.md#zones)* and *15 [\[Zones\]](./1_Terminology.md#zones)* [\[compositions\]](./1_Terminology.md#compositioncompositions), except for looking at the column count after extracting the *AUTHOR* data (see [Technical Details](./8_Technical%20Details.md)).

## File is not created by Composer
If you get this error message:
```
Import failed. File is not created by Composer.
```
* Avoid using a third party file explorer app to import the audio file and use Android's built in instead. Apps like *Solid Explorer* or *Google Drive* may try to modify the file and the import will fail.
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
      ALBUM           : Glyph Tools v2
      AUTHOR          : eNrtxqENAAAIAzBPwieI/X8dhg+wTU0zOV1xd3d3d3d3d3d3d3d3d/f3F8ocpN8=
      COMPOSER        : v1-Spacewar Glyph Composer
      CUSTOM1         : eNoljVsKAEEIwy60A+r4qPe/2E7pj8FAiZ340vvYh8S7HjBiPB7ivUQ1ZexS3owkUJxlDGWOUZZf
                      : yqrmrs24awVahVFhVIAKUAEqrAqrwg8LSR98
      CUSTOM2         : 5cols
```
Important are:
* Audio: **opus**
* The extension `.ogg`
* The presence of the metadata tags TITLE, ALBUM, AUTHOR, COMPOSITOR, CUSTOM1 and CUSTOM2 (the order is irrelevant).

### Wrong codec
You have two options:
* Reexport with Audacity&reg; (see [here](./4_First%20Composition/2_Using%20the%20Glyph%20Tools.md#exporting-audio-and-labels-from-audacity))
* Convert with ffmpeg (replace `MyGlyphCreation.ogg` with your audio): `ffmpeg -i MyGlyphCreation.ogg -strict -2 -c:a opus -map_metadata 0:s:a:0 output.ogg`

### Wrong extension
See [Wrong codec](#wrong-codec)

### No or missing metadata
Did you run the [\[GlyphModder\]](./1_Terminology.md#glyphmodder) correctly? See [here](./4_First%20Composition/2_Using%20the%20Glyph%20Tools.md#using-the-glyphmodder).

## No glyphs light up
See [Glyph Composer does not import my file](#glyph-composer-does-not-import-my-file).

## I can import my audio but my glyphs don't light up
Make sure that your [\[Labels\]](./1_Terminology.md#label) cover a region like this left [\[Label\]](./1_Terminology.md#label):  
![Audacity region Labels example](./assets/Audacity%20region%20Labels%20example.png)

You can convert the right [\[Point Label\]](./1_Terminology.md#point-label) to a [\[Region Label\]](./1_Terminology.md#region-label) if you drag on the left or right part of it.

## Some of my glyphs don't light up
See [I can import my audio but my glyphs don't light up](#i-can-import-my-audio-but-my-glyphs-dont-light-up).

## Locate FFmpeg - Audacity needs the file 'avformat.dll' (Legacy Problem)
> [!CAUTION]
> If you have this problem, please update your Audacity&reg; version to 3.5.1 or higher and it will disappear!

![Audacity&reg; - Locate FFmpeg prompt](assets/Audacity%20locate%20FFmpeg%20prompt.png)

This error is expected on Windows and can be solved the following way:
1. Download and extract this file to a location you'll remember (you might need [7-Zip](https://7-zip.org/) to extract it): https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full-shared.7z
2. Then click on the *Browse...* button in Audacity&reg; and navigate to the extracted content
3. Navigate into the `bin` folder
4. Select the `avformat.dll` - The filename might differ a little bit
5. Click *OK* in the Audacity&reg; dialog