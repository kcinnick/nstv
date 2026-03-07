"""
PowerShell automation script for NSTV download processing.

This script provides more advanced features than the batch file:
- Logging to file
- Email notifications (optional)
- Better error handling
- Environment validation

USAGE:
  Manual: .\run_download_processor.ps1
  Scheduled: Create a scheduled task that runs this script

TASK SCHEDULER SETUP:
  Action: Start a program
  Program: powershell.exe
  Arguments: -ExecutionPolicy Bypass -File "C:\Users\Nick\nstv\scripts\run_download_processor.ps1"
  Start in: C:\Users\Nick\nstv
"""

# Configuration
$ProjectRoot = "C:\Users\Nick\nstv"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "download_processor_$(Get-Date -Format 'yyyy-MM').log"
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

# Ensure log directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    # Write to console
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        default { Write-Host $LogMessage }
    }
    
    # Write to log file
    Add-Content -Path $LogFile -Value $LogMessage
}

# Main execution
try {
    Write-Log "=" * 80
    Write-Log "NSTV Download Processor Starting"
    Write-Log "=" * 80
    
    # Change to project directory
    Set-Location $ProjectRoot
    Write-Log "Working directory: $(Get-Location)"
    
    # Activate virtual environment
    if (Test-Path $VenvActivate) {
        Write-Log "Activating virtual environment..."
        & $VenvActivate
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to activate virtual environment"
        }
    } else {
        Write-Log "Virtual environment not found, using system Python" "WARNING"
    }
    
    # Validate environment variables
    $RequiredVars = @("NZBGET_COMPLETE_DIR", "PLEX_TV_SHOW_DIR", "PLEX_MOVIES_DIR")
    $MissingVars = @()
    foreach ($Var in $RequiredVars) {
        if (!(Test-Path env:$Var)) {
            $MissingVars += $Var
        }
    }
    
    if ($MissingVars.Count -gt 0) {
        Write-Log "Missing environment variables: $($MissingVars -join ', ')" "WARNING"
    }
    
    # Run Django management command
    Write-Log "Executing process_downloads command..."
    $StartTime = Get-Date
    
    & python manage.py process_downloads --verbose
    
    $ExitCode = $LASTEXITCODE
    $Duration = (Get-Date) - $StartTime
    
    Write-Log ""
    Write-Log "=" * 80
    if ($ExitCode -eq 0) {
        Write-Log "Processing completed successfully in $($Duration.TotalSeconds) seconds" "SUCCESS"
    } else {
        Write-Log "Processing failed with exit code $ExitCode" "ERROR"
    }
    Write-Log "=" * 80
    
    exit $ExitCode
    
} catch {
    Write-Log "Fatal error: $_" "ERROR"
    Write-Log $_.Exception.StackTrace "ERROR"
    exit 1
}
