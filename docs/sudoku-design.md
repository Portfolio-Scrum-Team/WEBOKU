# Weboku Sudoku Design

## 1. Purpose

The Sudoku engine is the deterministic Sudoku subsystem of Weboku.

It is responsible for all Sudoku-specific operations, including:

- Representing the 81 Sudoku cells.
- Storing cell values.
- Identifying Floors/Rings.
- Identifying Columns.
- Identifying Windows/Regions.
- Validating Sudoku moves.
- Calculating candidates.
- Detecting completed structures.
- Solving Sudoku puzzles.
- Protecting fixed clues.
- Tracking cell lock state where required by the game contract.
- Providing reliable Sudoku state to the Game engine.

The Sudoku engine is the authoritative source of truth for Sudoku state.

The Sudoku engine must not control:

- Young man/climber movement.
- Princess life.
- Rescue credits.
- Score calculations.
- Timer behavior.
- Victory or game-over decisions.
- CLI rendering.
- Player command handling.
- AI-generated narration.

Those responsibilities belong to other components.

The separation is:

```text
Sudoku Engine
      ↓
Sudoku Truth

Game Engine
      ↓
Gameplay Rules

Climber
      ↓
Automatic Movement

Scoring
      ↓
Points

Timer
      ↓
Objective Attempt Timing

Renderer / CLI
      ↓
Presentation and Interaction

AI Master
      ↓
Narration / Assistance
```

---

# 2. Weboku Board Structure

Weboku uses a logical 9×9 Sudoku board represented visually as a tall building.

The building contains exactly:

```text
9 Floors/Rings
9 Columns
81 Sudoku Cells
9 Windows/Regions
```

Therefore:

```text
9 × 9 = 81 cells
```

The building has a flat roof.

The princess is located above the roof.

The princess is NOT a Sudoku cell.

The roof is NOT part of the 81-cell Sudoku board.

The young man/climber is also NOT a Sudoku cell.

---

# 3. Floors / Rings

The Sudoku rows are represented in the game as Floors/Rings.

There are exactly 9:

```text
Floor 1 / Ring 1
Floor 2 / Ring 2
Floor 3 / Ring 3
Floor 4 / Ring 4
Floor 5 / Ring 5
Floor 6 / Ring 6
Floor 7 / Ring 7
Floor 8 / Ring 8
Floor 9 / Ring 9
```

Each Floor/Ring contains exactly 9 cells.

For Sudoku purposes, a Floor/Ring behaves exactly like a Sudoku row.

A completed Floor/Ring must contain:

```text
1 2 3 4 5 6 7 8 9
```

exactly once.

The terms `Floor` and `Ring` refer to the same logical Sudoku row.

The CLI should normally display the user-facing term:

```text
FLOOR
```

The domain may use:

```text
ring
```

where appropriate for compatibility with the game rules and interfaces.

---

# 4. Columns

The Sudoku columns are represented as building columns.

There are exactly 9:

```text
Column 1
Column 2
Column 3
Column 4
Column 5
Column 6
Column 7
Column 8
Column 9
```

Each Column contains exactly 9 cells.

A completed Column must contain:

```text
1 2 3 4 5 6 7 8 9
```

exactly once.

A Column is a logical Sudoku column.

A Column is also used by the Game engine when determining the young man's automatic climbing position.

The Sudoku engine only reports Column completion.

The Game engine decides what gameplay effect the completion causes.

---

# 5. Windows / Regions

Weboku contains exactly 9 Sudoku Windows.

Each Window contains exactly 9 cells.

A Window is the visual representation of a standard Sudoku 3×3 Region.

The nine Windows are:

```text
Window 1 = Floors 1–3 × Columns 1–3
Window 2 = Floors 1–3 × Columns 4–6
Window 3 = Floors 1–3 × Columns 7–9

Window 4 = Floors 4–6 × Columns 1–3
Window 5 = Floors 4–6 × Columns 4–6
Window 6 = Floors 4–6 × Columns 7–9

Window 7 = Floors 7–9 × Columns 1–3
Window 8 = Floors 7–9 × Columns 4–6
Window 9 = Floors 7–9 × Columns 7–9
```

There must never be:

```text
27 Windows
```

There are exactly:

```text
9 Windows
9 cells per Window
81 cells total
```

The terms `Window` and `Region` refer to the same 3×3 Sudoku structure.

`Window` is primarily a visual/game term.

`Region` is primarily a Sudoku/domain term.

---

# 6. Window Mapping

The Region/Window number can be calculated from a zero-based row/ring and column.

For:

```text
ring = 0–8
column = 0–8
```

the region index is:

