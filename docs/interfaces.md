# Weboku Module Interface Contracts

## Purpose

This document defines the contracts between Weboku modules.

The Python game engine is the source of truth for:

- Sudoku validity
- Game state
- Objective completion
- Cell locking
- Timer state
- Princess life
- Rescue credits
- Score
- Climber position
- Victory and game-over conditions

The CLI only receives state and user commands.

The renderer only displays state.

The AI Master may provide narration, hints, or dialogue, but it must never determine game truth.

---

# 1. Global Weboku Rules

Weboku uses:

- 9 floors/rings
- 9 columns
- 81 Sudoku cells
- 9 Sudoku windows/regions
- 9 cells per window
- 27 total objectives

The Sudoku board is internally represented as:

```text
board[ring][column]
```

Both `ring` and `column` use zero-based indexing internally:

```text
0 - 8
```

The CLI displays them as:

```text
1 - 9
```

The princess is located on the flat roof above Floor 1.

The princess is NOT a Sudoku cell.

The young man/climber begins at the building base at Floor 9.

The game flow is:

```text
SOLVE → UNLOCK → CLIMB → REACH → MARRY
```

---

# 2. Cell

File:

```text
weboku/cell.py
```

## Responsibility

Represents one Sudoku cell.

A Cell stores the state of one position on the 9×9 board.

## Required state

```python
ring: int
column: int
value: int | None
locked: bool
```

## Rules

`ring` must be between `0` and `8`.

`column` must be between `0` and `8`.

`value` must be:

```text
None
```

or:

```text
1 - 9
```

A locked cell cannot be modified.

## Required behavior

The Cell should provide behavior equivalent to:

```python
set_value(value)
clear()
lock()
is_locked()
is_empty()
```

The exact method signatures may be refined during implementation, but the behavior must remain compatible with this contract.

---

# 3. Board

File:

```text
weboku/board.py
```

## Responsibility

Stores the 9×9 collection of Cells.

## Structure

```text
9 rings × 9 columns = 81 cells
```

The Board does not decide whether a Sudoku move is valid.

That responsibility belongs to `SudokuEngine`.

## Required behavior

The Board should support operations equivalent to:

```python
get_cell(ring, column)
set_value(ring, column, value)
clear_value(ring, column)
lock_cells(cells)
get_ring(ring)
get_column(column)
get_region(region)
```

The Board must preserve Cell locking.

A locked Cell remains read-only.

---

# 4. SudokuEngine

File:

```text
weboku/sudoku.py
```

## Responsibility

Owns all Sudoku rules and validation.

The SudokuEngine is the authority on whether a Sudoku move is valid.

## Sudoku rules

Every completed ring must contain:

```text
1 - 9 exactly once
```

Every completed column must contain:

```text
1 - 9 exactly once
```

Every completed 3×3 region/window must contain:

```text
1 - 9 exactly once
```

## Region mapping

There are exactly 9 regions.

```text
Region 1 = Rings 1-3 × Columns 1-3
Region 2 = Rings 1-3 × Columns 4-6
Region 3 = Rings 1-3 × Columns 7-9

Region 4 = Rings 4-6 × Columns 1-3
Region 5 = Rings 4-6 × Columns 4-6
Region 6 = Rings 4-6 × Columns 7-9

Region 7 = Rings 7-9 × Columns 1-3
Region 8 = Rings 7-9 × Columns 4-6
Region 9 = Rings 7-9 × Columns 7-9
```

## Required behavior

The engine should support behavior equivalent to:

```python
is_valid_move(ring, column, value)
place_value(ring, column, value)
clear_value(ring, column)
get_candidates(ring, column)
is_ring_complete(ring)
is_column_complete(column)
is_region_complete(region)
```

The engine must reject:

- values outside 1-9
- invalid Sudoku placements
- modifications to locked cells

---

# 5. Objective System

Objectives are divided into three groups:

```text
9 Rings
9 Columns
9 Regions
```

Total:

```text
27 objectives
```

## Completion

A structure becomes completed only when all 9 cells belonging to it are filled and valid.

For example:

```text
Ring 5 complete
```

counts as one objective.

When an objective is completed, its nine cells become permanently locked.

## Completed sets

The game state maintains:

```python
completed_rings
completed_columns
completed_regions
```

The total is:

```python
completed_objectives = (
    len(completed_rings)
    + len(completed_columns)
    + len(completed_regions)
)
```

Maximum:

```text
27
```

An already completed objective can never count again.

---

# 6. Climber

File:

```text
weboku/climber.py
```

## Responsibility

Represents the young man climbing the building.

The player does NOT directly control movement.

Movement is automatically determined by newly completed Ring and Column objectives.

## Starting position

The climber starts:

```text
BASE / FLOOR 9
```

## Position

A climbing junction is represented conceptually as:

