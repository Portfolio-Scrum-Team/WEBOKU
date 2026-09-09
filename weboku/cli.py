import re


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


class CLI:
    def __init__(self, game=None, player=None, renderer=None):
        self.game = game
        self.player = player
        self.renderer = renderer

    def show_welcome(self):
        return (
            "========================================================\n"
            "                    WEBOKU\n"
            "              SOLVE • UNLOCK • CLIMB\n"
            "                 • REACH • MARRY\n"
            "========================================================\n"
            "Solve the Sudoku.\n"
            "Complete rings, columns and windows.\n"
            "The climber moves automatically.\n"
            "Reach the princess and complete the marriage."
        )

    def show_help(self):
        return (
            "Commands:\n"
            "  help             - show commands\n"
            "  status           - show current game state\n"
            "  move R5C5 7      - submit a Sudoku move\n"
            "  move 5 5 7       - submit a row/column move\n"
            "  R5C5 7           - submit a Sudoku move\n"
            "  save file.txt    - save the game\n"
            "  load file.txt    - load the game\n"
            "  quit             - leave the game\n"
            "  exit             - leave the game\n"
            "\n"
            "Symbol Legend:\n"
            "  1 → ●    2 → ■    3 → ▲    4 → ╱    5 → ◆\n"
            "  6 → ★    7 → ✚    8 → ○    9 → ♥\n"
            "\n"
            "Enter numbers 1-9. The symbols are displayed in the game."
        )

    def prompt_move(self):
        return "Enter move:"

    def _parse_move(self, command):
        value = command.strip()

        if not value:
            return None, None, "Invalid command: empty input."

        # Format:
        # move 5 5 7
        # 5 5 7
        row_col_match = re.fullmatch(
            r"(?:move\s+)?([1-9])\s+([1-9])\s+([1-9])",
            value,
        )

        if row_col_match:
            row = int(row_col_match.group(1))
            col = int(row_col_match.group(2))
            number = int(row_col_match.group(3))
            return f"R{row}C{col}", number, None

        # Format:
        # move R5C5 7
        # R5C5 7
        cell_match = re.fullmatch(
            r"(?:move\s+)?([Rr][1-9][Cc][1-9])\s+([1-9])",
            value,
        )

        if cell_match:
            cell = cell_match.group(1).upper()
            number = int(cell_match.group(2))
            return cell, number, None

        # Keep explicit short format support.
        short_match = re.fullmatch(
            r"([Rr][1-9][Cc][1-9])\s+([1-9])",
            value,
        )

        if short_match:
            cell = short_match.group(1).upper()
            number = int(short_match.group(2))
            return cell, number, None

        # Detect invalid numeric values such as 10 or 0.
        if re.fullmatch(
            r"(?:move\s+)?[1-9]\s+[1-9]\s+[0-9]+",
            value,
        ):
            return (
                None,
                None,
                "Invalid move: value must be between 1 and 9.",
            )

        if re.fullmatch(
            r"(?:move\s+)?[Rr][1-9][Cc][1-9]\s+[0-9]+",
            value,
        ):
            return (
                None,
                None,
                "Invalid move: value must be between 1 and 9.",
            )

        return (
            None,
            None,
            "Invalid move: format should be "
            "'R5C5 7', 'move 5 5 7', or 'move R5C5 7'.",
        )

    def _handle_save_load(self, command):
        parts = command.split()

        if len(parts) != 2:
            return (
                "Invalid command: expected "
                "'save <file>' or 'load <file>'."
            )

        action, filepath = parts[0].lower(), parts[1]

        if self.game is None:
            return {
                "action": action,
                "path": filepath,
                "ok": True,
            }

        if action == "save":
            return self.game.save(filepath)

        if action == "load":
            return self.game.load(filepath)

        return f"Unknown command: {command}"

    def _format_real_game_status(self):
        """
        Format the real Weboku Game status while preserving compatibility
        with the older DummyGame/test interface.
        """

        if not hasattr(self.game, "get_status"):
            return "STATUS: ready"

        status = self.game.get_status()

        if not isinstance(status, dict):
            return str(status)

        lines = [
            "WEBOKU STATUS",
            "========================================================",
            f"Objectives : "
            f"{status.get('completed_objectives', 0)}/27",
            f"Rings      : "
            f"{status.get('completed_rings', 0)}/9",
            f"Columns    : "
            f"{status.get('completed_columns', 0)}/9",
            f"Windows    : "
            f"{status.get('completed_regions', 0)}/9",
            f"Score      : "
            f"{status.get('score', 0)}",
            f"Princess   : "
            f"{status.get('princess_life', 27)}/27",
            f"Rescue     : "
            f"{status.get('rescue_credits', 0)}",
            f"Timeouts   : "
            f"{status.get('failed_timeouts', 0)}",
        ]

        position = status.get("current_position")

        if position is not None:
            lines.append(f"Position   : {position}")

        game_status = status.get("status")

        if game_status is not None:
            lines.append(f"Status     : {game_status}")

        lines.extend(
            [
                "========================================================",
                "",
                "Symbol Legend:",
                "  1 → ●    2 → ■    3 → ▲    4 → ╱    5 → ◆",
                "  6 → ★    7 → ✚    8 → ○    9 → ♥",
            ]
        )

        return "\n".join(lines)

    def handle_command(self, command):
        if command is None:
            return "Invalid command: empty input."

        text = command.strip()

        if not text:
            return "Invalid command: empty input."

        lowered = text.lower()

        # HELP
        if lowered == "help":
            return self.show_help()

        # STATUS
        if lowered == "status":
            if self.game is None:
                return "STATUS: ready"

            # Existing tests use DummyGame.status().
            if hasattr(self.game, "status"):
                return self.game.status()

            # Real Weboku Game uses get_status().
            if hasattr(self.game, "get_status"):
                return self._format_real_game_status()

            return "STATUS: ready"

        # QUIT / EXIT
        if lowered in {"quit", "exit"}:
            return "Goodbye!"

        # SAVE / LOAD
        if lowered.startswith("save ") or lowered.startswith("load "):
            return self._handle_save_load(text)

        # MOVE
        cell, value, error = self._parse_move(text)

        if error:
            return error

        if cell is None:
            return (
                "Invalid move: format should be "
                "'R5C5 7', 'move 5 5 7', or 'move R5C5 7'."
            )

        # Preserve the original CLI/test contract when the game exposes
        # move(cell, value).
        if hasattr(self.game, "move"):
            return self.game.move(cell, value)

        # The real Weboku Game uses process_move(row, column, symbol).
        if hasattr(self.game, "process_move"):
            row = int(cell[1])
            col = int(cell[3])

            symbol = SYMBOLS[value]

            return self.game.process_move(row, col, symbol)

        # CLI can still be tested without a game object.
        if self.game is None:
            return {
                "cell": cell,
                "value": value,
                "ok": True,
            }

        return "Game move handling is not available."

    def run(self):
        return self.show_welcome()