# Creating [\[compositions\]](1_Terminology.md#compositioncompositions) for Phone (3)
> [!NOTE]
> As the heading says, this only applies if you want to create compositions for the Nothing Phone (3).
> 
> Take a look at the [Create your first composition](./4_First%20Composition/README.md) topic for the other supported phones.

> [!IMPORTANT]
> If you have not already done so, [follow the download instructions here](./2_Downloading%20Glyph%20Tools.md) and [install the dependencies](./3_Installing%20Dependencies/README.md).

The *Nothing Phone (3)* has a 25x25 led matrix on the back of the device that we can use to play back more fleshed out animations than on previous phones. Because of that the previous method that the *Glyph Tools* used is not suitable any more.

Instead we can use the power of already existing software like video editing programs or animation software to create a video and then process that into data the phone can interpret for the matrix.

**TL;DR:** All you need is a preferably already rectangle video + audio and the *VideoToPhone3NGlyph* script will do the heavy lifting. If the video is not recangle it will be scaled down to 25x25.
> [!NOTE]
> The script currently does not support any form of cropping or adjustment of saturation or thresholds for the color to gray conversion.  
> These adjustments should be made beforehand in a suitable video editing software of your preference - I personally use [Kdenlive](https://kdenlive.org).

> [!IMPORTANT]
> Make sure that the audio has the same length as the video or the *GlyphModder* part mentioned at the end might not work!

Here is how to use the *VideoToPhone3NGlyph* script:
1. Open the Terminal in your [\[Glyph Tools location\]](./1_Terminology.md#glyph-tools-location)
> [!TIP]
> You can accomplish this on **Windows** by opening (double click) *Open_Terminal_Here.bat*.
2. Copy this into the terminal but do not press <kbd>ENTER</kbd> just yet
```bash
python VideoToPhone3NGlyph.py <VideoFile>
```
> [!IMPORTANT]
> On **Linux/MacOS** you need to use `python3` instead of `python`
3. Replace `<VideoFile>` with the path to your video **by drag and dropping it into the Terminal window**.

Your command should look something like this now:
```
python VideoToPhone3NGlyph.py "C:\Users\VM\Downloads\custom-nothing-glyph-tools-main\Video.mp4"
```
4. Now you can **execute the command** with the <kbd>ENTER</kbd> key. If everything went good and the file wasn't already upgraded beforehand you will have a new file named like your input video but with the `.nglyph` extension. You can use that [\[NGlyph File\]](./1_Terminology.md#nglyph-file) + your audio with the *GlyphModder* by following the linked portion here: [Using the Glyph Tools](./4_First%20Composition/2_Using%20the%20Glyph%20Tools.md#using-the-glyphmodder)

> [!TIP]
> If your video already has the audio you want to use, you can just pass it to the *GlyphModder* script and it will handle extracting the audio track for you.

> [!CAUTION]
> An existing [\[NGlyph File\]](./1_Terminology.md#nglyph-file) with the same name will be overridden without notice!

> [!TIP]
> Read the output and act accordingly if it tells you something. If you get stuck **read through the [Troubleshooting](./7_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](./README.md#need-help)).