```python
region = (ring // 3) * 3 + (column // 3)
```

This produces:

```text
0 → Window/Region 1
1 → Window/Region 2
2 → Window/Region 3
3 → Window/Region 4
4 → Window/Region 5
5 → Window/Region 6
6 → Window/Region 7
7 → Window/Region 8
8 → Window/Region 9
```

Example:

```text
Ring 1, Column 1
→ Region 1

Ring 2, Column 3
→ Region 1

Ring 3, Column 3
→ Region 1
```

Another example:

```text
Ring 5, Column 5
→ Region 5
```

And:

```text
Ring 9, Column 9
→ Region 9
```

---

# 7. Internal Board Representation

The Sudoku engine uses a 9×9 logical representation.

The recommended representation is:

```python
board[ring][column]
```

Python indexes are zero-based.

Therefore:

```text
board[0][0] → Floor/Ring 1, Column 1
board[0][1] → Floor/Ring 1, Column 2
board[0][8] → Floor/Ring 1, Column 9

board[1][0] → Floor/Ring 2, Column 1

board[8][8] → Floor/Ring 9, Column 9
```

The logical board is independent of the CLI drawing.

The renderer may display the board as a tall building with Windows, but the Sudoku engine continues to operate on the 9×9 logical structure.

---

# 8. Coordinate Convention

User-facing coordinates are:

```text
Floor 1–9
Column 1–9
```

Internal Python coordinates are:

```text
Ring 0–8
Column 0–8
```

Example:

```text
User:
Floor 5, Column 5

Internal:
board[4][4]
```

Another example:

```text
User:
Floor 9, Column 1

Internal:
board[8][0]
```

The CLI must not directly manipulate zero-based board indexes.

The conversion belongs at the appropriate application/domain boundary.

---

# 9. Cell Representation

Each playable Sudoku position is represented by a Cell object.

A Cell should contain information equivalent to:

```text
ring/floor
column
value
fixed
locked
```

The Cell may also expose additional state required by the implementation contract.

Conceptually:

```python
Cell(
    ring=1,
    column=1,
    value=5,
    fixed=False,
    locked=False
)
```

The exact constructor and methods are defined by the Cell interface contract.

The Sudoku subsystem owns the Cell implementation.

---

# 10. Empty Cells

An unsolved cell needs a consistent empty representation.

The recommended representation is:

```python
0
```

Therefore:

```text
0 = empty
1–9 = Sudoku values
```

The engine must use the same representation consistently.

An empty cell is not a valid completed Sudoku value.

---

# 11. Fixed Puzzle Clues

A generated or loaded Sudoku puzzle may contain fixed clues.

A fixed clue:

- is part of the original puzzle
- cannot be overwritten
- cannot be cleared
- remains visible throughout the game
- remains fixed after saving and loading

Example:

```text
Cell:
value = 7
fixed = True
```

The player must not modify this cell.

Attempting to modify a fixed clue must produce a controlled validation failure.

---

# 12. Locked Cells

A cell can become permanently locked as a result of objective completion.

A locked cell:

- remains visible
- retains its value
- cannot be changed
- cannot be cleared
- cannot be used for reward farming
- must remain locked after save/load

A cell may be locked because it belongs to a completed:

```text
Ring
Column
Window/Region
```

The Sudoku subsystem must expose enough state for the Game engine to enforce the game's objective-locking rules.

The distinction is:

```text
Fixed
→ locked from the beginning

Locked
→ becomes read-only because of gameplay
```

A cell may be both:

```text
fixed = True
locked = True
```

---

# 13. Sudoku Values

The Sudoku engine stores values as integers:

```text
1
2
3
4
5
6
7
8
9
```

The engine does not store decorative symbols as the primary value.

For example:

```text
5
```

is the actual Sudoku value.

The CLI may display that value as:

```text
◆
```

The renderer performs the visual conversion.

---

# 14. Weboku Symbol Mapping

Weboku uses nine unique symbols for values 1–9.

The authoritative mapping is:

| Value | Symbol | Bonus |
| ----: | :----: | ----: |
|     1 |   ●    |    +2 |
|     2 |   ■    |    +4 |
|     3 |   ▲    |    +6 |
|     4 |   ╱    |    +8 |
|     5 |   ◆    |   +10 |
|     6 |   ★    |   +12 |
|     7 |   ✚    |   +14 |
|     8 |   ○    |   +18 |
|     9 |   ♥    |   +26 |

The total symbol bonus is:

```text
100
```

The Sudoku engine itself does not calculate the gameplay score associated with the symbol.

The Sudoku engine only knows:

