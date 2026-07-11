[CmdletBinding()]
param(
    [Parameter(Mandatory, ParameterSetName = 'Compile')][string]$InputRoot,
    [Parameter(Mandatory, ParameterSetName = 'Compile')][string]$OutputDir,
    [Parameter(Mandatory, ParameterSetName = 'Compile')][string]$EvidenceZip,
    [Parameter(ParameterSetName = 'Compile')][string]$SourceRoot = (Join-Path $PSScriptRoot '..\..'),
    [Parameter(Mandatory, ParameterSetName = 'Verify')][string]$VerifyEvidenceZip,
    [Parameter(Mandatory, ParameterSetName = 'Resolver')][switch]$ResolverSelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'delivery_standard.py'

if ($ResolverSelfTest) {
    $Repository = 'Jktomy/atlas-prime'
    $ProbePath = '.github/workflows/prime-readonly-validation.yml'
    $ExactRef = '0000000000000000000000000000000000000000'
    $Query = "repos/${Repository}/contents/${ProbePath}?ref=${ExactRef}"
    [ordered]@{
        identity = 'CONSISTENT_PR_DELIVERY_STANDARD_R01'
        invocation = 'native-argument-array'
        strict_mode_query = $Query
        workflow_platforms = @('ubuntu-latest', 'windows-latest')
    } | ConvertTo-Json -Compress
    exit 0
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction Stop }
$arguments = @('-B', $scriptPath)
if ($PSCmdlet.ParameterSetName -eq 'Verify') {
    $arguments += @('verify-evidence', '--evidence-zip', $VerifyEvidenceZip)
} else {
    $resolvedInput = (Resolve-Path -LiteralPath $InputRoot).Path
    $resolvedSource = (Resolve-Path -LiteralPath $SourceRoot).Path
    $arguments += @(
        'compile',
        '--input-root', $resolvedInput,
        '--source-root', $resolvedSource,
        '--output-dir', $OutputDir,
        '--evidence-zip', $EvidenceZip
    )
}
if ($python.Name -eq 'py.exe') { $arguments = @('-3') + $arguments }
& $python.Source @arguments
exit $LASTEXITCODE
