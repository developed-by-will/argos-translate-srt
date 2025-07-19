# 🎬 Argos Translate SRT

> 🌍 Batch translation toolkit for SRT subtitles using Argos Translate

## ⚠️ Important Information

- 💻 **Only tested on Windows**
- 🐍 **Only supports Python up to version 3.12.x**

## 🛠️ Requirements

- 🐍 **Python 3.12+** with PATH configured and with admin privileges when installing py.exe [Download here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)

## ✨ Features

- 📁 Translate one or multiple .srt files at a time
- 1️⃣ Works with multiple language model installations
- ⏱️ Preserves SRT timing/metadata
- 📊 Progress tracking with visual feedback
- 🔍 Automatic language code detection
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
