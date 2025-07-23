import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable


def _download(url: str, dest: Path) -> None:
    """Download a URL to the given destination path."""
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        f.write(r.read())


def ensure_binaries(base_dir: Path, log_callback: Callable[[str], None]) -> tuple[Path, Path]:
    """Ensure yt-dlp.exe, ffmpeg.exe and ffprobe.exe exist, downloading them if necessary."""
    ytdlp = base_dir / "yt-dlp.exe"
    ffmpeg = base_dir / "ffmpeg.exe"
    ffprobe = base_dir / "ffprobe.exe"

    if not ytdlp.exists():
        log_callback("Downloading yt-dlp...")
        _download(
            "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
            ytdlp,
        )

    if not ffmpeg.exists() or not ffprobe.exists():
        log_callback("Downloading ffmpeg (this may take a while)...")
        zip_path = base_dir / "ffmpeg.zip"
        _download(
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            zip_path,
        )
        with zipfile.ZipFile(zip_path) as zf:
            for member in zf.namelist():
                if member.endswith("ffmpeg.exe"):
                    zf.extract(member, base_dir)
                    (base_dir / member).rename(ffmpeg)
                    break
            for member in zf.namelist():
                if member.endswith("ffprobe.exe"):
                    zf.extract(member, base_dir)
                    (base_dir / member).rename(ffprobe)
                    break
        zip_path.unlink(missing_ok=True)

    return ytdlp, ffmpeg


def download_and_clip_playlist(
    url: str,
    output_dir: Path,
    clip_length: int,
    log_callback: Callable[[str], None],
    mute: bool = False,
    delete_original: bool = False,
    format: str = "mp4",
    progress_callback: Callable[[float], None] | None = None,
):
    """Download videos from the playlist and clip them."""
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    ytdlp_path, ffmpeg_path = ensure_binaries(base_dir, log_callback)

    session_dir = output_dir / "session"
    session_dir.mkdir(exist_ok=True)

    cmd = [
        str(ytdlp_path),
        url,
        "-f", "bestvideo[ext=mp4]+bestaudio/best",
        "--no-playlist",  # will iterate manually
        "--print", "%(title)s|%(id)s|%(duration)s|%(ext)s|%(filename)s",
        "--skip-download",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    videos = []
    for line in proc.stdout.strip().splitlines():
        try:
            title, vid_id, duration, ext, filename = line.split("|")
        except ValueError:
            continue
        if int(float(duration)) > 20 * 60:
            log_callback(f"Skipping {title} (longer than 20 min)")
            continue
        out_file = session_dir / f"{vid_id}.{format}"
        if out_file.exists():
            log_callback(f"Using cached {out_file.name}")
            videos.append(out_file)
            continue
        download_cmd = [
            str(ytdlp_path),
            f"https://www.youtube.com/watch?v={vid_id}",
            "-o", str(out_file),
        ]
        log_callback(f"Downloading {title}")
        subprocess.run(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        videos.append(out_file)

    for video in videos:
        log_callback(f"Clipping {video.name}")
        clip_index = 0
        duration = get_duration(video)
        start = 0
        while start < duration:
            end = min(start + clip_length, duration)
            clip_file = video.with_name(f"{video.stem}_{clip_index}.{format}")
            ff_cmd = [
                str(ffmpeg_path),
                "-y",
                "-i",
                str(video),
                "-ss", str(start),
                "-t", str(end - start),
            ]
            if mute:
                ff_cmd += ["-an"]
            ff_cmd += [str(clip_file)]
            subprocess.run(ff_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            start += clip_length
            clip_index += 1
            if progress_callback and duration > 0:
                progress_callback(min(100, (start / duration) * 100))
        if delete_original:
            try:
                video.unlink()
            except Exception:
                pass


def get_duration(path: Path) -> int:
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    local_ffprobe = base_dir / "ffprobe.exe"
    ffprobe_cmd = [str(local_ffprobe if local_ffprobe.exists() else "ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    try:
        out = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT, text=True)
        return int(float(out.strip()))
    except Exception:
        return 0
