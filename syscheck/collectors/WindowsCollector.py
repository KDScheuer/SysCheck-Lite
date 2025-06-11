import fnmatch

DEFAULT_SERVICE_PATTERNS = [
    "*SQL*",          
    "*IIS*",            
    "*HTTP*",           
    "*DNS*",            
    "*DHCP*",           
    "*WinDefend*",      
    "*Firewall*",       
]

class WindowsCollector:
    def __init__(self, services=None):
        self.services = DEFAULT_SERVICE_PATTERNS + (services or [])

    def collect(self, connector):
        # Powershell commands for system info
        system_info = {
            "Hostname": connector.run_command("hostname", "Collecting Hostname").strip(),
            "Uptime": connector.run_command(
                "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime", "Collecting Uptime"
            ).strip(),
            "OS Version": connector.run_command(
                "(Get-CimInstance Win32_OperatingSystem).Caption", "Collecting OS Version"
            ).strip(),
            "Build": connector.run_command(
                "(Get-CimInstance Win32_OperatingSystem).Version", "Collecting Build Version"
            ).strip(),
            "CPU Usage": connector.run_command(
            "$cpu = Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 1 -MaxSamples 2; " +
            "[math]::Round(($cpu.CounterSamples | Select -ExpandProperty CookedValue | " +
            "Measure-Object -Average).Average, 2)", "Collecting CPU Usage"
            ).strip() + " %",
            "Memory Usage": connector.run_command(
                "(Get-CimInstance Win32_OperatingSystem | Select-Object @{Name='UsedMemory';Expression={$_.TotalVisibleMemorySize - $_.FreePhysicalMemory}},@{Name='TotalMemory';Expression={$_.TotalVisibleMemorySize}}) | ForEach-Object {\"{0:N2}% used\" -f (($_.UsedMemory / $_.TotalMemory) * 100)}", "Collecting Memory Usage"
            ).strip(),
            "Swap Usage": connector.run_command(
                "(Get-CimInstance Win32_PageFileUsage | Select-Object @{Name='UsedMB';Expression={$_.CurrentUsage}},@{Name='AllocatedMB';Expression={$_.AllocatedBaseSize}}) | ForEach-Object {\"{0:N2}% used\" -f (($_.UsedMB / $_.AllocatedMB) * 100)}", "Collecting SWAP Usage"
            ).strip(),
            "Last Windows Update": connector.run_command(
                "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1 -ExpandProperty InstalledOn", "Collecting Last Update"
            ).strip(),
            "TimeZone": connector.run_command(
                "(Get-TimeZone).Id", "Collecting Timezone"
            ).strip(),
            "Windows Defender Enabled": connector.run_command(
                "Get-MpComputerStatus | Select-Object -ExpandProperty AMServiceEnabled", "Collecting Windows Defender Status"
            ).strip(),
        }

        disk_usage = connector.run_command(
            "Get-PSDrive -PSProvider 'FileSystem' | Select-Object Name,Used,Free | ForEach-Object {\"{0}: Used: {1} Free: {2}\" -f $_.Name,($_.Used / 1GB -as [int]),($_.Free / 1GB -as [int])}", "Collecting Disk Usage"
        ).strip()

        system_info["Disk Usage"] = disk_usage.splitlines()

        # Get last 10 error events from System log
        system_errors = connector.run_command(
            "Get-EventLog -LogName System -EntryType Error -Newest 10 | Format-Table TimeGenerated,Source,EventID,Message -AutoSize | Out-String", "Collecitng System Error Log"
        ).strip()

        system_info["Last 10 System Errors"] = system_errors.splitlines()

        if self.services:
            # Get list of services
            all_services = connector.run_command(
                "Get-Service | Select-Object -ExpandProperty Name", "Collecting Service Information"
            ).splitlines()

            matched = set()
            for pattern in self.services:
                matched.update(fnmatch.filter(all_services, pattern))

            status_results = {}
            for service in matched:
                status = connector.run_command(
                    f"(Get-Service -Name '{service}').Status"
                ).strip()
                status_results[service] = status

            system_info["Services"] = status_results if status_results else "No matching services found"


        return system_info
