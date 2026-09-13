import os

import httpx
from dotenv import load_dotenv


load_dotenv()


class GeminiRouter:
    def __init__(self):
        self.base_url = os.getenv("ROUTER_BASE_URL")
        self.api_key = os.getenv("ROUTER_API_KEY")
        self.model = os.getenv("MODEL")

        if not self.base_url:
            raise RuntimeError("ROUTER_BASE_URL belum diset")

        if not self.api_key:
            raise RuntimeError("ROUTER_API_KEY belum diset")

        if not self.model:
            raise RuntimeError("MODEL belum diset")

    async def request(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
        }

        print("3. Mengirim request ke 9Router...")

        timeout = httpx.Timeout(
            connect=30.0,
            read=180.0,
            write=30.0,
            pool=30.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        print("4. Response diterima")
        print("HTTP STATUS:", response.status_code)

        if response.status_code != 200:
            raise RuntimeError(
                f"9Router error {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        return data["choices"][0]["message"]["content"]