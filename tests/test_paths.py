import os
import sys

# Make project root importable when running pytest from any cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from paths import user_data_path


def test_user_data_path_windows_uses_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    result = user_data_path("leaderboard.json")
    assert result.startswith(str(tmp_path))
    expected_suffix = os.path.join("ReptileRace", "leaderboard.json")
    assert result.endswith(expected_suffix)


def _fake_expanduser(tmp_path):
    """Substitute ~ with tmp_path so test runs never touch the real home directory."""
    def _expand(p):
        if p.startswith("~"):
            return str(tmp_path) + p[1:]
        return p
    return _expand


def test_user_data_path_windows_falls_back_when_appdata_unset(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(os.path, "expanduser", _fake_expanduser(tmp_path))
    result = user_data_path("leaderboard.json")
    assert "ReptileRace" in result
    assert result.startswith(str(tmp_path))   # write landed under tmp_path, not real home


def test_user_data_path_macos(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(os.path, "expanduser", _fake_expanduser(tmp_path))
    result = user_data_path("leaderboard.json")
    # Use forward slashes: expanduser produces them on all OSes for the ~ portion.
    normalized = result.replace("\\", "/")
    assert "Library/Application Support/ReptileRace" in normalized
    assert result.startswith(str(tmp_path))   # write landed under tmp_path, not real home


def test_user_data_path_linux_uses_xdg(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    result = user_data_path("leaderboard.json")
    assert result.startswith(str(tmp_path))
    expected_suffix = os.path.join("ReptileRace", "leaderboard.json")
    assert result.endswith(expected_suffix)


def test_user_data_path_linux_falls_back_to_local_share(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(os.path, "expanduser", _fake_expanduser(tmp_path))
    result = user_data_path("leaderboard.json")
    # Use forward slashes: expanduser produces them on all OSes for the ~ portion.
    normalized = result.replace("\\", "/")
    assert ".local/share/ReptileRace" in normalized
    assert result.startswith(str(tmp_path))   # write landed under tmp_path, not real home


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
def test_user_data_path_never_under_meipass(monkeypatch, tmp_path, platform):
    # Regression guard: user_data_path must never consult sys._MEIPASS even
    # when set. The implementation must derive writable paths from per-user
    # locations only, never from the PyInstaller temp-unpack directory.
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(sys, "_MEIPASS", "/MEIPASS_SENTINEL", raising=False)
    # Provide a writable tmp_path so makedirs succeeds on each platform branch.
    monkeypatch.setattr(os.path, "expanduser", _fake_expanduser(tmp_path))
    if platform == "win32":
        monkeypatch.setenv("APPDATA", str(tmp_path))
    elif platform == "linux":
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    result = user_data_path("x")
    assert "MEIPASS_SENTINEL" not in result


def test_user_data_path_creates_parent_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    nested = tmp_path / "nested" / "dir"
    monkeypatch.setenv("XDG_DATA_HOME", str(nested))
    user_data_path("x")
    assert os.path.isdir(tmp_path / "nested" / "dir" / "ReptileRace")


# --- Filename validation (Phase 2 basename guard) ---

def test_user_data_path_rejects_path_separator():
    with pytest.raises(ValueError):
        user_data_path("subdir/x.txt")
    with pytest.raises(ValueError):
        user_data_path(f"subdir{os.sep}x.txt")


def test_user_data_path_rejects_parent_traversal():
    with pytest.raises(ValueError):
        user_data_path("../evil")
    with pytest.raises(ValueError):
        user_data_path("..")
