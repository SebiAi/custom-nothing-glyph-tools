# Create Advanced [\[compositions\]](./1_Terminology.md#compositioncompositions) ([\[Zones\]](./1_Terminology.md#zones))
> [!CAUTION]
> This topic should only be read after completing at least one simple [\[composition\]](./1_Terminology.md#compositioncompositions).

Everything you have read in the [Create your first composition](./4_First%20Composition/README.md) chapter does apply when you want to utilize the individual [\[Zones\]](./1_Terminology.md#zones) on a phone.

The main difference is that the [\[glyphId\]](./1_Terminology.md#glyphid) can now be a decimal number. Here is an example for Nothing Phone (2):  
![Glyph Format second example (Zones): 4.1-0-100-LIN](./assets/Glyph%20Format%20example%202%20(Zones).png)

This [\[Region Label\]](./1_Terminology.md#region-label) does address a [\[Zone\]](./1_Terminology.md#zones) (*1*) inside the *Battery top right* [\[Glyph\]](./1_Terminology.md#glyphs) (*4*) of the Nothing Phone (2)  and *linearly interpolates* from *0%* brightness to *100%* brightness in the span of 1 second (0.5 to 1.5s).

> [!NOTE]
> To summarize:  
> If we want to address a [\[Zone\]](./1_Terminology.md#zones) we write the id of the [\[Glyph\]](./1_Terminology.md#glyphs) followed by a dot and then the number of the [\[Zone\]](./1_Terminology.md#zones) inside that [\[Glyph\]](./1_Terminology.md#glyphs).
>
> E.g.: The [\[glyphId\]](./1_Terminology.md#glyphid) for addressing the bottom most [\[Zone\]](./1_Terminology.md#zones) in the *USB Line* [\[Glyph\]](./1_Terminology.md#glyphs) on the Nothing Phone (2) would look like this: `10.8`.  
> A valid [\[Region Label\]](./1_Terminology.md#region-label) with this id would look like this: `10.8-100` (short form for `10.8-100-100-LIN`)

> [!IMPORTANT]
> You can have [\[Labels\]](./1_Terminology.md#label) that address [\[Glyphs\]](./1_Terminology.md#glyphs) *AND* [\[Zones\]](./1_Terminology.md#zones) in *ONE* [\[composition\]](./1_Terminology.md#compositioncompositions).

Click [here](./4_First%20Composition/1_Explaining%20the%20Glyph%20Format.md#glyphid) to jump to the [\[glyphId\]](./1_Terminology.md#glyphid) tables for the supported phones.

That's all! Have fun!