import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

try:
    from orchestrator.pipeline import UnifiedPipeline
    from orchestrator.learner import KnowledgeDistiller
except ImportError:
    from pipeline import UnifiedPipeline
    from learner import KnowledgeDistiller

load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser(description="AI-Team Dual-Phase Multi-Agent Engine")
    parser.add_argument(
        "--task",
        "-t",
        type=str,
        help="The design or engineering task for the 5-agent team",
    )
    parser.add_argument(
        "--task-file",
        type=str,
        help="Path to a text file containing the task",
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        default=None,
        help="Target workspace or project directory path (defaults to current dir)",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["council", "assembly", "full"],
        default="council",
        help="Execution mode: council (Phase 1 plan), assembly (Phase 2 code), full (both)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON results",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    task_content = args.task
    if args.task_file:
        tf = Path(args.task_file)
        if tf.exists():
            task_content = tf.read_text(encoding="utf-8")
        else:
            print(f"Error: task file not found: {tf}", file=sys.stderr)
            sys.exit(1)

    if not task_content:
        # Interactive fallback prompt if no args provided
        task_content = input("Enter engineering task for AI-Team: ").strip()
        if not task_content:
            print("No task provided. Exiting.")
            sys.exit(0)

    pipeline = UnifiedPipeline()
    result = await pipeline.run(
        task=task_content,
        target_path=args.project,
        mode=args.mode,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # Formatted Markdown Display
    print("\n" + "=" * 60)
    print("AI-TEAM FINAL DELIVERABLE")
    print("=" * 60 + "\n")

    print(result["blueprint"])

    if result.get("code"):
        print("\n" + "=" * 60)
        print("PHASE 2: GENERATED IMPLEMENTATION CODE")
        print("=" * 60 + "\n")
        print(result["code"])

    if result.get("review"):
        print("\n" + "=" * 60)
        print("PHASE 2: ADVERSARIAL QA AUDIT")
        print("=" * 60 + "\n")
        print(result["review"]["critique"])

    if result.get("learnings"):
        learner = KnowledgeDistiller()
        print(learner.format_proposals(result["learnings"]))


if __name__ == "__main__":
    asyncio.run(main())
