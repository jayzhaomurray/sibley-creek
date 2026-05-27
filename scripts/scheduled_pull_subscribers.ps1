# Scheduled wrapper for pull_subscribers.mjs
# Invoked daily by Windows Task Scheduler.
# Logs each run to work/outreach/recipients/scheduled_task.log

$ErrorActionPreference = 'Continue'
$repoRoot = 'C:\Users\jayzh\projects\macro-research-department'
$nodeExe  = 'C:\Program Files\nodejs\node.exe'
$script   = Join-Path $repoRoot 'scripts\pull_subscribers.mjs'
$logFile  = Join-Path $repoRoot 'work\outreach\recipients\scheduled_task.log'

Set-Location $repoRoot

$timestamp = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
Add-Content -Path $logFile -Value "[$timestamp] --- scheduled pull start ---" -Encoding utf8

try {
    $output = & $nodeExe $script 2>&1
    $output | ForEach-Object { Add-Content -Path $logFile -Value $_ -Encoding utf8 }
    Add-Content -Path $logFile -Value "[$timestamp] --- scheduled pull end (ok) ---`n" -Encoding utf8
} catch {
    Add-Content -Path $logFile -Value "[$timestamp] ERROR: $($_.Exception.Message)" -Encoding utf8
    Add-Content -Path $logFile -Value "[$timestamp] --- scheduled pull end (error) ---`n" -Encoding utf8
}
