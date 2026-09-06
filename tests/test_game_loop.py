"""Tests for the Weboku main game loop."""

from main import GameLoop


class FakeGame:
    """Small fake Game used to test the loop independently."""

    def __init__(self):
        self.started = False
        self.playing = True
        self.status_calls = 0

    def start(self):
        self.started = True
        return "started"

    def can_play(self):
        return self.playing

    def status(self):
        self.status_calls += 1
        return {
            "status": "PLAYING",
            "score": 0,
        }


def test_game_loop_starts_game():
    game = FakeGame()
    outputs = []

    loop = GameLoop(
        game,
        input_fn=lambda _: "quit",
        output_fn=outputs.append,
    )

    loop.start()

    assert game.started is True


def test_game_loop_stops_on_quit():
    game = FakeGame()

    loop = GameLoop(
        game,
        input_fn=lambda _: "quit",
        output_fn=lambda _: None,
    )

    loop.start()

    assert loop.running is False


def test_game_loop_accepts_exit():
    game = FakeGame()

    loop = GameLoop(game)

    result = loop.handle_command("exit")

    assert result is None
    assert loop.running is False


def test_game_loop_accepts_q():
    game = FakeGame()

    loop = GameLoop(game)

    loop.handle_command("q")

    assert loop.running is False


def test_game_loop_status_delegates_to_game():
    game = FakeGame()
    outputs = []

    loop = GameLoop(
        game,
        output_fn=outputs.append,
    )

    result = loop.handle_command("status")

    assert result == {
        "status": "PLAYING",
        "score": 0,
    }

    assert game.status_calls == 1
    assert outputs[-1] == {
        "status": "PLAYING",
        "score": 0,
    }


def test_game_loop_help_command():
    game = FakeGame()
    outputs = []

    loop = GameLoop(
        game,
        output_fn=outputs.append,
    )

    loop.handle_command("help")

    assert len(outputs) == 1
    assert "start" in outputs[0]
    assert "status" in outputs[0]
    assert "quit" in outputs[0]


def test_empty_command_does_nothing():
    game = FakeGame()
    outputs = []

    loop = GameLoop(
        game,
        output_fn=outputs.append,
    )

    result = loop.handle_command("   ")

    assert result is None
    assert outputs == []


def test_unknown_command_does_not_crash():
    game = FakeGame()
    outputs = []

    loop = GameLoop(
        game,
        output_fn=outputs.append,
    )

    loop.handle_command("something")

    assert len(outputs) == 1
    assert "not handled" in outputs[0]


def test_loop_can_stop_when_game_cannot_continue():
    game = FakeGame()
    game.playing = False

    inputs_called = []

    def fake_input(_):
        inputs_called.append(True)
        return "quit"

    loop = GameLoop(
        game,
        input_fn=fake_input,
        output_fn=lambda _: None,
    )

    loop.run()

    assert inputs_called == []


def test_loop_processes_multiple_commands():
    game = FakeGame()
    commands = iter(["help", "status", "quit"])
    outputs = []

    def fake_input(_):
        return next(commands)

    loop = GameLoop(
        game,
        input_fn=fake_input,
        output_fn=outputs.append,
    )

    loop.start()

    assert loop.running is False
    assert game.started is True
    assert game.status_calls == 1
    assert len(outputs) >= 3