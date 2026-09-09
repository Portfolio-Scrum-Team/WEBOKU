"""
Weboku application entry point.

RIC-05: Main Game Loop

The main loop coordinates the application while the Game class
remains the authoritative owner of game rules and state.
"""

from __future__ import annotations

import sys

from typing import Any


class GameLoop:
    """Coordinate the main Weboku application loop."""

    def __init__(
        self,
        game: Any,
        input_fn=input,
        output_fn=print,
    ) -> None:

        self.game = game
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.running = False

    def start(self) -> None:
        """Start the game loop."""

        self.game.start()
        self.running = True

        self.output_fn("Welcome to Weboku!")
        self.output_fn(
            "Solve → Unlock → Climb → Reach → Marry"
        )

        self.run()

    def run(self) -> None:
        """Run the command loop until the game ends."""

        while self.running and self._game_can_continue():

            command = self.input_fn("weboku> ")

            result = self.handle_command(command)

            if result is not None and result is not True:
                self._display_result(result)

    def handle_command(
        self,
        command: str,
    ) -> Any:
        """Process one top-level command."""

        if command is None:
            return None

        command = command.strip()

        if not command:
            return None

        command_name = command.split()[0].lower()

        # ------------------------------------------------------------
        # EXIT
        # ------------------------------------------------------------

        if command_name in {
            "quit",
            "exit",
            "q",
        }:
            self.stop()
            return None

        # ------------------------------------------------------------
        # START
        # ------------------------------------------------------------

        if command_name == "start":

            if hasattr(self.game, "start"):
                return self.game.start()

            return None

        # ------------------------------------------------------------
        # STATUS
        # ------------------------------------------------------------

        if command_name == "status":
            return self._show_status()

        # ------------------------------------------------------------
        # HELP
        # ------------------------------------------------------------

        if command_name == "help":
            return self._show_help()

        # ------------------------------------------------------------
        # DETAILED CLI COMMANDS
        # ------------------------------------------------------------

        if hasattr(self.game, "cli"):
            return self.game.cli.handle_command(
                command
            )

        if (
            command_name == "move"
            and hasattr(self.game, "move")
        ):
            return self.game.move(
                *command.split()[1:]
            )

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
            return bool(
                self.game.can_play()
            )

        if (
            hasattr(self.game, "is_victory")
            and self.game.is_victory()
        ):
            return False

        if (
            hasattr(self.game, "is_game_over")
            and self.game.is_game_over()
        ):
            return False

        return True

    def _show_status(self) -> Any:
        """Display the current game state when supported."""

        if hasattr(self.game, "status"):

            result = self.game.status()

            self.output_fn(result)

            return result

        self.output_fn(
            "Game status is not available yet."
        )

        return None

    def _show_help(self) -> str:
        """Return and display the complete Weboku command help."""

        if hasattr(self.game, "cli"):
            result = self.game.cli.show_help()

        else:
            result = (
                "\n"
                "Weboku commands:\n"
                "  start   Start the game\n"
                "  status  Show game status\n"
                "  help    Show this help\n"
                "  quit    Exit Weboku\n"
            )

        self.output_fn(result)

        return result

    def _display_result(
        self,
        result: Any,
    ) -> None:
        """Display command results safely."""

        if isinstance(result, str):
            self.output_fn(result)
            return

        if hasattr(result, "message"):

            self.output_fn(
                result.message
            )

            if getattr(
                result,
                "symbol",
                None,
            ):
                self.output_fn(
                    f"Position: "
                    f"R{result.floor}C{result.column}"
                )

                self.output_fn(
                    f"Symbol: {result.symbol}"
                )

            if getattr(
                result,
                "new_objectives",
                0,
            ):
                self.output_fn(
                    f"New objectives: "
                    f"{result.new_objectives}"
                )

            if getattr(
                result,
                "movement_occurred",
                False,
            ):
                self.output_fn(
                    f"Climber position: "
                    f"{result.current_position}"
                )

            self.output_fn(
                f"Score: {self.game.score}"
            )

            return

        if hasattr(
            result,
            "game_status",
        ):
            self.output_fn(
                f"Game status: "
                f"{result.game_status}"
            )
            return

        self.output_fn(
            str(result)
        )


def create_game():
    """Build the complete Weboku dependency graph."""

    from weboku.board import Board
    from weboku.sudoku import SudokuEngine
    from weboku.climber import Climber
    from weboku.scoring import Scoring
    from weboku.timer import (
        GameTimer,
        DIFFICULTY_SECONDS,
    )
    from weboku.player import Player
    from weboku.cli import CLI
    from weboku.game import Game

    # ------------------------------------------------------------
    # Core domain objects
    # ------------------------------------------------------------

    board = Board()

    sudoku_engine = SudokuEngine(
        board
    )

    climber = Climber()

    scoring = Scoring()

    # Beginner is the default difficulty.
    difficulty = "beginner"

    timer = GameTimer(
        DIFFICULTY_SECONDS[difficulty]
    )

    player = Player()

    # ------------------------------------------------------------
    # Game coordinator
    # ------------------------------------------------------------

    game = Game(
        board=board,
        sudoku_engine=sudoku_engine,
        climber=climber,
        scoring=scoring,
        timer=timer,
        player=player,
        difficulty=difficulty,
    )

    # ------------------------------------------------------------
    # Presentation layer
    # ------------------------------------------------------------

    game.cli = CLI(
        game=game,
        player=player,
    )

    return game


def main() -> None:
    """Application entry point."""

    if "--demo" in sys.argv:
        from weboku.demo import run_demo
        run_demo()
        return

    game = create_game()

    loop = GameLoop(
        game
    )

    loop.start()


if __name__ == "__main__":
    main()

