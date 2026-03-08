import re
import sys
import json
import subprocess
from pathlib import Path
from argostranslate import translate
import tkinter as tk
from tkinter import filedialog
import argostranslate.package
import chardet
import pycountry

# -------------------------
# COLORS & CONSOLE
# -------------------------
class Colors:
    YELLOW = '\033[93m'
    GREEN  = '\033[92m'
    BLUE   = '\033[94m'
    RED    = '\033[91m'
    END    = '\033[0m'

TEXT_SUB_CODECS = {"subrip", "ass", "ssa", "mov_text", "text", "webvtt"}
SUB_FILE_EXTENSIONS = [".srt", ".ass", ".ssa", ".vtt", ".txt"]

def setup_console():
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def update_progress(current, total, name):
    percent = int((current / total) * 100)
    bar = "[" + "#" * int(percent/2) + " " * (50 - int(percent/2)) + "]"
    sys.stdout.write(f"\r{Colors.BLUE}{bar} {percent}% {name[:30]}{Colors.END}")
    sys.stdout.flush()

# -------------------------
# LANGUAGE NORMALIZATION
# -------------------------
def normalize_lang(code):
    code = code.lower()
    if len(code) == 2:
        return code
    try:
        lang = pycountry.languages.get(alpha_3=code)
        if lang and hasattr(lang, "alpha_2"):
            return lang.alpha_2.lower()
    except KeyError:
        pass
    return code

# -------------------------
# FILE DIALOGS
# -------------------------
def file_dialog(title, types):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    files = filedialog.askopenfilenames(title=title, filetypes=types)
    root.attributes('-topmost', False)
    return [Path(f) for f in files]

def select_subtitle_files():
    files = file_dialog(
        "Select subtitle files",
        [("Subtitle files","*.srt *.ass *.ssa *.vtt *.txt"), ("All files","*.*")]
    )
    if not files:
        print(f"{Colors.RED}No files selected.{Colors.END}")
        sys.exit()
    return files

def select_video_files():
    return file_dialog(
        "Select video files",
        [("Video files","*.mkv *.mp4 *.avi *.mov"), ("All files","*.*")]
    )

# -------------------------
# ENCODING DETECTION
# -------------------------
def detect_encoding(file):
    with open(file,'rb') as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result['encoding'] if result['confidence'] > 0.7 else "utf-8"

# -------------------------
# SUBTITLE STREAM DETECTION
# -------------------------
def get_subtitle_streams(video):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index,codec_name:stream_tags=language",
        "-of", "json",
        str(video)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
    except:
        return []
    streams = []
    for stream in data.get("streams", []):
        codec = stream.get("codec_name", "unknown")
        if codec not in TEXT_SUB_CODECS:
            continue
        index = stream["index"]
        lang = stream.get("tags", {}).get("language", "unknown")
        streams.append((index, normalize_lang(lang), codec))
    return streams

