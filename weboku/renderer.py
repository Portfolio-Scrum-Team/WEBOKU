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


class Renderer:
    def _format_cell(self, value, row_index, col_index, locked_cells):
        if value in (0, None, ""):
            symbol = "·"
        else:
            symbol = SYMBOLS.get(int(value), str(value))
        if (row_index, col_index) in locked_cells:
            return f"[{symbol}L]"
        return f"[{symbol}]"

    def render_board(self, board, locked_cells=None):
        locked_cells = locked_cells or set()
        if not board:
            return "EMPTY BOARD"

        rows = []
        for row_index, row in enumerate(board):
            cells = []
            for col_index, value in enumerate(row):
                cells.append(self._format_cell(value, row_index, col_index, locked_cells))
            rows.append(" ".join(cells))

        output = "\n".join(rows)
        if len(board) == 9 and all(len(row) == 9 for row in board):
            window_labels = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9"]
            output = output + "\nWINDOWS: " + ", ".join(window_labels)
        output += "\nLOCKED: marked cells are fixed"
        return output

    def render_status(self, message=""):
        return message or "STATUS: ready"
