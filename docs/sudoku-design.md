# Weboku Sudoku Design

## 1. Purpose

The Sudoku engine is the deterministic core of Weboku.

It is responsible for:

- Representing the 81 Sudoku cells.
- Storing cell values.
- Identifying rings.
- Identifying columns/sectors.
- Identifying Sudoku regions.
- Validating moves.
- Calculating candidates.
- Detecting completed structures.
- Solving Sudoku puzzles.
- Providing reliable Sudoku state to the game engine.

The Sudoku engine must not control:

- Spider movement.
- Player health.
- Scoring.
- Timer behavior.
- CLI rendering.
- AI-generated explanations.

Those responsibilities belong to other components.

---

## 2. Board Geometry

The physical Weboku board is a regular nonagon/spider-web structure.

It contains exactly:

- 9 rings
- 9 columns/sectors
- 81 playable cells

The center is empty.

The center is NOT a Sudoku cell.

Each cell is located at the intersection of:

- One ring.
- One column/sector.

Therefore:

    9 rings × 9 columns = 81 cells

---

## 3. Internal Representation

The Sudoku engine uses a 9×9 logical representation.

The recommended structure is:

    board[ring][column]

The internal indexes may use Python's zero-based indexing:

    board[0][0] → Ring 1, Column 1
    board[0][1] → Ring 1, Column 2
    board[8][8] → Ring 9, Column 9

The presentation layer converts these positions into the circular
nonagon geometry.

The Sudoku engine does not need to know how the board is drawn.

---

## 4. Cell

Each playable position is represented by a Cell object.

A Cell should contain information such as:

- Ring index.
- Column index.
- Current value.
- Whether the value is a fixed puzzle clue.
- Whether the cell has been solved by the player.

Example conceptual interface:

    Cell(
        ring=1,
        column=1,
        value=5,
        fixed=False
    )

The exact implementation is owned by the Sudoku subsystem.

---

## 5. Values

The Sudoku engine stores values as integers:

    1
    2
    3
    4
    5
    6
    7
    8
    9

An empty cell is represented internally as:

    0

or another clearly defined empty-value representation.

The engine must use one representation consistently.

Fruit emojis are NOT stored as the cell's primary value.

The CLI is responsible for converting numbers to fruit symbols.

---

## 6. Fruit Mapping

The presentation layer uses the following mapping:

| Number | Symbol | Name       |
| -----: | ------ | ---------- |
|      1 | 🍎     | Apple      |
|      2 | 🍌     | Banana     |
|      3 | 🍉     | Watermelon |
|      4 | 🍇     | Grapes     |
|      5 | 🍆     | Eggplant   |
|      6 | 🥭     | Mango      |
|      7 | 🍒     | Cherries   |
|      8 | 🍑     | Peach      |
|      9 | 🍍     | Pineapple  |

The Sudoku engine should continue working with numeric values.

---

## 7. Rings

The 9 concentric rings correspond to the 9 Sudoku rows.

They are numbered:

    Ring 1
    Ring 2
    Ring 3
    Ring 4
    Ring 5
    Ring 6
    Ring 7
    Ring 8
    Ring 9

Each ring contains exactly 9 cells.

Example:

    Ring 1:
    C1 C2 C3 C4 C5 C6 C7 C8 C9

A ring is complete when it contains every value from 1 through 9
exactly once.

---

## 8. Columns / Sectors

The 9 radial sectors correspond to the 9 Sudoku columns.

They are numbered:

    Column 1
    Column 2
    ...
    Column 9

Each column contains exactly 9 cells.

A column is complete when it contains every value from 1 through 9
exactly once.

---

## 9. Sudoku Regions

The board contains 9 Sudoku regions.

The regions are created using groups of three rings and three columns.

Ring groups:

    Rings 1–3
    Rings 4–6
    Rings 7–9

Column groups:

    Columns 1–3
    Columns 4–6
    Columns 7–9

The resulting regions are:

    Region 1 = Rings 1–3, Columns 1–3
    Region 2 = Rings 1–3, Columns 4–6
    Region 3 = Rings 1–3, Columns 7–9

    Region 4 = Rings 4–6, Columns 1–3
    Region 5 = Rings 4–6, Columns 4–6
    Region 6 = Rings 4–6, Columns 7–9

    Region 7 = Rings 7–9, Columns 1–3
    Region 8 = Rings 7–9, Columns 4–6
    Region 9 = Rings 7–9, Columns 7–9

Each region contains exactly 9 cells.

Each region must contain values 1 through 9 exactly once when complete.

---

## 10. Coordinate Conversion

Game-level coordinates use:

    Ring 1–9
    Column 1–9

Python array coordinates may use:

    0–8

The Sudoku subsystem must handle this conversion consistently.

Example:

    Game coordinate:
    Ring 3, Column 5

    Python coordinate:
    board[2][4]

The CLI should not directly manipulate zero-based internal indexes.

---

