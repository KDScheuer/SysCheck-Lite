import pytest
from unittest.mock import patch, MagicMock, call
from syscheck.connectors.ssh import SSHConnection


@pytest.fixture
def mock_sshclient():
    with patch("paramiko.SSHClient") as mock:
        yield mock


def test_connect_with_password_success(mock_sshclient):
    instance = mock_sshclient.return_value
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")

    result = ssh.connect()

    assert result is True
    instance.set_missing_host_key_policy.assert_called_once()
    instance.connect.assert_called_once_with("1.2.3.4", username="testuser", password="secret", timeout=5)


def test_connect_with_key_success(mock_sshclient):
    instance = mock_sshclient.return_value
    with patch("paramiko.RSAKey.from_private_key_file") as mock_key:
        mock_key.return_value = "fake_key"
        ssh = SSHConnection(host="1.2.3.4", user="testuser", key_path="/fake/key")

        result = ssh.connect()

        assert result is True
        instance.set_missing_host_key_policy.assert_called_once()
        instance.connect.assert_called_once_with("1.2.3.4", username="testuser", pkey="fake_key", timeout=5)
        mock_key.assert_called_once_with("/fake/key")


def test_connect_raises_connection_error(mock_sshclient):
    instance = mock_sshclient.return_value
    instance.connect.side_effect = Exception("Connection failed")

    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")

    with pytest.raises(ConnectionError) as excinfo:
        ssh.connect()

    assert "Failed to establish connection" in str(excinfo.value)


def test_run_command_success(mock_sshclient):
    instance = mock_sshclient.return_value
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")
    ssh.client = instance

    # Mock exec_command to return mocked stdin, stdout, stderr
    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()

    mock_stdout.read.return_value = b"command output\n"
    mock_stderr.read.return_value = b""

    instance.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

    output = ssh.run_command("ls")

    assert output == "command output"


def test_run_command_error_output(mock_sshclient):
    instance = mock_sshclient.return_value
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")
    ssh.client = instance

    mock_stdin = MagicMock()
    mock_stdout = MagicMock()
    mock_stderr = MagicMock()

    mock_stdout.read.return_value = b""
    mock_stderr.read.return_value = b"some error"

    instance.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

    output = ssh.run_command("ls")

    assert output == "Error Collecting : some error"


def test_run_command_raises_if_not_connected():
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")

    with pytest.raises(RuntimeError) as excinfo:
        ssh.run_command("ls")

    assert "SSH client not connected" in str(excinfo.value)


def test_run_command_handles_exception(mock_sshclient):
    instance = mock_sshclient.return_value
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")
    ssh.client = instance

    instance.exec_command.side_effect = Exception("Execution failed")

    output = ssh.run_command("ls")

    assert output.startswith("Error Collecting : Execution failed")


def test_close_calls_client_close(mock_sshclient):
    instance = mock_sshclient.return_value
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")
    ssh.client = instance

    ssh.close()

    instance.close.assert_called_once()


def test_close_no_client_does_not_raise():
    ssh = SSHConnection(host="1.2.3.4", user="testuser", password="secret")
    ssh.client = None

    # Should not raise anything
    ssh.close()
