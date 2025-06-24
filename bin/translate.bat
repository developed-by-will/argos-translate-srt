@echo off
REM Enable ANSI color support
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

set "SCRIPT_DIR=%~dp0"
call "%SCRIPT_DIR%argos-env\Scripts\activate.bat"

:: Install tkinter if missing
python -c "import tkinter" || python -m pip install tk

python "%SCRIPT_DIR%script.py"
pause