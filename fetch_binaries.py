from pathlib import Path
import urllib.request
import zipfile

def download(url: str, dest: Path):
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        f.write(r.read())


def main():
    base = Path(__file__).parent
    ytdlp = base / "yt-dlp.exe"
    if not ytdlp.exists():
        download("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", ytdlp)

    ffmpeg = base / "ffmpeg.exe"
    ffprobe = base / "ffprobe.exe"
    if not ffmpeg.exists() or not ffprobe.exists():
        tmp = base / "ffmpeg.zip"
        download("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip", tmp)
        with zipfile.ZipFile(tmp) as z:
            for m in z.namelist():
                if m.endswith("ffmpeg.exe"):
                    z.extract(m, base)
                    (base / m).rename(ffmpeg)
                if m.endswith("ffprobe.exe"):
                    z.extract(m, base)
                    (base / m).rename(ffprobe)
        tmp.unlink()

if __name__ == "__main__":
    main()
