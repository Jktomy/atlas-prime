Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Initialize-AtlasSwordEncoding {
    [CmdletBinding()]
    param()

    $Utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    [Console]::InputEncoding = $Utf8
    [Console]::OutputEncoding = $Utf8
    $script:OutputEncoding = $Utf8
}

function Resolve-AtlasPythonCommand {
    [CmdletBinding()]
    param()

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $Python) {
        return [pscustomobject]@{
            FilePath = $Python.Source
            PrefixArguments = [string[]]@()
        }
    }

    $Py = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $Py) {
        return [pscustomobject]@{
            FilePath = $Py.Source
            PrefixArguments = [string[]]@('-3')
        }
    }

    throw 'Python 3 was not found.'
}

function Resolve-AtlasGitHubToken {
    [CmdletBinding()]
    param()

    foreach ($Name in @('OATHBRINGER_GITHUB_TOKEN', 'GH_TOKEN', 'GITHUB_TOKEN')) {
        $Value = [Environment]::GetEnvironmentVariable($Name, 'Process')
        if (-not [string]::IsNullOrWhiteSpace($Value)) {
            return [string]$Value
        }
    }

    $Gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -eq $Gh) {
        throw 'No GitHub token was found and GitHub CLI is unavailable. Authenticate with gh auth login or provide GH_TOKEN for this process.'
    }

    $Token = (& ([string]$Gh.Source) auth token 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($Token)) {
        throw 'GitHub CLI could not provide an authenticated token.'
    }

    return $Token
}

function ConvertTo-AtlasSafeFileName {
    [CmdletBinding()]
    param(
        [Parameter()][string]$Value,
        [Parameter()][string]$Fallback = 'mission'
    )

    $Safe = [regex]::Replace([string]$Value, '[^A-Za-z0-9._-]+', '-').Trim('-', '.')
    if ([string]::IsNullOrWhiteSpace($Safe)) {
        return $Fallback
    }
    return $Safe
}

