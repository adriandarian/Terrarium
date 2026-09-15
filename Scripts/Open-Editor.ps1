param([string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8')
$ErrorActionPreference = 'Stop'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path (Split-Path $PSScriptRoot -Parent) 'Terrarium.uproject'
if (!(Test-Path -LiteralPath $editor)) { throw "Unreal Editor not found: $editor" }
& $editor $project
