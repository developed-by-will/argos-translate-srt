@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%argos-env"

:: Enable ANSI colors
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

:: Create virtual environment if missing
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    echo Virtual environment created
)

:: Activate and install specific packages
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install argostranslate argostranslategui argos-translate-files

:: Launch GUI
python "%SCRIPT_DIR%argos-env\Scripts\argos-translate-gui"

pause