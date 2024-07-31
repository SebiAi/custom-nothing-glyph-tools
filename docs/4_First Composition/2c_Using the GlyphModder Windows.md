# Using the [\[GlyphModder\]](../1_Terminology.md#glyphmodder) on Windows
1. Open the Terminal in your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) by opening (double click) *Open_Terminal_Here.bat*.
2. Copy this into the Terminal but do not press <kbd>ENTER</kbd> just yet: `python GlyphModder.py write -t "<YourTitle>" <NGlyphFile> <AudioFile>`
3. Replace `<YourTitle>` with the name of your composition. Make sure that you **keep the double quotes** (`"`).
4. Replace `<NGlyphFile>` with the path to your [\[NGlyph File\]](../1_Terminology.md#nglyph-file) you created earlier **by drag and dropping the file into the Terminal window**.
5. Replace `<AudioFile>` with the path to your audio file **by drag and dropping the file into the Terminal window**.

Your command should look something like this now:
```
python GlyphModder.py write -t "Tutorial Composition" "C:\Users\VM\Downloads\custom-nothing-glyph-tools-main\Labels 1.nglyph" "C:\Users\VM\Downloads\custom-nothing-glyph-tools-main\Tutorial Composition.ogg"
```

6. Now you can **execute the command** with the <kbd>ENTER</kbd> key. If everything went good you will have a new file named like your input audio with `_composed` appended to it.
> [!CAUTION]
> An existing audio file with the same name will be overridden without notice!

> [!NOTE]
> The script might ask for your input in the form of yes (`y`) and no (`n`).

> [!TIP]
> Read the output and act accordingly if it tells you something. If you get stuck **read through the [Troubleshooting](../6_Troubleshooting.md) entry first**. If you still need help you can join the Discord (link at the [root of the wiki](../README.md#need-help)).

> [!IMPORTANT]
> If you make changes to your [\[Labels\]](../1_Terminology.md#label) then do not forget to export them and run them through the [\[GlyphTranslator\]](../1_Terminology.md#glyphtranslator) again!!