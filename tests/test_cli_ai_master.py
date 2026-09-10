"""Tests for AI Master commands exposed through the Weboku CLI."""

from __future__ import annotations

from unittest.mock import Mock

from weboku.ai_master import AIMaster
from weboku.cli import CLI


def make_cli(game=None):
    """Create a CLI with a mocked AI Master."""
    ai_master = Mock(spec=AIMaster)

    cli = CLI(
        game=game,
        ai_master=ai_master,
    )

    return cli, ai_master


def test_ai_command_shows_available_commands():
    cli, _ = make_cli()

    result = cli.handle_command("ai")

    assert "AI MASTER" in result
    assert "ai rules" in result
    assert "ai status" in result
    assert "ai hint R5C5" in result
    assert "ai ask <question>" in result


def test_ai_rules_calls_ai_master():
    cli, ai_master = make_cli()

    ai_master.explain_rules.return_value = "SOLVE → UNLOCK → CLIMB → REACH → MARRY"

    result = cli.handle_command("ai rules")

    assert "SOLVE" in result
    assert "UNLOCK" in result
    assert "CLIMB" in result
    assert "REACH" in result
    assert "MARRY" in result

    ai_master.explain_rules.assert_called_once()


def test_ai_status_uses_current_game():
    game = Mock()

    cli, ai_master = make_cli(game)

    ai_master.explain_status.return_value = (
        "Objectives: 5/27\n" "Score: 500\n" "Princess life: 27/27"
    )

    result = cli.handle_command("ai status")

    assert "Objectives: 5/27" in result
    assert "Score: 500" in result
    assert "Princess life: 27/27" in result

    ai_master.explain_status.assert_called_once_with(game)


def test_ai_hint_accepts_r1c1_format():
    game = Mock()

    cli, ai_master = make_cli(game)

    ai_master.get_hint.return_value = "AI MASTER — R1C1 candidates: 2, 4"

    result = cli.handle_command("ai hint R1C1")

    assert "R1C1" in result
    assert "2, 4" in result

    ai_master.get_hint.assert_called_once_with(
        game,
        1,
        1,
    )


def test_ai_hint_accepts_lowercase_position():
    game = Mock()

    cli, ai_master = make_cli(game)

    ai_master.get_hint.return_value = "AI MASTER — R5C5 candidates: 2, 5, 6"

    result = cli.handle_command("ai hint r5c5")

    assert "R5C5" in result
    assert "2, 5, 6" in result

    ai_master.get_hint.assert_called_once_with(
        game,
        5,
        5,
    )


def test_ai_hint_rejects_missing_position():
    game = Mock()

    cli, ai_master = make_cli(game)

    result = cli.handle_command("ai hint")

    assert "Usage: ai hint R5C5" in result

    ai_master.get_hint.assert_not_called()


def test_ai_hint_rejects_invalid_position():
    game = Mock()

    cli, ai_master = make_cli(game)

    result = cli.handle_command("ai hint R10C5")

    assert "Invalid position" in result

    ai_master.get_hint.assert_not_called()


def test_ai_hint_requires_active_game():
    cli, ai_master = make_cli(game=None)

    result = cli.handle_command("ai hint R5C5")

    assert "No active game" in result

    ai_master.get_hint.assert_not_called()


def test_ai_ask_sends_question_to_ai_master():
    game = Mock()

    cli, ai_master = make_cli(game)

    ai_master.explain_status.return_value = (
        "Objectives: 3/27\n" "Score: 100\n" "Princess life: 27/27"
    )

    ai_master.ask.return_value = (
        "Complete rows, columns and windows to unlock the tower."
    )

    result = cli.handle_command("ai ask How do I unlock the tower?")

    assert "Complete rows" in result

    ai_master.explain_status.assert_called_once_with(game)

    ai_master.ask.assert_called_once()

    prompt = ai_master.ask.call_args.args[0]

    assert "How do I unlock the tower?" in prompt
    assert "Objectives: 3/27" in prompt
    assert "Do not claim to change or control the game." in prompt


def test_ai_ask_requires_question():
    cli, ai_master = make_cli()

    result = cli.handle_command("ai ask")

    assert "Usage: ai ask <question>" in result

    ai_master.ask.assert_not_called()


def test_unknown_ai_command_is_rejected():
    cli, ai_master = make_cli()

    result = cli.handle_command("ai dance")

    assert "Unknown AI command" in result

    ai_master.explain_rules.assert_not_called()
    ai_master.explain_status.assert_not_called()
    ai_master.get_hint.assert_not_called()
    ai_master.ask.assert_not_called()
