import asyncio

from router import GeminiRouter


async def main():
    print("================================")
    print("ROUTER REQUEST TEST")
    print("================================")

    router = GeminiRouter()

    print("1. Router object OK")

    response = await router.request(
        system_prompt="You are a test agent.",
        user_prompt="Reply with exactly: ROUTER REQUEST OK",
    )

    print("2. Request selesai")
    print("--------------------------------")
    print("RESPONSE:")
    print(response)
    print("--------------------------------")
    print("ROUTER TEST SUCCESS")


asyncio.run(main())