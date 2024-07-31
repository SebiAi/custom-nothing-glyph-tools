# Installing Dependencies on MacOS - Manual method
> [!NOTE]
> I can't provide step by step instructions for MacOS right now because I do not have access to a Mac.  
> However, you can install all these dependencies with [brew](https://brew.sh/) or download them from their respective website.

<ol>
  <li>
    Install the following dependencies:
    <ul>
      <li><a href="https://www.python.org/downloads/"><b>python3</b><a></li>
      <li><a href="https://ffmpeg.org/download.html"><b>ffmpeg</b></a></li>
      <li><a href="https://ffmpeg.org/download.html"><b>ffprobe</b></a></li>
      <li><a href="https://www.audacityteam.org/"><b>Audacity&reg;</b></a></li>
    </ul>
  </li>
</ol>

2. Navigate to your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) in your terminal
3. Enter this command to install all the python packages needed
```bash
python3 -m pip install -U -r requirements.txt
```

> [!TIP]
> You can also set up a virtual environment to install the packages inside the [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location). More info [here](https://docs.python.org/3/library/venv.html).