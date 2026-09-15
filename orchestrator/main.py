import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

try:
    from orchestrator.pipeline import UnifiedPipeline
    from orchestrator.learner import KnowledgeDistiller
    from orchestrator.state import CheckpointStateManager
    from orchestrator.triage import WorkspaceDetector
except ImportError:
    from pipeline import UnifiedPipeline
    from learner import KnowledgeDistiller
    from state import CheckpointStateManager
    from triage import WorkspaceDetector

load_dotenv()

# Ensure clean UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="SuperSep v2.0 — 10-Agent Collaborative Engineering Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stage 1: UI/UX Discovery (with optional reference screenshot)
  python main.py --stage ui --task "Build a login page" --project ./my-app
  python main.py --stage ui --task "Redesign dashboard" --image ./screenshot.png

  # Stage 2: System Architecture
  python main.py --stage arch --task "Build a login page" --project ./my-app

  # Stage 3+4: Ensemble Coding + Auto Self-Healing
  python main.py --stage gas --task "Build a login page" --project ./my-app

  # Stage 4: Manual Self-Healing only
  python main.py --stage heal --project ./my-app

  # Check project pipeline status
  python main.py --stage status --project ./my-app

  # Legacy modes (backward compatible)
  python main.py --mode council --task "Design a checkout flow"
  python main.py --mode full --task "Build complete auth system" --project ./my-app
