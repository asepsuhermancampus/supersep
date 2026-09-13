import asyncio

from agent_runner import AgentRunner
from council import Council


async def main():
    task = """
Build a modern web dashboard for managing users.

The application should have:
- Login
- Dashboard
- User list
- User detail
- Search
- Pagination
- Responsive design
- API integration
"""

    print("================================")
    print("ROUND 1 - INDEPENDENT ANALYSIS")
    print("================================")

    runner = AgentRunner()

    results = await runner.run(task)

    print()
    print("ROUND 1 FINISHED")
    print()

    # Load the role prompts again.
    agent_prompts = {}

    for agent_id, agent_file in runner.agents:
        agent_prompts[agent_id] = runner.load_agent_prompt(
            agent_file
        )

    print("================================")
    print("ROUND 2 - CROSS CRITIQUE")
    print("================================")

    council = Council()

    critiques = await council.cross_critique(
        results=results,
        agent_prompts=agent_prompts,
    )

    print()
    print("================================")
    print("COUNCIL RESULTS")
    print("================================")

    for critique in critiques:
        print()
        print(f"### {critique['agent_id']}")
        print(f"STATUS: {critique['status']}")

        if critique["status"] == "success":
            print(critique["response"])
        else:
            print(f"ERROR: {critique['error']}")


if __name__ == "__main__":
    asyncio.run(main())