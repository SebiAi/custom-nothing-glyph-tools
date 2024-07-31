# Using the [\[GlyphTranslator\]](../1_Terminology.md#glyphtranslator) on Linux and MacOS
1. Open the Terminal in your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location).
2. Copy this into the Terminal but do not press <kbd>ENTER</kbd> just yet: `python3 GlyphTranslator.py <LabelFile>`
3. Replace `<LabelFile>` with the path to your [\[Label File\]](../1_Terminology.md#label-file) you exported earlier **by drag and dropping the file into the Terminal window**.

Your command should look something like this now:
```bash
python3 GlyphTranslator.py '/home/vm/Downloads/custom-nothing-glyph-tools-main/Labels 1.txt'
```

> [!NOTE]
> I highly recommend to also use a [\[Watermark File\]](../1_Terminology.md#watermark-file), especially if you plan to share your [\[NGlyph File\]](../1_Terminology.md#nglyph-file).
>
> The watermark could look like this:
> ```
> ╲                       ╱
>  ╔═════════════════════╗
>  ║  Glyphed by SebiAi  ║
>  ╚═════════════════════╝
> ╱                       ╲
> ```
>
> Save your watermark into a text file called `Watermark.txt` and append this to the command: `--watermark <WatermarkFile>`
>
> E.g.:
> ```bash
> python3 GlyphTranslator.py '/home/vm/Downloads/custom-nothing-glyph-tools-main/Labels 1.txt' --watermark '/home/vm/Downloads/custom-nothing-glyph-tools-main/Watermark.txt'
> ```
4. Now you can **execute the command** with the <kbd>ENTER</kbd> key. If everything went good you will have a new file named like your input [\[Label File\]](../1_Terminology.md#label-file) but with the *.nglyph* extension. This is the [\[NGlyph File\]](../1_Terminology.md#nglyph-file) which you'll need in the next steps.
> [!CAUTION]
> An existing [\[NGlyph File\]](../1_Terminology.md#nglyph-file) with the same name will be overridden without notice!

> [!NOTE]
> The script might ask for your input in the form of yes (`y`) and no (`n`).

> [!TIP]
> Read the output and act accordingly if it tells you something. If you get stuck **read through the [Troubleshooting](../6_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](../README.md#need-help)).

> [!IMPORTANT]
> If you make changes to your [\[Labels\]](../1_Terminology.md#label) then do not forget to export them again!!