```text
value 1
value 2
...
value 9
```

The scoring system interprets the corresponding symbol bonus.

---

# 15. Symbol Conversion

The renderer may use a mapping equivalent to:

```python
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
```

The inverse mapping may be used for CLI input:

```python
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
```

The exact location of these mappings belongs to the agreed module interfaces.

The Sudoku engine should remain independent of terminal formatting.

---

# 16. Sudoku Rules

Weboku follows standard 9×9 Sudoku rules.

For a completed board:

### Floor/Ring rule

Every Floor/Ring contains:

```text
1–9 exactly once
```

### Column rule

Every Column contains:

```text
1–9 exactly once
```

### Window/Region rule

Every Window/Region contains:

```text
1–9 exactly once
```

A value cannot be duplicated within any of these three structures.

---

# 17. Valid Move

A player move is valid when:

1. The Floor/Ring exists.
2. The Column exists.
3. The target cell exists.
4. The target cell is not fixed.
5. The target cell is not locked.
6. The value is between 1 and 9.
7. The value does not violate the Floor/Ring.
8. The value does not violate the Column.
9. The value does not violate the Window/Region.

If all conditions are satisfied, the Sudoku engine may apply the value.

---

# 18. Invalid Move

An invalid move must not corrupt the board.

Examples include:

```text
Floor 0
Floor 10
Column 0
Column 10
Value 0
Value 10
Duplicate in Floor
Duplicate in Column
Duplicate in Window
Editing fixed clue
Editing locked cell
```

The engine must reject the invalid move cleanly.

The application must be able to display a meaningful error to the player.

The program must not crash because of normal invalid user input.

---

# 19. Move Validation Order

A practical validation sequence is:

```text
1. Validate coordinates.
2. Retrieve the Cell.
3. Check fixed state.
4. Check locked state.
5. Validate the value.
6. Check Floor/Ring conflict.
7. Check Column conflict.
8. Check Window/Region conflict.
9. Accept the move.
```

The exact implementation may vary as long as the externally observable behavior follows the interface contract.

---

# 20. Board Mutation

An invalid move must not change the board.

For example:

```text
Before:
R5C5 = empty

Attempt:
set R5C5 = 7

If invalid:
R5C5 remains empty
```

A valid move:

```text
Before:
R5C5 = empty

Attempt:
set R5C5 = 7

If valid:
R5C5 = 7
```

The Game engine may then process the resulting gameplay event.

---

# 21. Candidate Calculation

For an empty cell, candidates are calculated using the intersection of:

```text
missing values in Floor/Ring
∩
missing values in Column
∩
missing values in Window/Region
```

Conceptually:

```python
candidates = (
    missing_from_ring
    & missing_from_column
    & missing_from_region
)
```

Candidates must be deterministic.

Given the same board state and same cell, the engine must return the same candidates.

---

# 22. Candidate Example

Suppose an empty cell has:

```text
Floor/Ring missing:
{2, 5, 7}

Column missing:
{1, 5, 7}

Window/Region missing:
{3, 5, 7}
```

Then:

```text
candidates = {5, 7}
```

The AI Master may use this information when generating hints.

The AI must not calculate a competing version of the Sudoku truth.

The Sudoku engine remains authoritative.

---

# 23. Completion Detection

The Sudoku engine must detect completion of:

```text
Floor/Ring
Column
Window/Region
Entire Sudoku
```

A structure is complete only when:

```text
9 cells are filled
AND
all values are 1–9
AND
no duplicate exists
```

A partially filled structure is not complete.

For example:

```text
8 filled cells
+
1 empty cell
=
NOT COMPLETE
```

---

# 24. Ring Completion

For Ring/Floor `R`:

```python
is_ring_complete(R)
```

should return true only when the corresponding nine cells contain:

```text
1–9 exactly once
```

Example:

```text
R5:
1 4 7 2 8 5 9 3 6
```

is complete.

A Ring completion can become a gameplay objective.

The Sudoku engine reports the completion.

The Game engine determines:

- objective counting
- score
- cell locking
- timer reset
- climber movement
- rescue processing

---

# 25. Column Completion

For Column `C`:

```python
is_column_complete(C)
```

returns true only when the nine cells contain:

```text
1–9 exactly once
```

Example:

```text
C3:
2
5
8
1
7
4
9
6
3
```

is complete.

The Sudoku engine reports the completion.

The Game engine determines the gameplay effect.

---

# 26. Window/Region Completion

For Window/Region `W`:

```python
is_region_complete(W)
```

returns true only when its nine cells contain:

```text
1–9 exactly once
```

The Sudoku engine reports the completion.

The Game engine may then:

