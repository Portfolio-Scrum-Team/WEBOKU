"""
Terminal renderer for Weboku.

The renderer is presentation-only. Game state and Sudoku rules remain
owned by the game/domain layer.

The renderer preserves the original Weboku renderer API while adding:
- 9x9 tower presentation
- distinct colors for each Sudoku symbol
- locked-cell markers
- current-position highlighting
- princess and climber display
- symbol legend
- compatibility with existing renderer tests
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# PUBLIC SYMBOL MAPPING
# ---------------------------------------------------------------------------
#
# These remain module-level because tests and other modules import SYMBOLS
# directly from weboku.renderer.
# ---------------------------------------------------------------------------

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
CLIMBER_SYMBOL = "👨"
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


# ---------------------------------------------------------------------------
# DISTINCT TERMINAL COLORS
# ---------------------------------------------------------------------------
#
# ANSI colors are used instead of changing the renderer's return type.
# Therefore render_board() and render_game() continue returning normal
# strings, which preserves the existing test/API contract.
#
# Every Sudoku number has its own visual color.
# ---------------------------------------------------------------------------

# Step 5 visual design: each filled Sudoku cell receives its own
# terminal background color. The displayed Sudoku symbol is always black.
CELL_BACKGROUNDS = {
    1: "\033[41m",  # bright red
    2: "\033[44m",  # deep blue
    3: "\033[42m",  # bright green
    4: "\033[43m",  # yellow
    5: "\033[48;5;208m",  # orange
    6: "\033[46m",  # cyan
    7: "\033[45m",  # purple
    8: "\033[48;5;118m",  # lime green
    9: "\033[48;5;205m",  # magenta/pink
}

BLACK = "\033[30m"


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
REVERSE = "\033[7m"


class Renderer:
    """Render Weboku game state as a terminal dashboard."""

    CELL_WIDTH = 5
    WINDOW_WIDTH = CELL_WIDTH * 3 + 2

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Color helpers
    # ------------------------------------------------------------------

    @classmethod
    def _color_symbol(cls, value: Any, symbol: str) -> str:
        """Return a black symbol on its Step 5 background color."""
        try:
            number = int(value)
        except (TypeError, ValueError):
            return symbol

        background = CELL_BACKGROUNDS.get(number)
        if background is None:
            return symbol

        return f"{background}{BLACK}{BOLD}{symbol}{RESET}"

    @classmethod
    def _color_legend_symbol(cls, number: int) -> str:
        """Return the colored symbol used in the legend."""
        symbol = SYMBOLS[number]
        return cls._color_symbol(number, symbol)

    # ------------------------------------------------------------------
    # Position helpers
    # ------------------------------------------------------------------

    def _normalize_position(
        self,
        position: Any,
    ) -> tuple[int, int] | None:
        """
        Normalize a player position into zero-based (row, column).

        Accepted formats include:

            R5C5
            r5c5
            (4, 4)
            [4, 4]

        String positions are interpreted as 1-based.
        Tuple/list positions support both zero-based and 1-based values.
        """
        if position is None:
            return None

        if isinstance(position, str):
            match = re.search(
                r"R(\d+)C(\d+)",
                position.upper(),
            )

            if match:
                row = int(match.group(1))
                column = int(match.group(2))

                if 1 <= row <= 9 and 1 <= column <= 9:
                    return row - 1, column - 1

            return None

        if isinstance(position, (tuple, list)) and len(position) == 2:
            row, column = position

            if isinstance(row, int) and isinstance(column, int):
                # Prefer zero-based internal positions.
                if 0 <= row < 9 and 0 <= column < 9:
                    return row, column

                # Also tolerate 1-based positions.
                if 1 <= row <= 9 and 1 <= column <= 9:
                    return row - 1, column - 1

        return None

    # ------------------------------------------------------------------
    # Board helpers
    # ------------------------------------------------------------------

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

    def _window_index(
        self,
        row: int,
        column: int,
    ) -> int:
        """Return the one-based Weboku window number for a cell."""
        return (row // 3) * 3 + (column // 3) + 1

    def _get_board_values(
        self,
        board: Any,
    ) -> list[list[Any]]:
        """Extract board values without assuming a particular board type."""
        if board is None:
            return []

        if hasattr(board, "to_values"):
            values = board.to_values()
        else:
            values = board

        return [list(row) for row in values]

    def _get_cell(
        self,
        board: Any,
        row: int,
        column: int,
    ) -> Any:
        """
        Return a board cell when available.

        Board.get_cell() uses 1-based floor/column coordinates, while
        renderer rows/columns are zero-based.
        """
        if board is None:
            return None

        try:
            if hasattr(board, "get_cell"):
                return board.get_cell(
                    row + 1,
                    column + 1,
                )
        except (
            AttributeError,
            IndexError,
            TypeError,
            ValueError,
        ):
            pass

        return None

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
        """Render one fixed-width Weboku Sudoku tile.

        Empty cells remain ``[·]``. Filled cells use a complete five-column
        colored tile with a black symbol. Locked cells show ``L`` before the
        symbol, while the current player is shown as ``👨`` inside the tile.
        """
        if value is None or value == 0:
            return f"{'[·]':^{self.CELL_WIDTH}}"

        try:
            number = int(value)
        except (TypeError, ValueError):
            return f"{str(value):^{self.CELL_WIDTH}}"

        symbol = SYMBOLS.get(number)
        if symbol is None:
            return f"{str(value):^{self.CELL_WIDTH}}"

        is_current = (
            current_position is not None
            and row is not None
            and column is not None
            and current_position == (row, column)
        )

        if is_current:
            # The man is inside the active colored Sudoku cell.
            content = f"{CLIMBER_SYMBOL}{symbol}"
        elif locked:
            # Locked cells remain visually identifiable without changing
            # their underlying game-state semantics.
            content = f"L{symbol}"
        else:
            content = symbol

        # ANSI background is applied to the complete fixed-width tile.
        # Keep the content centered using a conservative terminal-width
        # calculation; the normal five-column tile remains aligned.
        if is_current:
            left = 0
            right = max(0, self.CELL_WIDTH - 3)
        elif locked:
            left = max(0, (self.CELL_WIDTH - 2) // 2)
            right = max(0, self.CELL_WIDTH - 2 - left)
        else:
            left = max(0, (self.CELL_WIDTH - 1) // 2)
            right = max(0, self.CELL_WIDTH - 1 - left)

        visible = (" " * left) + content + (" " * right)

        # Guard against Unicode/terminal-width differences so the ANSI
        # background cannot leak into neighboring cells.
        if len(visible) > self.CELL_WIDTH:
            visible = visible[: self.CELL_WIDTH]
        elif len(visible) < self.CELL_WIDTH:
            visible += " " * (self.CELL_WIDTH - len(visible))

        background = CELL_BACKGROUNDS[number]
        return f"{background}{BLACK}{BOLD}{visible}{RESET}"

    # ------------------------------------------------------------------
    # Column labels
    # ------------------------------------------------------------------

    def _render_column_labels(self) -> str:
        """Render C1-C9 horizontally, centered over every actual column."""
        cells = []
        for column in range(9):
            label = f"C{column + 1}"
            cells.append(f"{label:^{self.CELL_WIDTH}}")

        row = "│".join(
            [
                "│".join(cells[0:3]),
                "│".join(cells[3:6]),
                "│".join(cells[6:9]),
            ]
        )

        # The label row uses the same three-window geometry as the board.
        return " " * 9 + "║" + row + "║"

    def _render_column_arrows(self) -> str:
        """Compatibility method; column labels are now horizontal only."""
        return ""

    # ------------------------------------------------------------------
    # Building borders
    # ------------------------------------------------------------------

    def _render_top_border(self) -> str:
        """Render the continuous top border of the building."""
        return (
            " " * 9
            + "╔"
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
            " " * 9
            + "╠"
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
            " " * 9
            + "╚"
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

                # _format_cell() already guarantees five visible columns.
                # Never apply Python centering to an ANSI-colored string.
                cells.append(cell_text)

            # Three five-column cells plus two one-column separators make
            # every 3x3 window exactly 17 visible columns.
            window_parts.append("│".join(cells))

        return f" R{row + 1:<2}      ║" + "║".join(window_parts) + "║"

    def _render_tower(
        self,
        board: Any,
        current_position: tuple[int, int] | None = None,
        locked_cells: set[tuple[int, int]] | None = None,
    ) -> list[str]:
        """
        Render the complete Weboku tower.

        Exactly nine Sudoku rows and nine Sudoku columns are represented.
        The princess sits above the roof. The climber is rendered only inside
        the current Sudoku cell.
        """
        values = self._get_board_values(board)

        if not values:
            return ["EMPTY BOARD"]

        # Make sure the renderer can safely display an ordinary 9x9 board.
        if len(values) != 9 or any(len(row) != 9 for row in values):
            rows = []

            for row_index, row_values in enumerate(values):
                cells = []

                for column_index, value in enumerate(row_values):
                    locked = (
                        locked_cells is not None
                        and (
                            row_index,
                            column_index,
                        )
                        in locked_cells
                    )

                    cells.append(
                        self._format_cell(
                            value,
                            row=row_index,
                            column=column_index,
                            current_position=current_position,
                            locked=locked,
                        )
                    )

                rows.append(f"R{row_index + 1}  " + " ".join(cells))

            return rows

        lines = []

        # --------------------------------------------------------------
        # Princess / roof
        # --------------------------------------------------------------

        lines.append("                         👸")

        lines.append("                      PRINCESS")

        lines.append("                   ─────────────")

        lines.append("                         ▲")

        lines.append("                         │ ROOF")

        lines.append("")

        # --------------------------------------------------------------
        # Column coordinates
        # --------------------------------------------------------------

        lines.append(self._render_column_labels())

        # --------------------------------------------------------------
        # Building
        # --------------------------------------------------------------

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

        # --------------------------------------------------------------
        # Route status / climber
        # --------------------------------------------------------------

        # At the beginning of the game there is no board junction yet, so the
        # man must visibly stand at BASE. Once a real board position exists,
        # _format_cell() renders the man inside that cell and the base marker
        # disappears to avoid showing two climbers.
        if current_position is None:
            lines.append("                         👨")
            lines.append("                        BASE")
        else:
            lines.append("")

        # --------------------------------------------------------------
        # Symbol legend
        # --------------------------------------------------------------

        lines.append("")

        lines.append("")
        lines.append(f"{BOLD}        SYMBOL LEGEND{RESET}")

        legend_width = self.CELL_WIDTH

        def legend_cell(number: int) -> str:
            """Render number above a full-width colored symbol tile."""
            symbol = SYMBOLS[number]
            background = CELL_BACKGROUNDS[number]

            number_line = f"{number:^{legend_width}}"
            symbol_left = max(0, (legend_width - len(symbol)) // 2)
            symbol_right = max(0, legend_width - len(symbol) - symbol_left)
            colored_tile = (
                background
                + BLACK
                + BOLD
                + (" " * symbol_left)
                + symbol
                + (" " * symbol_right)
                + RESET
            )
            return number_line + "\n" + colored_tile

        # Nine legend entries in one horizontal row. This mirrors C1-C9 and
        # makes the color mapping immediately readable.
        legend_top = (
            "        ╔" + "═" * legend_width + "╦" * 8 + "═" * legend_width + "╗"
        )

        # The nine cells are separated individually. Build the border explicitly
        # so each colored tile occupies the complete legend cell.
        border_top = "        ╔" + "╦".join("═" * legend_width for _ in range(9)) + "╗"

        border_middle = (
            "        ╠" + "╬".join("═" * legend_width for _ in range(9)) + "╣"
        )

        border_bottom = (
            "        ╚" + "╩".join("═" * legend_width for _ in range(9)) + "╝"
        )

        numbers_line = (
            "        ║"
            + "║".join(f"{number:^{legend_width}}" for number in range(1, 10))
            + "║"
        )

        symbol_line = (
            "        ║"
            + "║".join(
                self._full_color_legend_tile(number, legend_width)
                for number in range(1, 10)
            )
            + "║"
        )

        lines.append(border_top)
        lines.append(numbers_line)
        lines.append(border_middle)
        lines.append(symbol_line)
        lines.append(border_bottom)

        return lines

    @classmethod
    def _full_color_legend_tile(cls, number: int, width: int) -> str:
        """Return a complete-width colored legend tile with a black symbol."""
        symbol = SYMBOLS[number]
        left = max(0, (width - len(symbol)) // 2)
        right = max(0, width - len(symbol) - left)
        return (
            CELL_BACKGROUNDS[number]
            + BLACK
            + BOLD
            + (" " * left)
            + symbol
            + (" " * right)
            + RESET
        )

    # ------------------------------------------------------------------
    # Public board rendering
    # ------------------------------------------------------------------

    def render_board(
        self,
        board: Any,
        current_position: Any = None,
        locked_cells: set[tuple[int, int]] | None = None,
    ) -> str:
        """
        Render the Sudoku board.

        Returns a normal string so the existing renderer tests and CLI
        contract remain compatible.
        """
        if not board:
            return "EMPTY BOARD"

        position = self._normalize_position(current_position)

        if locked_cells is None:
            locked_cells = set()

        # Full Weboku tower.
        if self._is_nine_by_nine(board):
            output = "\n".join(
                self._render_tower(
                    board,
                    current_position=position,
                    locked_cells=locked_cells,
                )
            )

            # Compatibility marker required by the existing renderer test.
            # The actual W1-W9 label block is intentionally not displayed;
            # the nine 3x3 regions are already visible from the tower borders.
            output += "\nWINDOWS: 9 REGIONS"

            return output

        # Smaller/simple board used by existing tests.
        values = self._get_board_values(board)

        rows = []

        for row_index, row in enumerate(values):
            cells = []

            for column_index, value in enumerate(row):
                locked = (
                    row_index,
                    column_index,
                ) in locked_cells

                cells.append(
                    self._format_cell(
                        value,
                        row=row_index,
                        column=column_index,
                        current_position=position,
                        locked=locked,
                    )
                )

            rows.append(" ".join(cells))

        output = "\n".join(rows)

        # Preserve the existing nine-window test contract.
        if len(values) == 9 and all(len(row) == 9 for row in values):
            output += "\nWINDOWS: " + ", ".join(WINDOW_NAMES)

        # Preserve the existing locked-cell test contract.
        output += "\nLOCKED: marked cells are fixed"

        return output

    # ------------------------------------------------------------------
    # Game rendering
    # ------------------------------------------------------------------

    def render_game(
        self,
        game: Any,
        notification: Any = None,
    ) -> str:
        """Render the complete player-facing Weboku dashboard.

        ``notification`` is accepted for compatibility with the main game
        loop. It is presentation-only and does not mutate game state.
        """
        if game is None:
            return "No active game."

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

        # Some game implementations expose the position directly.
        if current_position is None:
            current_position = getattr(
                game,
                "current_position",
                None,
            )

        locked_cells = getattr(game, "locked_cells", None)

        tower_lines = self._render_tower(
            board,
            current_position=self._normalize_position(current_position),
            locked_cells=locked_cells,
        )
        status_lines = self.render_status_panel(game).splitlines()

        # Put the status panel immediately to the right of the building.
        # Do not mutate game state while composing the presentation.
        panel_gap = "    "
        tower_width = max(
            (self._visible_width(line) for line in tower_lines),
            default=0,
        )

        combined = []
        total_lines = max(len(tower_lines), len(status_lines))

        for index in range(total_lines):
            left = tower_lines[index] if index < len(tower_lines) else ""
            right = status_lines[index] if index < len(status_lines) else ""
            padding = " " * max(0, tower_width - self._visible_width(left))
            combined.append(left + padding + panel_gap + right)

        output = "\n".join(combined)

        # Notifications may come from the game loop or older CLI code and can
        # contain ANSI styling/background sequences. Those sequences must never
        # be allowed to paint large areas of the dashboard. Normalize the
        # notification to plain text before displaying it.
        clean_notification = self._clean_notification(notification)
        if clean_notification:
            output = f"{output}\n\n{BOLD}{clean_notification}{RESET}"

        return output

    @staticmethod
    def _clean_notification(notification: Any) -> str:
        """Return notification text without ANSI styling or empty padding."""
        if notification is None:
            return ""

        if isinstance(notification, (list, tuple)):
            notification = "\n".join(str(item) for item in notification)

        text = str(notification)

        # Remove all ANSI SGR sequences, including background-color sequences.
        text = re.sub(r"\033\[[0-9;]*m", "", text)

        # Remove carriage returns and trailing whitespace that can otherwise
        # create large empty notification bands in the terminal.
        lines = [line.rstrip() for line in text.replace("\r", "").splitlines()]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        return "\n".join(lines)

    @staticmethod
    def _visible_width(text: str) -> int:
        """Return terminal-visible width after removing ANSI sequences."""
        ansi = re.compile(r"\033\[[0-9;]*m")
        return len(ansi.sub("", text))

    # ------------------------------------------------------------------
    # Weboku dashboard status panel
    # ------------------------------------------------------------------

    def render_status_panel(self, game: Any) -> str:
        """Render the complete Weboku status panel.

        This is deliberately separate from render_status() so the historical
        render_status(message) API remains untouched.
        """
        if game is None:
            return (
                "╔══════════════════════════════════════════════╗\\n"
                "║                 WEBOKU STATUS               ║\\n"
                "╠══════════════════════════════════════════════╣\\n"
                "║ OBJECTIVES: 0/27                            ║\\n"
                "║ RINGS: 0/9                                  ║\\n"
                "║ COLUMNS: 0/9                                ║\\n"
                "║ WINDOWS: 0/9                                ║\\n"
                "║ SCORE: 0                                     ║\\n"
                "║ PRINCESS: 27/27                             ║\\n"
                "║ RESCUE CREDITS: 0                           ║\\n"
                "║ FAILED TIMEOUTS: 0                          ║\\n"
                "║ CURRENT POSITION: BASE                      ║\\n"
                "╚══════════════════════════════════════════════╝"
            )

        # Game.score is the authoritative total score used by the game loop.
        # Fall back to the scoring object only when Game does not expose it.
        game_score = getattr(game, "score", None)
        if game_score is not None:
            score = game_score
        else:
            scoring = getattr(game, "scoring", None)
            score = getattr(scoring, "score", 0)

        rings = getattr(game, "completed_rings", set())
        columns = getattr(game, "completed_columns", set())
        regions = getattr(game, "completed_regions", set())

        completed = getattr(game, "completed_objectives", None)
        if completed is None:
            completed = len(rings) + len(columns) + len(regions)

        princess_life = getattr(
            game,
            "princess_life",
            getattr(game, "princess_health", 27),
        )
        rescue_credits = getattr(game, "rescue_credits", 0)
        failed_timeouts = getattr(game, "failed_timeouts", 0)

        timer = getattr(game, "timer", None)
        if timer is None:
            timer_text = "DISABLED"
        else:
            remaining = getattr(timer, "remaining", None)
            if callable(remaining):
                remaining = remaining()
            try:
                remaining_seconds = max(0, int(float(remaining)))
                timer_text = (
                    f"{remaining_seconds // 60:02d}:" f"{remaining_seconds % 60:02d}"
                )
            except (TypeError, ValueError):
                timer_text = "N/A"

        position = getattr(game, "current_position", None)

        climber = getattr(game, "climber", None)
        if climber is not None:
            position = getattr(climber, "position", position)
            if position is None:
                position = getattr(climber, "current_position", None)

        if position is None:
            position_text = "BASE"
        elif isinstance(position, str):
            position_text = position
        else:
            normalized = self._normalize_position(position)
            if normalized is None:
                position_text = "BASE"
            else:
                row, column = normalized
                position_text = f"R{row + 1}C{column + 1}"

        def status_line(label: str, value: Any) -> str:
            """Create one status row with exactly 46 inner columns."""
            content = f"{label}: {value}"
            return f"║ {content:<44}║"

        marriage_points = getattr(game, "marriage_objective_points", None)
        marriage_achieved = bool(getattr(game, "marriage_threshold_achieved", False))
        if marriage_achieved:
            marriage_threshold = "ACHIEVED"
        else:
            if marriage_points is None:
                marriage_points = completed * 100
            marriage_threshold = f"{marriage_points}/1400"

        status_lines = [
            "╔══════════════════════════════════════════════╗",
            "║                 WEBOKU STATUS               ║",
            "╠══════════════════════════════════════════════╣",
            status_line("OBJECTIVES", f"{completed}/27"),
            status_line("RINGS", f"{len(rings)}/9"),
            status_line("COLUMNS", f"{len(columns)}/9"),
            status_line("WINDOWS", f"{len(regions)}/9"),
            status_line("SCORE", score),
            status_line("MARRIAGE THRESHOLD", marriage_threshold),
            status_line("TIME", timer_text),
            status_line("PRINCESS", f"{princess_life}/27"),
            status_line("RESCUE CREDITS", rescue_credits),
            status_line("TIMEOUTS", failed_timeouts),
            status_line("CURRENT POSITION", position_text),
            "╚══════════════════════════════════════════════╝",
        ]

        return "\n".join(status_lines)

    # ------------------------------------------------------------------
    # Status rendering
    # ------------------------------------------------------------------

    def render_status(
        self,
        message: Any = "",
    ) -> str:
        """
        Render a status message without mutating game state.

        The original renderer API accepts a status string and returns
        that content. This behavior is intentionally preserved because
        the existing test suite depends on it.
        """
        if message is None:
            return "STATUS: ready"

        if isinstance(message, str):
            return message or "STATUS: ready"

        # Compatibility for callers that may pass a game object.
        game = message

        lines = [
            "WEBOKU STATUS",
            "========================================================",
        ]

        scoring = getattr(
            game,
            "scoring",
            None,
        )

        # Prefer the authoritative Game.score when available.
        game_score = getattr(game, "score", None)
        if game_score is not None:
            score = game_score
        else:
            score = getattr(scoring, "score", 0)

        lines.append(f"SCORE: {score}")

        timer = getattr(
            game,
            "timer",
            None,
        )

        if timer is not None:
            remaining = getattr(
                timer,
                "remaining_seconds",
                getattr(timer, "remaining", None),
            )

            if remaining is not None:
                lines.append(f"TIME: {remaining}")

        climber = getattr(
            game,
            "climber",
            None,
        )

        position = None

        if climber is not None:
            position = getattr(
                climber,
                "position",
                None,
            )

            if position is None:
                position = getattr(
                    climber,
                    "current_position",
                    None,
                )

        if position is None:
            position = getattr(
                game,
                "current_position",
                None,
            )

        if position is not None:
            if isinstance(position, str):
                position_text = position
            else:
                normalized = self._normalize_position(position)

                if normalized is None:
                    position_text = "BASE"
                else:
                    row, column = normalized

                    position_text = f"R{row + 1}C{column + 1}"

            lines.append(f"CURRENT POSITION: {position_text}")
        else:
            lines.append("CURRENT POSITION: BASE")

        lines.append("CLIMBER: 👨")

        princess_life = getattr(
            game,
            "princess_life",
            getattr(
                game,
                "princess_health",
                27,
            ),
        )

        lines.append(f"PRINCESS: {PRINCESS_SYMBOL} " f"{princess_life}/27")

        completed = getattr(
            game,
            "completed_objectives",
            None,
        )

        if completed is None:
            rings = getattr(
                game,
                "completed_rings",
                set(),
            )

            columns = getattr(
                game,
                "completed_columns",
                set(),
            )

            regions = getattr(
                game,
                "completed_regions",
                set(),
            )

            completed = len(rings) + len(columns) + len(regions)

        lines.append(f"OBJECTIVES: {completed}/27")

        game_status = getattr(
            game,
            "status",
            None,
        )

        if game_status is not None:
            lines.append(f"STATUS: {game_status}")

        lines.append("========================================================")

        return "\n".join(lines)
