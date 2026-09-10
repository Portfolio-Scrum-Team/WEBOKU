# Weboku Game Rules

## 1. Game Objective

Weboku is a CLI-based Sudoku adventure game built around a tall building.

The building contains:

- 9 floors/rings
- 9 columns
- 81 Sudoku cells
- 9 Sudoku windows/regions

A young man begins at the base of the building and automatically climbs toward a princess waiting on the flat roof.

The player does not directly control the climber.

The player's primary action is solving Sudoku.

The overall game flow is:

```text
SOLVE → UNLOCK → CLIMB → REACH → MARRY
```

The final objective is to:

1. Complete all 27 Sudoku objectives.
2. Keep the princess alive.
3. Automatically move the climber to the roof.
4. Reach the princess.
5. Reach the required score threshold.
6. Complete the marriage ending.

---

# 2. Building Structure

The Weboku building contains exactly:

```text
9 floors × 9 columns = 81 cells
```

The nine floors/rings are numbered:

```text
Floor 1
Floor 2
Floor 3
Floor 4
Floor 5
Floor 6
Floor 7
Floor 8
Floor 9
```

The nine columns are numbered:

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

Internally, Python uses zero-based indexes:

```text
ring:   0–8
column: 0–8
```

The CLI displays:

```text
floor/ring: 1–9
column:     1–9
```

The building has a flat roof.

The princess is positioned above the roof and is not part of the Sudoku board.

---

# 3. Sudoku Structure

Weboku follows standard 9×9 Sudoku rules.

Every completed:

- Ring/Floor
- Column
- Window/Region

must contain the values:

```text
1–9 exactly once
```

The board is represented internally as:

```python
board[ring][column]
```

There are exactly:

```text
81 playable cells
```

---

# 4. Sudoku Windows

There are exactly 9 Sudoku windows.

Each window contains exactly 9 cells.

The windows correspond to the standard 3×3 Sudoku regions.

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

There must never be 27 windows.

There are exactly:

```text
9 windows
9 panes per window
81 panes/cells total
```

---

# 5. Cell Values and Symbols

The Sudoku engine stores values internally as integers:

```text
1–9
```

The CLI displays the values using nine unique symbols.

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

The total possible symbol bonus across the nine values is:

```text
100
```

Symbols are a presentation layer.

The game engine continues to work with integer values `1–9`.

---

# 6. Sudoku Moves

The player solves the Sudoku by entering values into empty cells.

The player may enter a value only when:

- the floor/ring is valid
- the column is valid
- the value is between 1 and 9
- the move does not violate Sudoku rules
- the cell is not locked

Invalid moves must be rejected without crashing the game.

A valid move may result in:

- a normal score increase
- a symbol bonus
- one or more newly completed objectives
- cell locking
- automatic climber movement
- timer reset
- rescue-credit processing
- victory checking

---

# 7. Objective System

Weboku has exactly:

```text
27 objectives
```

The objectives consist of:

```text
9 Ring objectives
9 Column objectives
9 Window/Region objectives
```

Therefore:

```text
9 + 9 + 9 = 27
```

An objective is counted only when its complete set of nine cells is filled correctly.

---

# 8. Ring Objectives

There are 9 Ring/Floor objectives:

```text
Ring 1
Ring 2
Ring 3
Ring 4
Ring 5
Ring 6
Ring 7
Ring 8
Ring 9
```

A Ring objective is completed when all nine cells in that ring contain:

```text
1–9 exactly once
```

Once completed:

- the Ring objective is permanently marked complete
- its nine cells become locked
- it cannot be counted again

---

# 9. Column Objectives

There are 9 Column objectives:

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

A Column objective is completed when all nine cells in that column contain:

```text
1–9 exactly once
```

Once completed:

- the Column objective is permanently marked complete
- its nine cells become locked
- it cannot be counted again

---

# 10. Window/Region Objectives

There are 9 Window/Region objectives.

A Window is complete when all nine cells inside that window contain:

```text
1–9 exactly once
```

Once completed:

- the Window objective is permanently marked complete
- its nine cells become locked
- it cannot be counted again

Window completion does not directly move the climber.

---

