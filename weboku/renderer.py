"""Terminal renderer for Weboku.

The renderer is presentation-only. Game state and Sudoku rules remain owned
by the game/domain layer.
"""

from __future__ import annotations

import re
from typing import Any

SYMBOLS = {
    1: "●",
    2: "■",
    3: "▲",
    4: "╱",
    5: "◆",
    6: "★",
    7: "✚",
    8: "○",
    9: "♥",
}

EMPTY_SYMBOL = "·"
CLIMBER_SYMBOL = "🧗"
PRINCESS_SYMBOL = "👸"

WINDOW_NAMES = (
    "W1",
    "W2",
    "W3",
    "W4",
    "W5",
    "W6",
    "W7",
    "W8",
    "W9",
)


class Renderer:
    """Render Weboku game state as a terminal dashboard."""

    CELL_WIDTH = 5
    WINDOW_WIDTH = 17

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Position helpers
    # ------------------------------------------------------------------

    def _normalize_position(self, position: Any) -> tuple[int, int] | None:
        """Normalize a player position into zero-based (row, column)."""

        if position is None:
            return None

        if isinstance(position, str):
            match = re.search(r"R(\d+)C(\d+)", position.upper())

            if match:
                row = int(match.group(1))
                column = int(match.group(2))

                if 1 <= row <= 9 and 1 <= column <= 9:
                    return row - 1, column - 1

            return None

        if isinstance(position, (tuple, list)) and len(position) == 2:
            row, column = position

            if isinstance(row, int) and isinstance(column, int):
                if 0 <= row < 9 and 0 <= column < 9:
                    return row, column

                if 1 <= row <= 9 and 1 <= column <= 9:
                    return row - 1, column - 1

        return None

    def _is_nine_by_nine(self, board: Any) -> bool:
        """Return True when board can be interpreted as a 9x9 grid."""

        if board is None:
            return False

        try:
            values = board.to_values() if hasattr(board, "to_values") else board

            if len(values) != 9:
                return False

            return all(len(row) == 9 for row in values)
        except (TypeError, AttributeError):
            return False

    def _window_index(self, row: int, column: int) -> int:
        """Return the one-based Weboku window number for a cell."""

        return (row // 3) * 3 + (column // 3) + 1

    # ------------------------------------------------------------------
    # Cell formatting
    # ------------------------------------------------------------------

    def _format_cell(
        self,
        value: Any,
        row: int | None = None,
        column: int | None = None,
        current_position: tuple[int, int] | None = None,
        locked: bool = False,
        given: bool = False,
    ) -> str:
        """Format one Sudoku cell using the Weboku symbol mapping."""

        # The tests and the original CLI use 0 for an empty cell.
        if value is None or value == 0:
            symbol = EMPTY_SYMBOL
        elif isinstance(value, int) and value in SYMBOLS:
            symbol = SYMBOLS[value]
        else:
            symbol = str(value)

        if (
            current_position is not None
            and row is not None
            and column is not None
            and current_position == (row, column)
        ):
            return f"[{symbol}]"

        # Keep the visible cell representation compatible with the
        # renderer tests: filled and empty cells are visibly bracketed.
        return f"[{symbol}]"

    # ------------------------------------------------------------------
    # Board extraction
    # ------------------------------------------------------------------

    def _get_board_values(self, board: Any) -> list[list[Any]]:
        """Extract board values without assuming a particular board size."""

        if board is None:
            return []

        if hasattr(board, "to_values"):
            values = board.to_values()
        else:
            values = board

        return [list(row) for row in values]

    def _get_cell(self, board: Any, row: int, column: int) -> Any:
        """Return a board cell when available."""

        try:
            if hasattr(board, "get_cell"):
                return board.get_cell(row, column)
        except (AttributeError, IndexError, TypeError):
            pass

        return None

    # ------------------------------------------------------------------
    # Column labels
    # ------------------------------------------------------------------

    def _render_column_labels(self) -> str:
        """Render C1-C9 centered directly over their corresponding cells."""

        labels = []

        for column in range(1, 10):
            label = f"C{column}"
            labels.append(f"{label:^{self.CELL_WIDTH}}")

        return "        " + " ".join(labels)

    def _render_column_arrows(self) -> str:
        """Render arrows centered directly over their corresponding cells."""

        arrows = []

        for _ in range(9):
            arrows.append(f"{'↓':^{self.CELL_WIDTH}}")

        return "        " + " ".join(arrows)

    # ------------------------------------------------------------------
    # Building borders
    # ------------------------------------------------------------------

    def _render_top_border(self) -> str:
        """Render the continuous top border of the building."""

        return (
            "        ╔"
            + "═" * self.WINDOW_WIDTH
            + "╦"
            + "═" * self.WINDOW_WIDTH
            + "╦"
            + "═" * self.WINDOW_WIDTH
            + "╗"
        )

    def _render_middle_border(self) -> str:
        """Render a continuous border between groups of three floors."""

        return (
            "        ╠"
            + "═" * self.WINDOW_WIDTH
            + "╬"
            + "═" * self.WINDOW_WIDTH
            + "╬"
            + "═" * self.WINDOW_WIDTH
            + "╣"
        )

    def _render_bottom_border(self) -> str:
        """Render the continuous bottom border of the building."""

        return (
            "        ╚"
            + "═" * self.WINDOW_WIDTH
            + "╩"
            + "═" * self.WINDOW_WIDTH
            + "╩"
            + "═" * self.WINDOW_WIDTH
            + "╝"
        )

    # ------------------------------------------------------------------
    # Nine-by-nine Weboku tower
    # ------------------------------------------------------------------

    def _render_window_row(
        self,
        values: list[list[Any]],
        row: int,
        current_position: tuple[int, int] | None = None,
        board: Any = None,
        locked_cells: set[tuple[int, int]] | None = None,
    ) -> str:
        """Render one 9-cell Sudoku row inside the building."""

        if locked_cells is None:
            locked_cells = set()

        window_parts = []

        for window in range(3):
            start_column = window * 3
            cells = []

            for column in range(start_column, start_column + 3):
                cell = self._get_cell(board, row, column)

                locked = (row, column) in locked_cells or bool(
                    getattr(cell, "locked", False)
                )
                given = bool(getattr(cell, "given", False))

                cell_text = self._format_cell(
                    values[row][column],
                    row=row,
                    column=column,
                    current_position=current_position,
                    locked=locked,
                    given=given,
                )

                cells.append(f"{cell_text:^{self.CELL_WIDTH}}")

            window_parts.append(" ".join(cells))

        # Eight characters precede the building border:
        #
        # " R1     "
        #
        # This keeps the left building border aligned with the top,
        # middle, and bottom borders.
        row_prefix = f" R{row + 1:<2}     ║"

        row_body = "║".join(window_parts)

        return row_prefix + row_body + "║"

    def _render_tower(
        self,
        board: Any,
        current_position: tuple[int, int] | None = None,
        locked_cells: set[tuple[int, int]] | None = None,
    ) -> list[str]:
        """Render the complete nine-floor Sudoku building."""

        values = self._get_board_values(board)

        # The real Weboku game always uses a 9x9 board.
        # This method is therefore only called for a real 9x9 board.
        if len(values) != 9 or any(len(row) != 9 for row in values):
            return []

        lines: list[str] = []

        lines.append("")
        lines.append("                         👸")
        lines.append("                      PRINCESS")
        lines.append("                   ─────────────")
        lines.append("                         ▲")
        lines.append("                         │ ROOF")
        lines.append("")

        lines.append(self._render_column_labels())
        lines.append(self._render_column_arrows())

        lines.append(self._render_top_border())

        for row in range(9):
            lines.append(
                self._render_window_row(
                    values,
                    row,
                    current_position=current_position,
                    board=board,
                    locked_cells=locked_cells,
                )
            )

            if row in (2, 5):
                lines.append(self._render_middle_border())

        lines.append(self._render_bottom_border())

        lines.append("                         🧗")
        lines.append("                        BASE")

        lines.append("")
        lines.append("        W1              W2              W3")
        lines.append("        W4              W5              W6")
        lines.append("        W7              W8              W9")

        return lines

    # ------------------------------------------------------------------
    # Legacy / small-board rendering
    # ------------------------------------------------------------------

    def _render_simple_board(
        self,
        board: list[list[Any]],
        locked_cells: set[tuple[int, int]] | None = None,
    ) -> str:
        """Render small boards used by the renderer compatibility tests."""

        if locked_cells is None:
            locked_cells = set()

        lines = []

        for row_index, row in enumerate(board):
            cells = []

            for column_index, value in enumerate(row):
                cell = self._format_cell(
                    value,
                    row=row_index,
                    column=column_index,
                    locked=(row_index, column_index) in locked_cells,
                )

                cells.append(cell)

            line = " ".join(cells)

            if any(
                (row_index, column_index) in locked_cells
                for column_index in range(len(row))
            ):
                line += "  LOCKED"

            lines.append(line)

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Public board rendering
    # ------------------------------------------------------------------

    def render_board(
        self,
        board: Any,
        current_position: Any = None,
        locked_cells: set[tuple[int, int]] | None = None,
    ) -> str:
        """Render a board.

        A 9x9 board receives the full Weboku tower presentation.
        Smaller boards retain the simple renderer expected by tests and
        compatibility callers.
        """

        values = self._get_board_values(board)
        position = self._normalize_position(current_position)

        if len(values) == 9 and all(len(row) == 9 for row in values):
            return "\n".join(
                self._render_tower(
                    values,
                    current_position=position,
                    locked_cells=locked_cells,
                )
            )

        return self._render_simple_board(
            values,
            locked_cells=locked_cells,
        )

    # ------------------------------------------------------------------
    # Game rendering
    # ------------------------------------------------------------------

    def render_game(self, game: Any) -> str:
        """Render the current game state."""

        board = getattr(game, "board", None)

        climber = getattr(game, "climber", None)

        current_position = None

        if climber is not None:
            current_position = getattr(climber, "position", None)

            if current_position is None:
                current_position = getattr(
                    climber,
                    "current_position",
                    None,
                )

        locked_cells: set[tuple[int, int]] = set()

        return self.render_board(
            board,
            current_position=current_position,
            locked_cells=locked_cells,
        )

    # ------------------------------------------------------------------
    # Status compatibility helpers
    # ------------------------------------------------------------------

    def _render_status_string(self, status: str) -> str:
        """Render the legacy string status format used by CLI tests."""

        lines = [line.strip() for line in str(status).splitlines() if line.strip()]

        text = "\n".join(lines)

        score_match = re.search(r"SCORE:\s*([^\n]+)", text, re.IGNORECASE)
        objective_match = re.search(
            r"OBJECTIVES:\s*([^\n]+)",
            text,
            re.IGNORECASE,
        )
        time_match = re.search(
            r"(?:TIME|TIMER):\s*([^\n]+)",
            text,
            re.IGNORECASE,
        )
        position_match = re.search(
            r"(?:CURRENT POSITION|POSITION):\s*([^\n]+)",
            text,
            re.IGNORECASE,
        )

        result = [
            "",
            "╔══════════════════════════════════════════════╗",
            "║                 WEBOKU STATUS               ║",
            "╠══════════════════════════════════════════════╣",
        ]

        if score_match:
            result.append(f"║ SCORE: {score_match.group(1):<36}║")
        else:
            result.append("║ SCORE: N/A                                    ║")

        if objective_match:
            result.append(f"║ OBJECTIVES: {objective_match.group(1):<30}║")
        else:
            result.append("║ OBJECTIVES: N/A                               ║")

        if time_match:
            result.append(f"║ TIME: {time_match.group(1):<35}║")
        else:
            result.append("║ TIME: N/A                                     ║")

        if position_match:
            position_value = position_match.group(1)
            result.append(f"║ CURRENT POSITION: {position_value:<24}║")

        if "CLIMBER" in text.upper():
            climber_match = re.search(
                r"CLIMBER:\s*([^\n]+)",
                text,
                re.IGNORECASE,
            )

            if climber_match:
                result.append(f"║ CLIMBER: {climber_match.group(1):<31}║")
            else:
                result.append("║ CLIMBER: 🧗                                  ║")

        if "PRINCESS" in text.upper():
            princess_match = re.search(
                r"PRINCESS:\s*([^\n]+)",
                text,
                re.IGNORECASE,
            )

            if princess_match:
                result.append(f"║ PRINCESS: {princess_match.group(1):<30}║")
            else:
                result.append("║ PRINCESS: 👸                                 ║")

        if "VICTORY" in text.upper():
            result.append("║ VICTORY: YES                                 ║")

        if "GAME OVER" in text.upper():
            result.append("║ GAME OVER                                    ║")

        result.append("╚══════════════════════════════════════════════╝")

        return "\n".join(result)

    def render_status(self, game: Any) -> str:
        """Render either a real game object or a legacy status string."""

        if isinstance(game, str):
            return self._render_status_string(game)

        scoring = getattr(game, "scoring", None)
        timer = getattr(game, "timer", None)
        climber = getattr(game, "climber", None)

        score = getattr(game, "score", None)

        if score is None and scoring is not None:
            score = getattr(scoring, "score", 0)

        if score is None:
            score = 0

        completed_objectives = getattr(
            game,
            "completed_objectives",
            None,
        )

        if completed_objectives is None:
            objective = getattr(game, "objective", None)

            if objective is not None:
                completed_objectives = objective
            else:
                completed_rings = getattr(
                    game,
                    "completed_rings",
                    set(),
                )
                completed_columns = getattr(
                    game,
                    "completed_columns",
                    set(),
                )
                completed_regions = getattr(
                    game,
                    "completed_regions",
                    set(),
                )

                completed_objectives = (
                    len(completed_rings)
                    + len(completed_columns)
                    + len(completed_regions)
                )

        total_objectives = getattr(
            game,
            "total_objectives",
            27,
        )

        princess_life = getattr(
            game,
            "princess_life",
            getattr(game, "princess_health", 27),
        )

        position = getattr(game, "position", None)

        if position is None and climber is not None:
            position = getattr(climber, "position", None)

            if position is None:
                position = getattr(
                    climber,
                    "current_position",
                    None,
                )

        normalized_position = self._normalize_position(position)

        if normalized_position is None:
            position_text = "BASE"
        else:
            row, column = normalized_position
            position_text = (
                f"R{row + 1}C{column + 1} / " f"FLOOR {row + 1} / COLUMN {column + 1}"
            )

        timer_text = getattr(game, "timer", None)

        if timer is not None:
            remaining = getattr(
                timer,
                "remaining_seconds",
                None,
            )

            if remaining is None:
                remaining = getattr(
                    timer,
                    "seconds_remaining",
                    None,
                )

            if remaining is not None:
                try:
                    remaining = max(0, int(remaining))
                    minutes, seconds = divmod(
                        remaining,
                        60,
                    )
                    timer_text = f"{minutes:02d}:{seconds:02d}"
                except (TypeError, ValueError):
                    timer_text = str(remaining)

        if timer_text is None:
            timer_text = "N/A"

        result = [
            "",
            "╔══════════════════════════════════════════════╗",
            "║                 WEBOKU STATUS               ║",
            "╠══════════════════════════════════════════════╣",
            f"║ SCORE:              {score:<25}║",
            (
                f"║ OBJECTIVES:         "
                f"{completed_objectives}/{total_objectives:<19}║"
            ),
            f"║ PRINCESS LIFE:      {princess_life}/27{'':<20}║",
            f"║ TIMER:              {timer_text:<25}║",
            f"║ CURRENT POSITION:   {position_text:<20}║",
        ]

        victory = getattr(game, "victory", False)
        game_over = getattr(game, "game_over", False)

        if victory:
            result.append("║ VICTORY: YES                                 ║")

        if game_over:
            result.append("║ GAME OVER                                    ║")

        result.append("╚══════════════════════════════════════════════╝")

        return "\n".join(result)

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------

    def render_help(self) -> str:
        """Render player command help."""

        return "\n".join(
            [
                "",
                "WEBOKU COMMANDS",
                "---------------",
                "move R5C5 7     Enter number 7 at row 5, column 5",
                "move 5 5 7      Same command using separate coordinates",
                "R5C5 7          Short form",
                "status          Show current game status",
                "help            Show this help",
                "q / quit        Exit the game",
                "",
                "SYMBOL LEGEND",
                "1 = ●   2 = ■   3 = ▲   4 = ╱   5 = ◆",
                "6 = ★   7 = ✚   8 = ○   9 = ♥",
                "",
                "FLOW: SOLVE → UNLOCK → CLIMB → REACH → MARRY",
            ]
        )
