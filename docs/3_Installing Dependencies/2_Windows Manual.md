# Installing Dependencies on Windows - Manual method

# Python
1. Download from there: https://www.python.org/downloads/
2. On the first step of the installer make sure that the checkbox *Add Python to PATH* is checked at the bottom. See [here](https://www.pitt.edu/~naraehan/python3/img/win-install-2.png) for a visual.
> [!NOTE]
> You can check if this worked by:
> 1. Pressing <kbd>WINDOWS + R</kbd>,
> 2. Entering `cmd` inside the run dialog and pressing *OK*
> 3. Entering `python --version` and pressing <kbd>ENTER</kbd>
>
> <details>
>    <summary>It should look like this (click to expand):</summary>
>    
>    ```
>    Python 3.11.6
>    ```
> </details>

# ffmpeg and ffprobe
1. Download from here: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `%localappdata%\ffmpeg` so that the `bin` directory is directly inside the `ffmpeg` directory.  
![Windows extracted ffmpeg directory](./assets/1a_Windows%20extracted%20ffmpeg%20directory.png)
3. Press <kbd>WINDOWS + R</kbd>
4. Input this into the run dialog: `SystemPropertiesAdvanced.exe` and press *OK*
5. Press the *Environment variables* button near the bottom of the dialog  
![Windows System Properties dialog](./assets/1b_Windows%20System%20Properties%20dialog.png)
6. Double click the *Path* variable under *User variables*  
![Windows Environment Variables user path location](./assets/1c_Windows%20Environment%20Variables%20user%20path.png)
7. Press the *New* button and paste `%localappdata%\ffmpeg\bin`  
![Windows entered environment variable](./assets/1d_Windows%20entered%20environment%20variable.png)
8. Confirm with `ENTER` and confirm all the dialogs with the *OK* button
> [!NOTE]
> You can check if this worked by:
> 1. Pressing <kbd>WINDOWS + R</kbd>,
> 2. Entering `cmd` inside the run dialog and pressing *OK*
> 3. Entering `ffmpeg -version` and pressing <kbd>ENTER</kbd>
>
> <details>
>    <summary>It should look like this (click to expand):</summary>
>    
>    ```
>    ffmpeg version 6.0-full_build-www.gyan.dev Copyright (c) 2000-2023 the FFmpeg developers
>    built with gcc 12.2.0 (Rev10, Built by MSYS2 project)
>    configuration: --enable-gpl --enable-version3 --enable-shared --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-sdl2 --enable-libaribb24 --enable-libdav1d --enable-libdavs2 --enable-libuavs3d --enable-libzvbi --enable-librav1e --enable-libsvtav1 --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxvid --enable-libaom --enable-libjxl --enable-libopenjpeg --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-ffnvcodec --enable-nvdec --enable-nvenc --enable-d3d11va --enable-dxva2 --enable-libvpl --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libilbc --enable-libgsm --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
>    libavutil      58.  2.100 / 58.  2.100
>    libavcodec     60.  3.100 / 60.  3.100
>    libavformat    60.  3.100 / 60.  3.100
>    libavdevice    60.  1.100 / 60.  1.100
>    libavfilter     9.  3.100 /  9.  3.100
>    libswscale      7.  1.100 /  7.  1.100
>    libswresample   4. 10.100 /  4. 10.100
>    libpostproc    57.  1.100 / 57.  1.100
>    ```
> </details>

# Audacity&reg;
1. Download from there: https://www.audacityteam.org/ and install

# python packages
1. Navigate to your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) in your file explorer
2. Double click the *Open_Terminal_Here.bat* file to open a terminal window
3. Enter this command to install all the python packages needed
```bash
python -m pip install -U -r requirements.txt
```
> [!NOTE]
> The output should look something like this:
> <details>
>    <summary>(click to expand):</summary>
>    
>    ```
>    Collecting termcolor (from -r requirements.txt (line 1))
>      Downloading termcolor-2.4.0-py3-none-any.whl.metadata (6.1 kB)
>    Collecting mido (from -r requirements.txt (line 2))
>      Downloading mido-1.3.2-py3-none-any.whl.metadata (6.4 kB)
>    Collecting colorama>=0.4.6 (from -r requirements.txt (line 3))
>      Downloading colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
>    Requirement already satisfied: packaging~=23.1 in c:\users\vm\appdata\local\programs\python\python311\lib\site-packages (from mido->-r requirements.txt (line 2)) (23.2)
>    Downloading termcolor-2.4.0-py3-none-any.whl (7.7 kB)
>    Downloading mido-1.3.2-py3-none-any.whl (54 kB)
>       ---------------------------------------- 54.6/54.6 kB 1.4 MB/s eta 0:00:00
>    Downloading colorama-0.4.6-py2.py3-none-any.whl (25 kB)
>    Installing collected packages: termcolor, mido, colorama
>    Successfully installed colorama-0.4.6 mido-1.3.2 termcolor-2.4.0
>    ```
> </details>