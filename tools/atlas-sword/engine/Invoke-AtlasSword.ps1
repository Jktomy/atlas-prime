[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$MissionPath,

    [Parameter(Mandatory)]
    [switch]$AuditOnly,

    [Parameter()]
    [switch]$Json,

    [Parameter()]
    [string]$ReceiptPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $AuditOnly) {
    throw 'This framework is PILOT_DISABLED. -AuditOnly is mandatory.'
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
$ModulePath = Join-Path $ScriptRoot 'AtlasSword.Common.psm1'
$ContractPath = Join-Path $ScriptRoot 'oathbringer_contract.py'

foreach ($PowerShellPath in @($MyInvocation.MyCommand.Path, $ModulePath)) {
    $Tokens = $null
    $ParseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $PowerShellPath,
        [ref]$Tokens,
        [ref]$ParseErrors
    ) | Out-Null

    if ($ParseErrors.Count -gt 0) {
        throw "PowerShell parser preflight failed: $($ParseErrors[0].Message)"
    }
}

Import-Module $ModulePath -Force
Initialize-AtlasSwordEncoding

$ResolvedMissionPath = (Resolve-Path -LiteralPath $MissionPath).Path
$ExitCode = 1
Invoke-AtlasOathbringerContract `
    -MissionPath $ResolvedMissionPath `
    -ContractPath $ContractPath `
    -PackageRoot $PackageRoot `
    -ExitCode ([ref]$ExitCode) `
    -Json:$Json `
    -ReceiptPath $ReceiptPath

if ($ExitCode -ne 0) {
    throw "Oathbringer contract failed (exit $ExitCode)."
}
