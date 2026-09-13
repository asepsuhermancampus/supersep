# SuperSep 1-Click Global Installer for Windows
$ErrorActionPreference = "Stop"

$PluginDir = "$env:USERPROFILE\.gemini\config\plugins\supersep"
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Installing SuperSep Global Plugin" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "1. Creating plugin directory: $PluginDir"
New-Item -ItemType Directory -Force -Path $PluginDir | Out-Null

Write-Host "2. Copying SuperSep files..."
Copy-Item -Recurse -Force -Exclude ".venv",".git" ./* $PluginDir

Write-Host "3. Initializing virtual environment in plugin..."
Set-Location $PluginDir
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path "$PluginDir\.env")) {
    Copy-Item "$PluginDir\.env.example" "$PluginDir\.env"
    Write-Host "Created default .env from .env.example. Please update your ROUTER_API_KEY in $PluginDir\.env" -ForegroundColor Yellow
}

Write-Host "=========================================" -ForegroundColor Green
Write-Host "  SuperSep Installed Successfully!" -ForegroundColor Green
Write-Host "  Commands available in any workspace:" -ForegroundColor Green
Write-Host "  - /mikirsep <ide / kebutuhan>" -ForegroundColor White
Write-Host "  - /gassep   <task / blueprint>" -ForegroundColor White
Write-Host "  - /commitsep [pesan commit]" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Green