# 11. Completed Objective Tracking

The game maintains separate sets:

```python
completed_rings
completed_columns
completed_regions
```

The total number of completed objectives is:

```python
completed_objectives = (
    len(completed_rings)
    + len(completed_columns)
    + len(completed_regions)
)
```

The valid range is:

```text
0–27
```

The game must never report:

```text
28/27
```

or any value greater than 27.

An objective that was already completed cannot become a new objective again.

If one Sudoku move completes multiple structures, only genuinely uncompleted structures count.

---

# 12. Cell Locking

When an objective becomes complete, all nine cells belonging to that objective become permanently locked.

A locked cell:

- remains visible
- keeps its value
- cannot be edited
- cannot be cleared
- cannot be counted as newly completed again

A cell may belong simultaneously to:

- one Ring
- one Column
- one Window

Therefore, completing any one of those objectives can cause the cell to become locked.

The game must preserve the locked state when saving and loading.

---

# 13. Young Man / Climber

The player character is a young man who climbs the building toward the princess.

The climber:

- starts at the base
- does not occupy a Sudoku cell
- does not obscure Sudoku values
- moves automatically
- cannot be manually controlled
- cannot be teleported by the player

The climber represents the player's progress through completed Sudoku objectives.

---

# 14. Starting Position

The climber starts at:

```text
BASE / FLOOR 9
```

Before a Ring has been completed, there is no active Ring position.

A completed Column by itself does not move the climber from the base.

---

# 15. Active Column

The latest newly completed Column becomes the active Column.

The active Column is used when the climber moves between Rings.

For example:

```text
Column 2 completed
```

means:

```text
Active Column = Column 2
```

If Ring 5 is subsequently completed, the climber moves to:

```text
R5C2
```

---

# 16. Automatic Movement

Movement is deterministic.

The player only solves Sudoku.

The game engine determines the climber's destination from newly completed Ring and Column objectives.

The player cannot choose the movement destination.

---

# 17. Column Completed Before Any Ring

If a Column is completed while there is no current Ring:

```text
C2 completed
```

the climber remains:

```text
BASE
```

The completed Column becomes the active Column.

Example:

```text
BASE
+
C2 completed
=
BASE / Active Column C2
```

---

# 18. Ring Completion

When a new Ring is completed and an active Column exists:

```text
new position = (new Ring, active Column)
```

Example:

```text
Active Column = C2
Ring 5 completed
```

The climber moves:

```text
BASE → R5C2
```

If another Ring is completed:

```text
Ring 4 completed
```

the climber moves:

```text
R5C2 → R4C2
```

---

# 19. Column Completion After a Ring

When a new Column is completed and the climber has a current Ring:

```text
new position = (current Ring, new Column)
```

Example:

```text
Current position = R4C2
Column 1 completed
```

The climber moves:

```text
R4C2 → R4C1
```

Column 1 then becomes the active Column.

---

# 20. Region Completion and Movement

Completing a Window/Region does not directly move the climber.

For example:

```text
Window 5 completed
```

may award objective points and lock its cells, but does not independently select a movement destination.

Movement is driven by Ring and Column completion events.

---

# 21. Forward/Inward Movement

When a newly completed Ring represents forward/inward progression according to the current game position, the climber receives the applicable movement reward.

Example:

```text
R5 → R4
```

The exact movement reward is controlled by the scoring implementation.

Forward/inward movement may provide escalating movement points.

A provisional example is:

```text
+10
+15
+20
+25
+30
```

The final numerical balance may be adjusted during playtesting.

---

# 22. Non-Consecutive Ring Movement

The player may complete a Ring that is not the immediately next Ring in the progression.

For example:

```text
R6 → R3
```

The climber still moves automatically to the deterministic junction.

The movement reward is lower than the preferred consecutive progression reward.

The exact numerical value is controlled by the scoring implementation.

---

# 23. Backward/Outward Movement

A newly completed Ring may cause movement in the opposite direction from the climber's current progression.

Backward/outward movement:

- still moves the climber
- still receives applicable Ring completion points
- uses the deterministic movement algorithm
- does not receive a symbol bonus for the movement
- may receive a reduced or inverted movement increment

