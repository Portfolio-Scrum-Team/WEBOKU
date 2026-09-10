from weboku.cli import CLI


class DummyGame:
    def __init__(self):
        self.moves = []

    def move(self, cell, value):
        self.moves.append((cell, value))
        return {"cell": cell, "value": value, "ok": True}

    def status(self):
        return "STATUS: ready"


def test_cli_welcome_contains_title():
    cli = CLI()
    text = cli.show_welcome()
    assert "WEBOKU" in text
    assert "SOLVE" in text


def test_cli_help_lists_commands():
    cli = CLI()
    text = cli.show_help()
    assert "help" in text.lower()
    assert "status" in text.lower()
    assert "quit" in text.lower()


def test_cli_handle_move_command():
    game = DummyGame()
    cli = CLI(game=game)
    result = cli.handle_command("move R5C5 7")
    assert result == {"cell": "R5C5", "value": 7, "ok": True}
    assert game.moves == [("R5C5", 7)]


def test_cli_accepts_short_move_format():
    game = DummyGame()
    cli = CLI(game=game)
    result = cli.handle_command("R5C5 7")
    assert result == {"cell": "R5C5", "value": 7, "ok": True}


def test_cli_accepts_row_column_move_format():
    game = DummyGame()
    cli = CLI(game=game)
    result = cli.handle_command("move 5 5 7")
    assert result == {"cell": "R5C5", "value": 7, "ok": True}


def test_cli_rejects_invalid_coordinates():
    cli = CLI()
    result = cli.handle_command("R0C1 5")
    assert "invalid" in str(result).lower()


def test_cli_save_and_load_commands():
    class SaveLoadGame:
        def __init__(self):
            self.saved = []
            self.loaded = []

        def save(self, path):
            self.saved.append(path)
            return {"action": "save", "path": path, "ok": True}

        def load(self, path):
            self.loaded.append(path)
            return {"action": "load", "path": path, "ok": True}

    game = SaveLoadGame()
    cli = CLI(game=game)
    assert cli.handle_command("save game.txt") == {
        "action": "save",
        "path": "game.txt",
        "ok": True,
    }
    assert cli.handle_command("load game.txt") == {
        "action": "load",
        "path": "game.txt",
        "ok": True,
    }


def test_cli_status_command_works():
    cli = CLI(game=DummyGame())
    assert "ready" in cli.handle_command("status").lower()


def test_cli_status_updates_after_move():
    class TrackingGame:
        def __init__(self):
            self.state = "ready"

        def move(self, cell, value):
            self.state = f"moved {cell}={value}"
            return {"cell": cell, "value": value, "ok": True}

        def status(self):
            return self.state

    cli = CLI(game=TrackingGame())
    cli.handle_command("move R5C5 7")
    assert "moved r5c5=7" in cli.handle_command("status").lower()


def test_cli_quit_command_works():
    cli = CLI()
    assert cli.handle_command("quit") == "Goodbye!"
