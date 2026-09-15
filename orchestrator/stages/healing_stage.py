"""
orchestrator/stages/healing_stage.py — Stage 4: Self-Healing War Room Loop
SuperSep v2.0

Triggered by: auto-triggered after ensemble_code_stage, or manually via --stage heal
Pipeline state: CODE_COMPLETED → HEALING_COMPLETED

Auto-detects project type (Next.js / Python) and runs build + tests.
On failure: 5-agent war room diagnoses error → applies patch → retries.
Max 5 healing cycles.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from orchestrator.router import GeminiRouter
    from orchestrator.state import CheckpointStateManager
except ImportError:
    from router import GeminiRouter
    from state import CheckpointStateManager


MAX_HEALING_CYCLES = 5


class HealingStage:
    def __init__(
        self,
        router: GeminiRouter | None = None,
        state_manager: CheckpointStateManager | None = None,
    ):
        self.router = router or GeminiRouter()
        self.state_manager = state_manager or CheckpointStateManager()
        self.agents_dir = Path(__file__).resolve().parent.parent.parent / "agents"

    def _load_agent_prompt(self, filename: str) -> str:
        path = self.agents_dir / filename
        return path.read_text(encoding="utf-8") if path.exists() else ""

    async def run(
        self,
        safe_name: str,
        target_path: Path,
        task: str = "",
    ) -> dict[str, Any]:
        """
        Execute Stage 4: Autonomous Self-Healing War Room.

        Detects project type, runs build/test, and loops up to MAX_HEALING_CYCLES
        times until the build is clean (return code 0) or cycles are exhausted.

        Args:
            safe_name: Sanitized project name (for state tracking).
            target_path: Absolute path to the target project workspace.
            task: Original task description (for context during war room).
        """
        print("\n" + "="*55)
        print("STAGE 4: SELF-HEALING WAR ROOM")
        print("="*55)

        target_path = Path(target_path)
        project_type = self._detect_project_type(target_path)

        if not project_type:
            print("[Healing] No buildable project detected (no package.json or pyproject.toml).")
            print("[Healing] Skipping self-healing. Marking as HEALING_COMPLETED.")
            self.state_manager.advance(safe_name=safe_name, next_state="HEALING_COMPLETED")
            return {"stage": "heal", "status": "skipped", "reason": "No buildable project"}

        print(f"[Healing] Detected project type(s): {project_type}")

        history = []
        for cycle in range(1, MAX_HEALING_CYCLES + 1):
            print(f"\n{'─'*40}")
            print(f"HEALING CYCLE {cycle}/{MAX_HEALING_CYCLES}")
            print(f"{'─'*40}")

            build_results = self._run_build_and_test(target_path, project_type)
            all_passed = all(r["returncode"] == 0 for r in build_results)

            cycle_record = {
                "cycle": cycle,
                "build_results": build_results,
                "passed": all_passed,
            }

            if all_passed:
                print(f"\n✅ BUILD CLEAN on cycle {cycle}. All checks passed!")
                history.append(cycle_record)
                break

            # Collect all stderr for war room
            combined_error = "\n\n".join(
                f"[{r['command']}]\n{r['stderr']}" for r in build_results if r["returncode"] != 0
            )

            print(f"\n❌ Build failed on cycle {cycle}. Entering War Room...")
            print(f"Error preview:\n{combined_error[:500]}...")

            # War room: 5 agents diagnose and patch
            patch = await self._war_room_diagnose(
                error_output=combined_error,
                target_path=target_path,
                task=task,
                cycle=cycle,
            )

            cycle_record["patch_applied"] = patch is not None
            history.append(cycle_record)

            if patch:
                self._apply_patch(patch, target_path)
            else:
                print(f"[Healing] No actionable patch generated on cycle {cycle}.")
                break
        else:
            print(f"\n⚠️  Max healing cycles ({MAX_HEALING_CYCLES}) reached. Review errors manually.")

        # Determine final status
        final_build = self._run_build_and_test(target_path, project_type)
        final_passed = all(r["returncode"] == 0 for r in final_build)

        self.state_manager.advance(
            safe_name=safe_name,
            next_state="HEALING_COMPLETED",
            metadata={"healing_passed": final_passed, "healing_cycles": len(history)},
        )

        return {
            "stage": "heal",
            "status": "passed" if final_passed else "failed",
            "cycles": len(history),
            "history": history,
            "final_build": final_build,
        }

    def _detect_project_type(self, target_path: Path) -> list[str]:
        """Detect project type based on config files present."""
        types = []
        if (target_path / "package.json").exists():
            types.append("nodejs")
        if (
            (target_path / "pyproject.toml").exists()
            or (target_path / "setup.py").exists()
            or (target_path / "requirements.txt").exists()
        ):
            types.append("python")
        return types

    def _run_build_and_test(
        self,
        target_path: Path,
        project_types: list[str],
    ) -> list[dict[str, Any]]:
        """Run build and test commands for each detected project type."""
        results = []

        if "nodejs" in project_types:
            # Check if a build script exists
            import json as _json
            pkg = target_path / "package.json"
            scripts = {}
            try:
                pkg_data = _json.loads(pkg.read_text(encoding="utf-8"))
                scripts = pkg_data.get("scripts", {})
            except Exception:
                pass

            if "build" in scripts:
                results.append(self._run_command("npm run build", target_path))
            if "test" in scripts:
                results.append(self._run_command("npm test -- --passWithNoTests", target_path))
            elif "type-check" in scripts:
                results.append(self._run_command("npm run type-check", target_path))

        if "python" in project_types:
            # Try pytest
            pytest_cmd = self._find_python_executable(target_path)
            results.append(self._run_command(f"{pytest_cmd} -x -q", target_path))

        return results

    def _run_command(self, command: str, cwd: Path) -> dict[str, Any]:
        """Execute a shell command and capture output."""
        print(f"[Healing] Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per command
                encoding="utf-8",
                errors="replace",
            )
            status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
            print(f"  {status} (exit code {result.returncode})")
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout[-3000:] if result.stdout else "",
                "stderr": result.stderr[-3000:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            print(f"  ⏰ TIMEOUT after 300s")
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 300 seconds.",
            }
        except Exception as e:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
            }

    def _find_python_executable(self, target_path: Path) -> str:
        """Find the correct Python/pytest executable."""
        # Check for virtual environment in target or parent dirs
        for venv_dir in [".venv", "venv", ".env"]:
            if sys.platform == "win32":
                exe = target_path / venv_dir / "Scripts" / "pytest.exe"
            else:
                exe = target_path / venv_dir / "bin" / "pytest"
            if exe.exists():
                return str(exe)
        return "pytest"

    async def _war_room_diagnose(
        self,
        error_output: str,
        target_path: Path,
        task: str,
        cycle: int,
    ) -> dict[str, str] | None:
        """
        5-agent war room: diagnose errors and generate patches.

        Returns a dict of {relative_file_path: new_content} to apply, or None.
        """
        # Load relevant file contents for context
        file_context = self._scan_relevant_files(target_path, error_output)

        system_prompt = """You are a 5-agent engineering War Room assembled to fix a critical build failure.
        
