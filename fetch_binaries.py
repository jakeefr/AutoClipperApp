from pathlib import Path
import urllib.request
import zipfile
from typing import Iterable

def download(url: str, dest: Path) -> bool:
    """Download a single URL to ``dest``. Returns ``True`` on success."""
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
            f.write(r.read())
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def download_first(urls: Iterable[str], dest: Path) -> bool:
    """Try each URL until one succeeds."""
    for url in urls:
        if download(url, dest):
            return True
    return False


def main():
    base = Path(__file__).parent / "bin"
    base.mkdir(exist_ok=True)
    ytdlp = base / "yt-dlp.exe"
    if not ytdlp.exists():
        if not download("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", ytdlp):
            print("Failed to download yt-dlp. Place yt-dlp.exe in the bin folder manually.")
            return

    ffmpeg = base / "ffmpeg.exe"
    ffprobe = base / "ffprobe.exe"
    if not ffmpeg.exists() or not ffprobe.exists():
        tmp = base / "ffmpeg.zip"
        ffmpeg_sources = [
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip",
        ]
        if not download_first(ffmpeg_sources, tmp):
            print(
                "Failed to download ffmpeg. Place ffmpeg.exe and ffprobe.exe in the bin folder manually."
            )
            return
        with zipfile.ZipFile(tmp) as z:
            for m in z.namelist():
                if m.endswith("ffmpeg.exe"):
                    z.extract(m, base)
                    (base / m).rename(ffmpeg)
                if m.endswith("ffprobe.exe"):
                    z.extract(m, base)
                    (base / m).rename(ffprobe)
        # cleanup extracted directories
        for item in base.glob("ffmpeg-*"):
            if item.is_dir():
                for sub in item.rglob("*"):
                    if sub.is_file():
                        sub.unlink()
                subdirs = sorted([p for p in item.rglob("*") if p.is_dir()], reverse=True)
                for d in subdirs:
                    d.rmdir()
                item.rmdir()
        tmp.unlink()

if __name__ == "__main__":
    main()
