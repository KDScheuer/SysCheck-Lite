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
        self.collection_commands = {
            "Hostname": "hostname",
            "Uptime": "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime",
            "OS Version": "(Get-CimInstance Win32_OperatingSystem).Caption",
            "Build": "(Get-CimInstance Win32_OperatingSystem).Version",
            "CPU Usage": "$cpu = Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 1 -MaxSamples 2; " + "[math]::Round(($cpu.CounterSamples | Select -ExpandProperty CookedValue | " + "Measure-Object -Average).Average, 2)",
            "Memory Usage": "(Get-CimInstance Win32_OperatingSystem | Select-Object @{Name='UsedMemory';Expression={$_.TotalVisibleMemorySize - $_.FreePhysicalMemory}},@{Name='TotalMemory';Expression={$_.TotalVisibleMemorySize}}) | ForEach-Object {\"{0:N2}% used\" -f (($_.UsedMemory / $_.TotalMemory) * 100)}",
            "Swap Usage": "(Get-CimInstance Win32_PageFileUsage | Select-Object @{Name='UsedMB';Expression={$_.CurrentUsage}},@{Name='AllocatedMB';Expression={$_.AllocatedBaseSize}}) | ForEach-Object {\"{0:N2}% used\" -f (($_.UsedMB / $_.AllocatedMB) * 100)}",
            "Last Windows Update": "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1 -ExpandProperty InstalledOn",
            "TimeZone": "(Get-TimeZone).Id",
            "Windows Defender Enabled": "Get-MpComputerStatus | Select-Object -ExpandProperty AMServiceEnabled",
            "Disk Usage": "Get-PSDrive -PSProvider 'FileSystem' | Select-Object Name,Used,Free | ForEach-Object {\"{0}: Used: {1}G Free: {2}G\" -f $_.Name,($_.Used / 1GB -as [int]),($_.Free / 1GB -as [int])}",
            "Last 10 System Errors": "Get-EventLog -LogName System -EntryType Error -Newest 10 | ForEach-Object { \"$($_.TimeGenerated) [$($_.EventID)] $($_.Message)`n\" }",
        }


    def collect(self, connector):
        system_info = {}

        for key, command in self.collection_commands.items():
            result = connector.run_command(command).strip()
            system_info[key] = result.splitlines() if '\n' in result else result

        if self.services:
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
