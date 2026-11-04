param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Unable to create the Python environment.' }
    & $python -m pip install -e .
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
function Get-AppHealth {
    try { return Invoke-RestMethod 'http://127.0.0.1:8766/api/health' -TimeoutSec 2 }
    catch [System.Net.WebException] { Write-Verbose 'Server not yet ready.' }
    catch [System.Net.Http.HttpRequestException] { Write-Verbose 'Server not yet ready.' }
}
$ready = Get-AppHealth
if (-not ($ready -and $ready.app -eq 'Stock Research Lab')) {
    $process = Start-Process -FilePath $python -ArgumentList '-m stocklab.server' -WorkingDirectory $PSScriptRoot -PassThru
    for ($i = 0; $i -lt 60; $i++) {
        if ($process.HasExited) { throw 'Server stopped. Check its terminal for details.' }
        Start-Sleep -Milliseconds 500
        $ready = Get-AppHealth
        if ($ready -and $ready.app -eq 'Stock Research Lab') { break }
    }
    if (-not ($ready -and $ready.app -eq 'Stock Research Lab')) { throw 'Server did not become ready.' }
}
Write-Host 'Stock Research Lab: http://127.0.0.1:8766'
if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:8766' }
