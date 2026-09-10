"""Tests for the Weboku OpenRouter AI adapter."""

from __future__ import annotations

import json
import urllib.error
from unittest.mock import patch

import pytest

from weboku.openrouter_engine import OpenRouterEngine
from weboku.openrouter_engine import OpenRouterError


def make_response(payload):
    """Create a fake urllib response."""

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    return FakeResponse()


def test_engine_uses_environment_api_key(monkeypatch):
    monkeypatch.setenv(
        "OPENROUTER_API_KEY",
        "test-key",
    )

    engine = OpenRouterEngine()

    assert engine.api_key == "test-key"
    assert engine.model == "nvidia/nemotron-3-super-120b-a12b:free"


def test_engine_can_be_created_without_api_key(monkeypatch):
    monkeypatch.delenv(
        "OPENROUTER_API_KEY",
        raising=False,
    )

    engine = OpenRouterEngine()

    assert engine.available is False


def test_engine_available_when_api_key_exists():
    engine = OpenRouterEngine(api_key="test-key")

    assert engine.available is True


def test_ask_rejects_missing_api_key(monkeypatch):
    monkeypatch.delenv(
        "OPENROUTER_API_KEY",
        raising=False,
    )

    engine = OpenRouterEngine(api_key=None)

    with pytest.raises(
        OpenRouterError,
        match="OPENROUTER_API_KEY",
    ):
        engine.ask("Hello Weboku")


def test_ask_rejects_empty_prompt():
    engine = OpenRouterEngine(api_key="test-key")

    with pytest.raises(
        ValueError,
        match="Prompt cannot be empty",
    ):
        engine.ask("")


def test_ask_sends_correct_request():
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "WEBOKU AI ONLINE",
                }
            }
        ]
    }

    engine = OpenRouterEngine(
        api_key="test-key",
        model="openrouter/free",
    )

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        return_value=make_response(payload),
    ) as mock_urlopen:
        result = engine.ask(
            "Say hello.",
            system_prompt="You are Weboku AI Master.",
        )

    assert result == "WEBOKU AI ONLINE"

    request = mock_urlopen.call_args.args[0]

    assert request.full_url == (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    assert request.get_header("Authorization") == "Bearer test-key"
    assert request.get_header("Content-type") == "application/json"

    sent_payload = json.loads(
        request.data.decode("utf-8")
    )

    assert sent_payload["model"] == "openrouter/free"
    assert sent_payload["stream"] is False
    assert sent_payload["temperature"] == 0.3
    assert sent_payload["max_tokens"] == 300

    assert sent_payload["messages"] == [
        {
            "role": "system",
            "content": "You are Weboku AI Master.",
        },
        {
            "role": "user",
            "content": "Say hello.",
        },
    ]


def test_ask_works_without_system_prompt():
    payload = {
        "choices": [
            {
                "message": {
                    "content": "Hello, player.",
                }
            }
        ]
    }

    engine = OpenRouterEngine(api_key="test-key")

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        return_value=make_response(payload),
    ):
        result = engine.ask("Hello.")

    assert result == "Hello, player."


def test_explain_uses_weboku_system_prompt():
    payload = {
        "choices": [
            {
                "message": {
                    "content": "Check the center window.",
                }
            }
        ]
    }

    engine = OpenRouterEngine(api_key="test-key")

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        return_value=make_response(payload),
    ) as mock_urlopen:
        result = engine.explain(
            "Explain R5C5."
        )

    assert result == "Check the center window."

    request = mock_urlopen.call_args.args[0]

    sent_payload = json.loads(
        request.data.decode("utf-8")
    )

    system_message = sent_payload["messages"][0]

    assert system_message["role"] == "system"
    assert "AI Master" in system_message["content"]
    assert "SOLVE" in system_message["content"]
    assert "UNLOCK" in system_message["content"]
    assert "CLIMB" in system_message["content"]
    assert "REACH" in system_message["content"]
    assert "MARRY" in system_message["content"]


def test_weboku_system_prompt_prevents_game_mutation_claims():
    prompt = OpenRouterEngine.weboku_system_prompt()

    assert "NOT the game engine" in prompt
    assert "Never claim to have changed the board" in prompt
    assert "Never invent Sudoku candidates" in prompt


def test_invalid_json_response_raises_error():
    engine = OpenRouterEngine(api_key="test-key")

    class InvalidResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def read(self):
            return b"not valid json"

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        return_value=InvalidResponse(),
    ):
        with pytest.raises(
            OpenRouterError,
            match="invalid JSON",
        ):
            engine.ask("Hello.")


def test_missing_assistant_content_raises_error():
    payload = {
        "choices": [
            {
                "message": {}
            }
        ]
    }

    engine = OpenRouterEngine(api_key="test-key")

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        return_value=make_response(payload),
    ):
        with pytest.raises(
            OpenRouterError,
            match="assistant content",
        ):
            engine.ask("Hello.")


def test_http_error_is_converted_to_openrouter_error():
    error = urllib.error.HTTPError(
        url="https://openrouter.ai/api/v1/chat/completions",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=None,
    )

    engine = OpenRouterEngine(api_key="test-key")

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        side_effect=error,
    ):
        with pytest.raises(
            OpenRouterError,
            match="HTTP 401",
        ):
            engine.ask("Hello.")


def test_url_error_is_converted_to_openrouter_error():
    error = urllib.error.URLError(
        "Connection failed"
    )

    engine = OpenRouterEngine(api_key="test-key")

    with patch(
        "weboku.openrouter_engine.urllib.request.urlopen",
        side_effect=error,
    ):
        with pytest.raises(
            OpenRouterError,
            match="Could not connect",
        ):
            engine.ask("Hello.")


def test_engine_does_not_store_prompt_or_game_state():
    engine = OpenRouterEngine(api_key="test-key")

    assert not hasattr(engine, "game")
    assert not hasattr(engine, "board")
    assert not hasattr(engine, "score")
    assert not hasattr(engine, "objectives")