import os
import sys


def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def user_data_path(filename: str) -> str:
    # Reject any filename containing a path separator or parent-traversal token.
    # Callers must pass a bare basename (e.g. "leaderboard.json"); sanitization is
    # harder to reason about than rejection, so we reject and let the caller fix
    # the call site. Guards against accidental misuse by future callers.
    if (
        os.path.basename(filename) != filename
        or filename in (".", "..")
        or os.sep in filename
        or (os.altsep is not None and os.altsep in filename)
    ):
        raise ValueError(
            f"user_data_path requires a bare filename (no path separators or traversal), got: {filename!r}"
        )
    # This function intentionally never references sys._MEIPASS.
    # user_data_path() is for writable per-user state (e.g. leaderboard.json),
    # not bundled read-only assets.  Writable files must never live inside the
    # PyInstaller temp-unpack directory (_MEIPASS), which is ephemeral and
    # read-only in the frozen exe.
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
        root = os.path.join(base, "TurtleRace")
    elif sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Application Support/TurtleRace")
    else:
        root = os.path.join(
            os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
            "TurtleRace",
        )
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, filename)
