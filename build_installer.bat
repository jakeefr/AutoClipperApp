@echo off
REM Build AutoClipper Windows executable
python -m pip install --upgrade pyinstaller >nul
python fetch_binaries.py
pyinstaller --onefile --noconsole --add-data "ffmpeg.exe;." --add-data "ffprobe.exe;." --add-data "yt-dlp.exe;." --hidden-import customtkinter --name AutoClipper app\main.py --distpath dist