# -------------------------
# SUBTITLE EXTRACTION
# -------------------------
def extract_subtitles():
    videos = select_video_files()
    if not videos:
        print(f"{Colors.YELLOW}No videos selected.{Colors.END}")
        return [], set()

    total = len(videos)
    extracted_files = []
    extracted_langs = set()
    print(f"\nExtracting subtitles from {total} video(s)\n")

    for i, video in enumerate(videos, 1):
        update_progress(i-1, total, video.name)
        streams = get_subtitle_streams(video)
        if not streams:
            sys.stdout.write('\r'+' '*100+'\r')
            print(f"{Colors.RED}The video does not contain any subtitles.{Colors.END}")
            input("Press any key to close...")
            sys.exit()
        out_dir = video.parent / "extracted subs"
        out_dir.mkdir(exist_ok=True)
        for index, lang, codec in streams:
            extracted_langs.add(lang)
            out_file = out_dir / f"{video.stem}.{lang}.srt"
            cmd = ["ffmpeg","-y","-i",str(video),"-map",f"0:{index}","-c:s","srt",str(out_file)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out_file.exists():
                extracted_files.append(out_file)
        sys.stdout.write('\r'+' '*100+'\r')
        print(f"{Colors.GREEN}✓ {video.name}{Colors.END}")
    update_progress(total, total, "Complete")
    print(f"\n\n{Colors.YELLOW}Extraction complete!{Colors.END}")
    return extracted_files, extracted_langs

# -------------------------
# TRANSLATION
# -------------------------
def is_timing(line):
    return re.match(r'^\d+$|^\d{2}:\d{2}:\d{2},', line.strip()) or line.strip().startswith("Dialogue:")

def clean_text(line):
    line = re.sub(r'<[^>]+>', '', line)
    line = re.sub(r'^-\s*', '', line)
    line = re.sub(r'\[.*?\]', '', line)
    return line

def get_pairs(langs):
    installed = {l.code for l in langs}
    pairs = []
    for pkg in argostranslate.package.get_installed_packages():
        if pkg.from_code in installed and pkg.to_code in installed:
            pairs.append(f"{pkg.from_code} → {pkg.to_code}")
    return pairs

def choose_translation(langs):
    pairs = sorted(get_pairs(langs))
    if not pairs:
        print("No translation pairs installed")
        sys.exit()
    print("\nWhich language pair are you looking for?")
    for i, p in enumerate(pairs, 1):
        print(f"{i}. {p}")
    while True:
        try:
            choice = int(input("\nSelect: ")) - 1
            pair = pairs[choice]
            f, t = pair.split(" → ")
            from_lang = next(l for l in langs if l.code == f)
            to_lang = next(l for l in langs if l.code == t)
            return from_lang.get_translation(to_lang), f, t
        except:
            print("Invalid selection")

def translate_subtitles(files=None):
    langs = translate.get_installed_languages()
    if len(langs) < 2:
        print("Need 2 language models installed.")
        return
    translator, source_lang, target_lang = choose_translation(langs)
    if files is None:
        files = select_subtitle_files()
    total = len(files)
    print(f"\nTranslating {total} files\n")
    for i, file in enumerate(files, 1):
        update_progress(i-1, total, file.name)
        enc = detect_encoding(file)
        content = file.read_text(encoding=enc, errors="ignore")
        lines = content.split("\n")
        out = []
        i2 = 0
        while i2 < len(lines):
            line = lines[i2]
            if is_timing(line):
                out.append(line)
                i2 += 1
                block = []
                while i2 < len(lines) and lines[i2].strip() and not is_timing(lines[i2]):
                    txt = clean_text(lines[i2])
                    if txt.strip():
                        block.append(txt)
                    i2 += 1
                if block:
                    text = " ".join(block)
                    translated = translator.translate(text).strip()
                    out.append(translated)
            else:
                out.append(line)
                i2 += 1
        result = "\n".join(out)
        new_name = re.sub(r'(\.[a-z]{2,3})?(\.srt|\.ass|\.ssa|\.vtt|\.txt)$',
                          f'.{target_lang}.srt', file.name, flags=re.I)
        file.with_name(new_name).write_text(result, encoding="utf-8")
        sys.stdout.write('\r'+' '*100+'\r')
        print(f"{Colors.GREEN}✓ {new_name}{Colors.END}")
    update_progress(total, total, "Complete")
    print(f"\n\n{Colors.YELLOW}Translation complete!{Colors.END}")

# -------------------------
# MAIN
# -------------------------
def main():
    setup_console()
    print("\n1. Translate subtitle files")
    print("2. Extract subtitles from videos")
    choice = input("\nSelect option: ")
    if choice == "1":
        translate_subtitles()
    elif choice == "2":
        langs = translate.get_installed_languages()
        translator, source_lang, target_lang = choose_translation(langs)
        extracted_files, extracted_langs = extract_subtitles()
        if not extracted_files:
            return
        source_lang = normalize_lang(source_lang)
        target_lang = normalize_lang(target_lang)
        if source_lang in extracted_langs and target_lang in extracted_langs:
            print(f"\n{Colors.GREEN}Subtitles were extracted for {source_lang.upper()} and {target_lang.upper()}, no need to translate.{Colors.END}")
            input("Press any key to close...")
            return
        if source_lang in extracted_langs and target_lang not in extracted_langs:
            print(f"\n{Colors.YELLOW}{target_lang.upper()} version was missing, do you want to translate? (y/n){Colors.END}")
            answer = input("> ").lower()
            if answer == "y":
                translate_subtitles(extracted_files)
        else:
            print(f"\n{Colors.RED}Expected source language ({source_lang.upper()}) was not found in extracted subtitles.{Colors.END}")
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()