Backward movement does not allow reward farming because completed objectives cannot be completed again.

---

# 24. Sideways Movement

When a new Column is completed while the climber has a current Ring:

```text
current Ring remains unchanged
new Column becomes active
```

Example:

```text
R4C2 → R4C1
```

Sideways movement is neutral with respect to princess life.

It may award a smaller movement score.

The exact numerical reward is controlled by the scoring implementation.

---

# 25. Climber Rendering

The climber must never cover a Sudoku cell, symbol, or value.

The renderer should show the climber:

- beside the relevant junction
- near the relevant position
- or adjacent to the building structure

The current position should also be displayed separately.

Example:

```text
CURRENT POSITION: R5C2
FLOOR: 5
COLUMN: 2
ACTIVE COLUMN: C2
```

The cell itself remains completely readable.

---

# 26. Princess

The princess waits above the flat roof of the building.

She is not part of the Sudoku board.

She has:

```text
27 / 27
```

life units at the beginning of the game.

Princess life is independent from player score.

---

# 27. Timer

The game does not use one fixed timer for the entire game.

Instead, the timer measures the current objective attempt/window.

Example difficulty settings:

```text
Beginner      10 minutes
Intermediate   5 minutes
Advanced       2 minutes
Pro            1 minute
```

These values may be tuned during playtesting.

---

# 28. Successful Objective Attempt

A timer attempt is successful when at least one genuinely new objective is completed during that attempt.

On successful completion:

```text
timer resets
```

The reset occurs even if the move completes:

```text
1 new objective
```

or:

```text
2 or 3 new objectives
```

Only genuinely new objectives count.

Already completed objectives do not cause another successful attempt.

---

# 29. Timeout

If the timer expires before a new objective is completed:

```text
failed_timeouts += 1
```

The timeout does not count as an objective.

If the princess is still alive, the timer resets for another attempt.

If the princess reaches zero life, the timer stops and the game ends.

---

# 30. Princess Life and Timeout

When a timeout occurs with no rescue credit available:

```text
princess_life -= 1
```

Exactly one life unit is lost.

Example:

```text
27/27 → 26/27
```

The loss is permanent unless later compensated by extra objective completions.

---

# 31. Rescue Credits

Rescue credits protect the princess from future timeout damage.

If a timeout occurs and the player has a rescue credit:

```text
rescue_credits -= 1
```

The princess does not lose life.

Example:

```text
Princess: 26/27
Rescue Credits: 1

Timeout

Princess: 26/27
Rescue Credits: 0
```

---

# 32. Extra Objective Completions

A single Sudoku move may complete multiple genuinely new objectives.

The first newly completed objective is the normal objective completion.

Additional newly completed objectives are extra completions.

Extra completions first compensate previously lost princess life.

Any remaining extra completions become rescue credits.

---

# 33. Rescue Example

Suppose:

```text
Princess life = 25/27
Rescue Credits = 0
```

The player makes one move that completes:

```text
3 new objectives
```

Processing:

```text
1 objective = normal completion
2 objectives = extra completions
```

The two extras restore the two lost life units:

```text
Princess life = 27/27
Rescue Credits = 0
```

---

# 34. Rescue Credit Example

Suppose:

```text
Princess life = 26/27
Rescue Credits = 0
```

One move completes:

```text
3 new objectives
```

Processing:

```text
1 objective = normal completion
2 objectives = extras
```

One extra restores the lost life.

The remaining extra becomes:

```text
Rescue Credits = 1
```

Final state:

```text
Princess life = 27/27
Rescue Credits = 1
```

---

# 35. No Lost Life to Restore

If the princess is already at:

```text
27/27
```

and one move completes multiple new objectives, all extra completions beyond the normal objective become rescue credits.

Example:

```text
3 new objectives

1 normal objective
2 extra objectives

→ 2 rescue credits
```

---

# 36. Princess Death

If princess life reaches:

```text
0/27
```

the game immediately enters:

```text
GAME OVER
```

The timer stops.

No additional objective processing occurs.

The player cannot continue making scoring moves.

Victory is impossible after princess death.

---

# 37. Scoring

