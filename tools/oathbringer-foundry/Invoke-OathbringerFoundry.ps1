[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InputRoot,
    [Parameter(Mandatory)][string]$OutputDir,
    [string]$SourceRoot = (Join-Path $PSScriptRoot '..\..'),
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'cli.py'
$resolvedInput = (Resolve-Path -LiteralPath $InputRoot).Path
$resolvedSource = (Resolve-Path -LiteralPath $SourceRoot).Path
$arguments = @('-B', $scriptPath, 'compile', '--input-root', $resolvedInput, '--source-root', $resolvedSource, '--output-dir', $OutputDir)
if ($Json) { $arguments += '--json' }

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction Stop }
if ($python.Name -eq 'py.exe') { $arguments = @('-3') + $arguments }
& $python.Source @arguments
exit $LASTEXITCODE
