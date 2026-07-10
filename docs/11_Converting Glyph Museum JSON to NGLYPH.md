# Converting Glyph Museum JSON to NGLYPH

This doc file explains how to convert animation files exported from the community **Glyph Museum** app (or [web editor](https://editor.glyphmuseum.com/)) into the [\[NGlyph File\]](./1_Terminology.md#nglyph-file) format used by the *Glyph Tools*.

> [!NOTE]
> This tool is intended for target devices with a Glyph Matrix, currently supporting **Nothing Phone (3)** (`PHONE3`) and **Nothing Phone (4a) Pro** (`PHONE4APRO`).

## How it works

The *Glyph Museum* animations are stored in a JSON format where:
1. Each frame has a duration `d` in milliseconds.
2. The pixel array `p` maps sequentially to the device's visible LEDs.

The `JsonToGlyphMatrix.py` script reads this JSON format, maps the visible LEDs to the physical row-major coordinates of the target device, interpolates the keyframes to a constant 60fps, and outputs a `.nglyph` file.

Unlike converting via video (which can introduce OpenCV nearest-neighbor scaling and cropping artifacts), the direct JSON converter maps physical LEDs 1-to-1 mathematically.

---

## How to use the script

1. Open the Terminal in your [\[Glyph Tools location\]](./1_Terminology.md#glyph-tools-location).
2. Run the following command:

```bash
python3 JsonToGlyphMatrix.py <JsonFile>
```

> [!IMPORTANT]
> By default, the script will automatically detect the phone model based on the number of pixels in the JSON array:
> - `PHONE4APRO` (Phone 4a Pro): if the array size is 169 or less (uses 137 visible LEDs).
> - `PHONE3` (Phone 3): if the array size is larger than 169 (uses 489 visible LEDs).

3. Once executed, a new `.nglyph` file with the same name as the input JSON file will be created in the same directory. You can then use it with the `GlyphModder.py` script to compile your composition.

---

## Options

You can customize the script's behavior by passing the following options:

| Option | Description |
| :--- | :--- |
| `-o`, `--output` | Specify a custom file path for the output `.nglyph` file. |
| `-m`, `--model` | Explicitly choose the target phone model (`PHONE3` or `PHONE4APRO`), rather than autodetecting the phone model. |
| `-i`, `--interpolation` | Interpolation mode between frames: `linear` (smooth transition) or `nearest` (default, instant transition). |
| `--fps` | Set the target frame rate of the output `.nglyph` file (default: `60.0` FPS). |
| `--version` | Show the version of the script and exit. |

### Example with nearest interpolation:
```bash
python3 JsonToGlyphMatrix.py glyph_data_test.json -i nearest
```