```text
(ring, column)
```

Example:

```text
R5C2
```

The climber must not obscure Sudoku cells or symbols in the CLI.

The renderer should display the climber beside/near the junction.

## Movement rules

### Column completed first

If a Column completes while no Ring is active:

```text
stay at BASE
```

The newly completed Column becomes the active Column.

### Ring completed

If a new Ring completes and an active/latest Column exists:

```text
move to:
(new_ring, active_column)
```

### Column completed

If a current Ring exists and a new Column completes:

```text
move to:
(current_ring, new_column)
```

The newly completed Column becomes the active Column.

### Region completed

A Region completion does NOT move the climber.

## Examples

```text
C2 completed
→ BASE
```

Then:

```text
R5 completed
→ R5C2
```

Then:

```text
R4 completed
→ R4C2
```

Then:

```text
C1 completed
→ R4C1
```

Movement is deterministic.

The player cannot choose or teleport the destination.

---

# 7. Scoring

File:

```text
weboku/scoring.py
```

## Responsibility

Calculates score from valid player actions and game events.

The scoring system must not modify Sudoku validity.

## Symbol bonuses

The nine symbols map to values and bonuses:

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

Total symbol bonus:

```text
100
```

Internally the game uses values `1-9`.

The renderer converts values into symbols.

## Important

Symbol bonuses are awarded for valid Sudoku moves.

Movement does not receive symbol bonuses.

Backward/outward movement specifically does not receive symbol bonuses.

---

# 8. Timer

File:

```text
weboku/timer.py
```

## Responsibility

Tracks the time available for the current objective attempt.

There is no fixed total-game timer.

The timer measures the current attempt/window.

## Example difficulty values

```text
Beginner     10 minutes
Intermediate  5 minutes
Advanced      2 minutes
Pro           1 minute
```

## Success

A successful attempt is one where at least one NEW objective is completed.

On success:

```text
reset timer
```

## Timeout

If the timer expires before a new objective is completed:

```text
failed_timeouts += 1
```

No objective is awarded.

If the princess is alive, the timer resets for the next attempt.

If the princess dies, the timer stops permanently.

---

# 9. Princess Life

The princess begins with:

```text
27 / 27
```

life units.

Princess life is separate from the score.

## Timeout consequence

If a timeout occurs with no rescue credit:

```text
princess_life -= 1
```

If rescue credit is available:

```text
rescue_credits -= 1
```

and:

```text
princess_life
```

does not decrease.

Princess life is not normally restored by ordinary successful moves.

---

# 10. Rescue Credits

Rescue credits are earned from extra objective completions.

Suppose a single Sudoku move completes:

```text
3 new objectives
```

The first is the normal objective completion.

The additional two are extra completions.

Extra completions first compensate previously lost princess-life units.

Only remaining extras become rescue credits.

Example:

```text
Princess lost 2 life.
One move completes 3 new objectives.

1 normal objective
2 extra objectives

→ restore 2 lost life
→ 0 rescue credits
→ princess returns to 27/27
```

Another example:

```text
Princess lost 1 life.
One move completes 3 new objectives.

1 normal objective
2 extra objectives

→ restore 1 lost life
→ 1 rescue credit
```

If there are no lost life units to restore, extra objective completions become rescue credits.

---

# 11. Player

File:

```text
weboku/player.py
```

## Responsibility

Stores player-facing progression information.

The player controls Sudoku entries only.

The player does not control climber movement.

Player state should include information equivalent to:

```python
score
current_position
```

The complete game state remains owned by `Game`.

---

# 12. Renderer

File:

```text
weboku/renderer.py
```

## Responsibility

Converts game state into terminal output.

The Renderer must NOT contain Sudoku rules or game logic.

## Building

The CLI represents:

```text
9 floors
9 columns
81 cells
```

The building has:

- solid outer structure
- 9 large Sudoku windows
- double-solid borders around each window
- dotted/dashed divisions between the 9 panes inside each window
- flat roof
- princess above the roof

There must be exactly:

```text
9 windows
```

Each window contains:

```text
9 panes
```

The final display must not create 27 windows.

## Current position

The current climber position must never cover a Sudoku symbol.

The selected/current pane may be highlighted.

Example:

```text
CURRENT POSITION: R5C5
FLOOR: 5
COLUMN: 5
```

The climber should be rendered near the junction rather than inside the cell.

---

# 13. CLI

File:

```text
weboku/cli.py
```

## Responsibility

Handles user interaction.

The CLI:

- reads commands
- validates command syntax
- calls Game methods
- displays results

The CLI does NOT implement Sudoku rules.

## Commands

Required commands include:

```text
play
set <floor> <column> <symbol>
clear <floor> <column>
hint
hint <floor> <column>
status
save
load
help
quit
```

The CLI should also support:

```bash
python main.py --help
python main.py --demo
```

