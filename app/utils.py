from pathlib import Path
import os
import sys


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_folder() -> Path:
    """Return the consistent output folder for clips."""
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Videos" / "AutoClipperApp"
    else:
        base = Path.home() / "Videos" / "AutoClipperApp"
    return ensure_dir(base)
