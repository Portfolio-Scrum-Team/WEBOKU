"""Integration tests for AI Master with the OpenRouter engine."""

from __future__ import annotations

from unittest.mock import Mock

from weboku.ai_master import AIMaster
from weboku.openrouter_engine import OpenRouterEngine


def test_ai_master_can_use_openrouter_engine():
    engine = Mock(spec=OpenRouterEngine)
    engine.explain.return_value = "WEBOKU AI ONLINE"

    ai = AIMaster(engine=engine)

    response = ai.ask("Reply with exactly: WEBOKU AI ONLINE")

    assert response == "WEBOKU AI ONLINE"
    engine.explain.assert_called_once()


def test_ai_master_remains_advisory_only():
    engine = Mock(spec=OpenRouterEngine)
    engine.explain.return_value = "The next move should follow Sudoku rules."

    ai = AIMaster(engine=engine)

    response = ai.ask("What should the player do next?")

    assert response == "The next move should follow Sudoku rules."
    assert not hasattr(ai, "board")
    assert not hasattr(ai, "score")
    assert not hasattr(ai, "game_state")


def test_ai_master_handles_openrouter_failure():
    engine = Mock(spec=OpenRouterEngine)
    engine.explain.side_effect = RuntimeError("OpenRouter unavailable")

    ai = AIMaster(engine=engine)

    response = ai.ask("Give me advice.")

    assert "unavailable" in response.lower()


def test_ai_master_explain_rules_does_not_call_api():
    engine = Mock(spec=OpenRouterEngine)

    ai = AIMaster(engine=engine)

    response = ai.explain_rules()

    assert "SOLVE" in response
    assert "UNLOCK" in response
    assert "CLIMB" in response
    assert "REACH" in response
    assert "MARRY" in response

    engine.explain.assert_not_called()


def test_ai_master_explain_status_does_not_call_api():
    engine = Mock(spec=OpenRouterEngine)

    game = Mock()
    game.completed_rings = {1, 2}
    game.completed_columns = {3}
    game.completed_regions = {1, 2}
    game.score = 500
    game.princess_life = 27
    game.game_status = "PLAYING"
    game.current_position = (3, 3)

    ai = AIMaster(engine=engine)

    response = ai.explain_status(game)

    assert "Objectives: 5/27" in response
    assert "Rings: 2/9" in response
    assert "Columns: 1/9" in response
    assert "Windows: 2/9" in response
    assert "Score: 500" in response
    assert "Princess life: 27/27" in response
    assert "R3C3" in response

    engine.explain.assert_not_called()
