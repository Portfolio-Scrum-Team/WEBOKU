import re


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
            "  save file.txt    - save the game\n"
            "  load file.txt    - load the game\n"
            "  quit             - leave the game\n"
            "  exit             - leave the game"
        )

    def prompt_move(self):
        return "Enter move:"

    def _parse_move(self, command):
        value = command.strip()
        if not value:
            return None, None, "Invalid command: empty input."

        row_col_match = re.fullmatch(r"(?:move\s+)?([1-9])\s+([1-9])\s+([1-9])", value)
        if row_col_match:
            row = int(row_col_match.group(1))
            col = int(row_col_match.group(2))
            number = int(row_col_match.group(3))
            return f"R{row}C{col}", number, None

        cell_match = re.fullmatch(r"(?:move\s+)?([Rr][1-9][Cc][1-9])\s+([1-9])", value)
        if cell_match:
            cell = cell_match.group(1).upper()
            number = int(cell_match.group(2))
            return cell, number, None

        short_match = re.fullmatch(r"([Rr][1-9][Cc][1-9])\s+([1-9])", value)
        if short_match:
            cell = short_match.group(1).upper()
            number = int(short_match.group(2))
            return cell, number, None

        if re.fullmatch(r"(?:move\s+)?[1-9]\s+[1-9]\s+[0-9]+", value):
            return None, None, "Invalid move: value must be between 1 and 9."

        if re.fullmatch(r"(?:move\s+)?[Rr][1-9][Cc][1-9]\s+[0-9]+", value):
            return None, None, "Invalid move: value must be between 1 and 9."

        return None, None, "Invalid move: format should be 'R5C5 7', 'move 5 5 7', or 'move R5C5 7'."

    def _handle_save_load(self, command):
        parts = command.split()
        if len(parts) != 2:
            return "Invalid command: expected 'save <file>' or 'load <file>'."

        action, filepath = parts[0].lower(), parts[1]
        if self.game is None:
            return {"action": action, "path": filepath, "ok": True}

        if action == "save":
            return self.game.save(filepath)
        if action == "load":
            return self.game.load(filepath)
        return f"Unknown command: {command}"

    def handle_command(self, command):
        if command is None:
            return "Invalid command: empty input."

        text = command.strip()
        if not text:
            return "Invalid command: empty input."

        lowered = text.lower()
        if lowered in {"help"}:
            return self.show_help()
        if lowered in {"status"}:
            if self.game is None:
                return "STATUS: ready"
            return self.game.status()
        if lowered in {"quit", "exit"}:
            return "Goodbye!"

        if lowered.startswith("save ") or lowered.startswith("load "):
            return self._handle_save_load(text)

        cell, value, error = self._parse_move(text)
        if error:
            return error
        if cell is None:
            return "Invalid move: format should be 'R5C5 7', 'move 5 5 7', or 'move R5C5 7'."

        if self.game is None:
            return {"cell": cell, "value": value, "ok": True}

        return self.game.move(cell, value)

    def run(self):
        return self.show_welcome()
