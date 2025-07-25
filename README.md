# AutoClipperApp

AutoClipper is a standalone Windows desktop application that downloads YouTube playlist videos and automatically clips them into segments of custom lengths. It includes both an Electron-based version and a Python GUI fallback.

![AutoClipper UI](https://github.com/user-attachments/assets/9a9fe75d-f218-4a7e-9e44-716b7e9e6145)

---

## Features

- Download full YouTube playlists using `yt-dlp`
- Automatically split videos into segments:
  - Options: 5s, 10s, 15s, 20s, 25s, 30s, 1m
- Clean, modern desktop UI (Electron)
- Optional standalone `.exe` version for Windows
- Python GUI fallback with `customtkinter`
- Automatic dependency handling:
  - Downloads `yt-dlp`, `ffmpeg`, and `ffprobe`
- Background processing with live task logging

---

## Usage

1. Paste your YouTube playlist URL into the app
2. Choose a segment length and video format (mp4/webm/mkv)
3. Click **Start** to begin download + clipping
4. Monitor progress in the log panel

---

## Output Location

Clips are saved to:

```
C:\Users\YourName\Videos\AutoClipperApp\
```

All videos and clips are placed directly inside this folder.

---

## Download

You can download the latest version of AutoClipper here:  
👉 [Download AutoClipper.exe](https://github.com/jakeefr/AutoClipperApp/releases/latest)

No Python or installation required — just download and run.

---

## Windows Standalone Executable

The repository includes a build script that creates `AutoClipper.exe` with no Python or npm installation required for end users.

### To Build the `.exe`:

1. Clone the repo  
2. Run:

```cmd
.\build_installer.bat
```

This bundles:

- All Python code via PyInstaller  
- All dependencies (`yt-dlp`, `ffmpeg`, `ffprobe`)  
- Output appears in the `dist/` directory as `AutoClipper.exe`

---

## Python GUI (Optional)

For testing or lightweight environments, a Python version is included using `customtkinter`.

### Run it with:

```bash
pip install -r requirements.txt
python -m app.main
```

---

## Binaries Storage

Auto-downloaded binaries are saved to:

```
D:\AutoClipper\bin  (preferred, if D:\ exists)
C:\AutoClipper\bin  (fallback)
```

These include:

- `yt-dlp.exe`
- `ffmpeg.exe`
- `ffprobe.exe`

---

## Requirements

- Windows 10 or 11  
- Internet connection (for dependencies and downloads)  
- 150MB+ free space for build and video files

---

## Development Stack

- Electron (TypeScript + Vite)  
- Python 3.x  
- `customtkinter`  
- `yt-dlp`, `ffmpeg`  
- PyInstaller (Windows packaging)

---

## Contributing

If you'd like to submit features, improvements, or bug fixes, feel free to open a pull request or file an issue.  
See full [Contributing Guidelines](CONTRIBUTING.md)

---

## License

Licensed under the [MIT License](LICENSE)

---

## Contact

[GitHub: jakeefr](https://github.com/jakeefr/AutoClipperApp)

