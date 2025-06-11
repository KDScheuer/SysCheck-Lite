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

class RHELCollector:
    def __init__(self, services=None):
        self.services = DEFAULT_SERVICE_PATTERNS + (services or [])

    def collect(self, connector):
        system_info = {
            "Hostname": connector.run_command("hostname", "Collecting Hostname").strip(),
            "Uptime": connector.run_command("uptime -p", "Collecting Uptime").strip(),
            "OS Version": connector.run_command("cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2", "Collecting OS").strip().strip('"'),
            "Kernel": connector.run_command("uname -r", "Collecting Kernel").strip(),
            "CPU Usage": connector.run_command("top -bn1 | grep \"Cpu(s)\" | awk '{print $2 + $4 \"% used\"}'", "Collecting CPU Usage").strip(),
            "Memory Usage": connector.run_command("free | awk '/Mem:/ { printf(\"%.2f%% used\\n\", $3/$2 * 100) }'", "Collecting Memory Usage").strip(),
            "Swap Usage": connector.run_command("free | awk '/Swap:/ && $2 > 0 { printf(\"%.2f%% used\\n\", $3/$2 * 100) }'", "Collecting SWAP Usage").strip(),
            "Last DNF Update": connector.run_command("stat -c %y /var/log/dnf.rpm.log", "Collecting Last DNF Update").strip(),
            "TimeZone": connector.run_command("timedatectl show -p Timezone --value", "Collecting Timezone").strip(),
            "SELinux Status": connector.run_command("getenforce", "Collecting SELinux Status").strip(),
        }

        disk_usage =  connector.run_command("df -h --output=source,size,used,avail,pcent,target", "Collecting Disk Usage").strip()
        system_info["Disk Usage"] = [line for line in disk_usage.split('\n')]

        system_errors = connector.run_command("journalctl -p 3 -n 10 --no-pager", "Collecting Error Logs").strip()
        system_info["Last 10 Journalctl Errors"] = [line for line in system_errors.split('\n')]

        if self.services:
            all_services = connector.run_command("systemctl list-units --type=service --no-pager --no-legend", "Collecting Service Information").splitlines()
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