- count the new objective
- award objective points
- lock the nine cells
- update objective progress
- process rescue mechanics
- reset the timer if appropriate

Completing a Window/Region does not independently move the young man.

---

# 27. Entire Puzzle Completion

The entire Sudoku is complete when:

```text
all 9 Rings are complete
AND
all 9 Columns are complete
AND
all 9 Windows/Regions are complete
```

Therefore:

```text
9 + 9 + 9 = 27 completed structures
```

The Game engine may use this state as part of the final victory check.

However, Sudoku completion by itself does not automatically mean the game has been won.

Victory also depends on the game rules, including:

```text
27/27 objectives
princess alive
climber reaches roof/princess
score threshold reached
```

---

# 28. Newly Completed Structures

The Game engine must distinguish between:

```text
currently complete
```

and:

```text
newly completed
```

For example:

```text
Ring 5 completes.
```

The Game engine records:

```text
Ring 5 ∈ completed_rings
```

Later, another move may still leave Ring 5 complete.

That does not create another objective.

The same Ring must never be counted twice.

The same rule applies to:

```text
Columns
Windows/Regions
```

---

# 29. Objective Tracking Boundary

The Sudoku engine detects Sudoku completion.

The Game engine owns the authoritative objective sets:

```python
completed_rings
completed_columns
completed_regions
```

The Game engine calculates:

```python
completed_objectives = (
    len(completed_rings)
    + len(completed_columns)
    + len(completed_regions)
)
```

The Sudoku engine should not independently award objective points.

---

# 30. Cell Locking and Objective Completion

When a newly completed objective is accepted by the Game engine:

```text
Ring
OR
Column
OR
Window/Region
```

the Game engine applies the locking rule.

All nine cells belonging to that completed objective become locked.

The Sudoku subsystem must preserve the locked state.

Example:

```text
Ring 5 completed
```

causes:

```text
R5C1 locked
R5C2 locked
R5C3 locked
R5C4 locked
R5C5 locked
R5C6 locked
R5C7 locked
R5C8 locked
R5C9 locked
```

The values remain visible.

---

# 31. Overlapping Locked Cells

A cell can belong to three structures:

```text
1 Ring
1 Column
1 Window/Region
```

For example:

```text
R5C5
```

belongs to:

```text
Ring 5
Column 5
Window 5
```

If any one of these structures becomes a completed objective and locks the cell, the cell becomes read-only.

The cell remains locked even if the other structures are completed later.

---

# 32. Locked Cells and Validation

Before accepting a move, the Sudoku subsystem must ensure the target cell is editable.

If:

```text
cell.locked == True
```

then:

```text
set_value()
```

must reject the change.

The existing value must remain unchanged.

---

# 33. Clearing Values

The game may allow a player to clear a previously entered value.

A clear operation must not:

- clear a fixed clue
- clear a locked cell
- corrupt Sudoku state

For example:

```text
clear R5C5
```

is allowed only if:

```text
R5C5 is player-editable
```

If the cell is fixed or locked, the operation must be rejected.

---

# 34. Replacing Values

A player-entered value may be replaced if the game permits corrections.

Example:

```text
R5C5 = 7
```

may become:

```text
R5C5 = 9
```

only if:

- the cell is editable
- the replacement is valid
- the resulting board remains valid

Fixed and locked cells cannot be replaced.

---

# 35. Sudoku Solver

The Sudoku subsystem should support solving a valid Sudoku puzzle.

A backtracking algorithm is acceptable.

The solver must:

- respect fixed clues
- respect Sudoku rules
- produce a valid solved board
- never produce duplicate values within a Ring
- never produce duplicate values within a Column
- never produce duplicate values within a Window/Region

A solved board must satisfy all Sudoku constraints.

---

# 36. Deterministic Solving

Given the same puzzle and deterministic solver configuration, the solver should produce deterministic results.

The solver must not rely on AI-generated text.

The solver must not depend on the renderer.

The solver must not depend on the CLI.

---

# 37. Puzzle Generation

Puzzle generation may use the following process:

```text
1. Generate a valid solved Sudoku.
2. Remove selected values.
3. Preserve puzzle validity.
4. Validate the resulting puzzle.
5. Provide it to the Game engine.
```

Generated puzzles must have at least one valid solution.

Difficulty should be configurable.

Possible difficulty factors include:

```text
number of clues
candidate complexity
required deduction patterns
time pressure
```

Fewer clues alone do not automatically guarantee a specific difficulty level.

---

# 38. Difficulty Levels

The Game may support:

```text
Beginner
Intermediate
Advanced
Pro
```

