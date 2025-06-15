import builtins
import pytest
from unittest.mock import patch, MagicMock
from syscheck.main import main

def test_interactive_prompt_for_linux_required_inputs(monkeypatch):
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        if "Host" in prompt:
            return "example.com"
        elif "username" in prompt:
            return "testuser"
        elif "OS" in prompt:
            return "rhel"
        return ""

    # Monkeypatch input() and getpass
    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("getpass.getpass", lambda _: "fakepassword")

    # Simulate running with no CLI args
    monkeypatch.setattr("sys.argv", ["syscheck"])

    # Patch create_connector and gather_info to prevent side effects
    with patch("syscheck.main.create_connector") as mock_connector, \
         patch("syscheck.main.gather_info", return_value={"test": "ok"}):

        mock_connector_instance = MagicMock()
        mock_connector_instance.connect.return_value = True
        mock_connector.return_value = mock_connector_instance

        main()

    # Assertions
    assert any("Host" in prompt for prompt in prompts), "Host prompt not found"
    assert any("username" in prompt for prompt in prompts), "Username prompt not found"
    assert any("OS" in prompt for prompt in prompts), "OS prompt not found"

def test_interactive_prompt_for_windows_required_inputs(monkeypatch):
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        if "Host" in prompt:
            return "example.com"
        elif "username" in prompt:
            return "testuser"
        elif "OS" in prompt:
            return "windows"
        elif "Domain" in prompt:
            return "ACMECORP"
        return ""

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("getpass.getpass", lambda _: "fakepassword")
    monkeypatch.setattr("sys.argv", ["syscheck"])

    with patch("syscheck.main.create_connector") as mock_connector, \
         patch("syscheck.main.gather_info", return_value={"test": "ok"}):

        mock_connector_instance = MagicMock()
        mock_connector_instance.connect.return_value = True
        mock_connector.return_value = mock_connector_instance

        main()

    assert any("Host" in prompt for prompt in prompts), "Host prompt not found"
    assert any("username" in prompt for prompt in prompts), "Username prompt not found"
    assert any("OS" in prompt for prompt in prompts), "OS prompt not found"
    assert any("Domain" in prompt for prompt in prompts), "Domain prompt not found"