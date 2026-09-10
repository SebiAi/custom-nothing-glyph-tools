# Converting other glyph data formats to NGlyph (ToNGlyph)
> [!NOTE]
> Are you a developer and want to add support for a glyph data format? See the [section dedicated to developers below](#heading-for-developers).
## For users
Use the *ToNGlyph* script to convert glyph data to a [\[NGlyph File\]](./1_Terminology.md#nglyph-file) through the implementation of "converters". The output file can be used with the other *Glyph Tools* like [\[GlyphModder\]](./1_Terminology.md#glyphmodder) to write the data to an audio file for ringtone or notification use.

> [!IMPORTANT]
> If you have not already done so, [follow the download instructions here](./2_Downloading%20Glyph%20Tools.md) and [install the dependencies](./3_Installing%20Dependencies/README.md).

Use the below instructions:
1. Open the Terminal in your [\[Glyph Tools location\]](./1_Terminology.md#glyph-tools-location)
> [!TIP]
> You can accomplish this on **Windows** by opening (double click) *Open_Terminal_Here.bat*.
2. Copy this into the terminal but do not press <kbd>ENTER</kbd> just yet
```sh
python ToNGlyph.py <glyph_data_file>
```
> [!IMPORTANT]
> On **Linux/MacOS** you need to use `python3` instead of `python`
4. Replace `<glyph_data_file>` with the path of the glyph data file you want to convert to a [\[NGlyph File\]](./1_Terminology.md#nglyph-file) **by drag and dropping the file into the Terminal window**.
5. Now you can **execute the command** with the <kbd>ENTER</kbd> key.  
The program tries to automatically select the right converter and the matching target device depending on glyph data format. If multiple potentially matching converter or target devices have been found, the program will ask you to decide.  
The program will create a new file named like your input but with the `nglyph` extension in your current working directory.

You may want to **extend/shorten or offset the glyph data**. Use the `--duration` and `--offset` arguments as described in the help output:
```sh
python ToNGlyph.py --help
```

> [!CAUTION]
> An existing [\[Label File\]](../1_Terminology.md#label-file) with the same name will be overridden without notice!

> [!TIP]
> Read the output and act accordingly if it tells you something. If you get stuck **read through the [Troubleshooting](./7_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](./README.md#need-help)).

---

<a name="heading-for-developers"></a>

## For developers
If you want to add support for a glyph data format you need to
1. Subclass `AToNGlyphConverter` and implement the abstract methods. You can use `PauwmaGlyphMuseumConverter` as a reference.
2. Add your converter to the `CONVERTERS` list.

It is generally discouraged to add more external dependencies but if your implementation requires that, please use a reputable package from PyPI, describe why you need it in your pull request and add it to the `requirements.txt` file.

**Additional Notes:**
* Use the `logger` to log user readable content to the terminal. Most implementation will not need to do so. `logger.debug()` must be used for debug output, do not use `print()`!!
* The `ReadableData` type is guaranteed to be seekabel.
* There is no guarantee that `AToNGlyphConverter.can_convert_to` will be called before `AToNGlyphConverter._convert` or vice versa.
* Your implementation of `AToNGlyphConverter` should be stateless (no state saved in the class).
* `AToNGlyphConverter` contains a few static helpers you can use. If you implement a function for your implementation that may be useful to other people, please put it as a static method inside the `AToNGlyphConverter` class.
* *Glyph Tools* aims to be a collection of ***self contained*** scripts. Therefore, implement all functionality for your converter inside the *ToNGlyph* script (except external libraries pulled through pip).