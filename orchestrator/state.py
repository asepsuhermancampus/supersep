"""
orchestrator/state.py — Checkpoint State Manager
SuperSep v2.0

Tracks pipeline progress automatically across sessions.
State is persisted to disk so work can be resumed after interruption.
Human approval gates are NOT used — pipeline advances automatically.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Ordered pipeline states
PIPELINE_STATES = [
    "INIT",
    "UI_COMPLETED",
    "ARCH_COMPLETED",
    "CODE_COMPLETED",
    "HEALING_COMPLETED",
    "DEPLOYED",
]


class CheckpointStateManager:
    """
    Manages project pipeline state persistently.

    State file location:
        memory/projects/<safe_name>/checkpoints/session_state.json

    Example session_state.json:
    {
        "project": "HariKita-Web-App",
        "current_state": "ARCH_COMPLETED",
        "history": [
            {"state": "INIT", "timestamp": "2026-09-15T00:00:00Z"},
            {"state": "UI_COMPLETED", "timestamp": "2026-09-15T00:05:32Z"},
            {"state": "ARCH_COMPLETED", "timestamp": "2026-09-15T00:12:18Z"}
        ],
        "metadata": {
            "ui_deliverable": "memory/projects/HariKita-Web-App/deliverables/ui_design_system.md",
            "arch_deliverable": "memory/projects/HariKita-Web-App/deliverables/master_architecture_blueprint.md"
        }
    }
    """

    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "memory"
        self.base_dir = base_dir
        self.projects_dir = self.base_dir / "projects"

    def _checkpoint_file(self, safe_name: str) -> Path:
        checkpoint_dir = self.projects_dir / safe_name / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        return checkpoint_dir / "session_state.json"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def load(self, safe_name: str) -> dict[str, Any]:
        """Load current session state. Returns INIT state if no checkpoint exists."""
        path = self._checkpoint_file(safe_name)
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # No existing state → start fresh
        return {
            "project": safe_name,
            "current_state": "INIT",
            "history": [{"state": "INIT", "timestamp": self._now_iso()}],
            "metadata": {},
        }

    def save(self, safe_name: str, state_data: dict[str, Any]) -> None:
        """Persist state data to disk."""
        path = self._checkpoint_file(safe_name)
        path.write_text(
            json.dumps(state_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_current(self, safe_name: str) -> str:
        """Return the current state name for this project."""
        return self.load(safe_name)["current_state"]

    def advance(self, safe_name: str, next_state: str, metadata: dict[str, Any] | None = None) -> None:
        """
        Advance pipeline to the next state.

        Args:
            safe_name: Sanitized project name (filesystem key).
            next_state: Target state (must be in PIPELINE_STATES).
            metadata: Optional key-value pairs to store alongside state
                      (e.g., paths to deliverable files).
        """
        if next_state not in PIPELINE_STATES:
            raise ValueError(
                f"Invalid state '{next_state}'. Valid states: {PIPELINE_STATES}"
            )

        state_data = self.load(safe_name)
        current = state_data["current_state"]

        # Validate forward progression
        current_idx = PIPELINE_STATES.index(current)
        next_idx = PIPELINE_STATES.index(next_state)
        if next_idx <= current_idx and next_state != "INIT":
            print(
                f"[State] Warning: Requested state '{next_state}' is not ahead of "
                f"current state '{current}'. Ignoring advance."
            )
            return

        state_data["current_state"] = next_state
        state_data["history"].append({
            "state": next_state,
            "timestamp": self._now_iso(),
        })

        if metadata:
            state_data["metadata"].update(metadata)

        self.save(safe_name, state_data)
        print(f"[State] ✓ Project '{safe_name}': {current} → {next_state}")

    def reset(self, safe_name: str) -> None:
        """Reset project pipeline back to INIT state."""
        state_data = {
            "project": safe_name,
            "current_state": "INIT",
            "history": [{"state": "INIT", "timestamp": self._now_iso()}],
            "metadata": {},
        }
        self.save(safe_name, state_data)
        print(f"[State] Project '{safe_name}' reset to INIT.")

    def get_metadata(self, safe_name: str, key: str) -> str | None:
        """Retrieve a specific metadata value (e.g., path to deliverable)."""
        return self.load(safe_name).get("metadata", {}).get(key)

    def print_status(self, safe_name: str) -> None:
        """Print a human-readable status summary for this project."""
        state_data = self.load(safe_name)
        print(f"\n{'='*50}")
        print(f"PROJECT: {state_data['project']}")
        print(f"CURRENT STATE: {state_data['current_state']}")
        print(f"PIPELINE: {' → '.join(PIPELINE_STATES)}")
        print("\nHISTORY:")
        for entry in state_data.get("history", []):
            print(f"  [{entry['timestamp']}] {entry['state']}")
        metadata = state_data.get("metadata", {})
        if metadata:
            print("\nMETADATA:")
            for k, v in metadata.items():
                print(f"  {k}: {v}")
        print("="*50)
