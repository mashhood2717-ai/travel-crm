# One-shot backup script for the Travel CRM (Windows / PowerShell version).
# Creates a timestamped .zip containing the SQLite DB, uploaded media, and .env.
# Run from the project root:   powershell -ExecutionPolicy Bypass -File .\backup.ps1

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$outDir = "backups"
$outFile = Join-Path $outDir "travelcrm-backup-$ts.zip"

if (-not (Test-Path $outDir)) { New-Item -ItemType Directory $outDir | Out-Null }

$items = @()
if (Test-Path "db.sqlite3") { $items += "db.sqlite3" }
if (Test-Path "media")      { $items += "media" }
if (Test-Path ".env")       { $items += ".env" }

if ($items.Count -eq 0) {
    Write-Host "Nothing to back up (no db.sqlite3, media/, or .env found)."
    exit 1
}

Compress-Archive -Path $items -DestinationPath $outFile -Force

$size = "{0:N2} MB" -f ((Get-Item $outFile).Length / 1MB)
Write-Host ""
Write-Host "Backup written to: $outFile"
Write-Host "Size:              $size"
Write-Host ""
Write-Host "Upload this zip to your new host, extract it into the project root,"
Write-Host "then run:  python manage.py migrate; python manage.py collectstatic --noinput"
