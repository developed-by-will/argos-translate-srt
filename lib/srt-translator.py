import os
import re
import sys
from pathlib import Path
from argostranslate import translate
import tkinter as tk
from tkinter import filedialog

class Colors:
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'

def setup_console():
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    files = filedialog.askopenfilenames(
        title="Select .srt file(s) to translate",
        filetypes=[("Subtitle files", "*.srt"), ("All files", "*.*")]
    )
    if not files:
        print(f"{Colors.RED}No files selected. Exiting.{Colors.END}")
        sys.exit(0)
    return [Path(f) for f in files]

def is_timing_line(line):
    return re.match(r'^\d+$|^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line.strip())

def translate_srt_content(content, translator):
    lines = content.split('\n')
    translated_lines = []
    for line in lines:
        if is_timing_line(line) or not line.strip():
            translated_lines.append(line)
        else:
            translated_lines.append(translator.translate(line))
    return '\n'.join(translated_lines)

def clean_filename(filename, target_lang_code):
    # Remove any existing language codes
    filename = re.sub(r'\.[a-z]{2,3}(?=\.srt$)', '', filename, flags=re.IGNORECASE)
    return filename.replace('.srt', f'.{target_lang_code}.srt')

def update_progress(current, total, filename):
    percent = int((current/total)*100)
    progress_bar = '[' + '#' * int(percent/2) + ' ' * (50 - int(percent/2)) + ']'
    sys.stdout.write(f"\r{Colors.BLUE}{progress_bar} {percent}% {filename[:30]+'...' if len(filename)>30 else filename}{Colors.END}")
    sys.stdout.flush()

def main():
    try:
        setup_console()
        
        installed_languages = translate.get_installed_languages()
        if len(installed_languages) < 2:
            print(f"{Colors.RED}Error: No language model installed.{Colors.END}")
            print(f"{Colors.YELLOW}Please install it through the GUI first.{Colors.END}")
            return
        
        en_to_pt = installed_languages[0].get_translation(installed_languages[1])
        target_lang_code = installed_languages[1].code  # Get the target language code
        
        # Get files from user selection
        srt_files = select_files()
        print(f"{Colors.YELLOW}Selected files:{Colors.END}")
        for f in srt_files:
            print(f"  - {f.name}")
        
        # Filter out files that already have the target language code
        srt_files = [f for f in srt_files if not f.name.lower().endswith(f'.{target_lang_code}.srt')]
        total_files = len(srt_files)
        
        if total_files == 0:
            print(f"{Colors.RED}No valid .srt files to translate (may already be translated){Colors.END}")
            return
        
        print(f"\nFound {total_files} files to translate\n")
        
        for i, filepath in enumerate(srt_files, 1):
            try:
                update_progress(i-1, total_files, filepath.name)
                content = filepath.read_text(encoding='utf-8')
                translated_content = translate_srt_content(content, en_to_pt)
                output_filename = clean_filename(filepath.name, target_lang_code)
                output_path = filepath.with_name(output_filename)
                output_path.write_text(translated_content, encoding='utf-8')
                sys.stdout.write('\r' + ' ' * 100 + '\r')
                print(f"{Colors.GREEN}✓ {output_path.name}{Colors.END}")
            except Exception as e:
                sys.stdout.write('\r' + ' ' * 100 + '\r')
                print(f"{Colors.RED}Error processing {filepath.name}: {str(e)}{Colors.END}")
        
        if total_files > 0:
            update_progress(total_files, total_files, "Complete!")
            print(f"\n\n{Colors.YELLOW}Translation complete!{Colors.END}")
    
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {str(e)}{Colors.END}")

if __name__ == "__main__":
    main()