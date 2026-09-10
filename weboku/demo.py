"""Deterministic end-to-end demonstration for Weboku."""

from io import StringIO
from typing import Callable

from .board import Board
from .climber import Climber
from .game import Game
from .scoring import Scoring
from .sudoku import SudokuEngine
from .timer import GameTimer

DEMO_SOLUTION = (
    (5, 3, 4, 6, 7, 8, 9, 1, 2),
    (6, 7, 2, 1, 9, 5, 3, 4, 8),
    (1, 9, 8, 3, 4, 2, 5, 6, 7),
    (8, 5, 9, 7, 6, 1, 4, 2, 3),
    (4, 2, 6, 8, 5, 3, 7, 9, 1),
    (7, 1, 3, 9, 2, 4, 8, 5, 6),
    (9, 6, 1, 5, 3, 7, 2, 8, 4),
    (2, 8, 7, 4, 1, 9, 6, 3, 5),
    (3, 4, 5, 2, 8, 6, 1, 7, 9),
)


def create_demo_game() -> Game:
    """Create a real Weboku game using the actual engine components."""

    board = Board()
    sudoku_engine = SudokuEngine(board)
    climber = Climber()
    scoring = Scoring()
    timer = GameTimer(600)

    return Game(
        board=board,
        sudoku_engine=sudoku_engine,
        climber=climber,
        scoring=scoring,
        timer=timer,
        difficulty="beginner",
        score_threshold=0,
    )


def _print_header(output: Callable[[str], None]) -> None:
    output("")
    output("=" * 64)
    output("                    WEBOKU RIC-09 DEMO")
    output("=" * 64)
    output("SOLVE -> UNLOCK -> CLIMB -> REACH -> MARRY")
    output("")


def _print_state(
    game: Game,
    output: Callable[[str], None],
    title: str = "ENGINE STATE",
) -> None:
    output("")
    output(f"[{title}]")
    output(f"Objectives : {game.completed_objectives}/27")
    output(
        f"Rings      : {len(game.completed_rings)}/9    "
        f"Columns    : {len(game.completed_columns)}/9    "
        f"Windows    : {len(game.completed_regions)}/9"
    )
    output(f"Score      : {game.score}    " f"Princess   : {game.princess_life}/27")
    output(
        f"Rescue     : {game.rescue_credits}    " f"Timeouts   : {game.failed_timeouts}"
    )
    output(f"Position   : {game.current_position}")
    output(f"Status     : {game.game_status}")


def _show_partial_board(
    game: Game,
    output: Callable[[str], None],
) -> None:
    """Demonstrate genuine Sudoku moves through the real Game engine."""

    output("[PARTIAL SUDOKU]")
    output("Entering several valid Sudoku values through " "Game.process_move().")

    moves = (
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
    )

    for ring, column in moves:
        value = DEMO_SOLUTION[ring - 1][column - 1]
        symbol = game.value_to_symbol(value)
        result = game.process_move(ring, column, symbol)

        output(f"  R{ring}C{column} = {symbol} " f"(value {value}) -> " f"{'VALID' if 
result.success else 'REJECTED'}")


def _demonstrate_timeout(
    game: Game,
    output: Callable[[str], None],
) -> None:
    """Demonstrate the real timeout and princess-life mechanic."""

    output("")
    output("[TIMEOUT TEST]")

    before = game.princess_life
    result = game.handle_timeout()

    output("Forcing one timer timeout through the real Game engine.")
    output(f"  Timeout result: " f"{'TIMEOUT' if result else 'REJECTED'}")
    output(
        f"  Timeout applied -> Princess life "
        f"{before}/{before} -> {game.princess_life}/{before}"
    )
    output(f"  Failed timeouts recorded: {game.failed_timeouts}")
    output(f"  Rescue credits: {game.rescue_credits}")


def _prepare_final_fixture(
    game: Game,
    output: Callable[[str], None],
) -> None:
    """
    Prepare a deterministic near-complete Sudoku fixture.

    The fixture contains one empty cell: R1C1.

    The other 80 cells form a valid completed Sudoku. Because Game's
    authoritative objective sets start empty, the final R1C1 move allows
    the real engine to discover all 27 completed objectives.
    """

    values = [list(row) for row in DEMO_SOLUTION]

    # Exactly one cell remains editable.
    # R1 is the roof, so the final movement reaches the princess.
    values[0][0] = None

    game.board.load_values(values)

    output("")
    output("[FINAL SUDOKU FIXTURE]")
    output("Loaded a deterministic valid Sudoku with exactly one cell empty.")
    output("Final editable cell: R1C1")


def _complete_final_objective(
    game: Game,
    output: Callable[[str], None],
) -> None:
    """Complete the final cell through the real Game.process_move() API."""

    value = DEMO_SOLUTION[0][0]
    symbol = game.value_to_symbol(value)

    output("")
    output("[FINAL MOVE]")
    output(f"Submitting R1C1 = {symbol} (value {value})")

    result = game.process_move(1, 1, symbol)

    output(f"  Move result: " f"{'VALID' if result.success else 'REJECTED'}")
    output(f"  New objectives: {result.new_objectives}")
    output(f"  Score gained: {result.score_gained}")
    output(f"  Automatic movement: " f"{'YES' if result.movement_occurred else 'NO'}")
    output(f"  Final objectives: {game.completed_objectives}/27")
    output(f"  Rescue credits: {game.rescue_credits}")

    if result.success:
        output("  R1C1 is now locked by the completed objectives.")


def run_demo(output: Callable[[str], None] = print) -> Game:
    """
    Run the deterministic complete-game demonstration.

    Returns the final Game instance so tests and callers can inspect the
    authoritative state.
    """

    game = create_demo_game()

    _print_header(output)

    output("[GAME START]")
    game.start()
    output("  Game started through Game.start().")

    _show_partial_board(game, output)

    _demonstrate_timeout(game, output)

    _prepare_final_fixture(game, output)

    _print_state(game, output, "READY FOR FINAL OBJECTIVE")

    _complete_final_objective(game, output)

    # The Sudoku objectives are complete. The deterministic demo now
    # completes the final climb using the real Climber API.
    if game.completed_objectives == 27:
        if game.climber is not None:
            game.climber.move_to(1, 1)
            game.climber.reach_princess()
        output("")
        output("  Final climb: R9C9 -> R1C1")
        output("  Climber reached the roof.")

    # Victory determination remains inside the real Game engine.
    game._check_victory()

    _print_state(game, output, "FINAL ENGINE STATE")

    output("")

    if game.is_victory():
        output("27/27 OBJECTIVES COMPLETE")
        output("CLIMBER REACHED THE PRINCESS")
        output("VICTORY!")
        output("MARRIAGE COMPLETE.")
    elif game.is_game_over():
        output("GAME OVER")
    else:
        output("DEMO INCOMPLETE — ENGINE STATE DID NOT REACH VICTORY")

    output("")
    output("=" * 64)
    output("                    END OF RIC-09 DEMO")
    output("=" * 64)

    return game


def demo_text() -> str:
    """Return the complete demo output as text."""

    buffer = StringIO()
    run_demo(output=lambda message: print(message, file=buffer))
    return buffer.getvalue()


if __name__ == "__main__":
    run_demo()
