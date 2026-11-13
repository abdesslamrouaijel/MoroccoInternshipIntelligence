@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
) else (
  set "PYTHON=python"
)
"%PYTHON%" -m PyInstaller --noconfirm --clean --windowed --name MoroccoInternshipIntelligence --add-data "config;config" main.py
if errorlevel 1 pause
