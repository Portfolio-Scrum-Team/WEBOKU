"""OpenRouter API adapter for Weboku AI Master.

This module provides a small, dependency-free HTTP client for OpenRouter.

The AI is advisory only. This class must never modify Weboku game state.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class OpenRouterError(RuntimeError):
    """Raised when the OpenRouter API cannot provide a response."""


class OpenRouterEngine:
    """Small dependency-free client for the OpenRouter chat API."""

    DEFAULT_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        api_url: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv(
            "OPENROUTER_MODEL",
            self.DEFAULT_MODEL,
        )
        self.api_url = api_url or self.DEFAULT_URL
        self.timeout = timeout

    @property
    def available(self) -> bool:
        """Return True when an OpenRouter API key is configured."""
        return bool(self.api_key)

    def ask(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 300,
    ) -> str:
        """Send a prompt to OpenRouter and return the assistant text.

        Raises:
            OpenRouterError: If configuration, networking, HTTP, or
                response parsing fails.
        """
        if not self.api_key:
            raise OpenRouterError("OPENROUTER_API_KEY is not configured.")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages: list[dict[str, str]] = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        request = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "Weboku",
                "X-Title": "Weboku AI Master",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw_response = response.read().decode("utf-8")

        except urllib.error.HTTPError as exc:
            details = self._read_http_error(exc)
            raise OpenRouterError(f"OpenRouter HTTP {exc.code}: {details}") from exc

        except urllib.error.URLError as exc:
            raise OpenRouterError(
                f"Could not connect to OpenRouter: {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise OpenRouterError("OpenRouter request timed out.") from exc

        except OSError as exc:
            raise OpenRouterError(f"OpenRouter network error: {exc}") from exc

        return self._extract_text(raw_response)

    def explain(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        """Ask OpenRouter for a Weboku explanation."""
        return self.ask(
            prompt,
            system_prompt=system_prompt or self.weboku_system_prompt(),
        )

    @staticmethod
    def weboku_system_prompt() -> str:
        """Return the safety/behavior rules for Weboku AI Master."""
        return (
            "You are AI Master, the advisory assistant for Weboku, "
            "a Sudoku climbing adventure.\n\n"
            "Your role is to explain, coach, and give advice to the "
            "player.\n\n"
            "You are NOT the game engine.\n"
            "Never claim to have changed the board, score, objectives, "
            "timer, climber position, princess life, or game status.\n"
            "Never invent Sudoku candidates or game-state information.\n"
            "Use only the Weboku state supplied in the prompt.\n"
            "If information is missing, say that it is unavailable.\n"
            "Keep answers concise and useful for a terminal game.\n\n"
            "Weboku flow:\n"
            "SOLVE → UNLOCK → CLIMB → REACH → MARRY"
        )

    @staticmethod
    def _extract_text(raw_response: str) -> str:
        """Extract assistant text from an OpenRouter JSON response."""
        try:
            data: Any = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise OpenRouterError("OpenRouter returned invalid JSON.") from exc

        try:
            choices = data["choices"]
            message = choices[0]["message"]
            content = message["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(
                "OpenRouter response did not contain assistant content."
            ) from exc

        if not isinstance(content, str):
            raise OpenRouterError("OpenRouter returned non-text assistant content.")

        content = content.strip()

        if not content:
            raise OpenRouterError("OpenRouter returned an empty assistant response.")

        return content

    @staticmethod
    def _read_http_error(exc: urllib.error.HTTPError) -> str:
        """Safely extract an API error without exposing credentials."""
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            return str(exc.reason)

        if not body:
            return str(exc.reason)

        try:
            data = json.loads(body)

            error = data.get("error")

            if isinstance(error, dict):
                message = error.get("message")
                if message:
                    return str(message)

            if isinstance(error, str):
                return error

            message = data.get("message")
            if message:
                return str(message)

        except json.JSONDecodeError:
            pass

        return body[:500]
