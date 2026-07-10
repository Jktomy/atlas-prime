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
    'Invoke-AtlasOathbringer'
)
