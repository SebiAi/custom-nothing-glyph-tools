# Migrating old [\[Label Files\]](./1_Terminology.md#label-file) to the v1 [\[Glyph Format\]](./1_Terminology.md#glyph-format)

> [!IMPORTANT]
> If you have not already done so, [follow the download instructions here](./2_Downloading%20Glyph%20Tools.md) and [install the dependencies](./3_Installing%20Dependencies/README.md).

The migration is fairly straight forward. We will use the *GlyphMigrate* script to do the job for us:
1. Open the Terminal in your [\[Glyph Tools location\]](./1_Terminology.md#glyph-tools-location)
> [!TIP]
> You can accomplish this on **Windows** by opening (double click) *Open_Terminal_Here.bat*.
2. Copy your [\[Label File\]](./1_Terminology.md#label-file) to your [\[Glyph Tools location\]](./1_Terminology.md#glyph-tools-location) - it should be right next to the *GlyphMigrate.py* script
3. Copy this into the terminal but do not press <kbd>ENTER</kbd> just yet
```bash
python GlyphMigrate.py <LabelFile>
```
> [!IMPORTANT]
> On **Linux/MacOS** you need to use `python3` instead of `python`
4. Replace `<LabelFile>` with the path to your [\[Label File\]](../1_Terminology.md#label-file) **by drag and dropping the file into the Terminal window**.

Your command should look something like this now:
```
python GlyphMigrate.py "C:\Users\VM\Downloads\custom-nothing-glyph-tools-main\Labels 1.txt"
```
5. Now you can **execute the command** with the <kbd>ENTER</kbd> key. If everything went good and the file wasn't already upgraded beforehand you will have a new file named like your input [\[Label File\]](../1_Terminology.md#label-file) but with `_migrated` added to the file name. You can use that migrated [\[Label File\]](../1_Terminology.md#label-file) with the *GlyphTranslator* now: [Using the Glyph Tools](./4_First%20Composition/2_Using%20the%20Glyph%20Tools.md#using-the-glyphtranslator)

> [!NOTE]
> The script might ask you for old "*Compatibility mode*" [\[compositions\]](./1_Terminology.md#compositioncompositions) to select a phone to migrate to.

> [!CAUTION]
> An existing [\[Label File\]](../1_Terminology.md#label-file) with the same name will be overridden without notice!

> [!TIP]
> Read the output and act accordingly if it tells you something. If you get stuck **read through the [Troubleshooting](./6_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](./README.md#need-help)).
