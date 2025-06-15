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

    monkeypatch.setattr("syscheck.main.get_profile_dir", lambda: tmp_path)

    create_profile_file(profile_name, args)

    profile_file = tmp_path / f"{profile_name}.profile"
    assert profile_file.exists()

    content = profile_file.read_text()
    assert "password=" not in content

    loaded_data = load_profile_file(profile_name)

    assert loaded_data["host"] == "acme.com"
    assert loaded_data["user"] == "root"
    assert loaded_data["os"] == "ubuntu"
    assert loaded_data["services"] == ["httpd", "sshd"]
