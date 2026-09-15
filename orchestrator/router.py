import os
import asyncio
import base64
import random
from pathlib import Path

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

        # Concurrency limiter: default 10 simultaneous API calls (matching 10 Gemini Pro accounts on round-robin)
        concurrency = int(os.getenv("ROUTER_CONCURRENCY", "10"))
        self._semaphore = asyncio.Semaphore(concurrency)

        # Retry configuration
        self._max_retries = 3
        self._retryable_status_codes = {429, 503, 502, 504}

    async def request(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str | None = None,
    ) -> str:
        """
        Send a request to the LLM router.

        Args:
            system_prompt: The system/role prompt for the model.
            user_prompt: The user message / task content.
            image_path: Optional path to a local image file (PNG/JPG/WEBP)
                        or an HTTP/HTTPS URL to an image.
                        Will be encoded as base64 for local files.

        Returns:
            The model's text response.
        """
        async with self._semaphore:
            return await self._request_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_path=image_path,
            )

    async def _request_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str | None = None,
    ) -> str:
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                return await self._do_request(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    image_path=image_path,
                )
            except httpx.TimeoutException as e:
                last_error = e
                print(f"[Router] Timeout on attempt {attempt + 1}/{self._max_retries}. Retrying...")
            except httpx.ConnectError as e:
                last_error = e
                print(f"[Router] Connection error on attempt {attempt + 1}/{self._max_retries}. Retrying...")
            except httpx.HTTPStatusError as e:
                if e.response.status_code in self._retryable_status_codes:
                    last_error = e
                    print(
                        f"[Router] HTTP {e.response.status_code} on attempt "
                        f"{attempt + 1}/{self._max_retries}. Retrying..."
                    )
                else:
                    # Non-retryable HTTP error (e.g., 400 Bad Request, 401 Unauthorized)
                    raise RuntimeError(
                        f"9Router error {e.response.status_code}: {e.response.text}"
                    ) from e

            if attempt < self._max_retries - 1:
                # Exponential backoff with jitter: 2^attempt + random(0, 1) seconds
                wait_seconds = (2 ** attempt) + random.uniform(0, 1)
                print(f"[Router] Waiting {wait_seconds:.1f}s before retry...")
                await asyncio.sleep(wait_seconds)

        raise RuntimeError(
            f"9Router failed after {self._max_retries} attempts. Last error: {last_error}"
        )

    async def _do_request(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str | None = None,
    ) -> str:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Build user message content — supports multimodal (text + image)
        user_content = self._build_user_content(user_prompt, image_path)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            "stream": False,
        }

        print("3. Mengirim request ke 9Router...")

        # Extended timeout for unconstrained, thorough model responses
        timeout = httpx.Timeout(
            connect=30.0,
            read=300.0,   # 5 minutes — allow model to think deeply
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
            raise httpx.HTTPStatusError(
                message=f"9Router error {response.status_code}",
                request=response.request,
                response=response,
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _build_user_content(
        self,
        text: str,
        image_path: str | None = None,
    ) -> str | list:
        """
        Build the user message content.
        Returns plain string if no image, or a list of content parts for multimodal.
        """
        if not image_path:
            return text

        # Multimodal: image + text
        content_parts = [{"type": "text", "text": text}]

        if image_path.startswith("http://") or image_path.startswith("https://"):
            # Remote URL — pass directly
            image_part = {
                "type": "image_url",
                "image_url": {"url": image_path},
            }
        else:
            # Local file — encode to base64
            local_path = Path(image_path)
            if not local_path.exists():
                print(f"[Router] Warning: Image file not found: {image_path}. Sending text-only.")
                return text

            suffix = local_path.suffix.lower()
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }
            mime_type = mime_map.get(suffix, "image/png")

            with open(local_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")

            image_part = {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64_data}"},
            }

        content_parts.append(image_part)
        return content_parts