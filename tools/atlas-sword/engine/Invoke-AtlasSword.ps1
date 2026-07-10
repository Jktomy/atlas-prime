[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$MissionPath,

    [Parameter()]
    [switch]$AuditOnly,

    [Parameter()]
    [switch]$Json,

    [Parameter()]
    [string]$ReceiptPath,

    [Parameter()]
    [string]$DeflectedSwordPath,

    [Parameter()]
    [switch]$NoColor,

    [Parameter()]
    [switch]$Ascii
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageRoot = Split-Path -Parent $ScriptRoot
$ModulePath = Join-Path $ScriptRoot 'AtlasSword.Common.psm1'
$AuditContractPath = Join-Path $ScriptRoot 'oathbringer_contract.py'
$ProductionContractPath = Join-Path $ScriptRoot 'oathbringer_github.py'

# Schema 1.2 compatibility: -AuditOnly is mandatory inside the audit contract.
# Historical audit adapter identity retained for static readback: Invoke-AtlasOathbringerContract.

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
if ([string]::IsNullOrWhiteSpace($ReceiptPath)) {
    $MissionDirectory = Split-Path -Parent $ResolvedMissionPath
    $MissionStem = [System.IO.Path]::GetFileNameWithoutExtension($ResolvedMissionPath)
    $ReceiptPath = Join-Path $MissionDirectory "$MissionStem.oathbringer.receipt.json"
}
else {
    $ReceiptPath = [System.IO.Path]::GetFullPath($ReceiptPath)
}
$ReceiptDirectory = Split-Path -Parent $ReceiptPath
New-Item -ItemType Directory -Path $ReceiptDirectory -Force | Out-Null
$TranscriptPath = Join-Path $ReceiptDirectory ([System.IO.Path]::GetFileNameWithoutExtension($ReceiptPath) + '.terminal-output.txt')

$PriorColorMode = [Environment]::GetEnvironmentVariable('OATHBRINGER_COLOR', 'Process')
$PriorUnicodeMode = [Environment]::GetEnvironmentVariable('OATHBRINGER_UNICODE', 'Process')
if ($NoColor) {
    [Environment]::SetEnvironmentVariable('OATHBRINGER_COLOR', 'never', 'Process')
}
if ($Ascii) {
    [Environment]::SetEnvironmentVariable('OATHBRINGER_UNICODE', 'never', 'Process')
}

$ExitCode = 1
$InvocationError = $null
$TranscriptStarted = $false
try {
    try {
        Start-Transcript -LiteralPath $TranscriptPath -Force | Out-Null
        $TranscriptStarted = $true
    }
    catch {
        $TranscriptStarted = $false
    }

    try {
        Invoke-AtlasOathbringer `
            -MissionPath $ResolvedMissionPath `
            -AuditContractPath $AuditContractPath `
            -ProductionContractPath $ProductionContractPath `
            -PackageRoot $PackageRoot `
            -ExitCode ([ref]$ExitCode) `
            -AuditOnly:$AuditOnly `
            -Json:$Json `
            -ReceiptPath $ReceiptPath
    }
    catch {
        $InvocationError = $_
        $ExitCode = 1
    }
}
finally {
    if ($TranscriptStarted) {
        try { Stop-Transcript | Out-Null } catch {}
    }
    [Environment]::SetEnvironmentVariable('OATHBRINGER_COLOR', $PriorColorMode, 'Process')
    [Environment]::SetEnvironmentVariable('OATHBRINGER_UNICODE', $PriorUnicodeMode, 'Process')
}

if ($ExitCode -ne 0) {
    $Deflected = $null
    try {
        $Deflected = New-AtlasDeflectedSword `
            -PackageRoot $PackageRoot `
            -MissionPath $ResolvedMissionPath `
            -ReceiptPath $ReceiptPath `
            -TranscriptPath $TranscriptPath `
            -OutputPath $DeflectedSwordPath
        Write-Host ''
        Write-Host '╔══════════════════════════════════════════════════════════════╗' -ForegroundColor Red
        Write-Host '║                     STRIKE DEFLECTED                         ║' -ForegroundColor Red
        Write-Host '╚══════════════════════════════════════════════════════════════╝' -ForegroundColor Red
        Write-Host ''
        Write-Host "Deflected Sword: $Deflected" -ForegroundColor Yellow
        Write-Host 'Paste the diagnostic block first; upload the Deflected Sword only if deeper forensics are needed.' -ForegroundColor Cyan
    }
    catch {
        Write-Warning "The Deflected Sword could not be created: $($_.Exception.Message)"
        Write-Warning "Durable receipt: $ReceiptPath"
    }

    if ($null -ne $InvocationError) {
        throw $InvocationError
    }
    throw "Oathbringer failed (exit $ExitCode). Review the terminal diagnostics or Deflected Sword before repair or recovery."
}