The Sudoku engine may expose difficulty configuration required to generate or load an appropriate puzzle.

The timer values belong to the Timer/Game configuration rather than Sudoku validation.

Example timer settings defined by the game rules:

```text
Beginner      10 minutes
Intermediate   5 minutes
Advanced       2 minutes
Pro            1 minute
```

---

# 39. Sudoku State Snapshot

The Sudoku subsystem should provide enough state for other components to inspect the board safely.

A Sudoku state may include:

```text
81 cell values
fixed state
locked state
candidate information when requested
completion state
```

The Game engine should not directly manipulate the internal data structures if the interface provides appropriate methods.

---

# 40. Sudoku Events

The Sudoku subsystem should provide enough information for the Game engine to detect changes.

A successful move may produce information equivalent to:

```text
move accepted
floor/ring
column
value
newly completed rings
newly completed columns
newly completed regions
puzzle complete
```

The exact event object or return structure is defined by the interface contract.

The Sudoku subsystem reports facts.

The Game subsystem determines gameplay consequences.

---

# 41. Completion Event Example

Example sequence:

```text
Player:
set 5 2 ◆
```

The CLI sends the request to the Game/Application layer.

The Game layer asks the Sudoku engine to validate the move.

The Sudoku engine determines:

```text
Value = 5
Move = valid
Ring 5 = newly complete
Column 2 = not complete
Region 4 = not complete
```

The Sudoku engine reports the facts.

The Game engine then decides:

```text
Objective +1
Lock Ring 5 cells
Award objective score
Process climber movement
Process timer success
Process rescue logic
```

The Sudoku engine does not perform those gameplay actions.

---

# 42. Automatic Movement Boundary

The young man's movement is not part of the Sudoku engine.

For example, when:

```text
Ring 5
```

is newly completed, the Sudoku engine reports:

```text
Ring 5 completed
```

The Game engine determines whether the climber moves to:

```text
R5C(active_column)
```

Likewise, when a Column is newly completed, the Game engine determines whether the climber moves sideways.

The Sudoku subsystem never moves the climber.

---

# 43. Princess Boundary

The Sudoku engine has no knowledge of:

```text
princess life
rescue credits
marriage
```

If a timeout occurs:

```text
Timer/Game
```

handles the timeout.

The Sudoku engine remains unchanged.

If the princess dies:

```text
Game = GAME_OVER
```

The Sudoku engine does not decide this.

---

# 44. Scoring Boundary

The Sudoku engine does not calculate gameplay score.

The Sudoku engine may provide:

```text
value = 9
```

The scoring system may then interpret:

```text
symbol ♥
symbol bonus +26
```

The separation is:

```text
Sudoku Engine
    ↓
Value = 9

Renderer
    ↓
♥

Scoring
    ↓
+26 symbol bonus
```

This keeps the Sudoku engine reusable and testable.

---

# 45. Timer Boundary

The Sudoku engine does not own the objective timer.

The Timer/Game system determines:

```text
timer started
timer running
timeout
successful objective attempt
timer reset
```

The Sudoku engine only reports whether a move is valid and whether structures became complete.

---

# 46. CLI Boundary

The Sudoku engine must not print directly to the terminal.

It should not contain:

```python
print(...)
input(...)
terminal color codes
terminal layout logic
```

The CLI and Renderer handle presentation.

This allows Sudoku tests to run without requiring terminal interaction.

---

# 47. AI Boundary

The AI Master may request Sudoku information such as:

```text
candidates
current board
possible hint
completion state
```

The AI must not modify Sudoku truth directly.

The AI may say:

```text
"Try looking at Floor 5, Column 5."
```

But the Game/Sudoku engine decides whether the move is valid.

The AI must never declare a move valid when the Sudoku engine rejects it.

---

# 48. Persistence Boundary

Save/load functionality must preserve Sudoku state.

At minimum, persistence should preserve:

```text
cell values
fixed state
locked state
```

The complete game state also includes non-Sudoku information such as:

```text
score
completed objectives
princess life
rescue credits
failed timeouts
climber position
active column
timer state/configuration
game status
difficulty
```

The Save/Load component owns serialization.

The Sudoku engine provides the state required for persistence.

---

# 49. Sudoku Invariants

The Sudoku subsystem must maintain these invariants:

```text
1. Board has exactly 81 cells.
2. Board has exactly 9 Floors/Rings.
3. Board has exactly 9 Columns.
4. Board has exactly 9 Windows/Regions.
5. Every Window/Region contains exactly 9 cells.
6. Every cell belongs to exactly one Floor/Ring.
7. Every cell belongs to exactly one Column.
8. Every cell belongs to exactly one Window/Region.
9. Values are empty or 1–9.
10. Fixed clues cannot be modified.
11. Locked cells cannot be modified.
12. Invalid moves do not mutate the board.
13. Completed structures contain 1–9 exactly once.
14. Completion detection is deterministic.
15. Candidate calculation is deterministic.
```

