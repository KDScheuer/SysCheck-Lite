import pytest
from unittest.mock import patch, MagicMock
from syscheck.connectors.winrm import WinRMConnection 


@pytest.fixture
def mock_winrm_session():
    with patch("winrm.Session") as mock_session:
        yield mock_session


def test_connect_success_without_domain(mock_winrm_session):
    mock_client = MagicMock()
    mock_client.run_cmd.return_value = None
    mock_winrm_session.return_value = mock_client

    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret", domain=None)
    assert conn.connect() is True

    mock_winrm_session.assert_called_once_with(
        "http://1.2.3.4:5985/wsman",
        auth=("testuser", "secret"),
        transport="ntlm",
    )
    mock_client.run_cmd.assert_called_once_with("whoami")


def test_connect_success_with_domain(mock_winrm_session):
    mock_client = MagicMock()
    mock_client.run_cmd.return_value = None
    mock_winrm_session.return_value = mock_client

    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret", domain="MYDOMAIN")
    assert conn.connect() is True

    mock_winrm_session.assert_called_once_with(
        "http://1.2.3.4:5985/wsman",
        auth=("MYDOMAIN\\testuser", "secret"),
        transport="kerberos",
    )
    mock_client.run_cmd.assert_called_once_with("whoami")


def test_connect_raises_connection_error(mock_winrm_session):
    mock_winrm_session.side_effect = Exception("Connection failed")

    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret")

    with pytest.raises(ConnectionError) as excinfo:
        conn.connect()

    assert "Failed to connect" in str(excinfo.value)


def test_run_command_success(mock_winrm_session):
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.std_out = b"output from command\n"
    mock_client.run_ps.return_value = mock_result
    mock_winrm_session.return_value = mock_client

    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret")
    conn.client = mock_client

    output = conn.run_command("Get-Process")
    assert output == "output from command"


def test_run_command_returns_error_collecting_if_empty_stdout(mock_winrm_session):
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.std_out = b""
    mock_client.run_ps.return_value = mock_result
    mock_winrm_session.return_value = mock_client

    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret")
    conn.client = mock_client

    output = conn.run_command("Get-Process")
    assert output == "Error Collecting"


def test_run_command_returns_error_collecting_on_exception(mock_winrm_session):
    mock_client = MagicMock()
    mock_client.run_ps.side_effect = Exception("Execution failed")
    mock_winrm_session.return_value = mock_client

    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret")
    conn.client = mock_client

    output = conn.run_command("Get-Process")
    assert output == "ERROR_COLLECTING"


def test_run_command_raises_if_not_connected():
    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret")
    conn.client = None

    with pytest.raises(RuntimeError) as excinfo:
        conn.run_command("Get-Process")

    assert "WinRM client not connected" in str(excinfo.value)


def test_close_resets_client(mock_winrm_session):
    conn = WinRMConnection(host="1.2.3.4", user="testuser", password="secret")
    conn.client = MagicMock()

    conn.close()
    assert conn.client is None
