# YouTube Playlist Auto-Clipper

A desktop application that downloads YouTube playlist videos and clips them into segments of specified lengths.

This repository now includes a lightweight Python GUI built with `customtkinter` that mirrors the Electron version's functionality.

## Features

- Download videos from YouTube playlists using yt-dlp
- Clip videos into segments of specified lengths (5s, 10s, 15s, 20s, 25s, 30s, 1m)
- Modern, responsive UI built with web technologies
- Automatic dependency management (yt-dlp and ffmpeg)
- Background processing to keep UI responsive
- Detailed progress logging

## Usage

1. Enter a YouTube playlist URL in the input field
2. Select your desired clip length from the dropdown
3. Click "Start Clipping" to begin the process
4. Monitor progress in the log viewer

## Output

All downloaded videos and clips are saved to:
`C:\Users\YourName\Videos\AutoClipper_YYYY-MM-DD_HH-MM-SS\`

Each video gets its own subfolder inside the session directory.

## Dependencies

The application automatically downloads and manages:
- yt-dlp.exe from GitHub
- ffmpeg.exe from gyan.dev

These are stored in:
- D:\AutoClipper\bin (if D: drive exists)
- C:\AutoClipper\bin (fallback)

## System Requirements

- Windows 10 or 11
- Internet connection for downloading videos and dependencies

## Development

This application is built with:
- Electron
- TypeScript
- Vite

To build from source:
```
npm install
npm run make
```

### Python GUI

The `app/` directory contains a `customtkinter` version. Install the requirements and run `python -m app.main`:

```bash
pip install -r requirements.txt
python -m app.main
```

## Support

For issues or feature requests, please contact [github.com/jakeefr]
