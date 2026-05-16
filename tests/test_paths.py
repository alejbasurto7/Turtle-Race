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
    expected_suffix = os.path.join("TurtleRace", "leaderboard.json")
    assert result.endswith(expected_suffix)


def test_user_data_path_windows_falls_back_when_appdata_unset(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.delenv("APPDATA", raising=False)
    result = user_data_path("leaderboard.json")
    assert "TurtleRace" in result


def test_user_data_path_macos(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    result = user_data_path("leaderboard.json")
    # Use forward slashes: expanduser produces them on all OSes for the ~ portion.
    normalized = result.replace("\\", "/")
    assert "Library/Application Support/TurtleRace" in normalized


def test_user_data_path_linux_uses_xdg(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    result = user_data_path("leaderboard.json")
    assert result.startswith(str(tmp_path))
    expected_suffix = os.path.join("TurtleRace", "leaderboard.json")
    assert result.endswith(expected_suffix)


def test_user_data_path_linux_falls_back_to_local_share(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    result = user_data_path("leaderboard.json")
    # Use forward slashes: expanduser produces them on all OSes for the ~ portion.
    normalized = result.replace("\\", "/")
    assert ".local/share/TurtleRace" in normalized


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
def test_user_data_path_never_under_meipass(monkeypatch, tmp_path, platform):
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(sys, "_MEIPASS", "/MEIPASS_SENTINEL", raising=False)
    # Provide a writable tmp_path so makedirs succeeds on each platform branch.
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
    assert os.path.isdir(tmp_path / "nested" / "dir" / "TurtleRace")
