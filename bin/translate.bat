@echo off
REM Enable ANSI color support
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%argos-env\Scripts\activate.bat"

:: Install required Python packages
python -c "import tkinter" || python -m pip install tk
python -c "import chardet" || python -m pip install chardet

python "%SCRIPT_DIR%..\lib\srt-translator.py"
pause