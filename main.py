"""
Weboku application entry point.

RIC-05: Main Game Loop

The main loop is intentionally thin. It starts the Game, receives
commands/input, delegates game actions to Game, and stops when the
game reaches a terminal state.

Business rules remain inside Game.
CLI presentation remains separate.
"""

from __future__ import annotations

from typing import Any


class GameLoop:
    """Coordinate the main Weboku application loop."""

    def __init__(self, game: Any, input_fn=input, output_fn=print) -> None:
        self.game = game
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.running = False

    def start(self) -> None:
        """Start the game loop."""
        self.game.start()
        self.running = True

        self.output_fn("Welcome to Weboku!")
        self.output_fn("Solve → Unlock → Climb → Reach → Marry")

        self.run()

    def run(self) -> None:
        """Run the main command/input loop until the game ends."""
        while self.running and self._game_can_continue():
            command = self.input_fn("weboku> ")
            self.handle_command(command)

    def handle_command(self, command: str) -> Any:
        """
        Process one top-level command.

        The loop owns command routing only. Game rules are delegated
        to the Game object.
        """
        if command is None:
            return None

        command = command.strip()

        if not command:
            return None

        command_name = command.split()[0].lower()

        if command_name in {"quit", "exit", "q"}:
            self.stop()
            return None

        if command_name == "start":
            if hasattr(self.game, "start"):
                return self.game.start()
            return None

        if command_name == "status":
            return self._show_status()

        if command_name == "help":
            return self._show_help()

        self.output_fn(
            "Command not handled by the core loop yet. "
            "Use the CLI layer for detailed commands."
        )
        return None

    def stop(self) -> None:
        """Stop the main application loop."""
        self.running = False

    def _game_can_continue(self) -> bool:
        """Return whether the game is still playable."""
        if hasattr(self.game, "can_play"):
            return bool(self.game.can_play())

        if hasattr(self.game, "is_victory") and self.game.is_victory():
            return False

        if hasattr(self.game, "is_game_over") and self.game.is_game_over():
            return False

        return True

    def _show_status(self) -> Any:
        """Display the current game state when supported."""
        if hasattr(self.game, "status"):
            status = self.game.status()
            self.output_fn(status)
            return status

        self.output_fn("Game status is not available yet.")
        return None

    def _show_help(self) -> None:
        """Display core-loop help."""
        self.output_fn(
            "\n"
            "Weboku commands:\n"
            "  start   Start the game\n"
            "  status  Show game status\n"
            "  help    Show this help\n"
            "  quit    Exit Weboku\n"
        )


def create_game():
    """
    Create the Weboku Game instance.

    Dependency construction will be connected here as the team modules
    become available.
    """
    from weboku.game import Game

    return Game()


def main() -> None:
    """Application entry point."""
    game = create_game()
    loop = GameLoop(game)
    loop.start()


if __name__ == "__main__":
    main()