## 11. Move Validation

Before accepting a player move, the Sudoku engine must verify:

1. The selected ring exists.
2. The selected column exists.
3. The cell is playable.
4. The cell is not a fixed clue.
5. The value is between 1 and 9.
6. The value does not duplicate another value in the ring.
7. The value does not duplicate another value in the column.
8. The value does not duplicate another value in the region.

A valid move may update the board.

An invalid move must not modify the board.

---

## 12. Candidate Calculation

For an empty cell, candidates are calculated using:

    candidates =
        missing values in ring
        ∩ missing values in column
        ∩ missing values in region

Example:

If:

    Ring missing = {2, 5, 7}
    Column missing = {1, 5, 7}
    Region missing = {3, 5, 7}

Then:

    candidates = {5, 7}

The AI may use candidate information to explain hints, but the
candidate calculation must come from the deterministic Sudoku engine.

---

## 13. Completion Detection

The engine must be able to determine whether a:

- Ring is complete.
- Column is complete.
- Region is complete.
- Entire Sudoku puzzle is complete.

A structure is complete when:

- It contains 9 filled cells.
- Its values are exactly 1 through 9.
- No duplicates exist.

Completion detection should return deterministic results.

---

## 14. Completion Events

The Sudoku engine should expose enough information for the game engine
to detect newly completed structures.

For example:

    completed_ring = 5

or:

    completed_column = 3

or:

    completed_region = 7

The Sudoku engine reports the completion.

The game engine decides what gameplay effect should happen.

For example:

    Sudoku Engine:
    "Ring 5 completed."

    Game Engine:
    "Move spider to Ring 5."

The Sudoku engine must not directly move the spider.

---

## 15. Solved Puzzle

The Sudoku engine should support a deterministic solved board.

A solved board contains:

- 9 valid rings.
- 9 valid columns.
- 9 valid regions.
- Every value from 1 through 9 exactly once in each structure.

The solver may use a backtracking algorithm.

The solver must never produce an invalid Sudoku solution.

---

## 16. Puzzle Generation

Puzzle generation may be implemented using a valid solved board followed
by controlled removal of values.

Generated puzzles must always have a valid solution.

Difficulty should be configurable.

Possible difficulty factors include:

- Number of clues.
- Required deduction patterns.
- Candidate complexity.
- Time pressure.

The project should not assume that fewer clues automatically means a
better or harder level.

---

## 17. Fixed Clues

Initial puzzle clues are fixed.

A player must not be allowed to overwrite a fixed clue.

Player-entered values may be changed or removed according to the CLI
rules defined by the game.

---

## 18. Undo / Correction

If supported by the game, the Sudoku engine may allow the player to
remove or replace a previously entered value.

Removing a player-entered value must not remove a fixed puzzle clue.

Any correction must still leave the board in a valid Sudoku state.

---

## 19. Sudoku Engine Interface

The Sudoku subsystem should expose a clean interface to the game layer.

Conceptually:

    SudokuEngine

    load_puzzle()
    get_cell()
    set_value()
    clear_value()
    validate_move()
    get_candidates()
    is_ring_complete()
    is_column_complete()
    is_region_complete()
    is_complete()
    solve()

The exact method signatures will be agreed before implementation.

---

## 20. Separation of Responsibilities

The Sudoku engine owns:

    Cell
    Board
    Sudoku validation
    Candidates
    Solver
    Completion detection

The Sudoku engine does NOT own:

    Spider
    Player health
    Score
    Timer
    CLI
    Ollama
    Save/load system

This separation keeps the system modular and testable.

---

## 21. Testing Requirements

The Sudoku subsystem must have tests for:

- Cell creation.
- Board creation.
- 81-cell count.
- Ring lookup.
- Column lookup.
- Region lookup.
- Valid moves.
- Invalid moves.
- Duplicate detection.
- Candidate calculation.
- Ring completion.
- Column completion.
- Region completion.
- Full puzzle completion.
- Solver correctness.
- Fixed clue protection.

At minimum, the Sudoku tests must verify that a valid Sudoku solution
satisfies all 9 rings, all 9 columns and all 9 regions.

---

## 22. Weboku Geometry and Sudoku Logic

The visual board may look like a circular staircase, spider web or
nonagon.

The underlying Sudoku mathematics remains a 9×9 logical structure.

Therefore:

    Visual Geometry
          ↓
    Ring × Column coordinates
          ↓
    9×9 Sudoku representation
          ↓
    Sudoku validation
          ↓
    Game events

The visual renderer must not change the Sudoku rules.

---

## 23. Source of Truth

The Sudoku engine is the authoritative source for Sudoku state.

The CLI displays Sudoku state.

The game engine reacts to Sudoku completion events.

The AI may explain Sudoku state.

The AI must never override the Sudoku engine.

Therefore:

    Sudoku Engine = Truth
    CLI = Presentation
    Game Engine = Gameplay
    AI = Explanation / Assistance
