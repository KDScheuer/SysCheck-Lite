import fnmatch

class RHELCollector:
    def __init__(self, services=None):
        self.services = services or []

    def collect(self, connector):
        system_info = {
            "Hostname": connector.run_command("hostname").strip(),
            "Uptime": connector.run_command("uptime -p").strip(),
            "OS Version": connector.run_command("cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2").strip().strip('"'),
            "Kernel": connector.run_command("uname -r").strip(),
            "CPU Usage": connector.run_command("top -bn1 | grep \"Cpu(s)\" | awk '{print $2 + $4 \"% used\"}'").strip(),
            "Memory Usage": connector.run_command("free | awk '/Mem:/ { printf(\"%.2f%% used\\n\", $3/$2 * 100) }'").strip(),
            "Swap Usage": connector.run_command("free | awk '/Swap:/ && $2 > 0 { printf(\"%.2f%% used\\n\", $3/$2 * 100) }'").strip(),
            "Last DNF Update": connector.run_command("stat -c %y /var/log/dnf.rpm.log").strip()

        }

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

            system_info["services"] = status_results

        return system_info