Invalid input must produce a readable error rather than crashing.

---

# 14. Game

File:

```text
weboku/game.py
```

## Responsibility

The Game is the central application/domain coordinator.

It connects:

```text
CLI
 ↓
Game
 ↓
SudokuEngine
 ↓
Board
 ↓
Game State
 ↓
Climber / Scoring / Timer
```

The Game owns the overall flow.

## Game state

Game state must contain information equivalent to:

```python
board
score
completed_rings
completed_columns
completed_regions
princess_life
rescue_credits
failed_timeouts
current_position
active_column
game_status
```

## Move flow

A player Sudoku move follows this general process:

```text
1. Receive player command
2. Validate coordinates
3. Validate value/symbol
4. Ask SudokuEngine whether move is valid
5. Reject invalid move
6. Apply valid move
7. Award move score
8. Apply symbol bonus
9. Detect newly completed Rings
10. Detect newly completed Columns
11. Detect newly completed Regions
12. Count only genuinely new objectives
13. Lock completed objectives
14. Apply objective scoring
15. Update automatic climber movement
16. Process timer/objective success
17. Check princess life
18. Check victory
19. Render updated state
```

Already completed objectives must not be counted again.

---

# 15. Victory Conditions

The game can only reach victory when ALL required conditions are satisfied:

```text
27/27 objectives completed
AND
princess is alive
AND
climber reaches the princess/roof
AND
player score reaches the required threshold
```

Marriage is the narrative ending after the victory conditions are satisfied.

---

# 16. Game Over

Game Over occurs when:

```text
princess_life == 0
```

The timer stops.

No further objective processing occurs.

The player cannot continue making scoring moves.

---

# 17. Save / Load

File:

```text
weboku/save_load.py
```

## Responsibility

Persists and restores game state.

Persistence may use JSON.

Saved state should preserve all information necessary to continue a game, including:

```text
board values
cell locked states
score
completed objectives
princess life
rescue credits
failed timeouts
climber position
active column
difficulty
game status
```

Save/load must not change game rules.

---

# 18. AI Master

File:

```text
weboku/ai_master.py
```

## Responsibility

Provides optional narration, dialogue, story presentation, or hints.

Ollama/LLM output is NOT authoritative game state.

The AI must never decide:

```text
whether a Sudoku move is valid
whether an objective is complete
whether the princess is alive
whether the player has won
the climber's actual position
the player's score
```

The deterministic Python engine decides those things.

AI output may explain what the engine has already decided.

---

# 19. Demo

File:

```text
weboku/demo.py
```

## Responsibility

Provides a deterministic complete-game demonstration.

The demo must use the actual Weboku engine.

It must not fake completion by simply printing success messages.

The demo should demonstrate:

```text
game start
partial Sudoku
valid moves
scoring
objective completion
cell locking
automatic movement
timer behavior
princess life
rescue credits
27/27 objectives
climber reaching the roof/princess
score threshold
victory
marriage ending
```

The demo is started with:

```bash
python main.py --demo
```

---

# 20. Main Entry Point

File:

```text
main.py
```

## Responsibility

Application entry point.

It should:

- parse command-line options
- launch normal CLI mode
- launch deterministic demo mode
- display help

Examples:

```bash
python main.py
```

```bash
python main.py --help
```

```bash
python main.py --demo
```

`main.py` must not contain the complete game logic.

---

# 21. Dependency Direction

The architecture follows:

```text
CLI
 ↓
Game / Application
 ↓
Domain
 ↓
Persistence / External Services
```

More specifically:

```text
CLI
 │
 ▼
Game
 │
 ├── SudokuEngine
 │     └── Board
 │          └── Cell
 │
 ├── Climber
 ├── Scoring
 ├── Timer
 ├── Player
 │
 ├── SaveLoad
 │
 └── AI Master
```

The renderer receives state and displays it.

The renderer must not become a second game engine.

---

# 22. Source of Truth

The deterministic Python engine is always authoritative.

Priority:

```text
Python Game State
        ↓
Domain Rules
        ↓
CLI / Renderer
        ↓
AI Narration
```

If AI output conflicts with game state, game state wins.

If CLI output conflicts with game state, game state wins.

---

# 23. Symbol Representation

The game internally stores:

```text
1 - 9
```

The CLI displays:

```text
1 → ●
2 → ■
3 → ▲
4 → ╱
5 → ◆
6 → ★
7 → ✚
8 → ○
9 → ♥
```

The mapping must remain consistent throughout the application.

---

# 24. Important Integration Rule

Team members must implement against these contracts.

They should NOT independently redefine:

- Sudoku rules
- objective rules
- movement rules
- princess life
- rescue credits
- symbol mapping
- game victory conditions
- CLI architecture

If an implementation detail needs to change, it must be agreed upon before changing the shared contract.
