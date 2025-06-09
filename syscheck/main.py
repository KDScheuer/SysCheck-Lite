import argparse
from getpass import getpass
import os

from connectors.ssh import SSHConnection
from connectors.winrm import WinRMConnection
from collectors.RHELCollector import RHELCollector
from collectors.WindowsCollector import WindowsCollector

def parse_args() -> object:
    parser = argparse.ArgumentParser( description="SysCheck-Lite: Collects Basic System Info and Provides Report")
    parser.add_argument("--host", help="Target Hostname or IP Address")
    parser.add_argument("-u", "--user", help="Username to connect with")
    parser.add_argument("--os", choices=["windows", "rhel", "debian", "ubuntu"], help="Target is a Windows based machine")
    parser.add_argument("--key", help="SSH Private Key for connection ")
    parser.add_argument("--services", nargs="*", help="Service name(s) to check, supports wildcards (e.g. '*sql*' or 'nginx mysql')")
    return parser.parse_args()


def create_connector(args) -> object:
    ssh_key_path = None
    if args.key:
        ssh_key_path = os.path.expandvars(os.path.expanduser(args.key))
        ssh_key_path = os.path.abspath(ssh_key_path)
        if not os.path.isfile(ssh_key_path):
            raise FileNotFoundError(f"SSH key file not found: {ssh_key_path}")
    
    password = None
    if not ssh_key_path:
        password = getpass("Enter Password: ")
        
    if args.os in ["rhel", "rocky",]:
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
    if args.os in ["rhel", "rocky"]:
        return RHELCollector(services=args.services)
    elif args.os in ["windows"]:
        return WindowsCollector(services=args.services)
    
    raise ValueError(f"No collector implemented for OS: {args.os}")


def gather_info(collector, connector) -> dict:
    
    if connector.connect():
        system_info = collector.collect(connector)
        return system_info
    else:
        raise ConnectionError("Failed to connect to target")
    

def display_results(results) -> None:
    GREEN = "\033[92m"
    RESET = "\033[0m"
    print(f"\n{GREEN}System Info:{RESET}")
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"{GREEN}{key.capitalize()}{RESET}:")
            for sub_key, sub_value in value.items():
                print(f"{GREEN} - {sub_key}{RESET}: {sub_value}")
        else:
            print(f"{GREEN}{key}{RESET}: {value}")


def validate_required_args(args) -> object:
    
    if not args.os:
        args.os = input("Enter OS (rhel, windows, ubuntu): ").strip()
    if args.os == "windows":
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
    

def main() -> None:
    args = parse_args()
    args = validate_required_args(args)
    connector = create_connector(args)
    collector = create_collector(args)
    results = gather_info(collector, connector)
    display_results(results)
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[93mProgram exited by user (Ctrl+C).\033[0m")
        exit(0)
    except ValueError as e:
        print(f"\n\033[91m[!] {e}\033[0m")
        exit(1)
    except ConnectionError as e:
        print(f"\n\033[91m[!] {e}\033[0m")
