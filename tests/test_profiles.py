import pytest
import argparse
from pathlib import Path
from syscheck.main import load_profile_file, create_profile_file

@pytest.fixture
def mock_profile_file(tmp_path) -> Path:
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    
    profile_path = profile_dir / "test.profile"
    profile_path.write_text("""
# This is a comment
host=acme.com
user=root
# This is a comment
services=httpd,sshd
    """.strip())

    return profile_path

def test_load_profile_file(monkeypatch, mock_profile_file):
    # Monkeypatch get_profile_dir() to point to temp dir
    monkeypatch.setattr("syscheck.main.get_profile_dir", lambda: mock_profile_file.parent)

    data = load_profile_file("test")

    assert data["host"] == "acme.com"
    assert data["user"] == "root"
    assert data["services"] == ["httpd", "sshd"]

def test_load_profile_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("syscheck.main.get_profile_dir", lambda: tmp_path)

    with pytest.raises(FileNotFoundError):
        load_profile_file("nonexistent")

def test_create_and_load_profile(tmp_path, monkeypatch):
    # Prepare a fake args namespace, including password which should be excluded
    args = argparse.Namespace(
        host="acme.com",
        user="root",
        os="ubuntu",
        services=["httpd", "sshd"],
        password="supersecret",
        createprofile=None,
        profile=None,
        key=None,
        domain=None,
        output=None
    )
    
    profile_name = "testprofile"

    # Monkeypatch get_profile_dir to point to tmp_path
    monkeypatch.setattr("syscheck.main.get_profile_dir", lambda: tmp_path)

    # Create profile file
    create_profile_file(profile_name, args)

    # Profile file path
    profile_file = tmp_path / f"{profile_name}.profile"
    assert profile_file.exists()

    # Read raw file content to assert password excluded
    content = profile_file.read_text()
    assert "password=" not in content

    # Load profile back
    loaded_data = load_profile_file(profile_name)

    # Confirm loaded values match expected (note services should be list)
    assert loaded_data["host"] == "acme.com"
    assert loaded_data["user"] == "root"
    assert loaded_data["os"] == "ubuntu"
    assert loaded_data["services"] == ["httpd", "sshd"]
