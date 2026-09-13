import re
import yaml
from pathlib import Path
from typing import List, Dict, Any

try:
    from orchestrator.triage import ProjectMemory
    from orchestrator.router import GeminiRouter
except ImportError:
    from triage import ProjectMemory
    from router import GeminiRouter


class KnowledgeDistiller:
    def __init__(
        self,
        memory: ProjectMemory | None = None,
        agents_dir: Path | None = None,
        router: GeminiRouter | None = None,
    ):
        self.memory = memory or ProjectMemory()
        self.agents_dir = agents_dir or (Path(__file__).resolve().parent.parent / "agents")
        self.router = router or GeminiRouter()

    async def extract_learnings(
        self,
        task: str,
        blueprint: str,
        safe_project_name: str,
    ) -> List[Dict[str, Any]]:
        system_prompt = """
You are a Knowledge Distiller for an autonomous AI engineering team.
Analyze the completed task and architecture blueprint.
Identify 1-3 concrete, high-value, reusable engineering rules discovered during this design session.
Rules must be specific, non-obvious, and concise (1 sentence each).

Categorize each as either:
- scope: "project" (rules specific to this project's architecture, conventions, or stack)
- scope: "global" (universal best practices for a specific agent role, e.g. agent_1, agent_2, agent_3, agent_4, agent_5)

You MUST respond strictly in YAML format:
learnings:
  - scope: "project"
    target: "current_project"
    rule: "Specific concise convention"
  - scope: "global"
    target: "agent_x"
    rule: "Specific concise best practice"
"""

        user_prompt = f"""
TASK:
{task}

BLUEPRINT:
{blueprint}

PROJECT NAME:
{safe_project_name}

Extract reusable rules in strict YAML format now.
"""

        try:
            raw_response = await self.router.request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            clean_yaml = re.sub(r"^```(?:yaml)?\n|```$", "", raw_response.strip(), flags=re.MULTILINE)
            parsed = yaml.safe_load(clean_yaml) or {}
            items = parsed.get("learnings", [])

            # Normalize targets
            normalized = []
            for item in items:
                scope = item.get("scope", "project")
                target = item.get("target", safe_project_name)
                if scope == "project" or target == "current_project":
                    target = safe_project_name
                normalized.append({
                    "scope": scope,
                    "target": target,
                    "rule": item.get("rule", "").strip(),
                })

            return [i for i in normalized if i["rule"]]

        except Exception as e:
            print(f"[Learner] Distillation error: {e}")
            return []

    def format_proposals(self, learnings: List[Dict[str, Any]]) -> str:
        if not learnings:
            return "No new distinct learning rules identified for this session."

        lines = ["\n### [KNOWLEDGE] Proposed Knowledge Learnings for Review:\n"]
        for idx, item in enumerate(learnings, 1):
            scope_str = f"Project [{item['target']}]" if item["scope"] == "project" else f"Global [{item['target']}]"
            lines.append(f"[{idx}] {scope_str}:")
            lines.append(f"    - \"{item['rule']}\"")

        lines.append("\nOptions: [A] Approve all, [Number] Approve specific, [D] Discard all")
        return "\n".join(lines)

    def apply(self, approved_items: List[Dict[str, Any]]) -> None:
        for item in approved_items:
            scope = item.get("scope", "project")
            target = item.get("target", "")
            rule = item.get("rule", "").strip()

            if not rule:
                continue

            if scope == "project":
                self.memory.append_decision(target, rule)
            elif scope == "global":
                # Determine agent file name, e.g. agent_3 -> agent3.md
                num_match = re.search(r"\d+", target)
                fname = f"agent{num_match.group(0)}.md" if num_match else f"{target}.md"
                agent_file = self.agents_dir / fname

                if agent_file.exists():
                    content = agent_file.read_text(encoding="utf-8")
                    if "## Learned Knowledge" not in content:
                        content += "\n\n## Learned Knowledge\n"
                    content += f"- {rule}\n"
                    agent_file.write_text(content, encoding="utf-8")
                else:
                    # Fallback to common rules
                    common_rules = self.memory.base_dir / "global" / "common_rules.md"
                    common_rules.parent.mkdir(parents=True, exist_ok=True)
                    with open(common_rules, "a", encoding="utf-8") as f:
                        f.write(f"\n- [{target}] {rule}\n")
