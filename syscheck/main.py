import argparse
from getpass import getpass

from connectors.ssh import SSHConnection
from collectors.RHELCollector import RHELCollector


def parse_args() -> object:
    parser = argparse.ArgumentParser( description="SysCheck-Lite: Collects Basic System Info and Provides Report")
    parser.add_argument("--host", required=True, help="Target Hostname or IP Address")
    parser.add_argument("-u", "--user", required=True, help="Username to connect with")
    parser.add_argument("--os", choices=["windows", "rhel", "debian", "ubuntu"], required=True, help="Target is a Windows based machine")
    parser.add_argument("--key", help="SSH Private Key for connection ")
    parser.add_argument("--services", nargs="*", help="Service name(s) to check, supports wildcards (e.g. '*sql*' or 'nginx mysql')")
    return parser.parse_args()


def create_connector(args) -> object:
    if args.os in ["rhel",]:
        password = getpass("Enter SSH Password: ")
        connector = SSHConnection(
            host=args.host,
            user=args.user,
            password=password,
        )
    else:
       raise ValueError(f"Unsupported OS: {args.os}")

    return connector


def create_collector(args) -> object:
    if args.os == "rhel":
        return RHELCollector(services=args.services)
    
    raise ValueError(f"No collector implemented for OS: {args.os}")


def gather_info(collector, connector) -> dict:
    if not connector.connect():
        print("Connection failed.")
        return

    system_info = collector.collect(connector)
    return system_info
    

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


def main() -> None:
    args = parse_args()
    connector = create_connector(args)
    collector = create_collector(args)
    results = gather_info(collector, connector)
    display_results(results)
        

if __name__ == "__main__":
    main()
