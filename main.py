"""
Weboku application entry point.

RIC-05: Main Game Loop

The main loop coordinates the application while the Game class
remains the authoritative owner of game rules and state.
"""

from __future__ import annotations

import re
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
        self._last_rendered_dashboard = ""
        self._timer_screen_row = None
        self._timer_value_column = None

    # ------------------------------------------------------------------
    # START
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the game loop."""
        self.game.start()
        self.running = True

        self.output_fn("Welcome to Weboku!")
        self.output_fn("Solve → Unlock → Climb → Reach → Marry")

        # Show the initial game board immediately.
        self._show_game_board()

        self.run()

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the command loop until the game ends.

        With the real terminal input function, stdin is polled once per
        second so the Beginner countdown remains visible and TIMEOUT is
        processed automatically at 00:00. Injected input functions used by
        tests retain normal blocking behavior.
        """
        while self.running and self._game_can_continue():
            command = self._read_command_with_live_timer()

            if command is None:
                self.stop()
                break

            self._check_timer_timeout()

            if not self.running or not self._game_can_continue():
                break

            result = self.handle_command(command)

            # Some CLI implementations return a lightweight value while
            # storing the authoritative MoveResult on Game.last_move_result.
            # Recover that result for move commands so the player always sees
            # the move notification and the updated cell.
            if self._looks_like_move_command(command):
                last_move = getattr(self.game, "last_move_result", None)
                if last_move is not None and hasattr(last_move, "message"):
                    result = last_move

            command_name = ""

            if command:
                command_name = command.strip().split()[0].lower()

            # Help and status display themselves.
            if (
                result is not None
                and result is not True
                and command_name
                not in {
                    "help",
                    "status",
                }
            ):
                self._display_result(result)

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape sequences for terminal column calculations."""
        return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)

    def _update_live_timer_display(self) -> None:
        """Update only the existing TIME field; never clear or redraw the screen."""
        if self.output_fn is not print:
            return

        row = self._timer_screen_row
        column = self._timer_value_column
        if row is None or column is None:
            return

        timer = getattr(self.game, "timer", None)
        if timer is None:
            return

        remaining = getattr(timer, "remaining", None)
        if callable(remaining):
            remaining = remaining()
        try:
            seconds = max(0, int(float(remaining)))
        except (TypeError, ValueError):
            return

        timer_text = f"{seconds // 60:02d}:{seconds % 60:02d}"

        # Save the input cursor, update ONLY the five-character TIME value,
        # then return the cursor to exactly where the player was typing.
        self.output_fn(
            f"\033[s\033[{row};{column}H\033[0m{timer_text} \033[u",
            end="",
            flush=True,
        )

    def _read_command_with_live_timer(self) -> str | None:
        """Read input without ever clearing the screen while the user types."""
        if self.input_fn is not input:
            try:
                return self.input_fn("weboku> ")
            except (EOFError, KeyboardInterrupt):
                return None

        timer = getattr(self.game, "timer", None)
        if timer is None:
            try:
                return self.input_fn("weboku> ")
            except (EOFError, KeyboardInterrupt):
                return None

        import select
        import termios
        import tty

        stdin_fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(stdin_fd)
        buffer = ""

        try:
            tty.setcbreak(stdin_fd)

            # The board has already been printed by start()/the previous
            # command. Establish the TIME coordinates once, then leave the
            # prompt and everything the user types completely untouched.
            self._set_timer_coordinates()
            self.output_fn("weboku> ", end="", flush=True)

            while self.running and self._game_can_continue():
                readable, _, _ = select.select([sys.stdin], [], [], 1.0)

                if readable:
                    char = sys.stdin.read(1)

                    if char in {"\r", "\n"}:
                        self.output_fn("")
                        return buffer

                    if char in {"\x03", "\x04"}:
                        self.output_fn("")
                        return None

                    if char in {"\x7f", "\x08"}:
                        if buffer:
                            buffer = buffer[:-1]
                            self.output_fn("\b \b", end="", flush=True)
                        continue

                    if char == "\x1b":
                        continue

                    buffer += char
                    self.output_fn(char, end="", flush=True)
                    continue

                # One second elapsed. Do not redraw the dashboard and do not
                # touch the prompt. Only replace the TIME field in place.
                timeout_handled = self._check_timer_timeout()

                if not self.running or not self._game_can_continue():
                    return ""

                if not timeout_handled:
                    self._update_live_timer_display()

            return ""

        except (OSError, ValueError, termios.error):
            try:
                return self.input_fn("weboku> ")
            except (EOFError, KeyboardInterrupt):
                return None
        finally:
            try:
                termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
            except (OSError, ValueError, termios.error):
                pass

    def _set_timer_coordinates(self) -> None:
        """Find the TIME field in the currently rendered dashboard."""
        dashboard = self._last_rendered_dashboard
        if not dashboard:
            return

        for index, line in enumerate(dashboard.splitlines()):
            plain = self._strip_ansi(line)
            label_index = plain.find("TIME:")
            if label_index >= 0:
                self._timer_screen_row = index + 1
                self._timer_value_column = label_index + len("TIME: ") + 1
                return

        self._timer_screen_row = None
        self._timer_value_column = None

    def _looks_like_move_command(self, command: str) -> bool:
        """Return True when a command is in Weboku's Sudoku move format."""
        if not command:
            return False

        text = command.strip()

        if text.lower().startswith("move "):
            return True

        return bool(re.match(r"^r\d+c\d+\s*\d?$", text, re.IGNORECASE))

    def _check_timer_timeout(self) -> bool:
        """Process an expired timer through Game without changing rules here."""
        timer = getattr(self.game, "timer", None)
        handler = getattr(self.game, "handle_timeout", None)
        if timer is None or not callable(handler):
            return

        remaining = None
        for name in (
            "remaining_seconds",
            "remaining",
            "seconds_remaining",
            "time_remaining",
        ):
            value = getattr(timer, name, None)
            if callable(value):
                try:
                    value = value()
                except TypeError:
                    value = None
            if value is not None:
                remaining = value
                break

        try:
            expired = remaining is not None and float(remaining) <= 0
        except (TypeError, ValueError):
            expired = False

        if not expired:
            return False

        handled = handler()
        if handled:
            events = (
                self.game.get_recent_events()
                if hasattr(self.game, "get_recent_events")
                else []
            )
            message = events[-1] if events else "Timer expired."
            self._show_game_board(
                notification=[
                    "⏱ TIMEOUT",
                    str(message),
                    f"Princess life: {getattr(self.game, 'princess_life', 27)}/27",
                    f"Timeouts: {getattr(self.game, 'failed_timeouts', 0)}",
                ]
            )

        return bool(handled)

    # ------------------------------------------------------------------
    # COMMAND HANDLING
    # ------------------------------------------------------------------

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
            if hasattr(
                self.game,
                "start",
            ):
                result = self.game.start()

                # Starting again should show the current board.
                self._show_game_board()

                return result

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
        # AI MASTER
        # ------------------------------------------------------------

        # AI commands belong to the CLI layer, where the current
        # AIMaster instance and its OpenRouter adapter are connected.
        # The GameLoop only routes the command and never changes game state.
        if command_name == "ai":
            if hasattr(self.game, "cli"):
                return self.game.cli.handle_command(command)

            return self._show_ai_advice()

        # ------------------------------------------------------------
        # TIMEOUT / TIMER TEST
        # ------------------------------------------------------------

        if command_name in {"timeout", "timeup"}:
            return self._process_timeout()

        # ------------------------------------------------------------
        # DETAILED CLI COMMANDS
        # ------------------------------------------------------------

        if hasattr(
            self.game,
            "cli",
        ):
            return self.game.cli.handle_command(command)

        # ------------------------------------------------------------
        # FALLBACK MOVE
        # ------------------------------------------------------------

        if command_name == "move" and hasattr(
            self.game,
            "move",
        ):
            return self.game.move(*command.split()[1:])

        self.output_fn(
            "Command not handled by the core loop yet. "
            "Use the CLI layer for detailed commands."
        )

        return None

    def _show_ai_advice(self) -> str:
        """Display read-only advice from the optional AI Master."""
        ai = getattr(self.game, "ai_master", None)
        if ai is None:
            try:
                from weboku.ai_master import AIMaster

                ai = AIMaster()
                self.game.ai_master = ai
            except (ImportError, ModuleNotFoundError):
                result = "AI Master is not installed in this build."
                self.output_fn(result)
                return result

        state = getattr(self.game, "state", self.game)
        if hasattr(ai, "strategy_advice"):
            result = ai.strategy_advice(state)
        elif hasattr(ai, "summarize"):
            result = ai.summarize(state)
        else:
            result = "AI Master is available, but no advice method is exposed."

        self.output_fn(str(result))
        return str(result)

    def _process_timeout(self) -> Any:
        """Explicitly process a timeout through the authoritative Game API."""
        handler = getattr(self.game, "handle_timeout", None)
        if not callable(handler):
            result = "Timer timeout handling is not available."
            self.output_fn(result)
            return result

        handled = handler()
        notification = [
            "⏱ TIMEOUT",
            (
                str(self.game.get_recent_events()[-1])
                if hasattr(self.game, "get_recent_events")
                and self.game.get_recent_events()
                else "TIMEOUT! Timer window expired."
            ),
            f"Princess life: {getattr(self.game, 'princess_life', 27)}/27",
            f"Timeouts: {getattr(self.game, 'failed_timeouts', 0)}",
        ]
        self._show_game_board(notification=notification)
        return handled

    # ------------------------------------------------------------------
    # STOP
    # ------------------------------------------------------------------

    def stop(self) -> None:
        """Stop the main application loop."""
        self.running = False

    # ------------------------------------------------------------------
    # GAME STATE
    # ------------------------------------------------------------------

    def _game_can_continue(self) -> bool:
        """
        Return True while the game can continue.

        The Game object remains authoritative. This method only reads
        its public state and never changes game state.
        """
        status = getattr(
            self.game,
            "game_status",
            None,
        )

        if callable(status):
            status = status()

        if status is None:
            state = getattr(
                self.game,
                "state",
                None,
            )

            if state is not None:
                status = getattr(
                    state,
                    "game_status",
                    None,
                )

        return status not in {
            "VICTORY",
            "GAME_OVER",
        }

    # ------------------------------------------------------------------
    # BOARD DISPLAY
    # ------------------------------------------------------------------

    def _move_notification_lines(self, result: Any) -> list[str]:
        """Build compact notification data from an authoritative MoveResult."""
        lines = []
        message = getattr(result, "message", None)
        if message:
            lines.append(str(message))

        floor = getattr(result, "floor", None)
        column = getattr(result, "column", None)
        symbol = getattr(result, "symbol", None)
        if floor is not None and column is not None and symbol:
            lines.append("✓ MOVE ACCEPTED")
            lines.append(f"Cell updated: R{floor}C{column} = {symbol}")

        score_gained = getattr(result, "score_gained", 0)
        score = getattr(self.game, "score", 0)
        lines.append(f"Score gained: +{score_gained}")
        lines.append(f"Total score: {score}")
        return lines

    def _show_game_board(self, notification: Any = None) -> str | None:
        """
        Render and display the current Weboku tower.

        This method is presentation-only. It never modifies the game.
        """
        cli = getattr(
            self.game,
            "cli",
            None,
        )

        renderer = getattr(
            cli,
            "renderer",
            None,
        )

        if renderer is None:
            return None

        if not hasattr(
            renderer,
            "render_game",
        ):
            return None

        # If a move result exists but the caller did not explicitly pass a
        # notification, recover the authoritative result from Game.
        if notification is None:
            last_move = getattr(self.game, "last_move_result", None)
            if last_move is not None and getattr(last_move, "success", False):
                notification = self._move_notification_lines(last_move)

        # Redraw in place instead of appending another full diagram.
        # Clear the real terminal before printing the refreshed dashboard,
        # which prevents the CLI from flooding with old diagrams.
        if self.output_fn is print:
            self.output_fn("\033[2J\033[H", end="")

        result = renderer.render_game(self.game, notification=notification)
        self._last_rendered_dashboard = result

        # The dashboard is printed once. Live timer updates later change only
        # this field and restore the user's typing cursor.
        self._last_rendered_dashboard = result
        self._set_timer_coordinates()

        self.output_fn(result)

        return result

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    def _show_status(self) -> str:
        """
        Display the complete Weboku dashboard.

        The tower is always rendered from the current authoritative
        game state, followed by the status panel.
        """
        cli = getattr(
            self.game,
            "cli",
            None,
        )

        renderer = getattr(
            cli,
            "renderer",
            None,
        )

        # ------------------------------------------------------------
        # Rich renderer
        # ------------------------------------------------------------

        if renderer is not None and hasattr(
            renderer,
            "render_game",
        ):
            result = renderer.render_game(self.game)

            self.output_fn(result)

            return result

        # ------------------------------------------------------------
        # Compatibility fallback: old game.status()
        # ------------------------------------------------------------

        if hasattr(
            self.game,
            "status",
        ):
            result = self.game.status()

            self.output_fn(result)

            return result

        # ------------------------------------------------------------
        # Compatibility fallback: real Game.get_status()
        # ------------------------------------------------------------

        if hasattr(
            self.game,
            "get_status",
        ):
            status = self.game.get_status()

            if isinstance(
                status,
                dict,
            ):
                lines = [
                    "WEBOKU STATUS",
                    "========================================================",
                    (f"Objectives : " f"{status.get('completed_objectives', 0)}/27"),
                    (f"Rings      : " f"{status.get('completed_rings', 0)}/9"),
                    (f"Columns    : " f"{status.get('completed_columns', 0)}/9"),
                    (f"Windows    : " f"{status.get('completed_regions', 0)}/9"),
                    (f"Score      : " f"{status.get('score', 0)}"),
                    (f"Princess   : " f"{status.get('princess_life', 27)}/27"),
                    (f"Rescue     : " f"{status.get('rescue_credits', 0)}"),
                    (f"Timeouts   : " f"{status.get('failed_timeouts', 0)}"),
                ]

                position = status.get("current_position")

                if position is not None:
                    lines.append(f"Position   : {position}")

                game_status = status.get("status")

                if game_status is not None:
                    lines.append(f"Status     : {game_status}")

                result = "\n".join(lines)

                self.output_fn(result)

                return result

            result = str(status)

            self.output_fn(result)

            return result

        result = "Game status is not available yet."

        self.output_fn(result)

        return result

    # ------------------------------------------------------------------
    # STATUS TEXT
    # ------------------------------------------------------------------

    def _build_status_text(self) -> str:
        """Build the status panel from authoritative game state."""
        state = getattr(
            self.game,
            "state",
            None,
        )

        # ------------------------------------------------------------
        # Objective counts
        # ------------------------------------------------------------

        completed_rings = getattr(
            self.game,
            "completed_rings",
            None,
        )

        if completed_rings is None:
            completed_rings = getattr(
                state,
                "completed_rings",
                set(),
            )

        completed_columns = getattr(
            self.game,
            "completed_columns",
            None,
        )

        if completed_columns is None:
            completed_columns = getattr(
                state,
                "completed_columns",
                set(),
            )

        completed_regions = getattr(
            self.game,
            "completed_regions",
            None,
        )

        if completed_regions is None:
            completed_regions = getattr(
                state,
                "completed_regions",
                set(),
            )

        completed_rings = completed_rings if completed_rings is not None else set()

        completed_columns = (
            completed_columns if completed_columns is not None else set()
        )

        completed_regions = (
            completed_regions if completed_regions is not None else set()
        )

        objective_count = (
            len(completed_rings) + len(completed_columns) + len(completed_regions)
        )

        # ------------------------------------------------------------
        # Score
        # ------------------------------------------------------------

        score = getattr(
            self.game,
            "score",
            None,
        )

        if score is None:
            scoring = getattr(
                self.game,
                "scoring",
                None,
            )

            score = getattr(
                scoring,
                "score",
                getattr(
                    state,
                    "score",
                    0,
                ),
            )

        # ------------------------------------------------------------
        # Princess
        # ------------------------------------------------------------

        princess_life = getattr(
            self.game,
            "princess_life",
            None,
        )

        if princess_life is None:
            princess_life = getattr(
                state,
                "princess_life",
                27,
            )

        # ------------------------------------------------------------
        # Rescue credits
        # ------------------------------------------------------------

        rescue_credits = getattr(
            self.game,
            "rescue_credits",
            None,
        )

        if rescue_credits is None:
            rescue_credits = getattr(
                state,
                "rescue_credits",
                0,
            )

        # ------------------------------------------------------------
        # Failed timeouts
        # ------------------------------------------------------------

        failed_timeouts = getattr(
            self.game,
            "failed_timeouts",
            None,
        )

        if failed_timeouts is None:
            failed_timeouts = getattr(
                state,
                "failed_timeouts",
                0,
            )

        # ------------------------------------------------------------
        # Current climber position
        # ------------------------------------------------------------

        position = getattr(
            self.game,
            "current_position",
            None,
        )

        if position is None:
            position = getattr(
                state,
                "current_position",
                None,
            )

        position_text = self._format_position(position)

        # ------------------------------------------------------------
        # Game status
        # ------------------------------------------------------------

        game_status = getattr(
            self.game,
            "game_status",
            None,
        )

        if callable(game_status):
            game_status = game_status()

        if game_status is None:
            game_status = getattr(
                state,
                "game_status",
                "PLAYING",
            )

        # ------------------------------------------------------------
        # Timer
        # ------------------------------------------------------------

        timer_text = self._get_timer_text()

        # ------------------------------------------------------------
        # Panel
        # ------------------------------------------------------------

        width = 44

        def panel_line(
            text: str,
        ) -> str:
            return "║ " + text[:width].ljust(width) + " ║"

        lines = [
            "",
            "╔══════════════════════════════════════════════╗",
            "║                 WEBOKU STATUS               ║",
            "╠══════════════════════════════════════════════╣",
            panel_line(f"OBJECTIVES: {objective_count}/27"),
            panel_line(f"RINGS: {len(completed_rings)}/9"),
            panel_line(f"COLUMNS: {len(completed_columns)}/9"),
            panel_line(f"WINDOWS: {len(completed_regions)}/9"),
            panel_line(f"SCORE: {score}"),
            panel_line(f"TIME: {timer_text}"),
            panel_line(f"PRINCESS: {princess_life}/27"),
            panel_line(f"RESCUE CREDITS: {rescue_credits}"),
            panel_line(f"FAILED TIMEOUTS: {failed_timeouts}"),
            panel_line(f"CURRENT POSITION: {position_text}"),
            panel_line(f"STATUS: {game_status}"),
            "╚══════════════════════════════════════════════╝",
        ]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # TIMER
    # ------------------------------------------------------------------

    def _get_timer_text(self) -> str:
        """Return the current timer value without changing it."""
        timer = getattr(
            self.game,
            "timer",
            None,
        )

        if timer is None:
            return "N/A"

        # Common timer attribute names.
        for attribute_name in (
            "remaining_seconds",
            "remaining",
            "seconds_remaining",
            "time_remaining",
        ):
            value = getattr(
                timer,
                attribute_name,
                None,
            )

            if value is not None:
                return self._format_timer_value(value)

        # Some timer implementations expose a method.
        for method_name in (
            "remaining_seconds",
            "time_remaining",
        ):
            method = getattr(
                timer,
                method_name,
                None,
            )

            if callable(method):
                try:
                    return self._format_timer_value(method())
                except TypeError:
                    pass

        return "N/A"

    @staticmethod
    def _format_timer_value(value: Any) -> str:
        """Format timer seconds as MM:SS while preserving formatted text."""
        if isinstance(value, str):
            text = value.strip()
            if ":" in text:
                return text
            try:
                value = float(text)
            except ValueError:
                return text

        try:
            total_seconds = max(0, int(float(value)))
        except (TypeError, ValueError):
            return str(value)

        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    # ------------------------------------------------------------------
    # POSITION
    # ------------------------------------------------------------------

    @staticmethod
    def _format_position(
        position: Any,
    ) -> str:
        """Format the authoritative climber position."""
        if position is None:
            return "BASE"

        if isinstance(
            position,
            str,
        ):
            return position

        if (
            isinstance(
                position,
                (tuple, list),
            )
            and len(position) == 2
        ):
            row, column = position

            if isinstance(row, int) and isinstance(column, int):
                # Game/climber positions are normally zero-based internally.
                if 0 <= row < 9 and 0 <= column < 9:
                    return f"R{row + 1}" f"C{column + 1}"

                # Also tolerate 1-based positions.
                if 1 <= row <= 9 and 1 <= column <= 9:
                    return f"R{row}" f"C{column}"

        return str(position)

    # ------------------------------------------------------------------
    # HELP
    # ------------------------------------------------------------------

    def _show_help(self) -> str:
        """Display the complete Weboku command help."""
        if hasattr(
            self.game,
            "cli",
        ):
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

    # ------------------------------------------------------------------
    # RESULT DISPLAY
    # ------------------------------------------------------------------

    def _get_completed_objective_count(self) -> int:
        """Read the authoritative completed-objective count."""
        completed = getattr(self.game, "completed_objectives", None)

        if completed is not None:
            try:
                return int(completed)
            except (TypeError, ValueError):
                pass

        rings = getattr(self.game, "completed_rings", set())
        columns = getattr(self.game, "completed_columns", set())
        regions = getattr(self.game, "completed_regions", set())

        return len(rings) + len(columns) + len(regions)

    def _display_result(
        self,
        result: Any,
    ) -> None:
        """
        Display the result of a command.

        For a successful Sudoku move, the board is redrawn AFTER the
        result is processed so the newly entered symbol immediately
        appears in its actual cell.
        """

        # ------------------------------------------------------------
        # Plain string result
        # ------------------------------------------------------------

        if isinstance(
            result,
            str,
        ):
            self.output_fn(result)

            return

        # ------------------------------------------------------------
        # MoveResult / result object
        # ------------------------------------------------------------

        if hasattr(
            result,
            "message",
        ):
            notification_lines = [str(result.message)]

            # --------------------------------------------------------
            # Sudoku entry confirmation
            #
            # This is the INPUT CELL, not necessarily the climber's
            # current position.
            # --------------------------------------------------------

            floor = getattr(
                result,
                "floor",
                None,
            )

            column = getattr(
                result,
                "column",
                None,
            )

            symbol = getattr(
                result,
                "symbol",
                None,
            )

            if floor is not None and column is not None and symbol:
                notification_lines.append("✓ MOVE ACCEPTED")
                notification_lines.append(f"Cell updated: R{floor}C{column} = {symbol}")

            # --------------------------------------------------------
            # Objective completion
            # --------------------------------------------------------

            new_objectives = getattr(
                result,
                "new_objectives",
                0,
            )

            new_rings = getattr(result, "new_rings", 0)
            new_columns = getattr(result, "new_columns", 0)
            new_regions = getattr(result, "new_regions", 0)

            # Report every newly completed objective individually.
            # A completion is an objective only when the Game/domain layer
            # reports it; the CLI never invents completion state.
            if new_rings:
                if isinstance(new_rings, (list, tuple, set)):
                    for ring in new_rings:
                        notification_lines.append(f"✓ RING {ring} COMPLETED!")
                else:
                    notification_lines.append(f"✓ RING {new_rings} COMPLETED!")

            if new_columns:
                if isinstance(new_columns, (list, tuple, set)):
                    for column_number in new_columns:
                        notification_lines.append(
                            f"✓ COLUMN {column_number} COMPLETED!"
                        )
                else:
                    notification_lines.append(f"✓ COLUMN {new_columns} COMPLETED!")

            if new_regions:
                if isinstance(new_regions, (list, tuple, set)):
                    for region in new_regions:
                        notification_lines.append(f"✓ WINDOW {region} COMPLETED!")
                else:
                    notification_lines.append(f"✓ WINDOW {new_regions} COMPLETED!")

            if new_objectives:
                notification_lines.append(
                    f"OBJECTIVES: {self._get_completed_objective_count()}/27"
                )

            # --------------------------------------------------------
            # Actual climber movement
            #
            # Only print this when Game says movement occurred.
            # --------------------------------------------------------

            movement_occurred = getattr(
                result,
                "movement_occurred",
                False,
            )

            if movement_occurred:
                current_position = getattr(
                    result,
                    "current_position",
                    None,
                )

                notification_lines.append(
                    "Climber moved to: " f"{self._format_position(current_position)}"
                )

            # --------------------------------------------------------
            # Score
            # --------------------------------------------------------

            score = getattr(
                self.game,
                "score",
                None,
            )

            if score is None:
                scoring = getattr(
                    self.game,
                    "scoring",
                    None,
                )

                score = getattr(
                    scoring,
                    "score",
                    0,
                )

            score_gained = getattr(result, "score_gained", 0)
            notification_lines.append(f"Score gained: +{score_gained}")
            notification_lines.append(f"Total score: {score}")

            # --------------------------------------------------------
            # REDRAW BOARD AFTER EVERY SUCCESSFUL MOVE
            # --------------------------------------------------------

            if getattr(result, "success", False):
                self._show_game_board(notification=notification_lines)
            else:
                rejection_message = getattr(result, "message", None)

                if rejection_message:
                    self.output_fn("✗ MOVE REJECTED")
                    self.output_fn(str(rejection_message))
                else:
                    self.output_fn("✗ MOVE REJECTED")
                    self.output_fn("Move could not be accepted.")

            # --------------------------------------------------------
            # End-state message
            # --------------------------------------------------------

            game_status = getattr(
                result,
                "game_status",
                None,
            )

            if game_status in {
                "VICTORY",
                "GAME_OVER",
            }:
                self.output_fn(f"Game status: " f"{game_status}")

            return

        # ------------------------------------------------------------
        # Other result types
        # ------------------------------------------------------------

        if hasattr(
            result,
            "game_status",
        ):
            self.output_fn(f"Game status: " f"{result.game_status}")

            return

        self.output_fn(str(result))


