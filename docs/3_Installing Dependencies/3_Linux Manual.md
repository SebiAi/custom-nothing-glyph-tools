# Installing Dependencies on Linux - Manual method
> [!NOTE]
> Depending on your distro the installation process may differ (other package managers, other package names etc.) You can also use a graphical package manager and search for the needed packages there.  
> **This will mainly cover Ubuntu based distros**.

1. To install *ffmpeg*, *ffprobe* and *python* you can use this command:
```bash
sudo apt update && sudo apt install -y ffmpeg python3
```
2. Navigate to your [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location) in your terminal
3. Enter this command to install all the python packages needed
```bash
python3 -m pip install -U -r requirements.txt
```
> [!TIP]
> You can also set up a virtual environment to install the packages inside the [\[Glyph Tools location\]](../1_Terminology.md#glyph-tools-location). More info [here](https://docs.python.org/3/library/venv.html).

4. Install Audacity&reg; with your package manager or from [the website](https://www.audacityteam.org/)