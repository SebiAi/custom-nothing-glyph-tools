Native support for the 15 Zone mode on Phone (1) plus **a complete rewrite** of the *custom-nothing-glyph-tools* coming to you!

With this rewrite **the Glyph and Zone addressing syntax will change** slightly. In my humble opinion: The new numbering makes much more sense now (top to bottom and "dot indexing" for the Zones in each Glyph). See the below for reference.

But to lighten your mood over this change, I plan on shipping a converter script which can convert from the old syntax to the new one, so you don't have to rewrite your Label files 👍

## The new Label syntax explained
Only the `glyphId` section of the Label syntax changes. The other components (`lightLevelFrom`, `lightLevelTo`, `Mode`) stay the same:
`glyphId-lightLevelFrom[-lightLevelTo[-Mode]]`

### Phone (1)
| glyphId   | Glyph name                        | Type  |
|-----------|-----------------------------------|-------|
| 1         | Camera                            | Glyph |
| 2         | Diagonal                          | Glyph |
| 3         | Battery                           | Glyph |
| 3.1       | Battery top right                 | Zone  |
| 3.2       | Battery top left                  | Zone  |
| 3.3       | Battery bottom left               | Zone  |
| 3.4       | Battery bottom right              | Zone  |
| 4         | USB Line                          | Glyph |
| 4.1 - 4.8 | USB Line Zones from top to bottom | Zones |
| 5         | USB Dot                           | Glyph |

**Examples with the new syntax:**
* `1-100` - Camera Glyph 100% on for the duration of the Label.
* `3.1-0-100` - The Battery top right Zone linearly interpolates from 0% to 100% for the duration of the Label.
* `4.8-100-29-EXP` - The Zone at the bottom of the USB Line exponentially interpolates from 100% to 29% for the duration of the Label.

### Phone (2)
| glyphId     | Glyph name                                 | Type  |
|-------------|--------------------------------------------|-------|
| 1           | Camera top                                 | Glyph |
| 2           | Camera bottom                              | Glyph |
| 3           | Diagonal                                   | Glyph |
| 4           | Battery top right                          | Glyph |
| 4.1 - 4.16  | Battery top right Zones from right to left | Zones |
| 5           | Battery top left                           | Glyph |
| 6           | Battery top vertical (left)                | Glyph |
| 7           | Battery bottom left                        | Glyph |
| 8           | Battery bottom right                       | Glyph |
| 9           | Battery bottom vertical (right)            | Glyph |
| 10          | USB Line                                   | Glyph |
| 10.1 - 10.8 | USB Line Zones from top to bottom          | Zones |
| 11          | USB Dot                                    | Glyph |

## Other noteworthy points
When using the new *GlyphTranslator* you need to tell it for which Phone you made that Label file.
So the new minimal required command syntax for Phone (1) will be: `python GlyphTranslator.py --phone-model Phone1 Label.txt`
For Phone (2) replace `Phone1` with `Phone2`

> [!WARNING]
> This does **NOT** magically convert your Phone (1) composition to a Phone (2) one or vice versa! Pass in the phone model you had in mind when creating your Label file or else the *GlyphTranslator* might error out.

***

## FAQ
### What prompted the rewrite and the syntax change?
To make it short: The Phone (2a) came out and the old version could not handle the third phone because it was never designed to do so - silly me.
The new version should be much more future-proof.

### Will the current version of the scripts be lost forever?
Nope. They will be available on a second branch with the name `v1.0.0` once the time arrives. But moving forward I recommend using the new version.

> [!CAUTION]
> The current version of the scripts (`v1.0.0`) will not be updated going forward.
> They will stay as is without any support on my part.

### When will the new version of the scripts be out?
I can't give an exact date yet ~~but I hope that I can publish them until the end of March~~.
To give you an idea of what I still need to do:
* ***GlyphTranslator:***
  * [x] Rework the watermark feature
  * [x] Test the hell out of the new implementation with the help of you guys ❤️
* ***GlyphModder:***
  * [x] Rewrite the basic functionality
  * [x] Implement the reworked watermark feature
  * [x] Implement the new media metadata tags introduced in *Glyph Composer* v1.4.0
  * [x] Probably more...
  * [x] Test, test, test
* **The converter script to convert Label files from the old syntax to the new syntax**
  * [x] Basic functionality - Migrate old Label files to the new Label syntax
  * [x] ~~Implement the conversion of glypha files with the old watermark implementation to the reworked one~~
  * [x] TESTINGGGGG
* **Documentation**
  * [x] New Label syntax with a reworked explanation of the glyphId
  * [x] Migration/Converter script
  * [x] New troubleshooting steps for common migration pitfalls
 
I try to update this list as I go along 👍
