import pytest
from unittest.mock import patch, MagicMock
from syscheck.main import create_connector
from syscheck.connectors.ssh import SSHConnection
from syscheck.connectors.winrm import WinRMConnection
import builtins
import os

def test_create_connector_with_ssh_key(tmp_path):
    key_file = tmp_path / "key.pem"
    key_file.write_text("fake key")

    args = MagicMock()
    args.key = str(key_file)
    args.host = "host"
    args.user = "user"
    args.os = "rhel"
    args.domain = None

    connector = create_connector(args)
    assert isinstance(connector, SSHConnection)

def test_create_connector_password_prompt(monkeypatch):
    args = MagicMock()
    args.key = None
    args.host = "host"
    args.user = "user"
    args.os = "windows"
    args.domain = "DOMAIN"

    monkeypatch.setattr("syscheck.main.getpass", lambda prompt: "password123")

    connector = create_connector(args)
    assert isinstance(connector, WinRMConnection)
    assert connector.password == "password123"

def test_create_connector_unsupported_os(monkeypatch):
    args = MagicMock()
    args.key = None
    args.host = "host"
    args.user = "user"
    args.os = "solaris"
    args.domain = None

    monkeypatch.setattr("syscheck.main.getpass", lambda prompt: "password123")

    with pytest.raises(ValueError):
        create_connector(args)

def test_create_connector_invalid_ssh_key_path(tmp_path, monkeypatch):
    fake_key_path = "~/fakekey"  # intentionally non-existent
    expanded_path = os.path.abspath(os.path.expanduser(fake_key_path))

    args = MagicMock()
    args.key = fake_key_path
    args.host = "host"
    args.user = "user"
    args.os = "rhel"
    args.domain = None

    with pytest.raises(FileNotFoundError) as exc_info:
        from syscheck.main import create_connector
        create_connector(args)

    assert str(exc_info.value).startswith("SSH key file not found")
    assert expanded_path in str(exc_info.value)