Score can come from:

- valid Sudoku moves
- symbol bonuses
- completed Ring objectives
- completed Column objectives
- completed Window objectives
- automatic climber movement
- applicable final bonuses
- unused rescue credits when converted at the end

The scoring system must not determine Sudoku validity.

---

# 38. Base Sudoku Move Score

A valid Sudoku move receives the configured base move reward.

The base value may be tuned during balancing.

The symbol bonus is added separately.

Invalid moves receive no normal move reward.

---

# 39. Symbol Bonus

A valid move using a symbol receives its corresponding symbol bonus.

```text
1 → ● → +2
2 → ■ → +4
3 → ▲ → +6
4 → ╱ → +8
5 → ◆ → +10
6 → ★ → +12
7 → ✚ → +14
8 → ○ → +18
9 → ♥ → +26
```

Movement never receives a symbol bonus.

---

# 40. Objective Completion Score

Completing a new objective awards the configured objective-completion score.

Objective scoring applies only to genuinely new objectives.

An already completed Ring, Column, or Window does not award the completion score again.

The exact objective score may be tuned during balancing.

---

# 41. Rescue Credit Final Conversion

Unused rescue credits may be converted into final score when the game reaches its final scoring stage.

A provisional conversion is:

```text
1 rescue credit = +100 points
```

The exact value may be tuned during playtesting.

---

# 42. Score Threshold

Victory requires the player to reach the configured score threshold.

The threshold is part of the game configuration.

The final numerical threshold may be adjusted during balancing.

Reaching 27/27 objectives alone is not sufficient if the score threshold has not been reached.

---

# 43. Victory Conditions

The player wins only when all of the following are true:

```text
27/27 objectives completed
AND
princess life > 0
AND
climber reaches the roof/princess
AND
score >= required score threshold
```

Once these conditions are satisfied, the game enters the victory state.

The narrative ending is:

```text
The young man reaches the princess.
They meet on the roof.
The rescue is complete.
They marry.
```

---

# 44. Game State

The central Game object maintains the authoritative state.

The state includes information equivalent to:

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
difficulty
```

The state must remain deterministic.

---

# 45. Game Move Processing

A valid player move follows this general sequence:

```text
1. Receive Sudoku input.
2. Validate floor/ring and column.
3. Convert symbol to internal value.
4. Ask SudokuEngine to validate the move.
5. Reject invalid moves.
6. Apply the valid value.
7. Award the base move score.
8. Award the symbol bonus.
9. Detect newly completed Rings.
10. Detect newly completed Columns.
11. Detect newly completed Windows.
12. Count only genuinely new objectives.
13. Lock completed objective cells.
14. Award objective-completion points.
15. Process automatic climber movement.
16. Process extra objective completions.
17. Process timer success/reset.
18. Check princess life.
19. Check victory.
20. Render the updated state.
```

---

# 46. Deterministic Movement

Movement must be deterministic.

The same game state and same newly completed objective event must always produce the same climber destination.

The player cannot:

- choose a destination
- manually move the climber
- teleport the climber
- repeat a completed objective to farm movement rewards

---

# 47. No Reward Farming

A completed objective is permanently completed.

Therefore:

```text
Ring completion
Column completion
Window completion
```

can each award their completion reward only once.

Movement is triggered only by newly completed Ring/Column objectives.

This prevents repeated movement or score farming.

---

# 48. CLI Rules

Weboku is a terminal/CLI game.

The CLI must:

- display the building
- display the Sudoku cells
- display objective progress
- display princess life
- display rescue credits
- display score
- display timer
- display climber position
- accept Sudoku commands
- report errors clearly

The CLI must not contain Sudoku validation logic.

---

# 49. Building Display

The terminal representation should visually communicate:

```text
             PRINCESS
          ─────────────
             FLAT ROOF
        ╔═══════════════════╗
        ║   SUDOKU WINDOW   ║
        ║                   ║
        ║   9 WINDOWS       ║
        ║   81 CELLS        ║
        ║                   ║
        ╚═══════════════════╝
             BASE
