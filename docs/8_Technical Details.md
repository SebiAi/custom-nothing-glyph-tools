# :wrench: The technical details
This documents the technical details of [\[compositions\]](./1_Terminology.md#compositioncompositions) created with the *Glyph Composer* app developed by Nothing Technology Limited (NOTHING).

> [!NOTE]
> The Phone (3) (Glyph Matrix) is NOT supported in the *Glyph Composer* but the same techniques can still be used to get custom ringtones working and are thus also documented here.

## Audio
The audio is disconnected from the lighting - it only determines the final length of the composition. The maximum you can produce in the app is 10s but it can be longer when making it custom.

## Metadata
There are the following tags in the ogg file (order irrelevant):
* TITLE
* ALBUM
* AUTHOR
* COMPOSER
* CUSTOM1
* CUSTOM2

The *AUTHOR* and *CUSTOM1* tags contain both *Base64* encoded and then *zlib compressed* data (Best Compression (no preset dictionary) - see [here](https://en.wikipedia.org/wiki/List_of_file_signatures)).

### TITLE
Contains the title given in the *Glyph Composer*. Weirdly enough the *Glyph Composer* does not use this tag when displaying the name of the composition - the filename is used instead.  
This title is used in the normal, non-glyph ringtone menu and may be displayed by other software like music players.

### ALBUM
Saves what sound pack was used when the composition was created. Can be changed without any effect on the audio or lights. It does display in the *Glyph Composer*.

### CUSTOM2
This indicates how many [\[Zones\]](./1_Terminology.md#zones) get addressed. This must match with the [*COMPOSER*](#composer) tag.

| Phone                                                                     | *CUSTOM2* string |
| ------------------------------------------------------------------------- | ---------------: |
| Nothing Phone (1)                                                         |          `5cols` |
| Nothing Phone (1) - special 15 [\[Zones\]](./1_Terminology.md#zones) mode |          `5cols` |
| Nothing Phone (2)                                                         |         `33cols` |
| Nothing Phone (2a) / Nothing Phone (2a) Plus                              |         `26cols` |
| Nothing Phone (3a) / Nothing Phone (3a) Pro                               |         `36cols` |
| Nothing Phone (3)                                                         |        `625cols` |

> [!NOTE]
> This tag was not always present before the 1.4.0 *Glyph Composer* update where only the Nothing Phone (1) and Nothing Phone (2) were supported. It was missing if the [\[composition\]](./1_Terminology.md#compositioncompositions) was made on the Nothing Phone (1). Otherwise it had the Nothing Phone (2) value.

### AUTHOR
After decoding and decompressing it contains the [\[Glyph\]](./1_Terminology.md#glyphs) light data in a csv like manner where in each line we have the [\[Zones\]](./1_Terminology.md#zones) separated and followed by a comma (`,`). Each line corresponds to 16.666ms (60Hz).

Depending on the phone we have n Zones:
| Phone                                                                     |   n |
| ------------------------------------------------------------------------- | --: |
| Nothing Phone (1)                                                         |   5 |
| Nothing Phone (1) - special 15 [\[Zones\]](./1_Terminology.md#zones) mode |  15 |
| Nothing Phone (2)                                                         |  33 |
| Nothing Phone (2a) / Nothing Phone (2a) Plus                              |  26 |
| Nothing Phone (3a) / Nothing Phone (3a) Pro                               |  36 |
| Nothing Phone (3)                                                         | 625 |

> [!NOTE]
> The Nothing Phone (1) is a bit of a special case:  
> It officially only supports addressing the 5 [\[Glyphs\]](./1_Terminology.md#glyphs) with no way to address the 4 [\[Zones\]](./1_Terminology.md#zones) in the *Battery* [\[Glyph\]](./1_Terminology.md#glyphs) and the 8 in the *USB Line* [\[Glyph\]](./1_Terminology.md#glyphs) with the normal functionality of the *Glyph Composer* app.
>
> Because the *Glyph Composer* uses essentially the *Glyph Developer Kit* in the backend we can increase the [\[Zone\]](./1_Terminology.md#zones) count from 5 to 15 to account for all the extra [\[Zones\]](./1_Terminology.md#zones) mentioned.
>
> ~~Why not always use the 15 [\[Zones\]](./1_Terminology.md#zones) mode on the Phone (1)?:~~  
> ~~Because it is not officially supported, the lights get stuck if the [\[composition\]](../1_Terminology.md#compositioncompositions) stops prematurely. Toggle the *Glyph Torch* to fix it.~~  
> This issue was fixed with `Nothing OS V3.2-250610-1104` and higher on the Phone (1).
>
> If we use the 15 [\[Zones\]](./1_Terminology.md#zones) mode on the Phone (1) we still need to set the [*CUSTOM2*](#custom2) tag to `5cols` or else it won't import. This makes it a bit tricky to discern 5 [\[Zones\]](./1_Terminology.md#zones) and 15 [\[Zones\]](./1_Terminology.md#zones) [\[compositions\]](./1_Terminology.md#compositioncompositions).

#### Indexes for the [\[Glyphs\]](./1_Terminology.md#glyphs)
Depending on the phone we have different indexes in the csv for the [\[Glyphs\]](./1_Terminology.md#glyphs):
##### Nothing Phone (1) indexes
| Index | Glyph    |
| ----: | :------- |
|     0 | Camera   |
|     1 | Diagonal |
|     2 | Battery  |
|     3 | USB Line |
|     4 | USB Dot  |

##### Nothing Phone (1) - 15 [\[Zones\]](./1_Terminology.md#zones) mode indexes
| Index | Glyph/Zone                  | Direction          |
| ----: | :-------------------------- | :----------------- |
|     0 | Camera                      | -                  |
|     1 | Diagonal                    | -                  |
|     2 | Battery bottom left corner  | -                  |
|     3 | Battery bottom right corner | -                  |
|     4 | Battery top right corner    | -                  |
|     5 | Battery top left corner     | -                  |
|     6 | USB Dot                     | -                  |
|  7-14 | USB Line                    | From bottom to top |

##### Nothing Phone (2) indexes
| Index | Glyph/Zone                           | Direction          |
| ----: | :----------------------------------- | :----------------- |
|     0 | Camera top                           | -                  |
|     1 | Camera bottom                        | -                  |
|     2 | Diagonal                             | -                  |
|  3-18 | Battery top right                    | From right to left |
|    19 | Battery top left                     | -                  |
|    20 | Battery top vertical (left side)     | -                  |
|    21 | Battery bottom left                  | -                  |
|    22 | Battery bottom right                 | -                  |
|    23 | Battery bottom vertical (right side) | -                  |
|    24 | USB Dot                              | -                  |
| 25-32 | USB Line                             | From bottom to top |

##### Nothing Phone (2a) / Nothing Phone (2a) Plus indexes
| Index | Glyph/Zone   | Direction                     |
| ----: | :----------- | :---------------------------- |
|  0-23 | Top left     | From bottom left to top right |
|    24 | Middle right | -                             |
|    25 | Bottom left  | -                             |

##### Nothing Phone (3a) / Nothing Phone (3a) Pro indexes
| Index | Glyph/Zone   | Direction                     |
| ----: | :----------- | :---------------------------- |
|  0-19 | Top left     | From bottom left to top right |
| 20-30 | Middle right | From top to bottom            |
| 31-35 | Bottom left  | From bottom right to top left |

##### Nothing Phone (3)
The first index maps to the top left pixel, the last index maps to the bottom right pixel. The mapping in between is row major, meaning every 25th index (e.g.: 0, 25, 50, ...) will be the leftmost pixel in each row.

Because of the round Glyph Matrix on the Phone (3), not all of the 625 [\[Zones\]](./1_Terminology.md#zones) can be used. Only 489 of these will be visible, the others will not be used and can be set to 0.  
Visible index range includes (counting from 0 onwards!!):
* 9-15 (top row)
* 32-42
* 55-69
* 79-95
* 103-121
* 127-147
* 152-172
* 176-198
* 201-223
* 225-399 (fully filled rows in the middle)
* 401-423
* 426-448
* 452-472
* 477-497
* 503-521
* 529-545
* 555-569
* 582-592
* 609-615 (bottom row)

See [here](https://raw.githubusercontent.com/Nothing-Developer-Programme/GlyphMatrix-Developer-Kit/refs/heads/main/image/pixel_coordinate.png) for a visual.

<br><br>

Each [\[Zone\]](./1_Terminology.md#zones) can have a light value from 0 to 4095 (2^12 values), the smallest step is 1. If the data is longer than the audio it will not be played.

The new line consists of Carriage Return (CR) and Line Feed (LF): `\r\n`
The data ends with a final new line `\r\n`.

*Example Nothing Phone (1):*
```csv
0,0,4095,0,0,
0,0,4095,0,2032,
0,0,0,0,0,
0,0,0,0,0,
0,0,0,0,0,

```
The *Battery* [\[Glyph\]](./1_Terminology.md#glyphs) is fully on for ~33.332ms and the *USB Dot* [\[Glyph\]](./1_Terminology.md#glyphs) is only on for 16.666ms after 16.666ms (after the start) at about 50% brightness.

*Example Nothing Phone (1) - 15 [\[Zone\]](./1_Terminology.md#zones) mode:*
```csv
0,0,4095,4095,4095,4095,0,0,0,0,0,0,0,0,0,
0,0,4095,4095,4095,4095,2032,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,

```
Same example as above but with the special 5 [\[Zone\]](./1_Terminology.md#zones) mode on Phone (1).

*Example Nothing Phone (2):*
```csv
0,0,0,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,2709,0,0,2709,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,1791,0,0,1791,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,919,919,919,919,919,919,919,919,919,919,919,919,919,919,919,919,0,0,919,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,245,245,245,245,245,245,245,245,245,245,245,245,245,245,245,245,0,0,245,0,0,0,0,0,0,0,0,0,0,0,

```

*Example Nothing Phone (2a) / Nothing Phone (2a) Plus:*
```csv
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,0,4095,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,0,4095,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,
0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,
0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,
0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,
0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,
0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,
4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,

```
A loading bar like animation in the *Top left* [\[Glyph\]](./1_Terminology.md#glyphs), while the *Middle right* and the *Bottom left* [\[Glyph\]](./1_Terminology.md#glyphs) alternate, starting with the *Middle right*.

### COMPOSER
This depends on what device the composition was created on:
| Phone                                                                     |             *Composer* string |
| ------------------------------------------------------------------------- | ----------------------------: |
| Nothing Phone (1)                                                         |  `v1-Spacewar Glyph Composer` |
| Nothing Phone (1) - special 15 [\[Zones\]](./1_Terminology.md#zones) mode |  `v1-Spacewar Glyph Composer` |
| Nothing Phone (2)                                                         |      `v1-Pong Glyph Composer` |
| Nothing Phone (2a)                                                        |    `v1-Pacman Glyph Composer` |
| Nothing Phone (2a) Plus                                                   | `v1-PacmanPro Glyph Composer` |
| Nothing Phone (3a) / Nothing Phone (3a) Pro                               | `v1-Asteroids Glyph Composer` |
| Nothing Phone (3)                                                         |   `v1-Metroid Glyph Composer` |

> [!IMPORTANT]
> Before the 1.4.0 *Glyph Composer* update the prefix `v1-` was missing and only the Nothing Phone (1) and the Nothing Phone (2) were supported.

> [!NOTE]
> The *Composer* string gets constructed with a Java *StringBuilder*:
> 1. Appending "v1-"
> 2. Appending the result of the Android `Build.DEVICE` field. (gets the `ro.product.device` property)
> 3. Appending " Glyph Composer" - yes, with the space infront

If the tag does not have the right form or not match with the device or if the [*CUSTOM2*](#custom2) tag does not correlate (e.g.: `33cols` for a Nothing Phone (1) would NOT correlate), the *Glyph Composer* will not import the file.

### CUSTOM1
This is mainly data for the *Glyph Composer* so it can display dots on the timeline when playing the file. After decoding and decompressing each dot in the app is defined by a timestamp (in ms and 1 ms steps) and an ID representing which of the 5 buttons in the app has been pressed. On most devices this ID can be correlated to a [\[Glyph\]](./1_Terminology.md#glyphs). The timestamp and the ID are separated by a dash (`-`). Between each dot is a comma (`,`) and at the end of the line also.

There are no new lines in this file, all dots are after one another.
It is entirely possible to mismatch the *CUSTOM1* and *ALBUM* data.

> [!NOTE]
> Keep in mind that the *Glyph Composer* only has 5 buttons (therefore 5 dot locations) which means that complex custom light animations which address Zones individually can not be properly displayed in the *Glyph Composer*.

#### IDs
##### Nothing Phone (1)
| Glyph/Zone |  ID |
| :--------- | --: |
| Camera     |   0 |
| Diagonal   |   1 |
| Battery    |   2 |
| USB Line   |   3 |
| USB DOT    |   4 |

##### Nothing Phone (2)
| Glyph/Zone                           |  ID |
| :----------------------------------- | --: |
| Camera top                           |   0 |
| Camera bottom                        |   0 |
| Diagonal                             |   1 |
| Battery top right                    |   2 |
| Battery top left                     |   2 |
| Battery top vertical (left side)     |   2 |
| Battery bottom left                  |   2 |
| Battery bottom right                 |   2 |
| Battery bottom vertical (right side) |   2 |
| USB Dot                              |   3 |
| USB Line                             |   4 |

##### Nothing Phone (2a) / Nothing Phone (2a) Plus indexes
| Glyph/Zone   |  ID |
| :----------- | --: |
| Top left     |   0 |
| Middle right |   1 |
| Bottom left  |   2 |

##### Nothing Phone (3a) / Nothing Phone (3a) Pro indexes
| Glyph/Zone   |  ID |
| :----------- | --: |
| Top left     |   0 |
| Middle right |   1 |
| Bottom left  |   2 |

> [!NOTE]
> Assigning every [\[Glyph\]](./1_Terminology.md#glyphs) an ID on the Nothing Phone (2a) / Nothing Phone (2a) Plus / Nothing Phone (3a) / Nothing Phone (3a) Pro is not possible because it only has three of them. I've just choosen these IDs.
> 
> Also no mapping for the Nothing Phone (3) is provided here.

## Aditional Notes
A [\[composition\]](./1_Terminology.md#compositioncompositions) *can* be manually imported by moving the audio file to `Ringtones/Compositions`. The phone will interpret the lighting data in it's own way if it was made for another phone.

A Nothing Phone (1) [\[composition\]](./1_Terminology.md#compositioncompositions) can be played back on a Nothing Phone (2) if it does **NOT** use 15 [\[Zones\]](./1_Terminology.md#zones).

A Nothing Phone (2a) [\[composition\]](./1_Terminology.md#compositioncompositions) can be played back on a Nothing Phone (2a) Plus and vice versa. They both have the same Glyph and Zone layout. The only difference is the [*COMPOSER*](#composer) tag.

A Nothing Phone (3a) [\[composition\]](./1_Terminology.md#compositioncompositions) can be played back on a Nothing Phone (3a) Pro and vice versa. They both have the same Glyph and Zone layout.
