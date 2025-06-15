<p align="center">

  ![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
  ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue)
  ![License](https://img.shields.io/badge/License-MIT-green)
  ![Status](https://img.shields.io/badge/Status-Active-Green)
</p>

# SysCheck-Lite
SysCheck-Lite is a lightweight CLI utility designed to provide a quick, high-level snapshot of a system's health. It is ideal for manual use at the beginning of a troubleshooting session, giving you instant access to basic but essential information such as compute resources, memory, disk status, services, errors, OS details, and pending updates.

## Table of Contents
- [Philosophy](#philosophy)
- [Installation (Development)](#installation-development)
- [Features](#features)
- [Arguments](#arguments)
- [Example Commands](#example-commands)
- [Example Outputs](#example-outputs)
- [Working with Profiles](#working-with-profiles)
- [Contributing](#contributing)
- [License](#license)

## Design Philosophy

SysCheck-Lite is a lightweight CLI utility designed for quick, high-level snapshots of system health. It helps administrators and engineers rapidly assess key system metrics—like CPU, memory, disk usage, service states, and updates—without the overhead of complex monitoring platforms.

It is intentionally minimal and user-triggered, ideal for:

- Quick snapshots of system health prior to troubleshooting
- Environments with limited tooling
- Fast, no-dependency diagnostics on jumpboxes or remote systems

SysCheck-Lite avoids persistent agents, background services, and complex alerting to maintain simplicity and speed.

## Installation
``` bash
pip install git+https://github.com/KDScheuer/SysCheck-Lite.git
```

## Features
- Supports both Linux and Windows
- Outputs to Terminal, JSON, or HTML
- SSH key-based or password authentication
- Lightweight, minimal dependencies
- Interactive prompts or CLI argument support

## Arguments
All Arguments are optional, if none are provided you will be prompted for them interactively.
- ⚠️ Avoid using --password directly in the terminal, as it will display your password in plain text. For better security, either omit it to be prompted interactively or use an environment variable to store the password securely. 
- When passing --domain "" explicitly, no domain prompt will appear.

| Argument       | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `-H`, `--host`       | Target machine IP address or DNS name                                            |
| `-u`, `--user`       | Username to authenticate with                                                    |
| `-o`, `--os`         | Target machine OS (`windows`, `rhel`, `debian`, `ubuntu`)                        |
| `-k`, `--key`        | SSH private key file path for passwordless authentication. This is only used if the target host is a linux based system.                       |
| `-s`, `--services`   | List of services to query (supports wildcards, e.g., `*sql*`, `http*`)           |
| `-d`, `--domain`     | Domain name for authentication. If provided, it will be combined as `DOMAIN\username`. If you prefer to use `username@domain.com`, leave this blank and enter the full username instead.                                |
| `-h`, `--help`       | Display Help                                                                     |
| `--version`          | Display the current version of SysCheck-Lite                                     |
| `-O`, `--output`      | Choices for program output (`terminal (default)`,`json`,`html`)                  |
| `-p`, `--password`    | Password to use for authentication. Optional will prompt securely if not provided | 
| `-P`, `--profile`    | Load a saved profile with connection settings. CLI Input will take priority over the values in the profile. | 
| `-C`, `--createprofile`    | Save arguments into profile for use later.| 

## Example Commands
Connecting to Linux host using ssh key and displaying webpage with the results
``` bash
syscheck -H testapp01 -o rhel -u root -k ../../rockytest.key -O html
```

Connecting to Linux host with an interactive password prompt
``` bash
syscheck -H 192.168.50.59 -o rhel -u root
```

Connecting to Windows host with JSON output and all other required arguments as an interactive prompt
```bash
syscheck -H wintestapp01 -O json
```

Connecting to host with all interactive prompts and querying services
```bash
syscheck -s *sql* *httpd* *nginx* *php*
```

Creating / Loading a profile
```bash
syscheck -C test -H 192.168.50.59 -o rhel -u root -s *nginx* *http* -k C:\Users\kdsch\OneDrive\Desktop\rockytest.key -O html
```
```bash
syscheck -P test
```
See [Working with Profiles](#working-with-profiles) for more information


## Example Outputs
### Terminal Output Examples
Linux System
![SCREENSHOT](./images/LinuxCollectionExample.png)

Windows System
![SCREENSHOT](./images/WindowsCollectionExample.png)

### JSON Output Example
![SCREENSHOT](./images/JSONOutputExample.png)

### HTML Output Example
![SCREENSHOT](./images/HTMLOutputExample.png)

## Working with Profiles
Profiles can be used to save the connection settings, then later loaded to provide values for the required arguments. Profiles are stored in the users home directory in key value format, and support comments. If a value is passed at runtime it will override any value in the profile.

### Example Profile Usage
![SCREENSHOT](./images/ProfileExample.png)

### Example Profile File Contents
![SCREENSHOT](./images/ProfileFileExample.png)

## Contributing
Contributions are welcome for bug fixes or simple improvements that align with the project’s goal of remaining lightweight. Please open an issue or submit a pull request for discussion.

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.