import winrm
from typing import Optional


class WinRMConnection:
    def __init__(self, host: str, user: str, password: Optional[str] = None, domain: Optional[str] = None):
        self.host = host
        self.user = user
        self.password = password
        self.domain = domain
        self.client = None

    def connect(self) -> bool:
        try:
            username = f"{self.domain}\\{self.user}" if self.domain else self.user
            transport = 'kerberos' if self.domain else 'ntlm'

            self.client = winrm.Session(
                f"http://{self.host}:5985/wsman",
                auth=(username, self.password),
                transport=transport
            )

            # Test connection
            self.client.run_cmd('whoami')
            return True
        
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.host} via WinRM: {e}")
        
    def run_command(self, command: str) -> str:
        if not self.client:
            raise RuntimeError("WinRM client not connected")

        try:
            result = self.client.run_ps(command)
            stdout = result.std_out.decode().strip()

            # if result.status_code != 0:
            #     return "ERROR_COLLECTING"

            return stdout if stdout else "NO_OUTPUT"

        except Exception:
            return "ERROR_COLLECTING"

    def close(self):
        self.client = None
