#requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $PackagePath,

    [Parameter(Mandatory = $true)]
    [string] $PackageSha256,

    [Parameter(Mandatory = $true)]
    [string] $OutputDirectory,

    [Parameter(Mandatory = $true)]
    [switch] $SpearBridgeDisabledProof,

    [Parameter(Mandatory = $true)]
    [switch] $CompileOnly,

    [string] $ReadOnlyRemoteUrl,

    [switch] $ResolverSelfTest
)

$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

if (-not $SpearBridgeDisabledProof -or -not $CompileOnly) {
    throw 'Gate 7G-A Spear bridge requires explicit disabled-proof and compile-only intent.'
}

$scriptPath = $PSCommandPath
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref] $tokens, [ref] $errors) | Out-Null
if ($errors.Count -ne 0) {
    throw 'PowerShell parser preflight failed for Invoke-AtlasThreadEngineSpearBridge.ps1.'
}

function Resolve-AtlasPythonApplication {
    $candidates = @(
        @{ Name = 'py'; Prefix = @('-3'); Route = 'py -3' },
        @{ Name = 'python'; Prefix = @(); Route = 'python' },
        @{ Name = 'python3'; Prefix = @(); Route = 'python3' }
    )
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -ne $command -and -not [string]::IsNullOrWhiteSpace($command.Source)) {
            return [pscustomobject]@{
                Executable = $command.Source
                PrefixArguments = [string[]] $candidate.Prefix
                Route = $candidate.Route
                ExecutableName = [System.IO.Path]::GetFileName($command.Source)
            }
        }
    }
    throw 'No Python 3 Application command found. Tried py -3, python, python3.'
}

$python = Resolve-AtlasPythonApplication
if ($ResolverSelfTest) {
    [pscustomobject]@{
        route = $python.Route
        executable_name = $python.ExecutableName
        prefix_argument_count = $python.PrefixArguments.Count
        invocation = 'native-argument-array'
    } | ConvertTo-Json -Depth 3
    exit 0
}

$scriptRoot = Split-Path -Parent $scriptPath
$resolvedPackage = (Resolve-Path -LiteralPath $PackagePath).Path
$argumentList = [System.Collections.Generic.List[string]]::new()
foreach ($item in $python.PrefixArguments) { $argumentList.Add($item) }
$argumentList.Add('-B')
$argumentList.Add('-m')
$argumentList.Add('spear_bridge.cli')
$argumentList.Add('--package')
$argumentList.Add($resolvedPackage)
$argumentList.Add('--package-sha256')
$argumentList.Add($PackageSha256)
$argumentList.Add('--output-dir')
$argumentList.Add($OutputDirectory)
$argumentList.Add('--spear-bridge-disabled-proof')
$argumentList.Add('--compile-only')
if (-not [string]::IsNullOrWhiteSpace($ReadOnlyRemoteUrl)) {
    $argumentList.Add('--read-only-remote-url')
    $argumentList.Add($ReadOnlyRemoteUrl)
}

Push-Location $scriptRoot
try {
    & $python.Executable @argumentList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