---

# 50. Board Invariant

The board must always represent:

```text
9 × 9 = 81 cells
```

No additional playable cell may be introduced.

The roof is outside the board.

The princess is outside the board.

The climber is outside the board.

Therefore:

```text
Playable Sudoku cells = 81
```

exactly.

---

# 51. Window Invariant

There are exactly 9 Windows.

Each Window has:

```text
3 Floors × 3 Columns = 9 cells
```

Therefore:

```text
9 Windows × 9 cells = 81 cells
```

The Window mapping must never change between modules.

---

# 52. Coordinate Invariant

Every cell has one logical coordinate:

```text
(ring, column)
```

where:

```text
ring ∈ {0,1,2,3,4,5,6,7,8}
column ∈ {0,1,2,3,4,5,6,7,8}
```

User-facing values are:

```text
Floor 1–9
Column 1–9
```

The same cell must always resolve to the same Window/Region.

---

# 53. Region Calculation Invariant

For:

```python
ring = 0–8
column = 0–8
```

the Region is:

```python
region = (ring // 3) * 3 + (column // 3)
```

The Region must be within:

```text
0–8
```

The user-facing Window number is:

```text
region + 1
```

---

# 54. Completion Invariant

A structure cannot be considered complete merely because all nine cells are filled.

For example:

```text
1 2 3 4 5 6 7 8 8
```

contains nine values but is invalid.

Therefore completion requires:

```text
9 filled cells
+
values exactly {1,2,3,4,5,6,7,8,9}
```

---

# 55. Objective Invariant

The Sudoku engine may report completion repeatedly while a structure remains complete.

The Game engine must count an objective only once.

Therefore:

```text
currently complete ≠ newly completed objective
```

The authoritative objective sets are maintained by the Game engine.

---

# 56. Locking Invariant

Once a cell becomes locked:

```text
locked = True
```

it remains read-only.

The value remains visible.

Saving and loading must preserve the locked state.

The renderer must not hide locked values.

---

# 57. Testing Requirements

The Sudoku subsystem must include automated tests.

Tests should cover:

```text
Cell creation
Board creation
81-cell count
Floor/Ring lookup
Column lookup
Window/Region lookup
Coordinate conversion
Valid moves
Invalid moves
Duplicate detection
Candidate calculation
Fixed clue protection
Locked cell protection
Ring completion
Column completion
Region completion
Full puzzle completion
Solver correctness
```

---

# 58. Board Tests

The tests should verify:

```text
9 Floors/Rings
9 Columns
81 cells
9 Windows/Regions
```

Each Window must contain exactly 9 cells.

The complete set of Windows must cover all 81 cells without duplication.

---

# 59. Sudoku Rule Tests

Tests should verify that:

```text
duplicate in same Floor → invalid
duplicate in same Column → invalid
duplicate in same Window → invalid
valid value → accepted
out-of-range value → rejected
```

An invalid move must leave the board unchanged.

---

# 60. Candidate Tests

Candidate tests should verify:

```text
candidates =
ring_missing
∩ column_missing
∩ region_missing
```

The returned candidates should be deterministic.

---

# 61. Completion Tests

Tests should verify:

```text
incomplete Ring → False
complete Ring → True

incomplete Column → False
complete Column → True

incomplete Window → False
complete Window → True

incomplete puzzle → False
complete puzzle → True
```

---

# 62. Locking Tests

Tests should verify:

```text
unlocked cell → editable
locked cell → rejected
fixed cell → rejected
fixed + locked cell → rejected
```

A rejected edit must not modify the cell value.

---

# 63. Solver Tests

Solver tests should verify that a solved board contains:

```text
9 valid Floors/Rings
9 valid Columns
9 valid Windows/Regions
```

Every structure must contain:

```text
1–9 exactly once
```

The solver must never return an invalid solution.

---

# 64. Separation Tests

The Sudoku subsystem should be testable independently of:

```text
CLI
Renderer
Climber
Scoring
Timer
AI
Princess system
```

This ensures that Sudoku correctness does not depend on other game systems.

---

# 65. Sudoku Engine Interface

The Sudoku engine should expose a clean interface to the Game/Application layer.

Conceptually:

```python
SudokuEngine
```

may provide operations equivalent to:

