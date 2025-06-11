<p align="center">

  ![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
  ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue)
  ![License](https://img.shields.io/badge/License-MIT-green)
  ![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
</p>

# SysCheck-Lite
Simple CLI tool to quickly check the health and status of a remote server.

## Arguments
Arguments are optional when running the command, if none are provided it will interactively prompt you for the required information.

| Argument       | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `-h`, `--host`       | Target machine IP address or DNS name                                       |
| `-u`, `--user`       | Username to authenticate with                                               |
| `-o`, `--os`         | Target machine OS (`windows`, `rhel`, `debian`, `ubuntu`)                   |
| `-k`, `--key`        | SSH private key file path for passwordless authentication                   |
| `-s`, `--services`   | List of services to query (supports wildcards, e.g., `*sql*`, `http*`)      |
| `-d`, `--domain`     | Domain name for authentication (Windows only)                               |
| `-h`, `--help`       | Display Help                                                                |
| `--version`          | Display the current version of SysCheck-Lite                                |


## General Collection Notes
- Make sure your SSH key path is correct and accessible.
- When passing --domain "" explicitly, no domain prompt will appear.
- Services argument supports wildcards for flexible querying.

## Linux Collection Example
Example Command for Linux Collection
``` python
syscheck.main --host 192.168.50.59 --os rhel --user root --key ../rockytest.key
```
Or without SSH key (will prompt for password):
``` python
syscheck.main --host 192.168.50.59 --os rhel --user root
```
Example Output from this collector
![SCREENSHOT](./images/LinuxCollectionExample.png)

## Windows Collection Example
Example Command for Windows Collection
```python
syscheck.main --host 192.168.50.217 --os windows --domain "" --user Administrator
```
Example Output from this collector
![SCREENSHOT](./images/WindowsCollectionExample.png)