# ----------------------------------------------------------------------
# APPLICATION FACTORY
# ----------------------------------------------------------------------


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
    from weboku.renderer import Renderer
    from weboku.game import Game

    # ------------------------------------------------------------
    # Core domain objects
    # ------------------------------------------------------------

    # The application starts with the fixed development Sudoku puzzle.
    # Board() itself remains empty for lower-level tests and domain use.
    board = Board.default_puzzle()

    sudoku_engine = SudokuEngine(board)

    climber = Climber()

    scoring = Scoring()

    # Level 1 currently exposes Beginner only.
    # Intermediate, Advanced, and Pro remain disabled until their levels
    # are formally defined and released.
    difficulty = "beginner"

    timer = GameTimer(600) if difficulty == "beginner" else None

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

    # Optional advisory AI. It never mutates authoritative game state.
    try:
        from weboku.ai_master import AIMaster

        ai_master = AIMaster()
    except (ImportError, ModuleNotFoundError):
        ai_master = None

    game.ai_master = ai_master

    # ------------------------------------------------------------
    # Presentation layer
    # ------------------------------------------------------------

    renderer = Renderer()

    game.cli = CLI(
        game=game,
        player=player,
        renderer=renderer,
        ai_master=ai_master,
    )

    return game


# ----------------------------------------------------------------------
# APPLICATION ENTRY POINT
# ----------------------------------------------------------------------


def main() -> None:
    """Application entry point."""

    if "--demo" in sys.argv:
        from weboku.demo import run_demo

        run_demo()

        return

    game = create_game()

    loop = GameLoop(game)

    loop.start()


if __name__ == "__main__":
    main()
