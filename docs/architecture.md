# Weboku Architecture

## 1. Architecture Goal

Weboku is a CLI-only Python application.

The architecture separates:

- User interaction
- Application/game flow
- Domain/game logic
- Persistence
- AI assistance

The goal is to keep business rules independent from the CLI and
external services.

---

## 2. Layered Architecture

The main architecture is:

    CLI
      ↓
    Application / Game Service
      ↓
    Domain
      ↓
    Repository / External Services

The main flow is:

    Player
      ↓
    CLI
      ↓
    Game
      ↓
    Sudoku / Spider / Scoring / Timer
      ↓
    Save Repository / AI Service

---

## 3. CLI Layer

The CLI is responsible for:

- Displaying menus.
- Reading user input.
- Validating basic input format.
- Displaying the board.
- Displaying status information.
- Displaying errors.
- Displaying game events.
- Displaying help.
- Starting demo mode.

The CLI must NOT contain core game rules.

The CLI should call application/game services instead of directly
changing domain state.

Primary component:

    cli.py

Supporting presentation component:

    renderer.py

---

## 4. Application / Game Layer

The game layer coordinates the overall gameplay.

Primary component:

    game.py

Responsibilities include:

- Starting a game.
- Processing player actions.
- Coordinating Sudoku validation.
- Detecting completed structures.
- Triggering spider movement.
- Updating score.
- Updating health.
- Updating timer state.
- Checking win conditions.
- Checking lose conditions.
- Coordinating level progression.
- Coordinating demo mode.

The game layer coordinates domain objects.

It should not contain CLI rendering code.

---

## 5. Domain Layer

The domain contains the actual Weboku rules.

Main components:

    cell.py
    board.py
    sudoku.py
    spider.py
    player.py
    scoring.py
    timer.py
    levels.py

These components represent the game's state and rules.

---

## 6. Sudoku Domain

The Sudoku subsystem owns:

    Cell
    Board
    SudokuEngine

Responsibilities:

- 81-cell representation.
- Ring management.
- Column management.
- Region management.
- Move validation.
- Candidate calculation.
- Completion detection.
- Sudoku solving.

The Sudoku subsystem is the source of truth for Sudoku validity.

It must not directly control the spider.

---

## 7. Spider Domain

The Spider component owns:

    Spider

Responsibilities:

- Spider position.
- Ring position.
- Column position.
- Health.
- Movement state.

Movement rules are coordinated with the game engine.

The spider does not modify Sudoku cells.

---

## 8. Player Domain

The Player component represents the human player.

Possible state includes:

- Player name.
- Score.
- Current level.
- Progress.

The Player object does not directly control the Sudoku board.

---

## 9. Scoring Domain

The scoring subsystem calculates rewards.

It handles:

- Ring completion rewards.
- Column completion rewards.
- Region completion rewards.
- Forward movement rewards.
- Sideways movement rewards.
- Backward movement rewards.
- Other configured bonuses.

The scoring system should not render output.

---

## 10. Timer Domain

The timer subsystem handles:

- Countdown state.
- Time remaining.
- Expiration detection.
- Level-specific time limits.

The timer does not decide what the player sees.

The CLI displays timer information.

---

## 11. Level Configuration

The level subsystem stores configurable difficulty information.

Possible level settings include:

- Sudoku puzzle.
- Initial clues.
- Time limit.
- Health configuration.
- Scoring configuration.
- Difficulty settings.

Different levels should be data-driven where practical.

---

## 12. Persistence Layer

Persistence is handled by:

    save_load.py

The persistence layer is responsible for:

- Saving game state.
- Loading game state.
- JSON serialization.
- JSON deserialization.
- Validating loaded state.

The save system should not contain game rules.

The game engine remains responsible for interpreting loaded state.

---

## 13. AI Service

AI assistance is handled by:

    ai_master.py

The AI service may communicate with Ollama.

The AI can provide:

- Sudoku hints.
- Warnings.
- Explanations.
- Gameplay guidance.

The AI must NOT:

- Validate Sudoku moves.
- Modify Sudoku state.
- Modify spider state.
- Modify health.
- Modify score.
- Decide whether the player wins.

Python game logic is always authoritative.

---

## 14. Demo System

The demo system provides:

    python main.py --demo

The demo should use:

    demo.py

The demo provides deterministic game data and a predetermined
successful sequence.

The demo must use the same game engine and domain rules as normal
gameplay.

The demo must not simply print a fake victory screen.

---

## 15. Main Entry Point

The application starts through:

    main.py

Responsibilities:

- Parse command-line arguments.
- Start normal CLI mode.
- Start demo mode.
- Display help.
- Pass control to the appropriate application service.

`main.py` should remain small.

It should not contain the actual Sudoku or spider logic.

---

## 16. Component Ownership

### Richie — Game Architect / Lead

