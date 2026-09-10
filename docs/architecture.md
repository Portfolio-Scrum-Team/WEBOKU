# Weboku Architecture

## 1. Project Overview

Weboku is a Python command-line Sudoku adventure game.

The game combines a deterministic Sudoku engine with an automatic climbing
system, scoring, objectives, timer mechanics, princess life, rescue credits,
persistence, and optional AI narration.

The game is played entirely through the terminal.

The player does not manually control the young man's movement.

The player solves Sudoku cells, and the game engine automatically determines
when and where the young man climbs.

The main game flow is:

SOLVE → UNLOCK → CLIMB → REACH → MARRY

The young man begins at the base of the building.

The princess is positioned above the flat roof.

The player must complete the required Sudoku objectives, reach the princess,
and satisfy the final victory requirements.

---

## 2. Architectural Style

Weboku follows a layered architecture:

CLI → Game/Application → Domain → Persistence/API/External

The architecture separates presentation, game coordination, domain rules,
persistence, and external services.

The Python game engine is the source of truth.

The CLI displays game information and accepts player commands.

The domain layer contains the actual game rules.

The persistence layer stores and loads game state.

The AI layer provides optional narration and dialogue.

The AI must never become the authority for game state.

---

## 3. Architecture Layers

Weboku is divided into the following major layers:

1. CLI / Presentation
2. Application / Game
3. Domain
4. Persistence
5. External / AI services

The dependency direction is:

CLI
↓
Game/Application
↓
Domain
↓
Persistence / External

---

## 4. CLI / Presentation Layer

The CLI layer is responsible for interaction with the player.

Main modules:

- `main.py`
- `weboku/cli.py`
- `weboku/renderer.py`

The CLI is responsible for:

- displaying the game
- receiving commands
- parsing command input
- displaying errors
- displaying status
- displaying help
- requesting actions from the Game layer

The CLI must not contain:

- Sudoku validation rules
- objective completion rules
- scoring calculations
- timer rules
- princess life rules
- rescue-credit rules
- climber movement rules
- victory logic
- game-over logic

The CLI delegates these responsibilities to the Game/Application layer.

---

## 5. Application / Game Layer

The main application coordinator is:

`weboku/game.py`

The Game class coordinates the major game systems.

Responsibilities include:

- starting a game
- processing Sudoku moves
- communicating with the Sudoku engine
- processing newly completed objectives
- updating game state
- coordinating scoring
- coordinating timer behavior
- coordinating princess life
- coordinating rescue credits
- coordinating automatic climber movement
- checking victory
- checking game over
- coordinating save/load
- providing state to the CLI
- coordinating the overall game loop

The Game class coordinates domain objects but should not duplicate their
internal responsibilities.

---

## 6. Domain Layer

The domain layer contains the core Weboku game concepts.

Main modules:

- `board.py`
- `cell.py`
- `sudoku.py`
- `climber.py`
- `scoring.py`
- `timer.py`
- `levels.py`
- `player.py`

These modules contain deterministic game rules and data structures.

The domain layer must not depend on the CLI renderer.

The domain layer must not print terminal dashboards.

The domain layer must not require terminal input.

---

## 7. Board Architecture

Weboku represents the Sudoku puzzle as a 9 × 9 board.

The board contains:

- 9 floors/rings
- 9 columns
- 81 Sudoku cells
- 9 windows/regions

The internal board representation remains a standard 9 × 9 structure.

Each cell can be identified using:

`R1C1` through `R9C9`

The CLI presents floor/ring and column numbers using 1–9.

Internally, Python may use zero-based indexes.

---

## 8. Building Structure

The Sudoku board is represented visually as a tall building.

The building has:

- 9 floors/rings
- 9 columns
- 81 cells
- a flat roof
- a princess above the roof

The young man begins at the base outside Floor 9.

The building is not a GUI.

The structure is rendered in the terminal using text characters.

---

## 9. Sudoku Windows

There are exactly 9 Sudoku windows.

Each window contains exactly 9 cells.

Each window represents a standard 3 × 3 Sudoku region.

The window mapping is:

```text
Window 1: R1–R3, C1–C3
Window 2: R1–R3, C4–C6
Window 3: R1–R3, C7–C9

Window 4: R4–R6, C1–C3
Window 5: R4–R6, C4–C6
Window 6: R4–R6, C7–C9

Window 7: R7–R9, C1–C3
Window 8: R7–R9, C4–C6
Window 9: R7–R9, C7–C9
```
