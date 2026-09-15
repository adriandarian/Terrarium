param(
    [string]$BlenderPython = 'C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $projectRoot 'Saved\BlenderMCP'
$uvPath = Join-Path $runtime 'tools\uv.exe'
if (-not (Test-Path -LiteralPath $BlenderPython)) { throw "Blender Python not found: $BlenderPython" }
New-Item -ItemType Directory -Force $runtime | Out-Null
if (-not (Test-Path -LiteralPath $uvPath)) {
    $installer = Join-Path $runtime 'install-uv.ps1'
    Invoke-WebRequest 'https://astral.sh/uv/install.ps1' -OutFile $installer
    $env:UV_UNMANAGED_INSTALL = Join-Path $runtime 'tools'
    & $installer
    if (-not (Test-Path -LiteralPath $uvPath)) { throw 'uv installation failed.' }
}
$env:UV_CACHE_DIR = Join-Path $runtime 'cache'
$python = Join-Path $runtime 'lab-venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & $uvPath venv (Join-Path $runtime 'lab-venv') --python $BlenderPython
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
$archive = Join-Path $runtime 'blender-lab-1.0.3.zip'
$source = Join-Path $runtime 'lab-1.0.3'
if (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest 'https://projects.blender.org/lab/blender_mcp/releases/download/v1.0.3/blender-1.0.3.mcpb' -OutFile $archive
}
$expectedHash = 'D6FE04DD17767F7C7FB452142F1F0E6787DB575DB49F3976A166142683B5B97E'
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'Blender Lab release checksum differs from the verified 1.0.3 download.'
}
Expand-Archive -LiteralPath $archive -DestinationPath $source -Force
& $uvPath pip install --python $python $source
if ($LASTEXITCODE -ne 0) { throw 'Blender MCP installation failed.' }
Write-Output 'Installed Blender Lab MCP 1.0.3 for Terrarium. Enable the matching Blender Lab MCP extension in Blender preferences.'
