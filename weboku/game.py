"""
Weboku Game/Application Coordinator.

This module owns the overall game flow and authoritative game state.

The Game class coordinates the domain modules. It does not reimplement
Sudoku, scoring, timer, climber, CLI, AI, or persistence internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Game constants
# ---------------------------------------------------------------------------

MAX_OBJECTIVES = 27
MAX_PRINCESS_LIFE = 27

GAME_STATUS_READY = "READY"
GAME_STATUS_PLAYING = "PLAYING"
GAME_STATUS_VICTORY = "VICTORY"
GAME_STATUS_GAME_OVER = "GAME_OVER"


# Weboku numeric value <-> terminal symbol mapping.
SYMBOL_TO_VALUE = {
    "●": 1,
    "■": 2,
    "▲": 3,
    "╱": 4,
    "◆": 5,
    "★": 6,
    "✚": 7,
    "○": 8,
    "♥": 9,
}

VALUE_TO_SYMBOL = {value: symbol for symbol, value in SYMBOL_TO_VALUE.items()}


@dataclass
class MoveResult:
    """
    Result returned after processing a player move.

    This keeps the Game layer deterministic while giving the CLI enough
    information to display what happened.
    """

    success: bool
    message: str

    floor: Optional[int] = None
    column: Optional[int] = None
    value: Optional[int] = None
    symbol: Optional[str] = None

    new_rings: list[int] = field(default_factory=list)
    new_columns: list[int] = field(default_factory=list)
    new_regions: list[int] = field(default_factory=list)

    new_objectives: int = 0
    score_gained: int = 0

    movement_occurred: bool = False
    current_position: Any = None

    game_status: str = GAME_STATUS_PLAYING


@dataclass
class GameState:
    """
    Serializable snapshot of the authoritative game state.

    The Game class remains the owner of this state.
    """

    board: Any = None
    score: int = 0

    completed_rings: set[int] = field(default_factory=set)
    completed_columns: set[int] = field(default_factory=set)
    completed_regions: set[int] = field(default_factory=set)

    princess_life: int = MAX_PRINCESS_LIFE
    rescue_credits: int = 0
    failed_timeouts: int = 0

    current_position: Any = None
    active_column: Optional[int] = None

    game_status: str = GAME_STATUS_READY
    difficulty: str = "beginner"

    @property
    def completed_objectives(self) -> int:
        """Return the number of genuinely completed objectives."""

        return (
            len(self.completed_rings)
            + len(self.completed_columns)
            + len(self.completed_regions)
        )


class Game:
    """
    Central Weboku application/game coordinator.

    Responsibilities:

    - maintain authoritative game state
    - receive Sudoku moves
    - coordinate Sudoku validation
    - detect newly completed objectives
    - coordinate objective locking
    - coordinate scoring
    - coordinate climber movement
    - coordinate timer success/timeout behavior
    - coordinate princess life and rescue credits
    - determine victory/game over

    Individual systems remain responsible for their own internal logic.
    """

    def __init__(
        self,
        board: Any = None,
        sudoku_engine: Any = None,
        climber: Any = None,
        scoring: Any = None,
        timer: Any = None,
        player: Any = None,
        difficulty: str = "beginner",
        score_threshold: int = 0,
    ) -> None:
        self.state = GameState(
            board=board,
            difficulty=difficulty,
        )

        self.sudoku_engine = sudoku_engine
        self.climber = climber
        self.scoring = scoring
        self.timer = timer
        self.player = player

        self.score_threshold = score_threshold

        self.last_move_result: Optional[MoveResult] = None
        self.recent_events: list[str] = []

    # ------------------------------------------------------------------
    # Basic state properties
    # ------------------------------------------------------------------

    @property
    def board(self) -> Any:
        return self.state.board

    @property
    def score(self) -> int:
        return self.state.score

    @property
    def completed_rings(self) -> set[int]:
        return self.state.completed_rings

    @property
    def completed_columns(self) -> set[int]:
        return self.state.completed_columns

    @property
    def completed_regions(self) -> set[int]:
        return self.state.completed_regions

    @property
    def completed_objectives(self) -> int:
        return self.state.completed_objectives

    @property
    def princess_life(self) -> int:
        return self.state.princess_life

    @property
    def rescue_credits(self) -> int:
        return self.state.rescue_credits

    @property
    def failed_timeouts(self) -> int:
        return self.state.failed_timeouts

    @property
    def current_position(self) -> Any:
        return self.state.current_position

    @property
    def active_column(self) -> Optional[int]:
        return self.state.active_column

    @property
    def game_status(self) -> str:
        return self.state.game_status

    @property
    def difficulty(self) -> str:
        return self.state.difficulty

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------

    def start(self) -> GameState:
        """Start the game."""

        if self.state.game_status == GAME_STATUS_GAME_OVER:
            return self.state

        if self.state.game_status == GAME_STATUS_VICTORY:
            return self.state

        self.state.game_status = GAME_STATUS_PLAYING

        self._start_timer_if_available()

        self._add_event("Game started.")

        return self.state

    def reset(self) -> GameState:
        """
        Reset game-level state.

        The board itself is not regenerated here. Board/puzzle creation
        belongs to the Sudoku/Board layer.
        """

        self.state.score = 0

        self.state.completed_rings.clear()
        self.state.completed_columns.clear()
        self.state.completed_regions.clear()

        self.state.princess_life = MAX_PRINCESS_LIFE
        self.state.rescue_credits = 0
        self.state.failed_timeouts = 0

        self.state.current_position = None
        self.state.active_column = None

        self.state.game_status = GAME_STATUS_READY

        self.last_move_result = None
        self.recent_events.clear()

        return self.state

    # ------------------------------------------------------------------
    # Move processing
    # ------------------------------------------------------------------

    def process_move(
        self,
        floor: int,
        column: int,
        symbol: str,
    ) -> MoveResult:
        """
        Process one player Sudoku move.

        Authoritative sequence:

        1. Validate coordinates.
        2. Convert symbol to value.
        3. Ask SudokuEngine to validate.
        4. Apply valid move.
        5. Award move score.
        6. Apply symbol bonus.
        7. Detect new objectives.
        8. Lock completed objectives.
        9. Award objective score.
        10. Process automatic movement.
        11. Process extra objectives.
        12. Process timer success.
        13. Check princess life.
        14. Check victory.
        """

        if self.state.game_status == GAME_STATUS_READY:
            self.start()

        if self.state.game_status in {
            GAME_STATUS_VICTORY,
            GAME_STATUS_GAME_OVER,
        }:
            return self._failed_move(
                "The game has already ended."
            )

        if not self._valid_coordinate(floor, column):
            return self._failed_move(
                "Invalid position. Floor and column must be from 1 to 9."
            )

        value = self.symbol_to_value(symbol)

        if value is None:
            return self._failed_move(
                "Invalid symbol. Use one of the Weboku symbols."
            )

        # SudokuEngine owns Sudoku validation.
        validation = self._validate_sudoku_move(
            floor,
            column,
            value,
        )

        if validation is not True:
            return self._failed_move(
                self._validation_message(validation)
            )

        # Apply the valid move through the Board/Sudoku layer.
        applied = self._apply_value(
            floor,
            column,
            value,
        )

        if not applied:
            return self._failed_move(
                "The move could not be applied."
            )

        score_before = self.state.score

        # Base move score + symbol bonus.
        self._award_move_score(value)

        # Detect genuinely new structures.
        new_rings = self._detect_new_rings()
        new_columns = self._detect_new_columns()
        new_regions = self._detect_new_regions()

        new_objective_count = (
            len(new_rings)
            + len(new_columns)
            + len(new_regions)
        )

        # Record and lock newly completed objectives.
        self._record_new_objectives(
            new_rings,
            new_columns,
            new_regions,
        )

        # Objective scoring.
        self._award_objective_score(
            new_objective_count
        )

        # Automatic movement.
        movement_occurred = self._process_automatic_movement(
            new_rings,
            new_columns,
        )

        # Extra objective handling.
        if new_objective_count > 1:
            self._process_extra_objectives(
                new_objective_count
            )

        # Timer success is based on at least one genuinely new objective.
        if new_objective_count > 0:
            self._process_successful_attempt()

        # Check princess/game-over state.
        self._check_princess_life()

        # Check victory after all move effects.
        self._check_victory()

        score_gained = self.state.score - score_before

        result = MoveResult(
            success=True,
            message="Move accepted.",
            floor=floor,
            column=column,
            value=value,
            symbol=self.value_to_symbol(value),
            new_rings=new_rings,
            new_columns=new_columns,
            new_regions=new_regions,
            new_objectives=new_objective_count,
            score_gained=score_gained,
            movement_occurred=movement_occurred,
            current_position=self.state.current_position,
            game_status=self.state.game_status,
        )

        self.last_move_result = result

        self._add_event(
            f"Valid move at R{floor}C{column}: {self.value_to_symbol(value)}"
        )

        return result

    # ------------------------------------------------------------------
    # Symbol conversion
    # ------------------------------------------------------------------

    @staticmethod
    def symbol_to_value(symbol: str) -> Optional[int]:
        """Convert a Weboku symbol into its internal numeric value."""

        if not isinstance(symbol, str):
            return None

        symbol = symbol.strip()

        if symbol in SYMBOL_TO_VALUE:
            return SYMBOL_TO_VALUE[symbol]

        # Also allow numeric input for convenience.
        if symbol.isdigit():
            value = int(symbol)

            if 1 <= value <= 9:
                return value

        return None

    @staticmethod
    def value_to_symbol(value: int) -> Optional[str]:
        """Convert an internal numeric value into a Weboku symbol."""

        return VALUE_TO_SYMBOL.get(value)

    # ------------------------------------------------------------------
    # Coordinate validation
    # ------------------------------------------------------------------

    @staticmethod
    def _valid_coordinate(floor: int, column: int) -> bool:
        return (
            isinstance(floor, int)
            and isinstance(column, int)
            and 1 <= floor <= 9
            and 1 <= column <= 9
        )

    # ------------------------------------------------------------------
    # Sudoku coordination
    # ------------------------------------------------------------------

    def _validate_sudoku_move(
        self,
        floor: int,
        column: int,
        value: int,
    ) -> Any:
        """Ask SudokuEngine to validate a move."""

        if self.sudoku_engine is None:
            # During early integration, allow Game to exist without
            # another member's implementation being present.
            return True

        engine = self.sudoku_engine

        for method_name in (
            "validate_move",
            "is_valid_move",
            "check_move",
        ):
            method = getattr(engine, method_name, None)

            if callable(method):
                try:
                    return method(
                        floor,
                        column,
                        value,
                    )
                except TypeError:
                    try:
                        return method(
                            floor - 1,
                            column - 1,
                            value,
                        )
                    except TypeError:
                        continue

        return True

    def _apply_value(
        self,
        floor: int,
        column: int,
        value: int,
    ) -> bool:
        """Apply a validated value through the available board interface."""

        if self.board is None:
            return True

        # Prefer a Board.set_value method.
        setter = getattr(self.board, "set_value", None)

        if callable(setter):
            try:
                result = setter(
                    floor,
                    column,
                    value,
                )
                return result is not False
            except TypeError:
                try:
                    result = setter(
                        floor - 1,
                        column - 1,
                        value,
                    )
                    return result is not False
                except TypeError:
                    pass

        # Try a generic set_cell_value method.
        setter = getattr(
            self.board,
            "set_cell_value",
            None,
        )

        if callable(setter):
            try:
                result = setter(
                    floor,
                    column,
                    value,
                )
                return result is not False
            except TypeError:
                try:
                    result = setter(
                        floor - 1,
                        column - 1,
                        value,
                    )
                    return result is not False
                except TypeError:
                    pass

        return True

    # ------------------------------------------------------------------
    # Objective detection
    # ------------------------------------------------------------------

    def _detect_new_rings(self) -> list[int]:
        """Return newly completed rings."""

        completed = self._get_completed_structures(
            "completed_rings"
        )

        return sorted(
            ring
            for ring in completed
            if ring not in self.state.completed_rings
        )

    def _detect_new_columns(self) -> list[int]:
        """Return newly completed columns."""

        completed = self._get_completed_structures(
            "completed_columns"
        )

        return sorted(
            column
            for column in completed
            if column not in self.state.completed_columns
        )

    def _detect_new_regions(self) -> list[int]:
        """Return newly completed windows/regions."""

        completed = self._get_completed_structures(
            "completed_regions"
        )

        return sorted(
            region
            for region in completed
            if region not in self.state.completed_regions
        )

    def _get_completed_structures(
        self,
        structure_name: str,
    ) -> set[int]:
        """Ask SudokuEngine for completed structures when supported."""

        if self.sudoku_engine is None:
            return set()

        engine = self.sudoku_engine

        method_names = {
            "completed_rings": (
                "get_completed_rings",
                "completed_rings",
            ),
            "completed_columns": (
                "get_completed_columns",
                "completed_columns",
            ),
            "completed_regions": (
                "get_completed_regions",
                "completed_regions",
                "get_completed_windows",
                "completed_windows",
            ),
        }

        for method_name in method_names[structure_name]:
            attribute = getattr(
                engine,
                method_name,
                None,
            )

            if callable(attribute):
                result = attribute()
            else:
                result = attribute

            if result is not None:
                try:
                    return set(result)
                except TypeError:
                    return set()

        return set()

    def _record_new_objectives(
        self,
        new_rings: list[int],
        new_columns: list[int],
        new_regions: list[int],
    ) -> None:
        """Record and lock newly completed objectives."""

        for ring in new_rings:
            if ring not in self.state.completed_rings:
                self.state.completed_rings.add(ring)
                self._lock_ring(ring)

        for column in new_columns:
            if column not in self.state.completed_columns:
                self.state.completed_columns.add(column)
                self._lock_column(column)

        for region in new_regions:
            if region not in self.state.completed_regions:
                self.state.completed_regions.add(region)
                self._lock_region(region)

        # Defensive invariant.
        if self.completed_objectives > MAX_OBJECTIVES:
            raise RuntimeError(
                "Weboku objective count exceeded 27."
            )

    # ------------------------------------------------------------------
    # Objective locking
    # ------------------------------------------------------------------

    def _lock_ring(self, ring: int) -> None:
        self._lock_structure("ring", ring)

    def _lock_column(self, column: int) -> None:
        self._lock_structure("column", column)

    def _lock_region(self, region: int) -> None:
        self._lock_structure("region", region)

    def _lock_structure(
        self,
        structure_type: str,
        number: int,
    ) -> None:
        """Delegate locking to Board/SudokuEngine when supported."""

        owner = self.board

        if owner is None:
            owner = self.sudoku_engine

        if owner is None:
            return

        method_map = {
            "ring": (
                "lock_ring",
                "lock_row",
            ),
            "column": (
                "lock_column",
            ),
            "region": (
                "lock_region",
                "lock_window",
            ),
        }

        for method_name in method_map[structure_type]:
            method = getattr(owner, method_name, None)

            if callable(method):
                try:
                    method(number)
                    return
                except TypeError:
                    try:
                        method(number - 1)
                        return
                    except TypeError:
                        continue

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _award_move_score(self, value: int) -> None:
        """Award base move score and symbol bonus through Scoring when possible."""

        if self.scoring is not None:
            method = getattr(
                self.scoring,
                "award_move",
                None,
            )

            if callable(method):
                result = method(value)

                if isinstance(result, int):
                    self.state.score += result

                return

        # Safe fallback while the Scoring module is under development.
        self.state.score += 10

        symbol_bonus = {
            1: 2,
            2: 4,
            3: 6,
            4: 8,
            5: 10,
            6: 12,
            7: 14,
            8: 18,
            9: 26,
        }

        self.state.score += symbol_bonus[value]

    def _award_objective_score(
        self,
        count: int,
    ) -> None:
        """Award objective completion points."""

        if count <= 0:
            return

        if self.scoring is not None:
            method = getattr(
                self.scoring,
                "award_objective",
                None,
            )

            if callable(method):
                result = method(count)

                if isinstance(result, int):
                    self.state.score += result

                return

        # Objective score is deliberately isolated so it can be changed
        # centrally when the Scoring module is integrated.
        objective_points = 100
        self.state.score += objective_points * count

    # ------------------------------------------------------------------
    # Automatic climber movement
    # ------------------------------------------------------------------

    def _process_automatic_movement(
        self,
        new_rings: list[int],
        new_columns: list[int],
    ) -> bool:
        """
        Process deterministic automatic climber movement.

        Movement rules:

        1. A newly completed Column becomes the active column.
        2. A Column completed before any Ring does not move the climber.
        3. A newly completed Ring moves the climber to:
               (new_ring, active_column)
           when an active column exists.
        4. A newly completed Column moves the climber to:
               (current_ring, new_column)
           when a current ring exists.
        5. Window completion never directly moves the climber.
        6. Movement is automatic and deterministic.
        7. Completed objectives cannot be farmed, so movement cannot
           be repeatedly triggered by the same objective.
        """

        moved = False

        # --------------------------------------------------------------
        # 1. Update the active column.
        # --------------------------------------------------------------
        #
        # The newest genuinely completed column becomes the active
        # column. Columns are supplied by the objective-detection stage.
        #
        if new_columns:
            self.state.active_column = new_columns[-1]

        # --------------------------------------------------------------
        # 2. Ring movement.
        # --------------------------------------------------------------
        #
        # A completed Ring uses the current active Column.
        #
        if new_rings:
            new_ring = new_rings[-1]
            active_column = self.state.active_column

            # A Ring cannot place the climber on a playable position
            # until a completed Column exists.
            if active_column is not None:
                self.state.current_position = (
                    new_ring,
                    active_column,
                )

                moved = True

                self._update_climber_position(
                    new_ring,
                    active_column,
                )

                self._add_event(
                    f"Climber moved to R{new_ring}C{active_column}."
                )

        # --------------------------------------------------------------
        # 3. Column movement.
        # --------------------------------------------------------------
        #
        # If there was no Ring movement during this move, but a new
        # Column completed and a current Ring already exists, move
        # horizontally to the new Column.
        #
        elif new_columns:
            current_ring = self._current_ring()
            new_column = new_columns[-1]

            if current_ring is not None:
                self.state.current_position = (
                    current_ring,
                    new_column,
                )

                moved = True

                self._update_climber_position(
                    current_ring,
                    new_column,
                )

                self._add_event(
                    f"Climber moved to R{current_ring}C{new_column}."
                )

        return moved
    def _current_ring(self) -> Optional[int]:
        """Return the current ring from the climber position."""

        position = self.state.current_position

        if isinstance(position, tuple) and len(position) >= 1:
            ring = position[0]

            if isinstance(ring, int):
                return ring

        return None

    def _update_climber_position(
        self,
        ring: int,
        column: int,
    ) -> None:
        """
        Update the external Climber module when it is available.

        Game state remains the authoritative position. The Climber
        module is only notified about the new position.
        """

        climber = getattr(self, "climber", None)

        if climber is None:
            return

        for method_name in (
            "move_to",
            "set_position",
            "update_position",
            "move",
        ):
            method = getattr(climber, method_name, None)

            if not callable(method):
                continue

            try:
                method(ring, column)
                return
            except TypeError:
                try:
                    method(
                        ring - 1,
                        column - 1,
                    )
                    return
                except TypeError:
                    continue
    # ------------------------------------------------------------------
    # Extra objective / rescue handling
    # ------------------------------------------------------------------

    def _process_extra_objectives(
        self,
        new_objective_count: int,
    ) -> None:
        """
        Process extra objective completions.

        One completion is the normal completion.

        Additional completions first restore previously lost princess life.

        Any remaining extras become rescue credits.
        """

        extras = max(
            0,
            new_objective_count - 1,
        )

        if extras == 0:
            return

        lost_life = MAX_PRINCESS_LIFE - self.state.princess_life

        life_restored = min(
            extras,
            lost_life,
        )

        if life_restored:
            self.state.princess_life += life_restored
            extras -= life_restored

            self._add_event(
                f"Princess recovered {life_restored} life."
            )

        if extras:
            self.state.rescue_credits += extras

            self._add_event(
                f"Earned {extras} rescue credit(s)."
            )

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------

    def _process_successful_attempt(self) -> None:
        """Reset timer after at least one new objective."""

        if self.timer is None:
            return

        for method_name in (
            "reset",
            "reset_timer",
            "restart",
        ):
            method = getattr(
                self.timer,
                method_name,
                None,
            )

            if callable(method):
                method()
                return

    def _start_timer_if_available(self) -> None:
        if self.timer is None:
            return

        for method_name in (
            "start",
            "start_timer",
        ):
            method = getattr(
                self.timer,
                method_name,
                None,
            )

            if callable(method):
                method()
                return

    def handle_timeout(self) -> bool:
        """
        Process a timer timeout.

        Returns True if the game continues.
        """

        if self.state.game_status in {
            GAME_STATUS_VICTORY,
            GAME_STATUS_GAME_OVER,
        }:
            return False

        self.state.failed_timeouts += 1

        if self.state.rescue_credits > 0:
            self.state.rescue_credits -= 1

            self._add_event(
                "Timeout protected by a rescue credit."
            )
        else:
            self.state.princess_life = max(
                0,
                self.state.princess_life - 1,
            )

            self._add_event(
                "Timeout! Princess lost 1 life."
            )

        self._check_princess_life()

        if self.state.game_status == GAME_STATUS_PLAYING:
            self._reset_timer_after_timeout()

        return self.state.game_status == GAME_STATUS_PLAYING

    def _reset_timer_after_timeout(self) -> None:
        if self.timer is None:
            return

        for method_name in (
            "reset",
            "reset_timer",
            "restart",
        ):
            method = getattr(
                self.timer,
                method_name,
                None,
            )

            if callable(method):
                method()
                return

    # ------------------------------------------------------------------
    # Princess / game over
    # ------------------------------------------------------------------

    def _check_princess_life(self) -> None:
        """Determine whether princess life has reached zero."""

        self.state.princess_life = min(
            MAX_PRINCESS_LIFE,
            max(0, self.state.princess_life),
        )

        if self.state.princess_life <= 0:
            self.state.game_status = GAME_STATUS_GAME_OVER

            self._stop_timer()

            self._add_event(
                "Game over: the princess has lost all life."
            )

    # ------------------------------------------------------------------
    # Victory
    # ------------------------------------------------------------------

    def _check_victory(self) -> bool:
        """
        Check the complete victory condition.

        Victory requires:

        - all 27 objectives
        - climber reaching the princess/roof
        - score threshold
        """

        if self.completed_objectives < MAX_OBJECTIVES:
            return False

        if not self._climber_has_reached_princess():
            return False

        if self.state.score < self.score_threshold:
            return False

        self.state.game_status = GAME_STATUS_VICTORY

        self._stop_timer()

        self._add_event(
            "VICTORY! The young man reached the princess."
        )

        self._add_event(
            "MARRIAGE COMPLETE."
        )

        return True

    def _climber_has_reached_princess(self) -> bool:
        """
        Determine whether the climber has reached the roof.

        The exact roof representation belongs to the Climber module.
        """

        if self.climber is not None:
            for attribute_name in (
                "has_reached_princess",
                "reached_princess",
                "at_roof",
            ):
                attribute = getattr(
                    self.climber,
                    attribute_name,
                    None,
                )

                if callable(attribute):
                    try:
                        return bool(attribute())
                    except TypeError:
                        continue

                if attribute is not None:
                    return bool(attribute)

        # Fallback: completing all rings and columns means the climber
        # has reached the final game position.
        return (
            len(self.state.completed_rings) == 9
            and len(self.state.completed_columns) == 9
        )

    def _stop_timer(self) -> None:
        if self.timer is None:
            return

        for method_name in (
            "stop",
            "stop_timer",
        ):
            method = getattr(
                self.timer,
                method_name,
                None,
            )

            if callable(method):
                method()
                return

    # ------------------------------------------------------------------
    # Status / snapshots
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Return a renderer-friendly snapshot of game state."""

        return {
            "score": self.state.score,
            "completed_rings": sorted(
                self.state.completed_rings
            ),
            "completed_columns": sorted(
                self.state.completed_columns
            ),
            "completed_regions": sorted(
                self.state.completed_regions
            ),
            "completed_objectives": self.completed_objectives,
            "max_objectives": MAX_OBJECTIVES,
            "princess_life": self.state.princess_life,
            "max_princess_life": MAX_PRINCESS_LIFE,
            "rescue_credits": self.state.rescue_credits,
            "failed_timeouts": self.state.failed_timeouts,
            "current_position": self.state.current_position,
            "active_column": self.state.active_column,
            "game_status": self.state.game_status,
            "difficulty": self.state.difficulty,
            "score_threshold": self.score_threshold,
        }

    def snapshot(self) -> GameState:
        """Return the current game state."""

        return self.state

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _add_event(self, message: str) -> None:
        """Record a recent game event."""

        self.recent_events.append(message)

        # Keep the dashboard compact.
        self.recent_events = self.recent_events[-10:]

    def get_recent_events(self) -> list[str]:
        """Return recent game events."""

        return list(self.recent_events)

    # ------------------------------------------------------------------
    # Error helpers
    # ------------------------------------------------------------------

    def _failed_move(self, message: str) -> MoveResult:
        """Create a failed MoveResult."""

        result = MoveResult(
            success=False,
            message=message,
            game_status=self.state.game_status,
        )

        self.last_move_result = result

        self._add_event(message)

        return result

    @staticmethod
    def _validation_message(validation: Any) -> str:
        """Convert a validation result into a useful CLI message."""

        if isinstance(validation, str):
            return validation

        if validation is False:
            return "Invalid Sudoku move."

        return "Invalid Sudoku move."

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def is_victory(self) -> bool:
        """Return whether the game has reached victory."""

        return self.state.game_status == GAME_STATUS_VICTORY

    def is_game_over(self) -> bool:
        """Return whether the game is over."""

        return self.state.game_status == GAME_STATUS_GAME_OVER

    def can_play(self) -> bool:
        """Return whether the game accepts player moves."""

        return self.state.game_status in {
            GAME_STATUS_READY,
            GAME_STATUS_PLAYING,
        }
