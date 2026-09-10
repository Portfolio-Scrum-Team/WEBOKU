"""AI Master advisory assistant for Weboku.

AI Master provides explanations, status summaries, Sudoku guidance,
and optional OpenRouter-powered advice.

IMPORTANT:
AI Master is advisory only. It must never modify Weboku game state.
"""

from __future__ import annotations

from typing import Any

from weboku.openrouter_engine import OpenRouterEngine, OpenRouterError


class AIMaster:
    """Advisory brain for Weboku rules, status, and player guidance."""

    def __init__(
        self,
        engine: OpenRouterEngine | None = None,
    ):
        """Create an AI Master.

        Args:
            engine: Optional OpenRouter engine.

        The engine is injected so tests and the game can control the
        AI backend without AI Master directly managing game state.
        """
        self.engine = engine or OpenRouterEngine()

    def explain_rules(self) -> str:
        """Explain the core Weboku rules."""
        return (
            "Weboku is a Sudoku climbing adventure.\n\n"
            "Solve the Sudoku to complete:\n"
            "- 9 rings\n"
            "- 9 columns\n"
            "- 9 windows\n\n"
            "Completed objectives unlock parts of the building.\n"
            "The climber moves automatically.\n"
            "Reach the princess on the roof to win.\n\n"
            "Flow:\n"
            "SOLVE → UNLOCK → CLIMB → REACH → MARRY"
        )

    def explain_status(self, game: Any) -> str:
        """Return a read-only summary of the current game state."""
        if game is None:
            return "Status unavailable."

        completed_rings = set(getattr(game, "completed_rings", set()) or [])
        completed_columns = set(getattr(game, "completed_columns", set()) or [])
        completed_regions = set(getattr(game, "completed_regions", set()) or [])

        objectives = (
            len(completed_rings) + len(completed_columns) + len(completed_regions)
        )

        score = getattr(game, "score", 0)
        princess_life = getattr(game, "princess_life", 0)
        status = getattr(game, "game_status", "UNKNOWN")
        position = getattr(game, "current_position", None)

        current_text = self._format_position(position)

        return (
            f"Objectives: {objectives}/27\n"
            f"Rings: {len(completed_rings)}/9\n"
            f"Columns: {len(completed_columns)}/9\n"
            f"Windows: {len(completed_regions)}/9\n"
            f"Score: {score}\n"
            f"Princess life: {princess_life}/27\n"
            f"Current position: {current_text}\n"
            f"Status: {status}"
        )

    def suggest_candidates(
        self,
        game: Any,
        ring: int,
        column: int,
    ) -> list[int]:
        """Return Sudoku candidates using the existing game engine.

        AI Master does not calculate or modify the board itself.
        It asks the authoritative Sudoku/game implementation for
        candidate values.
        """
        if game is None:
            return []

        for sudoku_attribute in ("sudoku", "sudoku_engine"):
            sudoku = getattr(game, sudoku_attribute, None)

            if sudoku is None:
                continue

            for method_name in ("get_candidates", "candidates"):
                method = getattr(sudoku, method_name, None)

                if callable(method):
                    return list(method(ring, column))

        for method_name in ("get_candidates", "candidates"):
            method = getattr(game, method_name, None)

            if callable(method):
                return list(method(ring, column))

        return []

    def get_hint(
        self,
        game: Any,
        ring: int,
        column: int,
    ) -> str:
        """Give a simple deterministic Sudoku hint."""
        options = self.suggest_candidates(game, ring, column)

        if not options:
            return "No hint available right now."

        return (
            f"AI MASTER — R{ring}C{column} candidates: "
            f"{', '.join(str(value) for value in options)}\n"
            "AI is advisory — you choose the move."
        )

    def ask(self, prompt: str) -> str:
        """Ask the configured AI backend for advisory guidance.

        AI Master does not receive or retain game state here.
        The caller decides what information is appropriate to include
        in the prompt.
        """
        if not prompt or not prompt.strip():
            return "AI Master needs a question."

        try:
            return self.engine.explain(prompt)
        except (OpenRouterError, RuntimeError, OSError) as exc:
            return f"AI Master is unavailable right now: {exc}"

    def explain_move_result(self, result: Any) -> str:
        """Explain a move result without changing game state."""
        if result is None:
            return "Move result unavailable."

        if not getattr(result, "success", False):
            floor = getattr(result, "floor", "?")
            column = getattr(result, "column", "?")

            return (
                "Move rejected.\n\n"
                f"The value cannot be placed at "
                f"R{floor}C{column} according to the Sudoku rules."
            )

        floor = getattr(result, "floor", "?")
        column = getattr(result, "column", "?")
        value = getattr(result, "value", "?")
        symbol = getattr(result, "symbol", str(value))

        new_rings = list(getattr(result, "new_rings", []) or [])
        new_columns = list(getattr(result, "new_columns", []) or [])
        new_regions = list(getattr(result, "new_regions", []) or [])

        current_position = getattr(
            result,
            "current_position",
            None,
        )

        lines = [
            "Move accepted.",
            "",
            f"R{floor}C{column} = {symbol} ({value})",
            "",
            "You completed:",
        ]

        if new_rings:
            for ring in new_rings:
                lines.append(f"- Ring {ring}")

        if new_columns:
            for column_id in new_columns:
                lines.append(f"- Column {column_id}")

        if new_regions:
            for region in new_regions:
                lines.append(f"- Window {region}")

        if not new_rings and not new_columns and not new_regions:
            lines = lines[:-1]
            lines.append("You completed no new objectives.")

        if isinstance(current_position, (tuple, list)):
            if len(current_position) == 2:
                row, col = current_position

                lines.extend(
                    [
                        "",
                        f"The climber moved to R{row}C{col}.",
                    ]
                )

        return "\n".join(lines)

    @staticmethod
    def _format_position(position: Any) -> str:
        """Format a game position for player-facing output."""
        if position is None:
            return "BASE"

        if isinstance(position, str):
            pos = position.upper()

            if pos == "ROOF":
                return "ROOF — PRINCESS REACHED"

            if pos == "BASE":
                return "BASE"

            return pos

        if isinstance(position, (tuple, list)):
            if len(position) == 2:
                row, column = position
                return f"R{row}C{column}"

        return str(position)
