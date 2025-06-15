import pytest
import re
import json
from syscheck.formatter.TerminalFormatter import to_terminal 
from syscheck.formatter.jsonFormatter import to_json
from syscheck.formatter.htmlFormatter import to_html
import os
import tempfile
from unittest.mock import patch


def strip_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def test_to_terminal_complex_output(capfd):
    results = {
        "Hostname": "test-rocky",
        "Uptime": "up 5 hours, 1 minute",
        "OS Version": '"Rocky Linux 9.6 (Blue Onyx)"',
        "Kernel": "5.14.0-570.18.1.el9_6.x86_64",
        "CPU Usage": "3.1% used",
        "Memory Usage": "5.73% used",
        "Swap Usage": "0.00% used",
        "Last Update": "2025-06-15 03:37:47.638780343 +0000",
        "TimeZone": "Etc/GMT",
        "SELinux Status": "Enforcing",
        "Disk usage": [
            "Filesystem                Size  Used Avail Use% Mounted on",
            "devtmpfs                  4.0M     0  4.0M   0% /dev",
            "tmpfs                     3.8G     0  3.8G   0% /dev/shm",
            "/dev/mapper/rl_vbox-root   17G  1.6G   16G   9% /",
            "/dev/sda1                 960M  337M  624M  36% /boot",
            "tmpfs                     769M     0  769M   0% /run/user/0"
        ],
        "Last 10 journalctl errors": [
            "Jun 14 23:52:56 test-rocky kernel: Warning: Deprecated Hardware ...",
            "Jun 14 23:52:56 test-rocky kernel: RETBleed: WARNING: Spectre v2 ...",
            "Jun 14 23:52:57 test-rocky systemd[1]: Invalid DMI field header."
        ],
        "Services": {
            "sshd": "active",
            "firewalld": "active"
        }
    }

    to_terminal(results)

    captured = capfd.readouterr()
    clean_output = strip_ansi_codes(captured.out)

    assert "System Info:" in clean_output
    assert "Hostname: test-rocky" in clean_output
    assert "Disk usage:" in clean_output
    assert "tmpfs                     3.8G     0  3.8G   0% /dev/shm" in clean_output
    assert "Services:" in clean_output
    assert "sshd" in clean_output
    assert "firewalld" in clean_output

def test_to_json_output(capfd):
    results = {
        "Hostname": "test-rocky",
        "Uptime": "up 5 hours, 1 minute",
        "Services": {
            "sshd": "active",
            "firewalld": "active"
        }
    }

    to_json(results)
    captured = capfd.readouterr()
    
    try:
        parsed = json.loads(captured.out)
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")

    assert parsed == results

    lines = captured.out.splitlines()
    assert lines[0] == "{"
    assert lines[1].startswith('    "Hostname":')

def test_to_html_creates_file_and_opens_browser(tmp_path):
    results = {
        "Hostname": "test-rocky",
        "Uptime": "up 5 hours, 1 minute",
        "Services": {
            "sshd": "active",
            "firewalld": "active"
        }
    }
    host = "test-rocky"

    with patch("webbrowser.open") as mock_open:
        to_html(results, host)

        mock_open.assert_called_once()
        
        file_url = mock_open.call_args[0][0]
        assert file_url.startswith("file://")

        file_path = file_url[len("file://"):]

        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert "<html>" in html_content
        assert f"System Info: {host}" in html_content
        assert "<strong>Hostname</strong>" in html_content
        assert "<strong>Uptime</strong>" in html_content
        assert "<strong>Services</strong>" in html_content
        assert "sshd" in html_content
        assert "firewalld" in html_content

        os.remove(file_path)