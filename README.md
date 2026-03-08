# 🎬 Jellingo - Formerly argus-translate-srt

> 🌍 Complete toolkit for subtitles managing

## ⚠️ Important Information

- 💻 **Only tested on Windows**
- 🐍 **Only supports Python up to version 3.12.x**

If you were using argus-translate-srt, please note:
- You must run update-dependencies.bat before using this new version (Jellingo).
- This ensures that all required packages and the updated Argos Translate integration are correctly installed.

Skipping this step may cause errors when extracting or translating subtitles.

## 🛠️ Requirements

- 🐍 **Python 3.12+** with PATH configured and with admin privileges when installing py.exe [Download here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)

## ✨ Features

- 📁 Translate one or multiple subtitle files at a time
- 🎬 Video subtitle extraction – Extract embedded subtitles from your video files (.mkv, .mp4, .avi, .mov)
- 📝 Multi-format support – Translate .ass, .ssa, .vtt, and plain text subtitles in addition to .srt
- 1️⃣ Works with multiple language model installations
- ⏱️ Preserves timing/metadata
- 📊 Progress tracking with visual feedback
- 🔍 Automatic language code detection
- 🔄 Smart translation prompts – Detects if subtitles already exist for your chosen languages and asks if you want to translate missing ones
- ⚡ Fast subsequent runs after initial setup

## How to use

1. Open `GUI.bat` and download the language models you will be using.
2. Open `translate.bat`.
3. Select the .srt files you want to translate.
4. That's it! 🎉

Notes:

- The first run will be slower as it sets up the environment.
- The script will still need the language model installed (it prompts you to install via GUI if missing).
- On Windows, you might need to run the script as Administrator the first time to set up the environment.