```python
load_puzzle()
get_cell()
set_value()
clear_value()
validate_move()
get_candidates()
get_ring()
get_column()
get_region()
is_ring_complete()
is_column_complete()
is_region_complete()
is_complete()
solve()
```

The exact method names and signatures must follow:

```text
docs/interfaces.md
```

The implementation must not invent conflicting public interfaces without updating the contract.

---

# 66. Board Interface

The Board subsystem is responsible for managing the collection of Cells.

Conceptually, it provides operations equivalent to:

```python
get_cell(ring, column)
set_cell(...)
clear_cell(...)
get_ring(ring)
get_column(column)
get_region(region)
```

The exact interface is defined by the project contracts.

---

# 67. Cell Interface

The Cell subsystem owns individual cell state.

A Cell should support concepts equivalent to:

```text
value
ring
column
fixed
locked
```

The Cell should provide controlled mutation rather than allowing arbitrary external state corruption.

---

# 68. No Direct Renderer Access

The Renderer should receive Sudoku state from the appropriate Game/Application interface.

It should not directly modify:

```python
board
cell.value
cell.locked
```

The Renderer is presentation-only.

---

# 69. No Direct CLI Sudoku Logic

The CLI should not independently implement:

```text
duplicate detection
candidate calculation
region calculation
completion detection
solver logic
```

Instead:

```text
CLI
 ↓
Game/Application
 ↓
Sudoku Engine
```

The Sudoku engine remains the source of truth.

---

# 70. No Duplicate Sudoku Engine

There must be only one authoritative Sudoku implementation.

The project must not contain competing logic such as:

```text
CLI Sudoku validation
+
Game Sudoku validation
+
AI Sudoku validation
```

The authoritative implementation is:

```text
weboku/sudoku.py
```

with supporting:

```text
weboku/board.py
weboku/cell.py
```

as defined by the project architecture.

---

# 71. Relationship to the 27 Objectives

The Sudoku engine supplies the facts needed to support 27 gameplay objectives:

```text
9 Ring objectives
9 Column objectives
9 Window/Region objectives
```

The Sudoku engine determines:

```text
Ring complete?
Column complete?
Region complete?
```

The Game engine determines:

```text
Is this newly completed?
Should it count?
Should cells lock?
Should score be awarded?
Should the timer reset?
Should rescue processing occur?
Should the climber move?
```

---

# 72. Multiple Completion Events

A single valid Sudoku move may cause more than one structure to become newly complete.

For example:

```text
one move
   ↓
Ring 5 completes
Column 2 completes
Window 4 completes
```

The Sudoku engine must be capable of reporting all relevant newly completed structures.

The Game engine then counts only structures that were not already recorded as completed objectives.

Therefore:

```text
1 move
→ potentially 1, 2, or 3 new objectives
```

but never more than:

```text
3 new structures from one cell
```

because one cell belongs to:

```text
1 Ring
1 Column
1 Window
```

---

# 73. Already Completed Structures

If a move leaves a previously completed structure complete, it does not create a new completion.

Example:

```text
Ring 5 already completed
Column 2 newly completed
Window 4 already completed
```

The Game engine records:

```text
1 new objective
```

not:

```text
3 objectives
```

This distinction is essential for correct scoring, timer behavior, rescue processing, and the 27-objective limit.

---

# 74. Full Board Completion

When the final Sudoku cell is filled, the Sudoku engine may report:

```text
Ring complete
Column complete
Window complete
Entire puzzle complete
```

The Game engine processes the resulting new objectives.

The final objective count must remain:

```text
27/27
```

The system must never produce:

```text
28/27
```

---

# 75. Sudoku and Climber Relationship

The Sudoku engine does not move the young man.

The relationship is:

```text
Sudoku completion
        ↓
Game event
        ↓
Automatic movement algorithm
        ↓
Climber position
```

For example:

```text
Ring 5 newly completed
+
Active Column C2
        ↓
Game decides
        ↓
Climber → R5C2
```

The Sudoku engine only reports:

```text
Ring 5 completed
```

---

# 76. Sudoku and Timer Relationship

The Sudoku engine does not reset the timer.

The relationship is:

```text
Valid Sudoku move
        ↓
New objective detected
        ↓
Game
        ↓
Successful attempt
        ↓
Timer reset
```

If the timer expires without a new objective:

```text
Timer
 ↓
Game timeout handling
 ↓
Princess/rescue processing
```

The Sudoku engine is not responsible for timeout consequences.

---

# 77. Sudoku and Scoring Relationship

The Sudoku engine supplies:

```text
valid move
value
newly completed structures
```

The Scoring/Game system converts these facts into points.

For example:

