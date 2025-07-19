import re
import sys
from pathlib import Path
from argostranslate import translate
import tkinter as tk
from tkinter import filedialog
import argostranslate.package
import chardet

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

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        rawdata = f.read(10000)  # Read first 10k bytes to guess encoding
    result = chardet.detect(rawdata)
    return result['encoding'] if result['confidence'] > 0.7 else None

def select_files():
    root = tk.Tk()
    root.withdraw()
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

def clean_text(line):
    """Remove ALL HTML tags, hyphens, and square brackets"""
    line = re.sub(r'<[^>]+>', '', line)  # Remove ALL HTML tags
    line = re.sub(r'^-\s*', '', line)    # Remove leading hyphens
    line = re.sub(r'\[.*?\]', '', line)  # Remove square bracket content
    return line.strip()

def get_available_pairs(installed_languages):
    """Check actual installed packages on disk"""
    available_pairs = []
    installed_codes = {lang.code for lang in installed_languages}
    
    # Get installed packages from Argos Translate
    packages = argostranslate.package.get_installed_packages()
    
    for pkg in packages:
        from_code = pkg.from_code
        to_code = pkg.to_code
        
        if from_code in installed_codes and to_code in installed_codes:
            available_pairs.append(f"{from_code} → {to_code}")
    
    return available_pairs

def select_translation_direction(installed_languages):
    print("\nAvailable language pairs:")
    pairs = get_available_pairs(installed_languages)
    
    if not pairs:
        print(f"{Colors.RED}No valid translation pairs found!{Colors.END}")
        sys.exit(1)
    
    for i, pair in enumerate(sorted(pairs), 1):
        print(f"{i}. {pair}")
    
    while True:
        try:
            choice = int(input("\nSelect language pair (number): ")) - 1
            selected_pair = sorted(pairs)[choice]
            from_code, to_code = selected_pair.split(" → ")
            
            from_lang = next(lang for lang in installed_languages if lang.code == from_code)
            to_lang = next(lang for lang in installed_languages if lang.code == to_code)
            
            return from_lang.get_translation(to_lang), to_code
        
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid selection. Please try again.{Colors.END}")

def translate_srt_content(content, translator):
    lines = content.split('\n')
    translated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if is_timing_line(line):
            translated_lines.append(line)
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() and not is_timing_line(lines[i]):
                cleaned_line = clean_text(lines[i])
                if cleaned_line:
                    text_lines.append(cleaned_line)
                i += 1
            if text_lines:
                text_to_translate = ' '.join(text_lines)
                translated_text = translator.translate(text_to_translate)
                
                # Remove unwanted additions
                translated_text = re.sub(r'\* I\'m sorry \*|\.{3,}$', '', translated_text).strip()
                translated_lines.append(translated_text)
        else:
            translated_lines.append(line)
            i += 1
    return '\n'.join(translated_lines)

def clean_filename(filename, target_lang_code):
    filename = re.sub(r'(\.[a-z]{2,3})?\.srt$', f'.{target_lang_code}.srt', filename, flags=re.IGNORECASE)
    return filename

def update_progress(current, total, filename):
    percent = int((current/total)*100)
    progress_bar = '[' + '#' * int(percent/2) + ' ' * (50 - int(percent/2)) + ']'
    sys.stdout.write(f"\r{Colors.BLUE}{progress_bar} {percent}% {filename[:30]+'...' if len(filename)>30 else filename}{Colors.END}")
    sys.stdout.flush()

def clean_srt_whitespace(content):
    lines = content.splitlines()
    cleaned_lines = [line.strip() for line in lines]
    return '\n'.join(cleaned_lines) + '\n'

def main():
    try:
        setup_console()
        
        installed_languages = translate.get_installed_languages()
        if len(installed_languages) < 2:
            print(f"{Colors.RED}Error: Need at least 2 language models installed.{Colors.END}")
            print(f"{Colors.YELLOW}Please install language models first.{Colors.END}")
            return
        
        translator, target_lang_code = select_translation_direction(installed_languages)
        
        srt_files = select_files()
        print(f"{Colors.YELLOW}Selected files:{Colors.END}")
        for f in srt_files:
            print(f"  - {f.name}")
        
        srt_files = [f for f in srt_files 
                    if f.suffix.lower() == '.srt' 
                    and not f.name.lower().endswith(f'.{target_lang_code}.srt')]
        
        total_files = len(srt_files)
        
        if total_files == 0:
            print(f"{Colors.RED}No valid .srt files to translate (may already be translated){Colors.END}")
            print(f"{Colors.YELLOW}Target language code: {target_lang_code}{Colors.END}")
            return
        
        print(f"\nFound {total_files} files to translate\n")
        
        for i, filepath in enumerate(srt_files, 1):
            try:
                update_progress(i-1, total_files, filepath.name)
                
                # Detect and handle file encoding
                encoding = detect_encoding(filepath)
                if not encoding:
                    encoding = 'utf-8'  # fallback
                
                # Try reading with detected encoding, then common alternatives
                content = None
                for enc in [encoding, 'utf-8', 'latin-1', 'windows-1252']:
                    try:
                        content = filepath.read_text(encoding=enc)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise UnicodeDecodeError(f"Could not decode {filepath.name} with any supported encoding")
                
                translated_content = translate_srt_content(content, translator)
                cleaned_translated = clean_srt_whitespace(translated_content)
                
                output_filename = clean_filename(filepath.name, target_lang_code)
                output_path = filepath.with_name(output_filename)
                output_path.write_text(cleaned_translated, encoding='utf-8')
                
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