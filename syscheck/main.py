import argparse
from getpass import getpass
import os

import syscheck
from syscheck.connectors.ssh import SSHConnection
from syscheck.connectors.winrm import WinRMConnection
from syscheck.collectors.RHELCollector import RHELCollector
from syscheck.collectors.WindowsCollector import WindowsCollector
from syscheck.formatter.TerminalFormatter import to_terminal
from syscheck.formatter.htmlFormatter import to_html
from syscheck.formatter.jsonFormatter import to_json


def parse_args() -> object:
    parser = argparse.ArgumentParser( description="SysCheck-Lite: Collects Basic System Info and Provides Report")
    parser.add_argument("-H", "--host", help="Target Hostname or IP Address")
    parser.add_argument("-u", "--user", help="Username to connect with")
    parser.add_argument("-o", "--os", choices=["windows", "rhel", "debian", "ubuntu"], help="Target is a Windows based machine")
    parser.add_argument("-k", "--key", help="SSH Private Key for connection ")
    parser.add_argument("-s", "--services", nargs="*", help="Service name(s) to check, supports wildcards (e.g. '*sql*' or 'nginx mysql')")
    parser.add_argument('--version', action='version', version=f"SysCheck-Lite {syscheck.__version__}")
    parser.add_argument("-d", "--domain", help="Target Domain for Authentication with Username")
    parser.add_argument("-O", "--output", choices=["terminal", "html", "json"], help="How to display the results.")
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


def validate_required_args(args) -> object:
    
    if not args.os:
        args.os = input("Enter OS (rhel, windows, ubuntu): ").strip()
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
    

def main() -> None:
    args = parse_args()
    args = validate_required_args(args)
    connector = create_connector(args)
    collector = create_collector(args)
    results = gather_info(collector, connector)

    if args.output == "html":
        to_html(results, args.host)
    elif args.output == "json":
        to_json(results)
    else:
        to_terminal(results)


def cli_entry_point():
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
        exit(1)


if __name__ == "__main__":
    cli_entry_point()
