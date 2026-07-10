from __future__ import annotations

import os
import sys
import time
from typing import Any, TextIO


ANSI = {
    "reset": "\x1b[0m",
    "bold": "\x1b[1m",
    "dim": "\x1b[2m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "gray": "\x1b[90m",
}

STAGE_ORDER = {
    "BUILD": [
        "MISSION_CONTRACT",
        "PACKAGE_INTEGRITY",
        "LIVE_IDENTITY",
        "TREE_READBACK",
        "PAYLOAD_AND_BLOBS",
        "CANDIDATE_TREE",
        "COMMIT",
        "BRANCH_AND_PR",
        "REMOTE_READBACK",
        "WORKFLOW_GATE",
        "STOP_BOUNDARY",
    ],
    "REPAIR": [
        "MISSION_CONTRACT",
        "PACKAGE_INTEGRITY",
        "LIVE_IDENTITY",
        "TREE_READBACK",
        "PAYLOAD_AND_BLOBS",
        "CANDIDATE_TREE",
        "COMMIT",
        "BRANCH_AND_PR",
        "REMOTE_READBACK",
        "WORKFLOW_GATE",
        "STOP_BOUNDARY",
    ],
    "EXECUTE": [
        "MISSION_CONTRACT",
        "PACKAGE_INTEGRITY",
        "LIVE_IDENTITY",
        "WORKFLOW_GATE",
        "INDEPENDENT_AUDIT",
        "READY_TRANSITION",
        "MERGE",
        "MERGED_READBACK",
        "STOP_BOUNDARY",
    ],
}


def _short_sha(value: Any) -> str:
    text = str(value or "")
    return text if len(text) <= 12 else f"{text[:12]}…"


def _elapsed_text(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class OathbringerConsole:
    """Presentation-only console for Oathbringer.

    This class never makes execution decisions. It only renders already-authoritative
    mission, stage, workflow, and result data.
    """

    def __init__(
        self,
        *,
        stream: TextIO | None = None,
        color: bool | None = None,
        unicode: bool | None = None,
        monotonic=time.monotonic,
    ) -> None:
        self.stream = stream or sys.stdout
        self._monotonic = monotonic
        self.color_enabled = self._resolve_color(color)
        self.unicode_enabled = self._resolve_unicode(unicode)
        self.started_at = self._monotonic()
        self.mission: dict[str, Any] = {}
        self._last_heartbeat_at = -10_000.0
        self._last_heartbeat_signature: tuple[Any, ...] | None = None

    def _resolve_color(self, explicit: bool | None) -> bool:
        if explicit is not None:
            return explicit
        mode = os.environ.get("OATHBRINGER_COLOR", "auto").strip().lower()
        if mode in {"always", "1", "true", "yes", "on"}:
            return True
        if mode in {"never", "0", "false", "no", "off"}:
            return False
        if "NO_COLOR" in os.environ or os.environ.get("TERM", "").lower() == "dumb":
            return False
        isatty = getattr(self.stream, "isatty", None)
        return bool(isatty and isatty())

    def _resolve_unicode(self, explicit: bool | None) -> bool:
        if explicit is not None:
            return explicit
        mode = os.environ.get("OATHBRINGER_UNICODE", "auto").strip().lower()
        if mode in {"always", "1", "true", "yes", "on"}:
            return True
        if mode in {"never", "0", "false", "no", "off"}:
            return False
        encoding = str(getattr(self.stream, "encoding", "") or "").lower()
        return "utf" in encoding

    def _style(self, text: str, *styles: str) -> str:
        if not self.color_enabled or not styles:
            return text
        prefix = "".join(ANSI[name] for name in styles)
        return f"{prefix}{text}{ANSI['reset']}"

    def _write(self, text: str = "") -> None:
        print(text, file=self.stream, flush=True)

    def _symbols(self) -> dict[str, str]:
        if self.unicode_enabled:
            return {
                "check": "✓",
                "active": "▶",
                "pending": "○",
                "wait": "◐",
                "sword": "⚔",
                "dot": "•",
                "ellipsis": "…",
                "h": "═",
                "v": "║",
                "tl": "╔",
                "tr": "╗",
                "bl": "╚",
                "br": "╝",
                "fill": "█",
                "empty": "░",
            }
        return {
            "check": "[OK]",
            "active": ">",
            "pending": "-",
            "wait": "~",
            "sword": "/\\",
            "dot": "|",
            "ellipsis": "...",
            "h": "=",
            "v": "|",
            "tl": "+",
            "tr": "+",
            "bl": "+",
            "br": "+",
            "fill": "#",
            "empty": ".",
        }

    def _box(self, title: str, *, style: str = "cyan", width: int = 62) -> None:
        s = self._symbols()
        top = s["tl"] + s["h"] * width + s["tr"]
        bottom = s["bl"] + s["h"] * width + s["br"]
        inner = f" {title} "
        if len(inner) > width:
            inner = inner[:width]
        left = max(0, (width - len(inner)) // 2)
        right = max(0, width - len(inner) - left)
        middle = s["v"] + " " * left + inner + " " * right + s["v"]
        self._write(self._style(top, style, "bold"))
        self._write(self._style(middle, style, "bold"))
        self._write(self._style(bottom, style, "bold"))

    def _field(self, label: str, value: Any, *, style: str | None = None) -> None:
        value_text = str(value if value not in {None, ""} else "—")
        label_text = self._style(f"  {label:<12}", "dim")
        if style:
            value_text = self._style(value_text, style)
        self._write(f"{label_text}{value_text}")

    def begin(self, mission: dict[str, Any]) -> None:
        self.mission = mission
        self.started_at = self._monotonic()
        s = self._symbols()
        self._write()
        self._box(f"{s['sword']}  O A T H B R I N G E R  {s['sword']}", style="cyan")
        self._write(self._style("                    ATLAS REPOSITORY STRIKE", "bold"))
        self._write()
        self._field("MISSION", mission.get("mission_id"), style="cyan")
        self._field("SWORD", mission.get("sword_identity"), style="magenta")
        self._field("LANE", mission.get("lane"), style="magenta")
        self._field("TARGET", mission.get("repository"))
        self._field("BASE", _short_sha(mission.get("expected_base")), style="gray")
        if mission.get("expected_head"):
            self._field("EXACT HEAD", _short_sha(mission.get("expected_head")), style="gray")
        if mission.get("pull_request"):
            self._field("PULL REQ", f"#{mission['pull_request']}")
        self._field("OPERATOR", mission.get("authorization", {}).get("github_login"))
        self._field("AUTHORITY", "JAYSON — EXECUTE APPROVED" if self.unicode_enabled else "JAYSON - EXECUTE APPROVED", style="green")
        self._write()
        self._write(self._style("  SAFETY SEAL", "bold", "cyan"))
        forbidden = set(mission.get("forbidden_actions") or [])
        safety = [
            ("DIRECT_MAIN" in forbidden, "Direct main write blocked"),
            ("FORCE_PUSH" in forbidden, "Force push blocked"),
            ("SCOPE_WIDENING" in forbidden, "Scope widening blocked"),
            ("TOKEN_PERSISTENCE" in forbidden, "Token persistence blocked"),
        ]
        for enabled, label in safety:
            icon = s["check"] if enabled else "!"
            style = "green" if enabled else "yellow"
            self._write(self._style(f"  {icon} {label}", style))
        self._write()

    def _progress_bar(self, percent: int, width: int = 28) -> str:
        s = self._symbols()
        filled = min(width, max(0, round(width * percent / 100)))
        return f"[{s['fill'] * filled}{s['empty'] * (width - filled)}]"

    def stage_enter(self, stage: str, percent: int, message: str) -> None:
        s = self._symbols()
        lane = str(self.mission.get("lane") or "BUILD")
        stages = STAGE_ORDER.get(lane, [])
        try:
            index = stages.index(stage) + 1
        except ValueError:
            index = 0
        sequence = f"{index:02d}/{len(stages):02d}" if stages else "--/--"
        progress = self._style(self._progress_bar(percent), "cyan")
        self._write(f"  {progress} {self._style(f'{percent:>3}%', 'bold')}  {self._style(sequence, 'dim')}")
        self._write(f"  {self._style(s['active'], 'cyan', 'bold')} {self._style(stage, 'cyan', 'bold')}  {message}")

    def stage_complete(self, detail: str) -> None:
        s = self._symbols()
        self._write(self._style(f"    {s['check']} {detail}", "green"))
        self._write()

    def workflow_heartbeat(self, snapshot: dict[str, Any]) -> None:
        now = self._monotonic()
        elapsed = float(snapshot.get("elapsed_seconds") or 0.0)
        states = snapshot.get("required") or {}
        signature = tuple(
            (name, str(item.get("status") or ""), item.get("run_id"), item.get("conclusion"))
            for name, item in sorted(states.items())
        )
        changed = signature != self._last_heartbeat_signature
        if not changed and now - self._last_heartbeat_at < 9.0:
            return
        self._last_heartbeat_at = now
        self._last_heartbeat_signature = signature
        s = self._symbols()
        self._write(self._style(f"    {s['wait']} WORKFLOW HEARTBEAT  {_elapsed_text(elapsed)} elapsed", "yellow", "bold"))
        for name, item in sorted(states.items()):
            status = str(item.get("status") or "UNKNOWN").upper()
            if status == "COMPLETED" and item.get("conclusion") == "success":
                icon, style, text = s["check"], "green", "PASSED"
            elif status == "COMPLETED":
                icon, style, text = "!", "red", f"{item.get('conclusion') or 'FAILED'}"
            elif status in {"IN_PROGRESS", "QUEUED", "PENDING"}:
                icon, style, text = s["active"], "cyan", status.replace("_", " ")
            else:
                icon, style, text = s["wait"], "yellow", status.replace("_", " ")
            run = f"  run {item['run_id']}" if item.get("run_id") else ""
            self._write(f"      {self._style(icon, style)} {name:<32} {self._style(text, style)}{self._style(run, 'dim')}")
        self._write(self._style("      GitHub is responding. Oathbringer is not frozen.", "dim"))
        self._write()

    def _workflow_ids(self, result: dict[str, Any]) -> list[str]:
        gate = result.get("workflow_gate") or {}
        required = gate.get("required") or {}
        values: list[str] = []
        for name, item in sorted(required.items()):
            run = item.get("run") or {}
            run_id = run.get("id") or run.get("databaseId")
            if run_id:
                values.append(f"{name} #{run_id}")
        return values

    def render_success(self, result: dict[str, Any]) -> None:
        self._write()
        self._box("STRIKE COMPLETE", style="green")
        self._write()
        self._field("RESULT", result.get("status"), style="green")
        self._field("MISSION", result.get("mission_id"))
        self._field("LANE", result.get("lane"), style="magenta")
        self._field("REPOSITORY", result.get("repository"))
        self._field("PULL REQ", f"#{result['pull_request']}" if result.get("pull_request") else None)
        self._field("BASE", _short_sha(result.get("expected_base") or self.mission.get("expected_base")), style="gray")
        prior = result.get("prior_head") or result.get("audited_head")
        if prior:
            self._field("PRIOR HEAD", _short_sha(prior), style="gray")
        new_head = result.get("commit_sha") or result.get("merge_sha")
        self._field("NEW HEAD", _short_sha(new_head), style="gray")
        changed_paths = list(result.get("changed_paths") or [])
        self._field("PATHS", f"{len(changed_paths)} verified")
        workflows = self._workflow_ids(result)
        self._field("CI", "GREEN" if result.get("workflow_gate", {}).get("status") == "PASS" else "NOT APPLICABLE", style="green")
        self._field("MUTATION", "YES" if result.get("completion_flags", {}).get("mutation_performed") else "NO")
        self._field("ELAPSED", _elapsed_text(self._monotonic() - self.started_at))
        self._write()
        self._write(self._style("  VERIFIED PATHS", "bold", "cyan"))
        if changed_paths:
            for path in changed_paths:
                self._write(f"    - {path}")
        else:
            self._write("    - none")
        if workflows:
            self._write()
            self._write(self._style("  WORKFLOW RUNS", "bold", "cyan"))
            for item in workflows:
                self._write(f"    - {item}")
        self._write()
        self._write(self._style("  STOP BOUNDARY", "bold", "cyan"))
        self._write(f"    {result.get('stop_boundary')}")
        self._write()
        self._write(self._style("--- OATHBRINGER RESULT BLOCK ---", "cyan", "bold"))
        copy_fields = [
            ("Mission", result.get("mission_id")),
            ("Sword", result.get("sword_identity")),
            ("Lane", result.get("lane")),
            ("Repository", result.get("repository")),
            ("Result", result.get("status")),
            ("Pull request", result.get("pull_request")),
            ("Commit / merge", new_head),
            ("Changed paths", ", ".join(changed_paths) if changed_paths else "none"),
            ("Workflow runs", ", ".join(workflows) if workflows else "none / not applicable"),
            ("Mutation performed", "YES" if result.get("completion_flags", {}).get("mutation_performed") else "NO"),
            ("Stop boundary", result.get("stop_boundary")),
        ]
        for label, value in copy_fields:
            self._write(f"{label}: {value}")
        self._write(self._style("--- END RESULT BLOCK ---", "cyan", "bold"))

    def render_failure(self, receipt: dict[str, Any], *, interrupted: bool = False) -> None:
        self._write()
        self._box("STRIKE INTERRUPTED" if interrupted else "STRIKE DEFLECTED", style="yellow" if interrupted else "red")
        self._write()
        ledger = receipt.get("stage_ledger") or {}
        remote = receipt.get("remote_state") or {}
        flags = receipt.get("completion_flags") or {}
        self._field("RESULT", receipt.get("status"), style="yellow" if interrupted else "red")
        self._field("MISSION", receipt.get("mission_id"))
        self._field("SWORD", receipt.get("sword_identity"))
        self._field("LANE", receipt.get("lane"), style="magenta")
        self._field("REPOSITORY", receipt.get("repository"))
        self._field("FAILED AT", ledger.get("current_stage"), style="red")
        self._field("LAST PASS", ledger.get("last_completed_stage"), style="green")
        self._field("MUTATION", "YES" if flags.get("mutation_performed") else "NO", style="yellow")
        self._field("PR", remote.get("pull_request"))
        self._field("CANDIDATE", _short_sha(remote.get("candidate_tree_sha")), style="gray")
        self._field("COMMIT", _short_sha(remote.get("commit_sha") or remote.get("merge_sha")), style="gray")
        self._field("DETAIL", receipt.get("detail"), style="red")
        self._write()
        self._write(self._style("  RECOVERY POSTURE", "bold", "yellow"))
        self._write("    Automatic retry: NO")
        self._write("    Automatic rollback: NO")
        self._write("    The thin PowerShell client will create one Deflected Sword ZIP.")
        self._write("    Paste this terminal block first; upload the Deflected Sword only for deeper forensics.")


def render_result_text(result: dict[str, Any]) -> str:
    """Stable plain-text compatibility helper for tests and non-interactive callers."""
    from io import StringIO

    stream = StringIO()
    console = OathbringerConsole(stream=stream, color=False, unicode=False)
    console.mission = {
        "expected_base": result.get("expected_base"),
        "lane": result.get("lane"),
    }
    console.render_success(result)
    return stream.getvalue().rstrip()
