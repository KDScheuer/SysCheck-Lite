import fnmatch

DEFAULT_SERVICE_PATTERNS = [
    "*ssh*", 
    "*http*",
    "*nginx*",
    "*sql*",
    "*mariadb*",
    "*mysql*",
    "*postgres*",
    "*firewalld*",
    "*sshd*"
    ]

class LinuxCollector:
    def __init__(self, services=None, distro=None):
        self.services = DEFAULT_SERVICE_PATTERNS + (services or [])
        
        
        if distro in ['rhel', 'rocky']:
            package_command = "stat -c %y /var/log/dnf.rpm.log"
        elif distro in ['debian', 'ubuntu']:
            package_command = "stat -c %y /var/log/apt/history.log"
        else:
            raise ValueError("Unsupported Distribution")
        
        self.collection_commands = {
            "Hostname": "hostname",
            "Uptime": "uptime -p",
            "OS Version": "cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2",
            "Kernel": "uname -r",
            "CPU Usage": "top -bn1 | grep \"Cpu(s)\" | awk '{print $2 + $4 \"% used\"}'",
            "Memory Usage": "free | awk '/Mem:/ { printf(\"%.2f%% used\\n\", $3/$2 * 100) }'",
            "Swap Usage": "free | awk '/Swap:/ && $2 > 0 { printf(\"%.2f%% used\\n\", $3/$2 * 100) }'",
            "Last Update": package_command,
            "TimeZone": "timedatectl show -p Timezone --value",
            "SELinux Status": "getenforce",
            "Disk Usage": "df -h --output=source,size,used,avail,pcent,target",
            "Last 10 Journalctl Errors": "journalctl -p 3 -n 10 --no-pager"
        }
    def collect(self, connector):
        system_info = {}

        for key, command in self.collection_commands.items():
            result = connector.run_command(command).strip()
            system_info[key] = result.splitlines() if '\n' in result else result

        if self.services:
            all_services = connector.run_command("systemctl list-units --type=service --no-pager --no-legend").splitlines()
            available_services = [line.split()[0].replace('.service', '') for line in all_services]

            matched = set()
            for pattern in self.services:
                matched.update(fnmatch.filter(available_services, pattern))

            status_results = {}
            for service in matched:
                status = connector.run_command(f"systemctl is-active {service}").strip()
                status_results[service] = status

            system_info["Services"] = status_results

        return system_info
