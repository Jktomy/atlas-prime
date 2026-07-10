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

function Invoke-AtlasOathbringerContract {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$MissionPath,
        [Parameter(Mandatory)][string]$ContractPath,
        [Parameter(Mandatory)][string]$PackageRoot,
        [Parameter(Mandatory)][ref]$ExitCode,
        [Parameter()][switch]$Json,
        [Parameter()][string]$ReceiptPath
    )

    $Python = Resolve-AtlasPythonCommand
    [string[]]$Arguments = @()
    $Arguments += [string[]]$Python.PrefixArguments
    $Arguments += [string[]]@(
        '-S',
        '-B',
        $ContractPath,
        '--mission',
        $MissionPath,
        '--audit-only',
        '--package-root',
        $PackageRoot
    )

    if ($Json) {
        $Arguments += '--json'
    }

    if ($ReceiptPath) {
        $Arguments += [string[]]@('--receipt', $ReceiptPath)
    }

    & ([string]$Python.FilePath) @Arguments
    $ExitCode.Value = $LASTEXITCODE
}

Export-ModuleMember -Function @(
    'Initialize-AtlasSwordEncoding',
    'Resolve-AtlasPythonCommand',
    'Invoke-AtlasOathbringerContract'
)
