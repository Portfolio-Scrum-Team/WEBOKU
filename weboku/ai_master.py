class AIMaster:
    def __init__(self, game=None):
        self.game = game

    def explain_rules(self):
        return (
            "Weboku is a CLI-first Sudoku adventure. Solve the board, complete windows, "
            "unlock floors, and help the climber reach the princess. The game uses Sudoku logic "
            "for validity, while the climber moves automatically as objectives are completed."
        )

    def explain_status(self):
        if self.game is None:
            return "No active game session."

        status = getattr(self.game, "status", "unknown")
        score = getattr(self.game, "score", 0)
        position = getattr(self.game, "position", "BASE")
        objectives = getattr(self.game, "objectives", [])
        return (
            f"Current status: {status}. Score: {score}. Position: {position}. "
            f"Objectives: {', '.join(objectives) if objectives else 'none'}."
        )

    def provide_hint(self):
        if self.game is None:
            return "Check the board for the next empty cell that follows Sudoku row, column, and window rules."

        board = getattr(self.game, "board", None)
        if not board:
            return "Look for an empty cell in a row or column with the fewest valid options."

        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] == 0:
                    return f"Consider checking row {row + 1}, column {col + 1}; it is a good candidate for a valid next move."

        return "No open cells remain on the current board."

    def explain_move_result(self, result):
        if not isinstance(result, dict):
            return "The move result could not be explained."

        cell = result.get("cell", "unknown cell")
        value = result.get("value", "?")
        ok = result.get("ok", False)
        status = "accepted" if ok else "rejected"
        return f"Move {cell} with value {value} was {status}."

    def explain_objectives(self):
        if self.game is None:
            return "No active objectives are currently available."

        objectives = getattr(self.game, "objectives", [])
        if not objectives:
            return "No objectives are active at the moment."
        return "The current objectives are: " + ", ".join(objectives) + "."

    def explain_climbing_system(self):
        if self.game is None:
            return "The climbing system tracks progress automatically as objectives are completed."

        position = getattr(self.game, "position", "BASE")
        climber = getattr(self.game, "climber", "base")
        return (
            f"The climber is currently at {position} and moves automatically as objectives advance. "
            f"Current climber context: {climber}."
        )
