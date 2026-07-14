from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


HANDOFF_IDENTITY = "OATHBRINGER_FOUNDRY_OPERATOR_HANDOFF_V1"
SAFE_CARRIER = re.compile(r"Oathbringer-Foundry-[A-Za-z0-9._-]+-R[0-9]{2,}\.zip")
SHA256 = re.compile(r"[0-9a-f]{64}")


class HandoffError(RuntimeError):
    """A carrier cannot be presented through the trusted operator handoff."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HandoffError(message)


def _carrier_name(value: Any) -> str:
    name = str(value or "")
    _require(name == Path(name).name, "carrier name must not contain a path")
    _require(SAFE_CARRIER.fullmatch(name) is not None, "carrier name does not match the Foundry contract")
    return name


def _carrier_sha256(value: Any) -> str:
    digest = str(value or "")
    _require(SHA256.fullmatch(digest) is not None, "carrier SHA-256 must be lowercase hexadecimal")
    return digest


def build_operator_command(carrier_name: str, carrier_sha256: str) -> str:
    """Return the canonical PowerShell 7 paste command for one sealed carrier."""

    name = _carrier_name(carrier_name)
    digest = _carrier_sha256(carrier_sha256)
    return f"""Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) {{ throw 'Oathbringer requires PowerShell 7 or newer.' }}
$DownloadRoot = if ($env:ATLAS_OATHBRINGER_DOWNLOADS) {{ $env:ATLAS_OATHBRINGER_DOWNLOADS }} else {{ Join-Path $HOME 'Downloads' }}
$Package = Join-Path $DownloadRoot '{name}'
$ExpectedSha256 = '{digest}'
if (-not (Test-Path -LiteralPath $Package -PathType Leaf)) {{ throw "Oathbringer carrier ZIP is missing: $Package" }}
$ActualSha256 = (Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ActualSha256 -ne $ExpectedSha256) {{ throw "Oathbringer carrier SHA-256 mismatch. Expected $ExpectedSha256, observed $ActualSha256." }}
$Workspace = Join-Path ([System.IO.Path]::GetTempPath()) ('atlas-oathbringer-' + [System.IO.Path]::GetFileNameWithoutExtension($Package) + '-' + [Guid]::NewGuid().ToString('N'))
$EvidenceRoot = Join-Path $DownloadRoot 'Atlas-Oathbringer-Evidence'
New-Item -ItemType Directory -Path $Workspace -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Path $EvidenceRoot -Force -ErrorAction Stop | Out-Null
$Completed = $false
try {{
    Expand-Archive -LiteralPath $Package -DestinationPath $Workspace -ErrorAction Stop
    $Launcher = Join-Path $Workspace 'launcher/Invoke-OathbringerCarrier.ps1'
    if (-not (Test-Path -LiteralPath $Launcher -PathType Leaf)) {{ throw 'The verified carrier is missing its canonical launcher.' }}
    $LauncherInfo = Get-Item -LiteralPath $Launcher -Force
    if (($LauncherInfo.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {{ throw 'The canonical carrier launcher must not be a reparse point.' }}
    $ReceiptPath = Join-Path $EvidenceRoot ([System.IO.Path]::GetFileNameWithoutExtension($Package) + '.receipt.json')
    Push-Location $EvidenceRoot
    try {{
        & $Launcher -ReceiptPath $ReceiptPath
        $ExitCode = $LASTEXITCODE
    }} finally {{
        Pop-Location
    }}
    if ($ExitCode -ne 0) {{ throw "Oathbringer exited with code $ExitCode. Review $EvidenceRoot for the receipt or Deflected Sword." }}
    $Completed = $true
    Write-Host "Oathbringer completed. Evidence: $EvidenceRoot"
}} finally {{
    if ($Completed -and (Test-Path -LiteralPath $Workspace)) {{ Remove-Item -LiteralPath $Workspace -Recurse -Force }}
    elseif (Test-Path -LiteralPath $Workspace) {{ Write-Warning "Oathbringer workspace retained for review: $Workspace" }}
}}
"""


def build_operator_handoff(carrier: Path) -> dict[str, Any]:
    """Read one verified carrier and return its stable one-download handoff."""

    resolved = carrier.resolve()
    _require(resolved.is_file() and not resolved.is_symlink(), "carrier must be a regular file")
    name = _carrier_name(resolved.name)
    digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    return {
        "identity": HANDOFF_IDENTITY,
        "operator_interface": "POWERSHELL_7_PASTE",
        "carrier_name": name,
        "carrier_sha256": digest,
        "download_count": 1,
        "separate_script_download_required": False,
        "operator_command": build_operator_command(name, digest),
    }
