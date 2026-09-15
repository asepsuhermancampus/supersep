"""
orchestrator/router.py — HTTP Transport Layer for SuperSep v3.0

Responsibilities (ONLY):
- Send HTTP requests to 9Router with retry + exponential backoff
- Persistent shared AsyncClient with connection pooling
- Circuit breaker: stop cascading failures when 9Router is down
- Configurable timeouts via environment variables

Does NOT contain business logic. Does NOT know about agents or council rounds.
"""
import asyncio
import base64
import os
import random
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()


class CircuitBreakerOpen(Exception):
    """Raised when the circuit breaker is open (9Router appears to be down)."""
    pass


class GeminiRouter:
    """
    HTTP transport layer for sending prompts to 9Router (OpenAI-compatible endpoint).

    Features:
    - Persistent AsyncClient with connection pooling (eliminates TCP handshake overhead)
    - Exponential backoff retry (configurable via RETRY_MAX_ATTEMPTS)
    - Circuit breaker: opens after 5 consecutive failures, auto-resets after 60s
    - Per-request timeout configurable via AGENT_TIMEOUT_SECONDS / SYNTHESIS_TIMEOUT_SECONDS
    - Multimodal support: local image files or HTTP URLs
    """

    # Circuit breaker state (class-level, shared across instances in same process)
    _failure_count: int = 0
    _circuit_open_since: float | None = None
    _CIRCUIT_TRIP_THRESHOLD: int = 5
    _CIRCUIT_RESET_SECONDS: int = 60

    def __init__(self):
        self.base_url = os.getenv("ROUTER_BASE_URL")
        self.api_key = os.getenv("ROUTER_API_KEY")
        self.model = os.getenv("MODEL")

        if not self.base_url:
            raise RuntimeError("ROUTER_BASE_URL belum diset di .env")
        if not self.api_key:
            raise RuntimeError("ROUTER_API_KEY belum diset di .env")
        if not self.model:
            raise RuntimeError("MODEL belum diset di .env")

        concurrency = int(os.getenv("ROUTER_CONCURRENCY", "10"))
        self._semaphore = asyncio.Semaphore(concurrency)
        self._max_retries = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
        self._agent_timeout = float(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))
        self._synthesis_timeout = float(os.getenv("SYNTHESIS_TIMEOUT_SECONDS", "600"))
        self._retryable_status_codes = {429, 502, 503, 504}

        # Shared persistent AsyncClient — eliminates TCP handshake on every request
        limits = httpx.Limits(
            max_connections=10,
            max_keepalive_connections=10,
            keepalive_expiry=60,
        )
        self._client = httpx.AsyncClient(
            limits=limits,
            timeout=httpx.Timeout(
                connect=30.0,
                read=self._agent_timeout,
                write=30.0,
                pool=10.0,
            ),
        )

    async def close(self) -> None:
        """Close the shared HTTP client. Call when done with the router."""
        await self._client.aclose()

    def _check_circuit_breaker(self) -> None:
        """
        Check if circuit breaker is open.

        Raises:
            CircuitBreakerOpen: If the circuit is open and reset window has not passed.
        """
        if GeminiRouter._circuit_open_since is not None:
            elapsed = time.monotonic() - GeminiRouter._circuit_open_since
            if elapsed >= self._CIRCUIT_RESET_SECONDS:
                print(f"[Router] Circuit breaker auto-reset after {elapsed:.0f}s.")
                GeminiRouter._failure_count = 0
                GeminiRouter._circuit_open_since = None
            else:
                raise CircuitBreakerOpen(
                    f"9Router circuit breaker OPEN. "
                    f"Auto-reset in {self._CIRCUIT_RESET_SECONDS - elapsed:.0f}s. "
                    f"Check 9Router at {self.base_url}"
                )

    def _record_success(self) -> None:
        """Record a successful request — reset failure count."""
        GeminiRouter._failure_count = 0
        GeminiRouter._circuit_open_since = None

    def _record_failure(self) -> None:
        """Record a failed request — trip circuit if threshold reached."""
        GeminiRouter._failure_count += 1
        if GeminiRouter._failure_count >= self._CIRCUIT_TRIP_THRESHOLD:
            if GeminiRouter._circuit_open_since is None:
                GeminiRouter._circuit_open_since = time.monotonic()
                print(
                    f"[Router] CIRCUIT BREAKER OPEN after "
                    f"{GeminiRouter._failure_count} consecutive failures. "
                    f"Auto-reset in {self._CIRCUIT_RESET_SECONDS}s."
                )

    async def request(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str | None = None,
        is_synthesis: bool = False,
    ) -> str:
        """
        Send a request to the LLM router.

        Args:
            system_prompt: The system/role prompt for the model.
            user_prompt: The user message / task content.
            image_path: Optional local file path or HTTP URL for multimodal input.
            is_synthesis: If True, uses SYNTHESIS_TIMEOUT_SECONDS (longer timeout).

        Returns:
            The model text response as a string.

        Raises:
            CircuitBreakerOpen: If 9Router is detected as down.
            RuntimeError: If all retry attempts are exhausted.
        """
        self._check_circuit_breaker()
        async with self._semaphore:
            return await self._request_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_path=image_path,
                is_synthesis=is_synthesis,
            )

    async def _request_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str | None,
        is_synthesis: bool,
    ) -> str:
        """Retry loop with exponential backoff."""
        last_error: Exception | None = None
        delays = [0, 2, 5, 10, 20]  # seconds between attempts

        for attempt in range(self._max_retries):
            try:
                result = await self._do_request(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    image_path=image_path,
                    is_synthesis=is_synthesis,
                )
                self._record_success()
                return result

            except httpx.TimeoutException as e:
                last_error = e
                self._record_failure()
                print(f"[Router] Timeout on attempt {attempt + 1}/{self._max_retries}.")

            except httpx.ConnectError as e:
                last_error = e
                self._record_failure()
                print(f"[Router] Connection error on attempt {attempt + 1}/{self._max_retries}: {e}")

            except httpx.HTTPStatusError as e:
                if e.response.status_code in self._retryable_status_codes:
                    last_error = e
                    self._record_failure()
                    print(f"[Router] HTTP {e.response.status_code} on attempt {attempt + 1}/{self._max_retries}.")
                else:
                    self._record_failure()
                    raise RuntimeError(
                        f"9Router non-retryable error {e.response.status_code}: {e.response.text}"
                    ) from e

            except CircuitBreakerOpen:
                raise  # Never catch circuit breaker in retry loop

            if attempt < self._max_retries - 1:
                delay = delays[min(attempt, len(delays) - 1)] + random.uniform(0, 0.5)
                print(f"[Router] Waiting {delay:.1f}s before retry {attempt + 2}...")
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"9Router failed after {self._max_retries} attempts. Last error: {last_error}"
        )

    async def _do_request(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str | None,
        is_synthesis: bool,
    ) -> str:
        """Execute a single HTTP request to 9Router."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        user_content = self._build_user_content(user_prompt, image_path)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
        }

        # Use longer timeout for synthesis requests (Round 3)
        read_timeout = self._synthesis_timeout if is_synthesis else self._agent_timeout
        timeout = httpx.Timeout(connect=30.0, read=read_timeout, write=30.0, pool=10.0)

        response = await self._client.post(url, headers=headers, json=payload, timeout=timeout)

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                message=f"9Router error {response.status_code}",
                request=response.request,
                response=response,
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _build_user_content(self, text: str, image_path: str | None) -> str | list:
        """
        Build user message content, supporting multimodal (text + image).

        Args:
            text: The text prompt
            image_path: Optional local file path or HTTP/HTTPS URL to image

        Returns:
            Plain string if no image, list of content parts for multimodal
        """
        if not image_path:
            return text

        content_parts = [{"type": "text", "text": text}]

        if image_path.startswith("http://") or image_path.startswith("https://"):
            content_parts.append({"type": "image_url", "image_url": {"url": image_path}})
        else:
            local_path = Path(image_path)
            if not local_path.exists():
                print(f"[Router] Warning: Image not found: {image_path}. Sending text-only.")
                return text
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }
            mime_type = mime_map.get(local_path.suffix.lower(), "image/png")
            b64_data = base64.b64encode(local_path.read_bytes()).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64_data}"},
            })

        return content_parts