Your collective mission: Diagnose the root cause of the build error and output EXACT file patches to fix it.

Analysis protocol:
1. Identify the specific file(s) and line(s) causing the error
2. Determine the root cause (type mismatch, import error, syntax error, missing export, etc.)
3. Generate the minimum targeted fix — do not rewrite files that are working

OUTPUT FORMAT (JSON only, no markdown):
{
  "diagnosis": "Root cause in 1-2 sentences",
  "patches": [
    {
      "path": "relative/path/to/file.tsx",
      "full_content": "COMPLETE fixed file content — write the entire file, not just the diff"
    }
  ]
}

If no fix is possible from the available information, output: {"diagnosis": "Cannot determine fix from available context", "patches": []}
"""

        user_prompt = f"""BUILD ERROR (Cycle {cycle}):
{error_output[:4000]}

RELEVANT FILE CONTENTS:
{file_context}

ORIGINAL TASK:
{task[:500] if task else 'Not provided'}

Diagnose and patch now. Output JSON only.
"""

        try:
            import json
            import re

            raw = await self.router.request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            clean = re.sub(r"^```(?:json)?\n|```$", "", raw.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean)

            diagnosis = parsed.get("diagnosis", "")
            patches = parsed.get("patches", [])

            print(f"\n[War Room] Diagnosis: {diagnosis}")
            print(f"[War Room] Patches proposed: {len(patches)}")

            if not patches:
                return None

            return {p["path"]: p["full_content"] for p in patches if p.get("path") and p.get("full_content")}

        except Exception as e:
            print(f"[War Room] Diagnosis error: {e}")
            return None

    def _scan_relevant_files(self, target_path: Path, error_output: str) -> str:
        """Extract file contents mentioned in the error output for context."""
        lines = []
        # Find file paths mentioned in error (TypeScript/Python style)
        import re
        patterns = [
            r"(?:\.\/|src\/|app\/|lib\/|pages\/)[\w\/\-\.]+\.(?:ts|tsx|js|jsx|py)",
            r"at\s+([\w\/\-\.]+\.(?:ts|tsx|js|py)):\d+",
        ]

        mentioned_files = set()
        for pattern in patterns:
            for match in re.finditer(pattern, error_output):
                mentioned_files.add(match.group().strip())

        for rel_path in list(mentioned_files)[:5]:  # Max 5 files to stay within context
            full_path = target_path / rel_path.lstrip("./")
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                    if len(content) > 2000:
                        content = content[:2000] + "\n[... truncated ...]"
                    lines.append(f"\n=== {rel_path} ===\n{content}")
                except Exception:
                    pass

        return "\n".join(lines) if lines else "No specific files identified from error output."

    def _apply_patch(self, patches: dict[str, str], target_path: Path) -> None:
        """Write patch files to the target workspace."""
        for rel_path, content in patches.items():
            try:
                full_path = (target_path / rel_path).resolve()
                # Security: prevent path traversal
                if not str(full_path).startswith(str(target_path.resolve())):
                    print(f"  [Security] Skipping suspicious patch path: {rel_path}")
                    continue
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                print(f"  [Patch] Applied: {rel_path}")
            except Exception as e:
                print(f"  [Patch] Failed to apply {rel_path}: {e}")
