import json
import re
from pathlib import Path
from typing import Dict, Any


class WorkspaceDetector:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent

    def detect(self, current_path: Path | str | None = None) -> Dict[str, str]:
        if current_path is None:
            current_path = Path.cwd()
        else:
            current_path = Path(current_path)

        project_name = current_path.name
        # Sanitize name for filesystem storage (collapse multiple symbols into single dash)
        safe_name = re.sub(r"[^a-zA-Z0-9]+", "-", project_name).strip("-")

        return {
            "name": project_name,
            "safe_name": safe_name,
            "path": str(current_path),
        }


class ProjectMemory:
    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "memory"
        self.base_dir = base_dir
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, safe_name: str) -> Path:
        pdir = self.projects_dir / safe_name
        pdir.mkdir(parents=True, exist_ok=True)
        return pdir

    def load(self, safe_name: str) -> Dict[str, Any]:
        pdir = self._get_project_dir(safe_name)
        ctx_file = pdir / "context.json"
        decisions_file = pdir / "decisions.md"

        context = {}
        if ctx_file.exists():
            try:
                context = json.loads(ctx_file.read_text(encoding="utf-8"))
            except Exception:
                context = {}

        decisions = ""
        if decisions_file.exists():
            decisions = decisions_file.read_text(encoding="utf-8")

        return {
            "project": safe_name,
            "context": context,
            "decisions": decisions,
        }

    def save_context(self, safe_name: str, context: Dict[str, Any]) -> None:
        pdir = self._get_project_dir(safe_name)
        ctx_file = pdir / "context.json"
        ctx_file.write_text(json.dumps(context, indent=2), encoding="utf-8")

    def append_decision(self, safe_name: str, decision: str) -> None:
        pdir = self._get_project_dir(safe_name)
        decisions_file = pdir / "decisions.md"
        with open(decisions_file, "a", encoding="utf-8") as f:
            f.write(f"\n- {decision.strip()}\n")
