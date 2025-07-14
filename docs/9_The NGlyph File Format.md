# The [\[NGlyph File\]](./1_Terminology.md#nglyph-file) Format
## Introduction
This is an intermediate file format that is used by the Glyph Tools. It soley contains the raw light data (no audio) and can thus be shared online without infringing on any copyright laws.  
A person who knows what audio to use along this light data can then utilize the Glyph Tools with the [\[NGlyph File\]](./1_Terminology.md#nglyph-file) to create the final [\[composition\]](./1_Terminology.md#compositioncompositions).

To prevent people other than the author itself from claiming ownership of the light data and thus the [\[composition\]](./1_Terminology.md#compositioncompositions), a basic watermark system is included.

A full example file can be found at the end of this documentation.

## Explanation of the format
The [\[NGlyph File\]](./1_Terminology.md#nglyph-file) is a UTF-8 encoded [JSON](https://www.w3schools.com/whatis/whatis_json.asp) file that contains the following field names in the top level:

| Field Name                  | Required                                             | Value Type       |
| --------------------------- | ---------------------------------------------------- | ---------------- |
| [VERSION](#version)         | :white_check_mark:                                   | Integer          |
| [PHONE_MODEL](#phone_model) | :white_check_mark:                                   | String           |
| [AUTHOR](#author)           | :white_check_mark:                                   | Array of Strings |
| [CUSTOM1](#custom1)         | :white_check_mark:                                   | Array of Strings |
| [WATERMARK](#watermark)     | :heavy_multiplication_x:                             | Array of Strings |
| [SALT](#salt)               | Required if and only if field *WATERMARK* is present | String           |
| [LEGACY](#legacy)           | :heavy_multiplication_x:                             | Boolean          |

### VERSION
**This is a required field.** It is the version number of the [\[NGlyph File\]](./1_Terminology.md#nglyph-file) format. It is there to account for possible incompatible changes to the format in the future. It must always be positive and starts at `1`. This documentation always documents the latest version that can be seen in the table below.

**Changes between versions:**
| VERSION | Migration steps needed from previous version |
| :-----: | -------------------------------------------- |
|  **1**  | -                                            |
<!--When a new format version is made, add it here and provide a link to each documented version--->

### PHONE_MODEL
**This is a required field.** To identify the phone model the light data was made for. Must be one of the below listed values.
| Device Name                                  | PHONE_MODEL |
| -------------------------------------------- | ----------- |
| Nothing Phone (1)                            | `PHONE1`    |
| Nothing Phone (2)                            | `PHONE2`    |
| Nothing Phone (2a) / Nothing Phone (2a) Plus | `PHONE2A`   |
| Nothing Phone (3a) / Nothing Phone (3a) Pro  | `PHONE3A`   |
| Nothing Phone (3)                            | `PHONE3`    |

> [!IMPORTANT]
> The special 15 [\[Zones\]](./1_Terminology.md#zones) mode for the Nothing Phone (1) does not have it's own value. *PHONE_MODEL* is `PHONE1` in this case.
> If you want to know if light data is made for this mode, you can count the number of columns in the *AUTHOR* data.
> 
> More info [here](./8_Technical%20Details.md#author).

### AUTHOR
**This is a required field.** Contains the author data as described in the [Technical Details](./8_Technical%20Details.md#author) but split by each new line, resulting in a string array (except when there is a watermark, see following sections). This allows the data to be humanly readable when the JSON is pretty formatted, which is done on purpose when creating the file via the Glyph Tools.

> [!WARNING]
> When a watermark is present (*[WATERMARK](#watermark)* field) the **light data is encrypted** with the contents of the watermark to stop people from simply removing the watermark or changing it to their name.

#### Encryption process
> [!CAUTION]
> When reading a [\[composition\]](./1_Terminology.md#compositioncompositions), watch out for the `GLYPHER_WATERMARK` metadata tag on the audio. It contains the watermark with a new line `\n` prepended to it.
> 
> **Make sure that when you write composition data sourced from a [\[NGlyph File\]](./1_Terminology.md#nglyph-file) to the audio that you also include that metadata tag in the data written, if a watermark is present!**

> [!IMPORTANT]
> Only needed if you plan to use the *[WATERMARK](#watermark)* field!!!

First the watermark is cleaned up by accounting for all the different ways OS's represent new lines:
```python
clean_watermark = watermark.replace('\r\n', '\n').replace('\r', '\n')
```
Then the key is derived from that by encoding the string as UTF-8 bytes and by passing that through PBKDF2 using HMAC-SHA256 with the following settings:
* length: 32
* iterations: 480000
* salt: 16 bytes - see *[Salt](#salt)* field. Should be randomly generated.

And then base64 url safe encoded.
```python
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC # 'cryptography' package

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
key = base64.urlsafe_b64encode(kdf.derive(clean_watermark.encode('utf-8')))
```
The author data (`\r\n` for new lines) encoded as UTF-8 bytes is then zlib compressed (with best compression), encrypted with [Fernet](https://cryptography.io/en/latest/fernet/) (symmetric encryption) and compressed again with zlib (with best compression).
```python
import zlib
from cryptography.fernet import Fernet # 'cryptography' package

f = Fernet(key)
compressed_token: bytes = zlib.compress(f.encrypt(zlib.compress(author_string.encode('utf-8'), zlib.Z_BEST_COMPRESSION)), zlib.Z_BEST_COMPRESSION)
```
Then the string is constructed to look like the original author data: Each byte of the `compressed_token` is converted to an integer, the length of `compressed_token` is prepended and depending on the column count of the unencrypted data, written as it were the brightness values.  
If there are not enough bytes to completely fill the last row with the correct number of brightness values, 0's are used as padding.
```python
import math

encrypt_author_data: list[list[int]] = [[0 for _ in range(n_columns)] for _ in range(math.ceil((len(compressed_token) + 1) / n_columns))]
encrypt_author_data[0][0] = len(compressed_token)
for i, byte in enumerate(compressed_token, 1):
    encrypt_author_data[i // n_columns][i % n_columns] = byte
encrypted_author_str = '\r\n'.join([f"{','.join([str(e) for e in line])}," for line in encrypt_author_data])
```

#### Decryption process
> [!IMPORTANT]
> Only needed if there is a *[WATERMARK](#watermark)* field!!!

Follow the rough steps from above but in reverse order:
1. Clean watermark string and derive key
2. Get length of compressed token - first element
3. Get compressed token by removing padding and first element
4. Decompress with zlib, decrypt with [Fernet](https://cryptography.io/en/latest/fernet/), decompress again with zlib
5. Decode as UTF-8

### CUSTOM1
**This is a required field.** Contains the custom1 data as described in the [Technical Details](./8_Technical%20Details.md#custom1) but split by each new line, resulting in a string array. This allows the data to be humanly readable when the JSON is pretty formatted, which it is when creating the file via the Glyph Tools.

If you do not have any *CUSTOM1* data just leave the array empty.

### WATERMARK
This is an optional field. Is essentially a string but split by each new line, resulting in a string array.

> [!CAUTION]
> If this fild is present, then the *[SALT](#salt)* field must be present as well!

### SALT
This must only be present if the *[WATERMARK](#watermark)* field is present. It contains a base64 encoded representation of the 16 bytes used as the salt in the encryption process for the *AUTHOR* field.

The salt bytes should be randomly generated.

### LEGACY
This is an optional field. This boolean flag should be set if a [\[composition\]](./1_Terminology.md#compositioncompositions) with desync issues is detected. Older Glyph Tools versions had a bug that caused the lights to fall behind the audio, resulting in a desync over time.  
If this field is not present `false` is the default.

> [!IMPORTANT]
> New compositions created with current tooling should never have this set!

If a composition is considered a "legacy" composition can be determined via the following criteria - only one of them needs to be true:
| Criteria                                    | Additional Notes                                                                                                                                                                                                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `COMPOSER` metadata not starting with `v1-` | Pre *Glyph Composer* App 1.4.0 this versioning was not present and the bug was fixed in Glyph Tools when 1.4.0 came out. No other [\[composition\]](./1_Terminology.md#compositioncompositions) composition creation tool existed at that time except Glyph Tools. |
| `ALBUM` metadata equals `Glyphify`          | Early versions of the popular [Glyphify](https://play.google.com/store/apps/details?id=com.frank.glyphify) App had this bug. When this bug was fixed the album changed to `v1-Glyphify`.                                                                           |
| `ALBUM` metadata equals `custom`            | Early versions of [Better-Nothing-Glyph-Composer](https://better-nothing-glyph-composer.pages.dev/) (BNGC) had this bug. When the bug was fixed the album changed to `BNGC v1`.                                                                                    |

> [!NOTE]
> More info on the metadata strings of a [\[composition\]](./1_Terminology.md#compositioncompositions) can be found in the [Technical Details](./8_Technical%20Details.md).

## Example
> [!NOTE]
> Both of the below contain the same data - one is without a watermark, the other is with one.

### Without Watermark
```JSON
{
    "VERSION": 1,
    "PHONE_MODEL": "PHONE2A",
    "AUTHOR": [
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,0,",
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,0,4095,",
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,0,",
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,0,4095,",
        "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,",
        "0,0,0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,",
        "0,0,0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,",
        "0,0,0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,",
        "0,0,0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,",
        "0,0,0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,",
        "0,0,0,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,",
        "4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,0,4095,"
    ],
    "CUSTOM1": [
        "1-0",
        "150-1"
    ]
}
```

### With Watermark
```JSON
{
    "VERSION": 1,
    "PHONE_MODEL": "PHONE2A",
    "AUTHOR": [
        "187,120,218,21,193,97,19,66,48,0,0,208,95,228,174,196,201,199,176,44,84,87,50,110,95,220,",
        "200,104,75,204,76,248,245,93,239,213,135,63,167,43,173,44,221,228,106,253,104,126,51,45,117,216,",
        "168,190,51,61,178,217,210,212,118,176,212,250,217,112,79,115,43,173,76,207,104,167,143,73,65,114,",
        "234,136,81,61,146,184,88,209,216,169,160,31,32,194,168,15,160,186,166,47,109,25,132,207,99,248,",
        "108,46,81,21,174,226,138,36,46,92,23,13,152,140,95,150,157,185,55,73,17,236,236,119,242,153,",
        "2,169,32,160,149,9,151,59,182,243,59,1,224,21,106,235,197,0,249,131,176,186,109,188,3,7,",
        "54,163,122,107,85,28,126,119,102,20,45,106,62,10,67,222,202,82,62,245,61,59,241,120,159,86,",
        "236,7,138,90,71,73,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"
    ],
    "CUSTOM1": [
        "1-0",
        "150-1"
    ],
    "WATERMARK": [
        "Your Watermark",
        "Second Line"
    ],
    "SALT": "kRMhWkP9rxQxpPEJzv+NxA=="
}
```
