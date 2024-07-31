# Create your first [\[composition\]](../1_Terminology.md#compositioncompositions)
## :writing_hand: Table of contents
The table of contents for this topic is the following:
- [Prepairing your project](./README.md)
- [Explaining the Glyph Format](./1_Explaining%20the%20Glyph%20Format.md)
- **Using the Glyph Tools**
- [Final steps](./3_Final%20steps.md)

## Using the Glyph Tools
> [!IMPORTANT]
> If you have not already done so, [follow the download instructions here](../2_Downloading%20Glyph%20Tools.md) and [install the dependencies](../3_Installing%20Dependencies/README.md).

Now that you have your audio and the light sequence part you can move on to combining both parts. This chapter will cover the following:
* Exporting the audio and the [\[Labels\]](../1_Terminology.md#label) from Audacity&reg;
* Using the [\[GlyphTranslator\]](../1_Terminology.md#glyphtranslator) and optionally adding a [\[Watermark File\]](../1_Terminology.md#watermark-file) to get an intermediate file ([\[NGlyph File\]](../1_Terminology.md#nglyph-file))
* Using the [\[GlyphModder\]](../1_Terminology.md#glyphmodder) to produce the final [\[composition\]](../1_Terminology.md#compositioncompositions)

> [!NOTE]
> Transfering the [\[composition\]](../1_Terminology.md#compositioncompositions) to your phone will be covered in the next chapter.

<!-- TOC --><a name="exporting-audio-and-labels-from-audacity"></a>
### :outbox_tray: Exporting audio and [\[Labels\]](../1_Terminology.md#label) from Audacity&reg;
1. In Audacity&reg; press <kbd>CONTROL + A</kbd> to select all the tracks - they should be light blue/white now.
2. Export your [\[Labels\]](../1_Terminology.md#label): *File* -> *Export Other* -> *Export Labels*  
![Audacity&reg; export labels option](./assets/Audacity%20export%20labels%20option.png)
> [!IMPORTANT]
> If the option is grayed out repeat step 1 again.
3. Save the file into your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location). The [\[Label File\]](../1_Terminology.md#label-file) should now be right next to scripts.  
![Audacity&reg; Label export dialog](./assets/Audacity%20Label%20export%20dialog.png)
4. Export your audio: *File* -> *Export Audio*  
![Audacity&reg; export audio option](./assets/Audacity%20export%20audio%20option.png)
5. Select *Export to computer*  
![Audacity&reg; how to export audio dialog](./assets/Audacity%20how%20to%20export%20audio%20dialog.png)
> [!NOTE]
> You might not see this dialog.
6. Configure the export dialog
    1. Name the audio file. E.g.: `<SongName> for <phone name> by <Your Name>`
    2. Select ***Opus Files*** as the *Format*. The extension in the *File Name* should now be *.opus*.
    3. Leave everything else default.  
![Audacity&reg; configured audio export dialog](./assets/Audacity%20configured%20audio%20export%20dialog.png)
> [!IMPORTANT]
> If you get a popup asking you to *Locate FFmpeg* or if the *Export Audio* dialog looks different, update your Audacity&reg; version to 3.5.1 or higher.
7. Press the *Export* button.
8. Open your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) and change the extension of the audio file from *.opus* to *.ogg*
> [!WARNING]
> On Windows you need to show *file name extensions* in the file explorer. Here is how to do it:
> * [Windows 10](https://fileinfo.com/img/help/windows_10_file_name_extensions_checkbox.png)
> * [Windows 11](https://lazyadmin.nl/wp-content/uploads/2021/08/image-5.png.webp)

***

### Using the [\[GlyphTranslator\]](../1_Terminology.md#glyphtranslator)
Your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) should now contain the [\[Label File\]](../1_Terminology.md#label-file) and your exported audio file:  
![Glyph Tools location after export](./assets/Glyph%20Tools%20location%20after%20export.png)

In this step you'll generate the [\[NGlyph File\]](../1_Terminology.md#nglyph-file) which you'll need in the last step.

**Depending on your operating system you need to follow different instructions:**
* **[<img src="https://www.vectorlogo.zone/logos/microsoft/microsoft-icon.svg" height="15"/> Windows](./2a_Using%20the%20GlyphTranslator%20Windows.md)**
* **[:penguin: <img src="https://www.vectorlogo.zone/logos/apple/apple-tile.svg" height="16"/> Linux and MacOS](./2b_Using%20the%20GlyphTranslator%20Linux%20and%20MacOS.md)**

> [!TIP]
> You can use the `--help` argument to see all the available arguments you can pass to the script.

> [!TIP]
> If you get stuck **read through the [Troubleshooting](../6_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](../README.md#need-help)).

***

### Using the [\[GlyphModder\]](../1_Terminology.md#glyphmodder)
Your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) should now contain the [\[Label File\]](../1_Terminology.md#label-file), your exported audio file and the [\[NGlyph File\]](../1_Terminology.md#nglyph-file):  
![Glyph Tools location after export](./assets/Glyph%20Tools%20location%20after%20GlyphTranslator.png)

This is the final step to get your completed [\[composition\]](../1_Terminology.md#compositioncompositions).

**Depending on your operating system you need to follow different instructions:**
* **[<img src="https://www.vectorlogo.zone/logos/microsoft/microsoft-icon.svg" height="15"/> Windows](./2c_Using%20the%20GlyphModder%20Windows.md)**
* **[:penguin: <img src="https://www.vectorlogo.zone/logos/apple/apple-tile.svg" height="17"/> Linux and MacOS](./2d_Using%20the%20GlyphModder%20Linux%20and%20MacOS.md)**

> [!TIP]
> You can use the `--help` argument to see all the available arguments you can pass to the script.

> [!TIP]
> If you get stuck **read through the [Troubleshooting](../6_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](../README.md#need-help)).

## The next step
Now that you have your finished [\[composition\]](../1_Terminology.md#compositioncompositions) you can continue to the last chapter.

<div align="right"><h3><a href="3_Final steps.md">Go to next chaper</a></h3></div>