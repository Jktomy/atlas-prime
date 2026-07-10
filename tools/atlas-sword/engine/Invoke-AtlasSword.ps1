[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$MissionPath,

    [Parameter()]
    [switch]$AuditOnly,

    [Parameter()]
    [switch]$Json,

    [Parameter()]
    [string]$ReceiptPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
$ModulePath = Join-Path $ScriptRoot 'AtlasSword.Common.psm1'
$AuditContractPath = Join-Path $ScriptRoot 'oathbringer_contract.py'
$ProductionContractPath = Join-Path $ScriptRoot 'oathbringer_github.py'

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
Invoke-AtlasOathbringer `
    -MissionPath $ResolvedMissionPath `
    -AuditContractPath $AuditContractPath `
    -ProductionContractPath $ProductionContractPath `
    -PackageRoot $PackageRoot `
    -ExitCode ([ref]$ExitCode) `
    -AuditOnly:$AuditOnly `
    -Json:$Json `
    -ReceiptPath $ReceiptPath

if ($ExitCode -ne 0) {
    throw "Oathbringer failed (exit $ExitCode). Review the durable receipt before repair or recovery."
}
