#requires -Version 7.0
[CmdletBinding()]
param(
    [string] $WeavePath,

    [Parameter(Mandatory = $true)]
    [switch] $FixtureOnly,

    [Parameter(Mandatory = $true)]
    [switch] $AuditOnly,

    [string] $SandboxRoot,

    [switch] $AllowFixtureDelete,

    [string] $DeleteAuthorityId,

    [switch] $ResolverSelfTest
)

$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

if (-not $FixtureOnly -or -not $AuditOnly) {
    throw 'Gate 7B Thread Engine requires explicit -FixtureOnly and -AuditOnly.'
}

$scriptPath = $PSCommandPath
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref] $tokens, [ref] $errors) | Out-Null
if ($errors.Count -ne 0) {
    throw 'PowerShell parser preflight failed for Invoke-AtlasThreadEngine.ps1.'
}

function Resolve-AtlasPythonApplication {
    $candidates = @(
        @{ Name = 'py'; Prefix = @('-3'); Route = 'py -3' },
        @{ Name = 'python'; Prefix = @(); Route = 'python' },
        @{ Name = 'python3'; Prefix = @(); Route = 'python3' }
    )

    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -eq $command) {
            continue
        }
        if ([string]::IsNullOrWhiteSpace($command.Source)) {
            continue
        }
        return [pscustomobject]@{
            Executable = $command.Source
            PrefixArguments = [string[]] $candidate.Prefix
            Route = $candidate.Route
            ExecutableName = [System.IO.Path]::GetFileName($command.Source)
        }
    }

    throw 'No Python 3 Application command found. Tried py -3, python, python3.'
}

$scriptRoot = Split-Path -Parent $scriptPath
$engineFile = Join-Path $scriptRoot 'engine/thread_engine.py'
if (-not (Test-Path -LiteralPath $engineFile)) {
    throw 'Packaged Python Thread Engine core is missing.'
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

if ([string]::IsNullOrWhiteSpace($WeavePath)) {
    throw '-WeavePath is required unless -ResolverSelfTest is supplied.'
}

$resolvedWeave = (Resolve-Path -LiteralPath $WeavePath).Path

$argumentList = [System.Collections.Generic.List[string]]::new()
foreach ($item in $python.PrefixArguments) {
    $argumentList.Add($item)
}
$argumentList.Add('-B')
$argumentList.Add('-m')
$argumentList.Add('engine.thread_engine')
$argumentList.Add('--weave')
$argumentList.Add($resolvedWeave)
$argumentList.Add('--fixture-only')
$argumentList.Add('--audit-only')

if ($SandboxRoot) {
    $argumentList.Add('--sandbox-root')
    $argumentList.Add((Resolve-Path -LiteralPath $SandboxRoot).Path)
}
if ($AllowFixtureDelete) {
    $argumentList.Add('--allow-fixture-delete')
}
if ($DeleteAuthorityId) {
    $argumentList.Add('--delete-authority-id')
    $argumentList.Add($DeleteAuthorityId)
}

Push-Location $scriptRoot
try {
    & $python.Executable @argumentList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