""",
    )

    # Task input
    task_group = parser.add_mutually_exclusive_group()
    task_group.add_argument("--task", "-t", type=str, help="Engineering task description")
    task_group.add_argument("--task-file", type=str, help="Path to a text file containing the task")

    # Project path
    parser.add_argument(
        "--project", "-p",
        type=str,
        default=None,
        help="Target workspace/project directory (defaults to current directory)",
    )

    # v2.0 granular stage
    parser.add_argument(
        "--stage", "-s",
        choices=["ui", "arch", "gas", "heal", "status"],
        default=None,
        help=(
            "v2.0 Granular stage: "
            "ui (Stage 1: UI/UX Discovery), "
            "arch (Stage 2: Architecture), "
            "gas (Stage 3+4: Ensemble Code + Self-Healing), "
            "heal (Stage 4: Self-Healing only), "
            "status (Show pipeline status)"
        ),
    )

    # Legacy mode (kept for backward compat with existing SKILL.md commands)
    parser.add_argument(
        "--mode", "-m",
        choices=["council", "assembly", "full"],
        default="council",
        help="Legacy execution mode: council (Phase 1), assembly (Phase 2), full (both)",
    )

    # Multimodal image input
    parser.add_argument(
        "--image", "-i",
        type=str,
        default=None,
        help="Path or URL to reference screenshot/mockup image for UI stage (multimodal)",
    )

    # Output format
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON result",
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    # Resolve task content
    task_content = args.task
    if args.task_file:
        tf = Path(args.task_file)
        if tf.exists():
            task_content = tf.read_text(encoding="utf-8")
        else:
            print(f"Error: task file not found: {tf}", file=sys.stderr)
            sys.exit(1)

    # Status stage doesn't require a task
    if args.stage == "status":
        pipeline = UnifiedPipeline()
        await pipeline.run(task="", target_path=args.project, stage="status")
        return

    if not task_content:
        # Interactive fallback
        task_content = input("Enter engineering task for SuperSep: ").strip()
        if not task_content:
            print("No task provided. Exiting.")
            sys.exit(0)

    # Validate image path if provided
    image_path = args.image
    if image_path and not (
        image_path.startswith("http://")
        or image_path.startswith("https://")
        or Path(image_path).exists()
    ):
        print(f"Warning: Image path not found: {image_path}. Proceeding without image.", file=sys.stderr)
        image_path = None

    # Run pipeline
    pipeline = UnifiedPipeline()
    result = await pipeline.run(
        task=task_content,
        target_path=args.project,
        mode=args.mode,
        stage=args.stage,
        image_path=image_path,
    )

    # ── Output ────────────────────────────────────────────────────────────────
    if args.json:
        # Remove non-serializable objects before JSON dump
        safe_result = _make_json_serializable(result)
        print(json.dumps(safe_result, indent=2, ensure_ascii=False))
        return

    # Human-readable formatted output
    print("\n" + "=" * 60)
    print("SUPERSEP v2.0 — DELIVERABLE")
    print("=" * 60 + "\n")

    stage = args.stage or args.mode

    if stage in ("ui",):
        print(result.get("blueprint", ""))
        if p := result.get("ui_design_system_path"):
            print(f"\n✅ Design System saved: {p}")
        if p := result.get("preview_html_path"):
            print(f"✅ Preview HTML saved: {p}")

    elif stage in ("arch",):
        print(result.get("blueprint", ""))
        if p := result.get("blueprint_path"):
            print(f"\n✅ Blueprint saved: {p}")

    elif stage in ("gas",):
        written = result.get("written_files", [])
        print(f"✅ {len(written)} file(s) written to workspace.")
        for f in written[:20]:
            print(f"   {f}")
        if len(written) > 20:
            print(f"   ... and {len(written) - 20} more.")

        heal = result.get("healing", {})
        if heal.get("status") == "passed":
            print(f"\n✅ Self-Healing: BUILD CLEAN ({heal.get('cycles', 0)} cycle(s))")
        elif heal.get("status") == "failed":
            print(f"\n⚠️  Self-Healing: Build still failing after {heal.get('cycles', 0)} cycle(s). Manual review needed.")
        elif heal.get("status") == "skipped":
            print(f"\nℹ️  Self-Healing: Skipped ({heal.get('reason', '')})")

    elif stage in ("heal",):
        heal_status = result.get("status", "unknown")
        cycles = result.get("cycles", 0)
        if heal_status == "passed":
            print(f"✅ BUILD CLEAN after {cycles} healing cycle(s).")
        else:
            print(f"⚠️  Build still failing after {cycles} cycle(s). Review errors manually.")

    elif stage in ("council", None):
        briefs = result.get("briefs", [])
        debates = result.get("debates", [])

        if briefs:
            print("\n" + "=" * 60)
            print("ROUND 1: 10-AGENT INDEPENDENT THINKING & MICRO-BRIEFS")
            print("=" * 60 + "\n")
            for b in briefs:
                agent_id = b.get("agent_id", "unknown")
                print(f"### [{agent_id}]")
                raw = b.get("raw", "")
                if raw:
                    print(raw)
                else:
                    if d := b.get("directives"):
                        print("**Directives:**")
                        for x in d:
                            print(f"  - {x}")
                    if c := b.get("constraints"):
                        print("**Constraints:**")
                        for x in c:
                            print(f"  - {x}")
                    if rf := b.get("red_flags"):
                        print("**Red Flags / Risks:**")
                        for x in rf:
                            print(f"  - {x}")
                print("\n" + "-" * 40 + "\n")

        if debates:
            print("\n" + "=" * 60)
            print("ROUND 2: MATRIX DEBATE & CROSS-CRITIQUE")
            print("=" * 60 + "\n")
            for db in debates:
                agent_id = db.get("agent_id", "unknown")
                print(f"### [{agent_id}]")
                raw = db.get("raw", "")
                if raw:
                    print(raw)
                else:
                    if e := db.get("endorse"):
                        print("**Endorsements:**")
                        for x in e:
                            print(f"  - {x}")
                    if o := db.get("objection"):
                        print("**Objections:**")
                        for x in o:
                            print(f"  - {x}")
                    if cv := db.get("consensus_vote"):
                        print("**Consensus Votes:**")
                        for x in cv:
                            print(f"  - {x}")
                print("\n" + "-" * 40 + "\n")

        print("\n" + "=" * 60)
        print("ROUND 3: MASTER BLUEPRINT SYNTHESIS")
        print("=" * 60 + "\n")
        print(result.get("blueprint", ""))

    elif stage in ("assembly",):
        print(result.get("blueprint", ""))
        if result.get("code"):
            print("\n" + "=" * 60)
            print("GENERATED IMPLEMENTATION CODE")
            print("=" * 60 + "\n")
            print(result["code"])
        if result.get("review"):
            print("\n" + "=" * 60)
            print("ADVERSARIAL QA AUDIT")
            print("=" * 60 + "\n")
            r = result["review"]
            print(r.get("critique", "") if isinstance(r, dict) else r)

    elif stage == "full":
        if p := result.get("arch", {}).get("blueprint_path"):
            print(f"✅ Architecture Blueprint: {p}")
        written = result.get("code", {}).get("written_files", [])
        if written:
            print(f"✅ {len(written)} code file(s) written.")
        heal = result.get("healing", {})
        if heal.get("status") == "passed":
            print(f"✅ Build Clean: {heal.get('cycles', 0)} healing cycle(s)")

    # Knowledge learnings proposal
    if learnings := result.get("learnings"):
        learner = KnowledgeDistiller()
        print(learner.format_proposals(learnings))


def _make_json_serializable(obj):
    """Recursively convert non-serializable objects to strings."""
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_serializable(i) for i in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


if __name__ == "__main__":
    asyncio.run(main())
