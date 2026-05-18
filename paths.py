import os
import shutil
import sys


def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def _legacy_user_data_root() -> str:
    """Pre-rename per-user data root (the project was once called Turtle Race).

    Only used by the one-shot migration in `user_data_path`; never returned to
    callers directly.
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
        return os.path.join(base, "TurtleRace")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/TurtleRace")
    return os.path.join(
        os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
        "TurtleRace",
    )


def _migrate_legacy_file(new_root: str, filename: str) -> None:
    """Copy `filename` from the old TurtleRace data dir into the new one if needed.

    No-op when the new file already exists or the old one is absent. Best-effort:
    any OS error during the copy is swallowed so a broken migration never
    prevents the game from launching with a fresh leaderboard.
    """
    new_path = os.path.join(new_root, filename)
    if os.path.exists(new_path):
        return
    legacy_path = os.path.join(_legacy_user_data_root(), filename)
    if not os.path.isfile(legacy_path):
        return
    try:
        shutil.copy2(legacy_path, new_path)
    except OSError:
        pass


def user_data_path(filename: str) -> str:
    """Return the per-user app-data path for `filename` (created if needed).

    `filename` must be a bare basename (e.g. `"leaderboard.json"`). Raises
    `ValueError` if it contains a path separator or parent-traversal token.
    Never returns a path under `sys._MEIPASS`.
    """
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
        root = os.path.join(base, "ReptileRace")
    elif sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Application Support/ReptileRace")
    else:
        root = os.path.join(
            os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
            "ReptileRace",
        )
    os.makedirs(root, exist_ok=True)
    _migrate_legacy_file(root, filename)
    return os.path.join(root, filename)