function New-AtlasDeflectedSword {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$PackageRoot,
        [Parameter(Mandatory)][string]$MissionPath,
        [Parameter(Mandatory)][string]$ReceiptPath,
        [Parameter()][string]$TranscriptPath,
        [Parameter()][string]$OutputPath
    )

    $ResolvedPackageRoot = (Resolve-Path -LiteralPath $PackageRoot).Path
    $ResolvedMissionPath = (Resolve-Path -LiteralPath $MissionPath).Path
    $Mission = Get-Content -LiteralPath $ResolvedMissionPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $MissionId = ConvertTo-AtlasSafeFileName -Value ([string]$Mission.mission_id) -Fallback 'mission'
    $SwordIdentity = [string]$Mission.sword_identity
    $Revision = 'r00'
    if ($SwordIdentity -match '(?i)(r[0-9]+)$') {
        $Revision = $Matches[1].ToLowerInvariant()
    }

    if ([string]::IsNullOrWhiteSpace($OutputPath)) {
        $DestinationDirectory = Split-Path -Parent $ReceiptPath
        if ([string]::IsNullOrWhiteSpace($DestinationDirectory)) {
            $DestinationDirectory = (Get-Location).Path
        }
        $OutputPath = Join-Path $DestinationDirectory "Atlas-Deflected-Sword-$MissionId-$Revision.zip"
    }

    $OutputDirectory = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($OutputDirectory)) {
        New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    }
    $OutputPath = [System.IO.Path]::GetFullPath($OutputPath)

    $EvidenceRoot = Join-Path $env:TEMP ('Atlas-Deflected-Sword-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $EvidenceRoot -Force | Out-Null
    try {
        $ReceiptObject = $null
        if (Test-Path -LiteralPath $ReceiptPath -PathType Leaf) {
            Copy-Item -LiteralPath $ReceiptPath -Destination (Join-Path $EvidenceRoot 'receipt.json') -Force
            $ReceiptObject = Get-Content -LiteralPath $ReceiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        $ReceiptSidecar = "$ReceiptPath.sha256"
        if (Test-Path -LiteralPath $ReceiptSidecar -PathType Leaf) {
            Copy-Item -LiteralPath $ReceiptSidecar -Destination (Join-Path $EvidenceRoot 'receipt.json.sha256') -Force
        }
        if (-not [string]::IsNullOrWhiteSpace($TranscriptPath) -and (Test-Path -LiteralPath $TranscriptPath -PathType Leaf)) {
            Copy-Item -LiteralPath $TranscriptPath -Destination (Join-Path $EvidenceRoot 'terminal-output.txt') -Force
        }

        Copy-Item -LiteralPath $ResolvedMissionPath -Destination (Join-Path $EvidenceRoot 'mission.json') -Force
        foreach ($Name in @('MANIFEST.json', 'FORGE-RECEIPT.json', 'README-FIRST.txt', 'README-FIRST.md')) {
            $Candidate = Join-Path $ResolvedPackageRoot $Name
            if (Test-Path -LiteralPath $Candidate -PathType Leaf) {
                Copy-Item -LiteralPath $Candidate -Destination (Join-Path $EvidenceRoot $Name) -Force
            }
        }

        if ($null -ne $Mission.independent_audit -and -not [string]::IsNullOrWhiteSpace([string]$Mission.independent_audit.receipt_path)) {
            $AuditCandidate = Join-Path $ResolvedPackageRoot ([string]$Mission.independent_audit.receipt_path)
            if (Test-Path -LiteralPath $AuditCandidate -PathType Leaf) {
                Copy-Item -LiteralPath $AuditCandidate -Destination (Join-Path $EvidenceRoot 'independent-audit.json') -Force
            }
        }

        $Status = if ($null -eq $ReceiptObject) { 'RECEIPT_UNAVAILABLE' } else { [string]$ReceiptObject.status }
        $Detail = if ($null -eq $ReceiptObject) { 'The durable receipt was not available.' } else { [string]$ReceiptObject.detail }
        $CurrentStage = if ($null -eq $ReceiptObject) { 'UNKNOWN' } else { [string]$ReceiptObject.stage_ledger.current_stage }
        $LastCompletedStage = if ($null -eq $ReceiptObject) { 'UNKNOWN' } else { [string]$ReceiptObject.stage_ledger.last_completed_stage }
        $MutationPerformed = if ($null -eq $ReceiptObject) { 'UNKNOWN' } elseif ($ReceiptObject.completion_flags.mutation_performed) { 'YES' } else { 'NO' }
        @(
            'ATLAS DEFLECTED SWORD',
            "Mission: $($Mission.mission_id)",
            "Sword: $($Mission.sword_identity)",
            "Lane: $($Mission.lane)",
            "Repository: $($Mission.repository)",
            "Status: $Status",
            "Failed stage: $CurrentStage",
            "Last completed stage: $LastCompletedStage",
            "Mutation performed: $MutationPerformed",
            "Detail: $Detail",
            'Automatic retry: NO',
            'Automatic rollback: NO',
            "Generated UTC: $([DateTime]::UtcNow.ToString('o'))"
        ) | Set-Content -LiteralPath (Join-Path $EvidenceRoot 'failure-summary.txt') -Encoding UTF8

        if ($null -ne $ReceiptObject) {
            $ReceiptObject.remote_state | ConvertTo-Json -Depth 64 | Set-Content -LiteralPath (Join-Path $EvidenceRoot 'sanitized-remote-state.json') -Encoding UTF8
            $WorkflowState = if ($null -ne $ReceiptObject.result -and $null -ne $ReceiptObject.result.workflow_gate) { $ReceiptObject.result.workflow_gate } else { [pscustomobject]@{} }
            $WorkflowState | ConvertTo-Json -Depth 64 | Set-Content -LiteralPath (Join-Path $EvidenceRoot 'workflow-state.json') -Encoding UTF8
        }
        else {
            '{}' | Set-Content -LiteralPath (Join-Path $EvidenceRoot 'sanitized-remote-state.json') -Encoding UTF8
            '{}' | Set-Content -LiteralPath (Join-Path $EvidenceRoot 'workflow-state.json') -Encoding UTF8
        }

        if (Test-Path -LiteralPath $OutputPath -PathType Leaf) {
            Remove-Item -LiteralPath $OutputPath -Force
        }
        Compress-Archive -Path (Join-Path $EvidenceRoot '*') -DestinationPath $OutputPath -Force
        return $OutputPath
    }
    finally {
        Remove-Item -LiteralPath $EvidenceRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-AtlasOathbringer {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$MissionPath,
        [Parameter(Mandatory)][string]$AuditContractPath,
        [Parameter(Mandatory)][string]$ProductionContractPath,
        [Parameter(Mandatory)][string]$PackageRoot,
        [Parameter(Mandatory)][ref]$ExitCode,
        [Parameter()][switch]$AuditOnly,
        [Parameter()][switch]$Json,
        [Parameter()][string]$ReceiptPath
    )

    $Python = Resolve-AtlasPythonCommand
    [string[]]$Arguments = @()
    $Arguments += [string[]]$Python.PrefixArguments
    $Arguments += [string[]]@('-S', '-B')

    if ($AuditOnly) {
        $Arguments += [string[]]@(
            $AuditContractPath,
            '--mission',
            $MissionPath,
            '--audit-only',
            '--package-root',
            $PackageRoot
        )
    }
    else {
        $Arguments += [string[]]@(
            $ProductionContractPath,
            '--mission',
            $MissionPath,
            '--package-root',
            $PackageRoot
        )
    }

    if ($Json) {
        $Arguments += '--json'
    }

    if ($ReceiptPath) {
        $Arguments += [string[]]@('--receipt', $ReceiptPath)
    }

    $PriorToken = [Environment]::GetEnvironmentVariable('OATHBRINGER_GITHUB_TOKEN', 'Process')
    try {
        if (-not $AuditOnly) {
            $Token = Resolve-AtlasGitHubToken
            [Environment]::SetEnvironmentVariable(
                'OATHBRINGER_GITHUB_TOKEN',
                $Token,
                'Process'
            )
        }

        & ([string]$Python.FilePath) @Arguments
        $ExitCode.Value = $LASTEXITCODE
    }
    finally {
        if ($null -eq $PriorToken) {
            [Environment]::SetEnvironmentVariable(
                'OATHBRINGER_GITHUB_TOKEN',
                $null,
                'Process'
            )
        }
        else {
            [Environment]::SetEnvironmentVariable(
                'OATHBRINGER_GITHUB_TOKEN',
                $PriorToken,
                'Process'
            )
        }
    }
}

Export-ModuleMember -Function @(
    'Initialize-AtlasSwordEncoding',
    'Resolve-AtlasPythonCommand',
    'Resolve-AtlasGitHubToken',
    'ConvertTo-AtlasSafeFileName',
    'New-AtlasDeflectedSword',
    'Invoke-AtlasOathbringer'
)
