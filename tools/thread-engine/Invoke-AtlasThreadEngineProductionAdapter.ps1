#requires -Version 7.0
[CmdletBinding()]
param(
    [string] $MissionPath,

    [string] $MissionSha256,

    [switch] $MissionScopedDraftPr,

    [switch] $ExecuteDraftPr,

    [switch] $AegisBreakProtectedRoute,

    [string] $AegisBreakAuthorityId,

    [switch] $GeneratedCheckpointRoute,

    [string] $WorkRoot,

    [switch] $ResolverSelfTest
)

$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$scriptPath = $PSCommandPath
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref] $tokens, [ref] $errors) | Out-Null
if ($errors.Count -ne 0) {
    throw 'PowerShell parser preflight failed for Invoke-AtlasThreadEngineProductionAdapter.ps1.'
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
$adapterModule = Join-Path $scriptRoot 'production_adapter/cli.py'
if (-not (Test-Path -LiteralPath $adapterModule -PathType Leaf)) {
    throw 'Packaged Python production adapter CLI is missing.'
}

$python = Resolve-AtlasPythonApplication

if ($ResolverSelfTest) {
    [pscustomobject]@{
        route = $python.Route
        executable_name = $python.ExecutableName
        prefix_argument_count = $python.PrefixArguments.Count
        invocation = 'native-argument-array'
        implementation_state = 'THREAD_ENGINE_ACTIVE_MISSION_SCOPED'
    } | ConvertTo-Json -Depth 3
    exit 0
}

if ([string]::IsNullOrWhiteSpace($MissionPath)) {
    throw 'Thread Engine production adapter requires a mission path.'
}
if (-not $MissionScopedDraftPr -or -not $ExecuteDraftPr) {
    throw 'Thread Engine production adapter requires explicit mission-scoped and draft-PR-only intent.'
}
if ($AegisBreakProtectedRoute -and [string]::IsNullOrWhiteSpace($AegisBreakAuthorityId)) {
    throw 'Aegis Break protected-route intent requires an exact authority id.'
}
if (-not $AegisBreakProtectedRoute -and -not ([string]::IsNullOrWhiteSpace($AegisBreakAuthorityId))) {
    throw 'Aegis Break authority id requires protected-route intent.'
}
if ($AegisBreakProtectedRoute -and $GeneratedCheckpointRoute) {
    throw 'Aegis Break and generated checkpoint intents are mutually exclusive.'
}

$resolvedMission = (Resolve-Path -LiteralPath $MissionPath).Path
$argumentList = [System.Collections.Generic.List[string]]::new()
foreach ($item in $python.PrefixArguments) {
    $argumentList.Add($item)
}
$argumentList.Add('-B')
$argumentList.Add('-m')
$argumentList.Add('production_adapter.cli')
$argumentList.Add('--mission')
$argumentList.Add($resolvedMission)
if ($MissionSha256) {
    $argumentList.Add('--mission-sha256')
    $argumentList.Add($MissionSha256)
}
$argumentList.Add('--mission-scoped-draft-pr')
$argumentList.Add('--execute-draft-pr')
if ($AegisBreakProtectedRoute) {
    $argumentList.Add('--aegis-break-protected-route')
    $argumentList.Add('--aegis-break-authority-id')
    $argumentList.Add($AegisBreakAuthorityId)
}
if ($GeneratedCheckpointRoute) {
    $argumentList.Add('--generated-checkpoint-route')
}

if ($WorkRoot) {
    try {
        $resolvedWorkRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($WorkRoot)
    }
    catch {
        throw 'WorkRoot could not be resolved as a filesystem path.'
    }
    if (Test-Path -LiteralPath $resolvedWorkRoot -PathType Leaf) {
        throw 'WorkRoot must be a directory path.'
    }
    try {
        [System.IO.Directory]::CreateDirectory($resolvedWorkRoot) | Out-Null
    }
    catch {
        throw 'WorkRoot directory could not be created.'
    }
    if (-not (Test-Path -LiteralPath $resolvedWorkRoot -PathType Container)) {
        throw 'WorkRoot directory was not created.'
    }
    $argumentList.Add('--work-root')
    $argumentList.Add($resolvedWorkRoot)
}

Push-Location $scriptRoot
try {
    & $python.Executable @argumentList
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
