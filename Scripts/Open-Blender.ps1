param(
    [string]$BlenderPath = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
    [string]$BlendFile
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $projectRoot 'Saved\BlenderMCP'
if (-not (Test-Path -LiteralPath $BlenderPath)) { throw "Blender not found: $BlenderPath" }
if (-not (Test-Path -LiteralPath (Join-Path $runtime 'lab-venv\Scripts\blender-mcp.exe'))) {
    throw 'Run Scripts\Install-BlenderMCP.ps1 first.'
}
if (Get-NetTCPConnection -State Listen -LocalPort 9876 -ErrorAction SilentlyContinue) {
    throw 'Port 9876 is already in use. Close the existing Blender MCP session before launching another.'
}
$launchArgs = @('--online-mode')
if ($BlendFile) {
    $resolvedBlend = (Resolve-Path -LiteralPath $BlendFile).Path
    $launchArgs += '"' + $resolvedBlend + '"'
}
$launchArgs += @('--python', ('"' + (Join-Path $PSScriptRoot 'start_blender_mcp.py') + '"'))
Start-Process -FilePath $BlenderPath -ArgumentList $launchArgs -WorkingDirectory $projectRoot -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $runtime 'blender.log') `
    -RedirectStandardError (Join-Path $runtime 'blender-error.log') -PassThru |
    Select-Object Id, ProcessName
