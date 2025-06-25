# 🎬 Argos Translate SRT

> 🌍 Batch translation toolkit for SRT subtitles using Argos Translate

## ⚠️ Important Information

- 💻 **Only tested on Windows**
- 1️⃣ Designed to work with **single language model installations**
- 🐍 Does not support Python 3.13

## 🛠️ Requirements

- 🐍 **Python 3.12+** with PATH configured and with admin privileges when installing py.exe [Download here](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)

## ✨ Features

- 📁 One-click translation of entire subtitle folders
- ⏱️ Preserves SRT timing/metadata
- 📊 Progress tracking with visual feedback
- 🔍 Automatic language detection
- ⚡ Fast subsequent runs after initial setup

## How to use

1. Open `GUI.bat` and download the language model you will be using (download just one).
2. Open `translate.bat`.
3. Select the directory with the .srt files you want to translate.

Notes:

- The first run will be slower as it sets up the environment.
- The script will still need the language model installed (it prompts you to install via GUI if missing).
- On Windows, you might need to run the script as Administrator the first time to set up the environment.
