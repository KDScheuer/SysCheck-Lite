import paramiko
from typing import Optional


class SSHConnection:
    def __init__(self, host: str, user: str, password: Optional[str] = None, key_path: Optional[str] = None):
        self.host = host
        self.user = user
        self.password = password
        self.key_path = key_path
        self.client = None

    def connect(self) -> bool:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_path:
                private_key = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.client.connect(self.host, username=self.user, pkey=private_key, timeout=5)
            else:
                self.client.connect(self.host, username=self.user, password=self.password, timeout=5)

            return True
        
        except Exception as e:
            raise ConnectionError (f"Failed to establish connection to {self.host}")
            # print(f"\n\033[91m[!] SSH connection error: {e}\033[0m")
            return False

    def run_command(self, command: str, log = "") -> str:
        if not self.client:
            raise RuntimeError("SSH client not connected")

        try:
            if log:
                print(log, end="\r", flush=True)
            stdin, stdout, stderr = self.client.exec_command(command)
            if log:
                print("                                                         ", end="\r", flush=True)
            return stdout.read().decode().strip()
        except Exception as e:
            print(f"[!] Error {log} : {e}")
            return "Error Collecting"

    def close(self):
        if self.client:
            self.client.close()