Primary ownership:

    main.py
    game.py

Responsible for:

- Game rules.
- Overall game flow.
- Sudoku interaction design.
- CLI behavior specification.
- Game-state coordination.
- Integration.
- Demo integration.
- Final presentation.

---

### Sharlmon — Sudoku Engine

Primary ownership:

    cell.py
    board.py
    sudoku.py

Responsible for:

- Cell implementation.
- Board implementation.
- Region mapping.
- Sudoku validation.
- Candidate calculation.
- Sudoku solver.
- Completion detection.
- Sudoku tests.

---

### Tracy — Spider & Game Mechanics

Primary ownership:

    spider.py
    scoring.py
    timer.py
    levels.py

Responsible for:

- Spider.
- Forward movement.
- Backward movement.
- Sideways movement.
- Active column.
- Health.
- Fruit energy.
- Scoring.
- Timer.
- Level configuration.

---

### Nicole — CLI & Player Experience

Primary ownership:

    cli.py
    renderer.py
    player.py

Responsible for:

- CLI framework.
- Menus.
- Commands.
- Input handling.
- Board rendering.
- Completion visualization.
- Spider visualization.
- HUD.
- Progress bars.
- Event messages.
- Help screen.
- Player state.

---

### Alvin — AI, Persistence & Testing

Primary ownership:

    ai_master.py
    save_load.py
    tests/

Responsible for:

- JSON persistence.
- Ollama integration.
- AI hints.
- AI warnings.
- AI safety boundary.
- Persistence tests.
- AI tests.
- Integration testing coordination.
- Development setup documentation.

---

## 17. Communication Between Components

The components communicate through Python objects and clearly defined
interfaces.

Example player move:

    CLI
      ↓
    Game
      ↓
    SudokuEngine.validate_move()
      ↓
    SudokuEngine.set_value()
      ↓
    Game checks completion
      ↓
    Spider / Scoring updated
      ↓
    Renderer displays result

---

## 18. Sudoku Completion Flow

Example:

    Player enters value
          ↓
    CLI receives input
          ↓
    Game receives action
          ↓
    SudokuEngine validates move
          ↓
    Board is updated
          ↓
    Game checks completed structures
          ↓
    Ring/Column/Region event detected
          ↓
    Game applies gameplay effect
          ↓
    Spider / Score / Health updated
          ↓
    CLI displays event

---

## 19. Spider Movement Flow

Example:

    Ring completed
          ↓
    Game determines ring position
          ↓
    Compare with spider position
          ↓
    Forward / Backward / No movement
          ↓
    Active column used
          ↓
    Spider position updated
          ↓
    Health updated
          ↓
    Score updated
          ↓
    CLI displays movement

For a newly completed column:

    Column completed
          ↓
    New column becomes active
          ↓
    Spider moves sideways
          ↓
    Health / score updated
          ↓
    CLI displays event

---

## 20. AI Hint Flow

The AI hint flow is:

    Player requests hint
          ↓
    CLI
          ↓
    Game
          ↓
    SudokuEngine calculates candidates
          ↓
    AI receives trusted game information
          ↓
    Ollama generates explanation
          ↓
    CLI displays explanation

The AI does not determine the candidates itself.

The Sudoku engine supplies the authoritative information.

---

## 21. Save / Load Flow

Save:

    Player requests save
          ↓
    CLI
          ↓
    Game state
          ↓
    SaveLoad
          ↓
    JSON file

Load:

    Player requests load
          ↓
    CLI
          ↓
    SaveLoad
          ↓
    JSON validation
          ↓
    Game state restored
          ↓
    Game continues

---

## 22. Dependency Rules

The following rules should be maintained:

1. CLI depends on application/game services.
2. Game coordinates domain components.
3. Domain components should not depend on CLI rendering.
4. Sudoku must not depend on Spider.
5. Spider must not depend on CLI.
6. AI must not be the source of truth.
7. Persistence must not contain gameplay rules.
8. `main.py` should remain a thin entry point.

---

## 23. Testing Strategy

Testing should occur at multiple levels.

### Unit tests

Test individual classes:

- Cell
- Board
- SudokuEngine
- Spider
- Scoring
- Timer
- Player

### Integration tests

Test interactions between:

- Game + Sudoku
- Game + Spider
- Game + Scoring
- Game + Timer
- Game + Persistence

### CLI tests

Test:

- Commands.
- Input validation.
- Help.
- Menu behavior.
- Demo mode.

### Demo test

The demo should verify that a complete deterministic game reaches:

    WON

without bypassing the game engine.

---

## 24. Architectural Principle

The central principle of Weboku is:

    CLI displays the game.
    Game coordinates the game.
    Domain implements the rules.
    Repository stores the state.
    AI explains the game.

The deterministic Python engine remains the source of truth.