```

The final renderer should use:

- solid outer building lines
- double-solid borders around the 9 windows
- dotted/dashed lines inside windows
- clear floor and column alignment

There must be exactly 9 windows.

---

# 50. Current Position Display

The current position must be displayed separately from the Sudoku cell.

Example:

```text
CURRENT POSITION
R5C5
FLOOR 5
COLUMN 5
ACTIVE COLUMN C5
```

The climber may be visually positioned beside the junction.

The climber must never cover a Sudoku value.

---

# 51. Invalid Input

Invalid commands and values must not crash the application.

Examples include:

```text
invalid floor
invalid column
invalid symbol
attempt to modify locked cell
invalid Sudoku value
unknown command
```

The CLI should display a clear error and allow the player to continue.

---

# 52. Save and Load

The game may persist state using JSON.

A saved game should preserve enough state to continue correctly, including:

```text
board values
locked cells
score
completed Rings
completed Columns
completed Windows
princess life
rescue credits
failed timeouts
current climber position
active Column
difficulty
game status
```

Loading a game must restore the same deterministic game state.

---

# 53. AI Master

The AI Master may provide:

- narration
- dialogue
- hints
- story descriptions
- contextual explanations

The AI does not control game truth.

The AI must never independently decide:

```text
whether a Sudoku move is valid
whether an objective is complete
the player's score
princess life
the climber's actual position
whether the player has won
```

The deterministic Python engine remains authoritative.

If AI output conflicts with the engine state:

```text
ENGINE STATE WINS
```

---

# 54. Demo

The project must provide a deterministic complete-game demonstration.

Run:

```bash
python main.py --demo
```

The demo must use the actual game engine.

It must not fake success by merely printing messages.

The demo should demonstrate:

```text
game start
partial Sudoku
valid Sudoku moves
scoring
objective completion
cell locking
automatic movement
timer behavior
timeout behavior
princess life
rescue credits
27/27 objectives
climber reaching the roof
score threshold
victory
marriage ending
```

---

# 55. Game Status

The game should expose a clear status such as:

```text
READY
PLAYING
VICTORY
GAME_OVER
```

The exact internal representation may be implemented using an Enum.

The status must be deterministic and serializable.

---

# 56. Source of Truth

The deterministic Python engine is the single source of truth.

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

The responsibility boundaries are:

```text
SudokuEngine
→ Sudoku rules

Game
→ Overall game flow and state

Climber
→ Automatic movement

Scoring
→ Score calculations

Timer
→ Attempt timing

SaveLoad
→ Persistence

AI Master
→ Narration/hints

Renderer
→ Terminal presentation

CLI
→ Player interaction
```

No presentation component should become a second game engine.

---

# 57. Final Game Flow

The complete Weboku experience is:

```text
START
  ↓
SOLVE SUDOKU
  ↓
COMPLETE OBJECTIVE
  ↓
UNLOCK CELLS
  ↓
UPDATE SCORE
  ↓
AUTOMATIC CLIMBER MOVEMENT
  ↓
RESET OBJECTIVE TIMER
  ↓
CONTINUE SOLVING
  ↓
27/27 OBJECTIVES
  ↓
CLIMBER REACHES ROOF
  ↓
PRINCESS REMAINS ALIVE
  ↓
SCORE THRESHOLD REACHED
  ↓
VICTORY
  ↓
PRINCESS + YOUNG MAN
  ↓
MARRIAGE
```

If the timer expires:

```text
TIMEOUT
  ↓
NO NEW OBJECTIVE
  ↓
FAILED TIMEOUT +1
  ↓
USE RESCUE CREDIT?
  ├── YES → consume credit → princess life unchanged
  └── NO  → princess loses 1 life
  ↓
PRINCESS ALIVE?
  ├── YES → reset timer → continue
  └── NO  → GAME OVER
```

---

# 58. Rule Change Policy

These rules are the authoritative Weboku game rules for implementation.

Team members must not independently redefine:

- board structure
- Sudoku rules
- window mapping
- symbol mapping
- objective counting
- cell locking
- climber movement
- princess life
- rescue credits
- timer behavior
- victory conditions

If a rule needs to change, the team must agree on the change and update the relevant documentation before implementation diverges.