```text
value = 9
        ↓
symbol = ♥
        ↓
symbol bonus = +26
```

The Sudoku engine does not own the scoring formula.

---

# 78. Sudoku and Victory Relationship

The Sudoku engine may report:

```text
entire Sudoku complete
```

But it does not declare victory.

The Game engine must verify the complete victory conditions:

```text
27/27 objectives
AND
princess alive
AND
climber reaches roof/princess
AND
score >= required threshold
```

Only the Game engine may transition the overall game into:

```text
VICTORY
```

---

# 79. Error Handling

The Sudoku subsystem should use controlled errors or result objects according to the project's interface contract.

Expected invalid conditions include:

```text
invalid coordinates
invalid value
fixed cell
locked cell
Sudoku conflict
invalid board state
```

The CLI should convert these into understandable player-facing messages.

The engine must not terminate the entire application because of an ordinary invalid move.

---

# 80. Determinism

The Sudoku engine must be deterministic for all validation and state operations.

Given the same:

```text
board state
cell
value
```

the result of validation must be the same.

Given the same board:

```text
candidate calculation
completion detection
region mapping
```

must produce the same result.

---

# 81. Source of Truth

The authoritative responsibilities are:

```text
Sudoku Engine
→ Sudoku truth

Game Engine
→ Game truth

Scoring
→ Score truth

Timer
→ Timer truth

Climber
→ Movement state

Save/Load
→ Persistence representation

Renderer
→ Visual presentation

CLI
→ User interaction

AI Master
→ Narration and assistance
```

No component should silently create a competing version of Sudoku truth.

---

# 82. Final Sudoku Data Flow

The complete Sudoku data flow is:

```text
Player Input
     ↓
CLI
     ↓
Game/Application
     ↓
Sudoku Engine
     ↓
Validate Move
     ↓
Update Cell
     ↓
Detect Completed Structures
     ↓
Return Sudoku Facts
     ↓
Game Engine
     ↓
Objectives / Locking / Score / Movement / Timer
     ↓
Renderer
     ↓
Updated Building Display
```

---

# 83. Final Sudoku Model

The authoritative logical model is:

```text
                    WEBOKU SUDOKU

                 9 Floors/Rings
                       ×
                    9 Columns
                       =
                    81 Cells

                       │
          ┌────────────┼────────────┐
          │            │            │
       Rings        Columns      Windows
          │            │            │
          9            9            9
          │            │            │
          └────────────┼────────────┘
                       │
                 27 Objectives
```

Each Window contains:

```text
3 Floors × 3 Columns
=
9 Cells
```

The complete game therefore has:

```text
81 Sudoku cells
9 Floors/Rings
9 Columns
9 Windows/Regions
27 Objectives
```

---

# 84. Authoritative Rules Summary

The Sudoku subsystem must always preserve these rules:

```text
1. The board is 9×9.
2. There are exactly 81 playable cells.
3. There are exactly 9 Floors/Rings.
4. There are exactly 9 Columns.
5. There are exactly 9 Windows/Regions.
6. Each Window contains exactly 9 cells.
7. Values are integers 1–9.
8. Empty cells use the defined empty representation.
9. Each completed Floor/Ring contains 1–9 exactly once.
10. Each completed Column contains 1–9 exactly once.
11. Each completed Window/Region contains 1–9 exactly once.
12. Fixed clues cannot be modified.
13. Locked cells cannot be modified.
14. Invalid moves do not modify the board.
15. Candidates use Ring ∩ Column ∩ Region missing values.
16. Completion detection is deterministic.
17. The Sudoku engine does not control game mechanics.
18. The Game engine owns gameplay consequences.
19. The Renderer owns visual representation.
20. The AI cannot override Sudoku truth.
```

---

# 85. Final Integration Rule

The Sudoku engine is the single source of truth for Sudoku.

When other systems need Sudoku information, they must request it from the Sudoku subsystem rather than recreating Sudoku logic.

The correct dependency direction is:

```text
CLI
 ↓
Game/Application
 ↓
Sudoku Engine
 ↓
Board / Cell
```

Other systems react to the Game/Application layer:

```text
Game
 ├── Scoring
 ├── Timer
 ├── Climber
 ├── Save/Load
 ├── AI Master
 └── Renderer
```

The final principle is:

```text
SOLVE
  ↓
SUDOKU ENGINE
  ↓
REPORT TRUTH
  ↓
GAME ENGINE
  ↓
UNLOCK / SCORE / TIMER / MOVE
  ↓
RENDER
```

The Sudoku engine solves Sudoku.

The Game engine turns Sudoku events into Weboku gameplay.
