import os
import subprocess
import sys
import urllib.request
import zipfile
import json
import time
from pathlib import Path
from typing import Callable, Iterable


def _run_command(cmd: list[str], log_callback: Callable[[str], None] | None = None) -> tuple[int, str]:
    """Run a command without blocking the UI and optionally log each output line."""
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        creationflags=creationflags,
    )
    output_lines: list[str] = []
    if proc.stdout:
        while True:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                time.sleep(0.05)
                continue
            line = line.rstrip()
            if line:
                output_lines.append(line)
                if log_callback:
                    log_callback(line)
    proc.wait()
    return proc.returncode, "\n".join(output_lines)


def _download(url: str, dest: Path, log_callback: Callable[[str], None] | None = None) -> bool:
    """Download a URL to the given destination path. Returns True on success."""
    try:
        with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
            f.write(r.read())
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"Failed to download {url}: {e}")
        return False


def _download_first(urls: Iterable[str], dest: Path, log_callback: Callable[[str], None] | None = None) -> bool:
    for url in urls:
        if _download(url, dest, log_callback):
            return True
    return False


def ensure_binaries(base_dir: Path, log_callback: Callable[[str], None]) -> tuple[Path, Path]:
    """Ensure yt-dlp.exe, ffmpeg.exe and ffprobe.exe exist in a bin directory."""
    bin_dir = base_dir / "bin"
    bin_dir.mkdir(exist_ok=True)
    ytdlp = bin_dir / "yt-dlp.exe"
    ffmpeg = bin_dir / "ffmpeg.exe"
    ffprobe = bin_dir / "ffprobe.exe"

    if not ytdlp.exists():
        log_callback("Downloading yt-dlp...")
        if not _download(
            "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
            ytdlp,
            log_callback,
        ):
            raise RuntimeError(
                "Could not download yt-dlp. Place yt-dlp.exe in the bin folder and restart."
            )

    if not ffmpeg.exists() or not ffprobe.exists():
        log_callback("Downloading ffmpeg (this may take a while)...")
        zip_path = bin_dir / "ffmpeg.zip"
        ffmpeg_sources = [
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip",
        ]
        if _download_first(ffmpeg_sources, zip_path, log_callback):
            with zipfile.ZipFile(zip_path) as zf:
                for member in zf.namelist():
                    if member.endswith("ffmpeg.exe"):
                        zf.extract(member, bin_dir)
                        (bin_dir / member).rename(ffmpeg)
                        break
                for member in zf.namelist():
                    if member.endswith("ffprobe.exe"):
                        zf.extract(member, bin_dir)
                        (bin_dir / member).rename(ffprobe)
                        break
            # remove extracted directories
            for item in bin_dir.glob("ffmpeg-*"):
                if item.is_dir():
                    for sub in item.rglob("*"):
                        if sub.is_file():
                            sub.unlink()
                    subdirs = sorted([p for p in item.rglob("*") if p.is_dir()], reverse=True)
                    for d in subdirs:
                        d.rmdir()
                    item.rmdir()
        else:
            raise RuntimeError(
                "Could not download ffmpeg. Place ffmpeg.exe and ffprobe.exe in the bin folder and restart."
            )
        zip_path.unlink(missing_ok=True)

    return ytdlp, ffmpeg


def confirm_binaries(ytdlp: Path, ffmpeg: Path, log_callback: Callable[[str], None]) -> bool:
    """Run the binaries to ensure they work."""
    rc, _ = _run_command([str(ytdlp), "--version"], log_callback)
    if rc != 0:
        log_callback("yt-dlp failed to run")
        return False
    rc, _ = _run_command([str(ffmpeg), "-version"], log_callback)
    if rc != 0:
        log_callback("ffmpeg failed to run")
        return False
    return True


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
    """Download videos from the playlist and clip them.

    Returns a tuple of ``(clips_created, playlist_title, success_list, skipped_list)``.
    """
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    ytdlp_path, ffmpeg_path = ensure_binaries(base_dir, log_callback)
    if not confirm_binaries(ytdlp_path, ffmpeg_path, log_callback):
        raise RuntimeError("yt-dlp or ffmpeg failed to run. Please reinstall and try again.")

    # downloads only use public access; cookies are never loaded


    info_cmd = [
        str(ytdlp_path),
        url,
        "--skip-download",
        "--dump-json",
    ]
    rc, out = _run_command(info_cmd, log_callback)
    if rc != 0:
        log_callback(
            "Skipped: Requires login (private, age-restricted, or unavailable)"
        )
        return 0, url, [], []

    videos = []
    skipped: list[str] = []
    playlist_title = url
    for line in out.strip().splitlines():
        try:
            data = json.loads(line)
        except Exception:
            continue
        if "playlist_title" in data:
            playlist_title = data["playlist_title"] or playlist_title
        title = data.get("title") or data.get("id")
        vid_id = data.get("id")
        duration = int(float(data.get("duration") or 0))
        if not vid_id:
            continue
        if duration > 20 * 60:
            log_callback(f"Skipping {title} (longer than 20 min)")
            continue
        out_file = output_dir / f"{vid_id}.{format}"
        if out_file.exists():
            log_callback(f"Using cached {out_file.name}")
            videos.append((title, out_file))
            continue
        download_cmd = [
            str(ytdlp_path),
            f"https://www.youtube.com/watch?v={vid_id}",
            "-o", str(out_file),
            "-f", "bestvideo[ext=mp4]+bestaudio/best/best",
        ]
        log_callback(f"Downloading {title}")
        rc, _ = _run_command(download_cmd, log_callback)
        if rc != 0:
            # try fallback format
            fallback_cmd = download_cmd[:-2] + ["-f", "best"]
            rc, _ = _run_command(fallback_cmd, log_callback)
            if rc != 0:
                log_callback(
                    "Skipped: Requires login (private, age-restricted, or unavailable)"
                )
                skipped.append(f"{title} - login required")
                continue
        videos.append((title, out_file))

    clips_created = 0
    success: list[str] = []
    for title, video in videos:
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
            rc, _ = _run_command(ff_cmd, log_callback)
            if rc != 0:
                log_callback(f"❌ Skipped: {title} (ffmpeg error)")
                skipped.append(f"{title} - ffmpeg error")
                break
            start += clip_length
            clip_index += 1
            clips_created += 1
            if progress_callback and duration > 0:
                progress_callback(min(100, (start / duration) * 100))
        if delete_original:
            try:
                video.unlink()
            except Exception:
                pass
        else:
            success.append(video.stem)

    return clips_created, playlist_title, success, skipped


def get_duration(path: Path) -> int:
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    local_ffprobe = base_dir / "bin" / "ffprobe.exe"
    ffprobe_cmd = [str(local_ffprobe if local_ffprobe.exists() else "ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    rc, out = _run_command(ffprobe_cmd, None)
    if rc == 0:
        try:
            return int(float(out.strip()))
        except Exception:
            return 0
    return 0
