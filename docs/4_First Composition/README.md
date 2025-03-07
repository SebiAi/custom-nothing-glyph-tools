# Create your first [\[composition\]](../1_Terminology.md#compositioncompositions)
This topic will have multiple chapters, starting with prepairing your audio inside Audacity.  
The table of contents will be visible in each chapter at the top so you can see where you are (bold title and not clickable).

## :writing_hand: Table of contents
The table of contents for this topic is the following:
- **Prepairing your project**
- [Explaining the Glyph Format](./1_Explaining%20the%20Glyph%20Format.md)
- [Using the Glyph Tools](./2_Using%20the%20Glyph%20Tools.md)
- [Final steps](./3_Final%20steps.md)

## Prepairing your project
### Importing the audio
To get started, **open Audacity&reg;** which you installed in the [*Installing Dependencies*](../3_Installing%20Dependencies/README.md) step. It is a very versatile open-source software that can do a lot of stuff.

> [!CAUTION]
> This wiki is not meant to be a Audacity&reg; tutorial, the wiki will only teach you a few required things. In combination with common sense you should be able to create your composition just fine.
>
> There may also be links to the [wiki of Audacity&reg;](https://manual.audacityteam.org/index.html) which may contain additional information. This info can aid you in doing a task at hand.

Then open your audio by
* drag and dropping it in.
* using the *File* -> *Open...* option.

> [!NOTE]
> I would recommend choosing a melodically simple audio to start off with, like this one: https://youtu.be/xvFZjo5PgG0
>
> More simple songs:
> * https://youtu.be/H4BAEf5V-Yc

### Cutting your audio
> [!NOTE]
> If you plan on sharing your creation later on, note down at what timestamps you cut your audio (e.g.: `00h01m21.041s`)!  
> You can see the timestamps of your selection on the bottom bar in Audacity&reg;.

You can now select parts of the audio you want to cut away by **clicking and draging your mouse across the waveform and then pressing the <kbd>DELETE</kbd> key**.
![Audacity&reg; selected audio](./assets/Audacity%20selected%20audio.png)

> [!TIP]
> You can use fading effects to smooth out audio transitions and more by selecting a piece of audio and then selecting one effect from the *Effect* menu up at the top. More infos on effects [here](https://manual.audacityteam.org/man/effect_menu.html).

### Adding a [\[Label Track\]](../1_Terminology.md#label-track)
To create the lighting part of the [\[composition\]](../1_Terminology.md#compositioncompositions) we will utilize the *Label Track* feature of Audacity&reg;.  
Start by adding one to your (hopefully already saved: <kbd>CONTROL + S</kbd>) project like this: *Tracks* -> *Add New* -> *Label Track*
![Audacity&reg; new label track](./assets/Audacity%20add%20new%20label%20track.png)

We now create [\[Labels\]](../1_Terminology.md#label) (<kbd>CONTROL + B</kbd>) and name them a certain way to make the [\[Glyphs\]](../1_Terminology.md#glyphs) light up like we want them to - more info on that in the upcoming chapters.

> [!TIP]
> You can add multiple [\[Label Tracks\]](../1_Terminology.md#label-track) to keep your [\[Labels\]](../1_Terminology.md#label) more organized.

> [!TIP]
> More info on [\[Label Tracks\]](../1_Terminology.md#label-track) can be found [in the Audacity&reg; wiki](https://manual.audacityteam.org/man/label_tracks.html).

### Working with [\[Labels\]](../1_Terminology.md#label)
You may skip this section now and come back to it later when you need to know more about creating/deleting/moving them.

> [!TIP]
> Use the snapping function of the cursor (yellow line) to precisely place your labels. See [here](https://manual.audacityteam.org/man/boundary_snap_guides.html) for more info.

> [!TIP]
> You can view, edit and fine tune all your [\[Labels\]](../1_Terminology.md#label) with the *Label Editor*: *Edit* -> *Labels* -> *Label Editor*
>
> See the [Audacity&reg; wiki on the *Label Editor*](https://manual.audacityteam.org/man/labels_editor.html) for more info.

#### Create
You can create [\[Labels\]](../1_Terminology.md#label) by
* setting your cursor (left-click) at the desired position (creates a [\[Point Label\]](../1_Terminology.md#point-label))
* selecting a region (clicking and draging) (creates a [\[Region Label\]](../1_Terminology.md#region-label))

and then pressing <kbd>CONTROL + B</kbd> on your keyboard.  
More info [here](https://manual.audacityteam.org/man/label_tracks.html#Creating_and_selecting_Labels).

> [!TIP]
> You can transform a [\[Point Label\]](../1_Terminology.md#point-label) into a [\[Region Label\]](../1_Terminology.md#region-label) by clicking and dragging either of its chevron handles aka. the arrows pointing away from the center dot.

#### Delete
Delete [\[Labels\]](../1_Terminology.md#label) by
* right-clicking on the name of one and selecting *Delete Label*.
* selecting a region containing [\[Labels\]](../1_Terminology.md#label) *in the [\[Label Track\]](../1_Terminology.md#label-track)* and pressing <kbd>CONTROL + ALT + K</kbd>.

Both of these methods will retain audio synchronization, which means that the [\[Labels\]](../1_Terminology.md#label) after the deleted ones will not move and remain on their position.  
More info [here](https://manual.audacityteam.org/man/label_tracks.html#Removing_Labels_only).

#### Moving
You can move a [\[Label\]](../1_Terminology.md#label) by clicking and dragging
* on the circle dot - moves the start/end position.
* on the line below the name (for [Region Labels\]](../1_Terminology.md#region-label) only) - moves the start **and** end position.

More info [here](https://manual.audacityteam.org/man/label_tracks.html#Editing.2C_resizing_and_moving_Labels).

> [!TIP]
> You can move all [\[Labels\]](../1_Terminology.md#label) in a [\[Label Track\]](../1_Terminology.md#label-track) by holding <kbd>SHIFT</kbd> and then click and dragging on one of the [\[Labels\]](../1_Terminology.md#label) line below the name.

## The next step
Now that you *cut your audio*, *set up the [\[Label Track\]](../1_Terminology.md#label-track)* and *experimented with creating and deleting [\[Labels\]](../1_Terminology.md#label)*, you should think about for which supported phone you want to make this composition. **Supported phones** by the Glyph Tools are:
* Nothing Phone (1)
* Nothing Phone (2)
* Nothing Phone (2a)
* Nothing Phone (2a) Plus
* Nothing Phone (3a)
* Nothing Phone (3a) Pro

> [!IMPORTANT]
> Because Nothing Phone (2a) compositions are compatible with the Nothing Phone (2a) Plus and vice versa, the Glyph Tools do not have a separate "Nothing Phone (2a) Plus" mode. Create your composition for the Nothing Phone (2a) instead.  
The same applies for the Nothing Phone (3a) and Nothing Phone (3a) Pro.

*After* you have made up your mind about it, continue to the next chapter.
<div align="right"><h3><a href="1_Explaining the Glyph Format.md">Go to next chaper</a></h3></div>