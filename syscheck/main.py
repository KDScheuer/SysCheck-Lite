import argparse
import os
import time
import getpass
from pathlib import Path

import syscheck
from syscheck.connectors.ssh import SSHConnection
from syscheck.connectors.winrm import WinRMConnection

from syscheck.collectors.LinuxCollector import LinuxCollector
from syscheck.collectors.WindowsCollector import WindowsCollector

from syscheck.formatter.TerminalFormatter import to_terminal
from syscheck.formatter.htmlFormatter import to_html
from syscheck.formatter.jsonFormatter import to_json


def parse_args() -> object:
    parser = argparse.ArgumentParser( description="SysCheck-Lite: Collects Basic System Info and Provides Report")
    parser.add_argument("-H", "--host", help="Target Hostname or IP Address")
    parser.add_argument("-u", "--user", help="Username to connect with")
    parser.add_argument("-o", "--os", choices=["windows", "rhel", "debian", "ubuntu"], type=str.lower, help="Target is a Windows based machine")
    parser.add_argument("-k", "--key", help="SSH Private Key for connection ")
    parser.add_argument("-s", "--services", nargs="*", help="Service name(s) to check, supports wildcards (e.g. '*sql*' or 'nginx mysql')")
    parser.add_argument('--version', action='version', version=f"SysCheck-Lite {syscheck.__version__}")
    parser.add_argument("-d", "--domain", help="Target Domain for Authentication with Username")
    parser.add_argument("-O", "--output", choices=["terminal", "html", "json"], type=str.lower, help="How to display the results.")
    parser.add_argument("-p", "--password", help="Password used to authenticate with the target host")
    parser.add_argument("-P", "--profile", help="Load a saved profile with connection settings. CLI Input will take priority over the values in the profile")
    parser.add_argument("-C", "--createprofile", help="Save arguments into profile for use later.")
    return parser.parse_args()


def get_profile_dir() -> Path:
    if os.name == "nt":
        local_appdata = os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local"
        return Path(local_appdata) / "SysCheck" / "profiles"
    else:
        return Path.home() / ".syscheck_profiles"


def load_profile_file(profile_name: str) -> dict:
    profile_dir = get_profile_dir()
    profile_path = profile_dir / f"{profile_name}.profile"
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile '{profile_name}' not found at {profile_path}")

    profile_data = {}
    with profile_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            profile_data[key.strip()] = value.strip()

    profile_data["Services"] = [s.strip() for s in profile_data['Services'].split(',')]
   
    return profile_data


def create_profile_file(profile_name: str, args) -> None:
    profile_dir = get_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)

    profile_path = profile_dir / f"{profile_name}.profile"
    with profile_path.open("w") as f:
        f.write("# SysCheck-Lite Profile\n")
        for key in vars(args):
            if key in ["createprofile", "profile", "password"]:  
                continue
            value = getattr(args, key)
            if value is None:
                continue
            if isinstance(value, list):
                value = ",".join(value)
            f.write(f"{key}={value}\n")
    
    print(f"\n\033[92mProfile '{profile_name}' saved to {profile_path}\033[0m")


def create_connector(args) -> object:
    ssh_key_path = None
    if args.key:
        ssh_key_path = os.path.expandvars(os.path.expanduser(args.key))
        ssh_key_path = os.path.abspath(ssh_key_path)
        if not os.path.isfile(ssh_key_path):
            raise FileNotFoundError(f"SSH key file not found: {ssh_key_path}")
    
    if args.os not in ["rhel", "rocky", "debian", "ubuntu", "windows"]:
        raise ValueError(f"Unsupported OS: {args.os}")

    password = None
    if not ssh_key_path:
        password = getpass.getpass("Enter Password: ")
        
    if args.os in ["rhel", "rocky", "debian", "ubuntu"]:
        connector = SSHConnection(
            host=args.host,
            user=args.user,
            password=password,
            key_path=ssh_key_path,
        )
    elif args.os in ["windows",]:
        connector = WinRMConnection(
            host=args.host,
            user=args.user,
            password=password,
            domain=args.domain
        )
    else:
       raise ValueError(f"Unsupported OS: {args.os}")

    return connector


def create_collector(args) -> object:
    if args.os in ["rhel", "rocky", "debian", "ubuntu"]:
        return LinuxCollector(services=args.services, distro=args.os)
    elif args.os in ["windows"]:
        return WindowsCollector(services=args.services)
    
    raise ValueError(f"No collector implemented for OS: {args.os}")


def gather_info(collector, connector) -> dict:
    
    if connector.connect():
        system_info = collector.collect(connector)
        return system_info
    else:
        raise ConnectionError("Failed to connect to target")


def validate_required_args(args) -> object:
    
    if not args.os:
        args.os = input("Enter OS (rhel, windows, ubuntu, etc.): ").strip().lower()
    if args.os == "windows" and args.domain == None:
        domain_input = input("Enter Domain (leave blank if none): ").strip()
        args.domain = domain_input if domain_input else None
    else:
        args.domain = None
    if not args.host:
        args.host = input("Enter Target Host: ").strip()
    if not args.user:
        args.user = input("Enter username: ").strip()
    
    
    if not args.host or not args.user or not args.os:
        raise ValueError("Required arguments not provided")

    return args
    

def display_results(results, args) -> None:
    if args.output == "html":
        to_html(results, args.host)
    elif args.output == "json":
        to_json(results)
    else:
        to_terminal(results)


def main() -> None:
    args = parse_args()
    print(f"\033[92m============================================================================\nSysCheck-Lite Version {syscheck.__version__}\n============================================================================\033[0m")
    if args.profile:
        profile_data = load_profile_file(args.profile)
        for key, value in profile_data.items():
            if getattr(args, key, None) is None:
                setattr(args, key, value)
    if args.createprofile:
        create_profile_file(args.createprofile, args)
        return
    args = validate_required_args(args)
    connector = create_connector(args)
    collector = create_collector(args)
    results = gather_info(collector, connector)
    display_results(results, args)


def cli_entry_point():
    try:
        start_time = time.time()
        main()
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"\033[92m\n============================================================================\nCollection Complete: Total Time {elapsed:.2f} Seconds\n============================================================================\033[0m")

    except KeyboardInterrupt:
        print("\n\033[93mProgram exited by user (Ctrl+C).\033[0m")
        exit(0)
    except ValueError as e:
        print(f"\n\033[91m[!] {e}\033[0m")
        exit(1)
    except ConnectionError as e:
        print(f"\n\033[91m[!] {e}\033[0m")
        exit(1)
    except FileNotFoundError as e:
        print(f"\n\033[91m[!] {e}\033[0m")
        exit(1)


if __name__ == "__main__":
    cli_entry_point()
