import asyncio

from agent_runner import AgentRunner


async def main():
    runner = AgentRunner()

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

    results = await runner.run(task)

    print()
    print("================================")
    print("AGENT RESULTS")
    print("================================")

    for result in results:
        print()
        print(f"### {result['agent_id']}")
        print(f"STATUS: {result['status']}")

        if result["status"] == "success":
            print(result["response"])
        else:
            print(f"ERROR: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())