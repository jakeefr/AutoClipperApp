@echo off
REM Build AutoClipper Windows executable
python -m pip install --upgrade pyinstaller >nul
python fetch_binaries.py
pyinstaller --onefile --noconsole --add-data "bin\\ffmpeg.exe;bin" --add-data "bin\\ffprobe.exe;bin" --add-data "bin\\yt-dlp.exe;bin" --hidden-import customtkinter --name AutoClipper app\main.py --distpath dist
