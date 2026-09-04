# Weboku CLI Design

## 1. Purpose

Weboku is a CLI-only game.

The CLI is responsible for presenting the game to the player and
collecting player commands.

The CLI must not contain the core Sudoku, spider, scoring, timer,
or win/lose business rules.

The CLI communicates with the game/application layer.

---

## 2. Starting Weboku

Normal game:

    python main.py

Help:

    python main.py --help

Demo:

    python main.py --demo

The `main.py` file should remain a thin entry point.

---

## 3. Main Menu

When Weboku starts normally, display a main menu similar to:

    ╔══════════════════════════════════════════╗
    ║                🕷️ WEBOKU                ║
    ║        THE SPIDER SUDOKU ADVENTURE       ║
    ╠══════════════════════════════════════════╣
    ║  1. Start Game                           ║
    ║  2. Load Game                            ║
    ║  3. Instructions                         ║
    ║  4. Help                                 ║
    ║  5. Quit                                 ║
    ╚══════════════════════════════════════════╝

The exact visual style may be improved during implementation.

---

## 4. Player Name

At the beginning of a new game:

    Enter your player name:

The name is stored in the Player object.

The player name may be displayed in the game HUD.

---

## 5. Game Screen

The main game screen should contain:

1. Player information.
2. Health.
3. Score.
4. Timer.
5. Current level.
6. Spider position.
7. Active column.
8. Sudoku board.
9. Progress information.
10. Event messages.
11. Available commands.

Example:

    ╔════════════════════════════════════════════╗
    ║ PLAYER: Richie       LEVEL: 1              ║
    ║ SCORE: 450           HEALTH: 72/100        ║
    ║ TIME: 04:32           ACTIVE COLUMN: C4    ║
    ║ SPIDER: RING 3 × COLUMN 4                  ║
    ╚════════════════════════════════════════════╝

    WEBOKU BOARD

    [Circular/nonagon Weboku board displayed here]

    Progress:
    Rings:    ██████░░░ 6/9
    Columns:  ████░░░░░ 4/9
    Regions:  █████░░░░ 5/9

    Event:
    ✅ Ring 6 completed!
    🕷️ Spider moved forward.

---

## 6. Board Rendering

The board renderer must represent the Weboku board as a
nonagon/spider-web structure.

The board contains exactly:

    81 playable cells

The center is empty.

The center must NOT be rendered as an additional cell.

There are:

    9 rings
    9 radial columns/sectors
    81 cells

The renderer must visually distinguish:

- Individual cells.
- Ring boundaries.
- Column boundaries.
- Region boundaries.
- Completed structures.
- Spider position.

---

## 7. Spider Rendering

The spider occupies a junction between a ring and a column.

The spider does not occupy a Sudoku cell.

Example:

    Spider:
    🕷️ R3 × C5

The Sudoku value inside the corresponding cell remains visible.

The renderer should make the spider's junction position visually clear
without hiding the cell's Sudoku value.

---

## 8. Sudoku Values

The game engine stores numbers 1–9.

The CLI displays:

    1 = 🍎
    2 = 🍌
    3 = 🍉
    4 = 🍇
    5 = 🍆
    6 = 🥭
    7 = 🍒
    8 = 🍑
    9 = 🍍

Empty cells should have a clear empty representation.

For example:

    ·

The exact empty-cell symbol may be changed during implementation if
necessary for terminal compatibility.

---

## 9. Cell Input

The player must be able to select a cell and enter a value.

The recommended command format is:

    set <ring> <column> <value>

Example:

    set 6 4 3

This means:

    Ring 6
    Column 4
    Value 3

The CLI may display the equivalent fruit:

    🍉

The game engine validates the move.

---

## 10. Invalid Input

The CLI must gracefully handle invalid commands.

Examples:

    set six four three

    set 12 2 5

    set 3 4 15

    set 3 4

The CLI should display a useful error:

    ❌ Invalid command.

or:

    ❌ Ring must be between 1 and 9.

or:

    ❌ Column must be between 1 and 9.

or:

    ❌ Value must be between 1 and 9.

The program must not crash because of normal invalid player input.

---

## 11. Invalid Sudoku Move

If the command format is valid but the Sudoku move violates the rules:

    set 6 4 3

The Sudoku engine may return:

    Invalid move.

The CLI displays:

    ❌ Move rejected.
    🍉 cannot be placed at Ring 6 × Column 4.

The exact reason should be displayed where available.

---

## 12. Changing a Player Value

The CLI may allow a player to remove a value they previously entered.

Recommended command:

    clear <ring> <column>

Example:

    clear 6 4

Fixed puzzle clues cannot be cleared.

The game engine remains responsible for deciding whether the operation
is allowed.

---

## 13. Candidate / Hint Command

The player may request a hint.

Recommended command:

    hint

The game should calculate trusted Sudoku information first.

The AI may then explain the result.

Example:

    💡 Hint

    Look at Ring 6 × Column 4.

    Only 🍉 can fit here because the other possible values
    already appear in its ring, column, or region.

The AI explanation is not the source of truth.

---

## 14. Specific Cell Hint

If supported:

    hint 6 4

This requests a hint for:

    Ring 6 × Column 4

The Sudoku engine calculates the candidates.

The AI may convert the information into natural language.

---

## 15. Status Command

The player can request current game information:

    status

Example:

    ╔════════════════════════════════════╗
    ║            GAME STATUS             ║
    ╠════════════════════════════════════╣
    ║ Player: Richie                     ║
    ║ Level: 1                           ║
    ║ Score: 450                         ║
    ║ Health: 72/100                     ║
    ║ Time: 04:32                        ║
    ║ Spider: R3 × C4                    ║
    ║ Active Column: C4                  ║
    ╚════════════════════════════════════╝

---

## 16. Save Command

Recommended command:

    save

The current game state is sent to the persistence layer.

The CLI displays:

    💾 Game saved successfully.

The CLI does not directly write JSON files.

---

## 17. Load Command

Recommended command:

    load

The persistence layer loads the saved state.

The CLI displays:

    📂 Game loaded successfully.

Invalid or corrupted save data must be handled gracefully.

---

## 18. Help Command

The player can type:

    help

The CLI displays the available commands.

Example:

    WEBOKU COMMANDS

    set <ring> <column> <value>
        Enter a Sudoku value.

    clear <ring> <column>
        Remove a player-entered value.

    hint
        Request a Sudoku hint.

    hint <ring> <column>
        Request a hint for a specific cell.

    status
        Display game status.

    save
        Save the current game.

    load
        Load a saved game.

    help
        Display this help.

    quit
        Exit the game.

---

## 19. Quit Command

The player can type:

    quit

The CLI should ask for confirmation if there are unsaved changes.

Example:

    You have unsaved progress.
    Quit without saving? (y/n):

The game must not crash or lose data unexpectedly.

---

## 20. Ring Completion Display

When a ring is completed:

    ✅ RING 6 COMPLETE!

The board renderer should visually distinguish the completed ring.

The game engine decides whether spider movement occurs.

The CLI only displays the result.

---

## 21. Column Completion Display

When a column is completed:

    ✅ COLUMN 4 COMPLETE!

    ⭐ Column 4 is now the ACTIVE COLUMN.

The renderer should visually distinguish the completed column.

---

## 22. Region Completion Display

When a region is completed:

    ✅ REGION 5 COMPLETE!

    🏆 Region reward earned!

The spider does not automatically move because of region completion.

---

## 23. Forward Movement Display

Example:

    🟢 FORWARD MOVEMENT

    Ring 3 × Column 4
          ↓
    Ring 6 × Column 4

    🕷️ Spider moved forward!

    ❤️ Health +20
    🍉 Fruit energy +10
    🏆 Movement reward earned.

The actual values come from the game engine.

The CLI must display the values supplied by the game state.

---

## 24. Backward Movement Display

Example:

    🔴 BACKWARD MOVEMENT

    Ring 6 × Column 4
          ↓
    Ring 3 × Column 4

    ⚠️ Spider moved backward.

    ❤️ Health -10
    🏆 Reduced movement reward.

Backward movement should be clearly distinguishable from forward
movement.

---

## 25. Sideways Movement Display

Example:

    🟡 SIDEWAYS MOVEMENT

    Column 7 completed!

    Active column:
    C4 → C7

    🕷️ Spider moves along Ring 3.

    Ring 3 × Column 4
          →
    Ring 3 × Column 7

    ❤️ Health gained.
    🏆 Half movement reward.

---

## 26. Health Warning

When health becomes low, the CLI should display a warning.

Example:

    ⚠️ WARNING
    Spider health is low: 18/100

The exact warning threshold is configurable.

---

## 27. Timer Warning

When remaining time becomes low:

    ⚠️ TIME WARNING
    Only 30 seconds remaining!

The exact warning threshold is configurable.

---

## 28. Blocked Movement

If the game cannot perform a required movement:

    ⚠️ SPIDER BLOCKED

The CLI should explain the reason supplied by the game engine.

The AI may provide an additional explanation.

The CLI must not invent the movement result.

---

## 29. Level Completion

When the player completes the current level:

    ╔══════════════════════════════════════════╗
    ║             LEVEL COMPLETE! 🏆           ║
    ╠══════════════════════════════════════════╣
    ║ Spider reached the outside!              ║
    ║ Water found! 💧                          ║
    ║                                          ║
    ║ Final Score: 1,250                       ║
    ║ Final Health: 100/100                    ║
    ╚══════════════════════════════════════════╝

Then:

    Next level unlocked!

---

## 30. Victory Screen

The final objective is:

    CENTER
      ↓
    RING 1
      ↓
    ...
      ↓
    RING 9
      ↓
    OUTSIDE
      ↓
    💧 WATER
      ↓
    🏆 WIN

The victory screen should clearly communicate success.

Example:

    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║             🏆 WEBOKU WON!               ║
    ║                                          ║
    ║       🕷️ THE SPIDER ESCAPED THE WEB      ║
    ║                                          ║
    ║             💧 WATER FOUND!              ║
    ║                                          ║
    ║       Final Score: 1,250                 ║
    ║       Final Health: 100/100              ║
    ║       Time Remaining: 01:42              ║
    ║                                          ║
    ╚══════════════════════════════════════════╝

---

## 31. Lose Screen

If health reaches zero:

    ╔══════════════════════════════════════════╗
    ║              GAME OVER                  ║
    ╠══════════════════════════════════════════╣
    ║ 🕷️ The spider ran out of health.         ║
    ║                                          ║
    ║ Score: 380                               ║
    ║                                          ║
    ╚══════════════════════════════════════════╝

If time reaches zero:

    ╔══════════════════════════════════════════╗
    ║              GAME OVER                  ║
    ╠══════════════════════════════════════════╣
    ║ ⏰ Time has run out.                     ║
    ║                                          ║
    ║ Score: 380                               ║
    ║                                          ║
    ╚══════════════════════════════════════════╝

---

## 32. Demo Mode

Demo mode is started with:

    python main.py --demo

The demo should provide a reliable presentation of a complete game.

It should show:

- Game initialization.
- Sudoku activity.
- Cell updates.
- Structure completion.
- Spider movement.
- Active column.
- Health.
- Fruit energy.
- Score.
- Timer.
- Progress.
- Ring 9 completion.
- Outside objective.
- Water.
- Victory.

The demo should use deterministic game data.

The demo should use the real game engine.

The demo must not bypass the game engine by simply printing a fake
victory message.

---

## 33. Demo Output

The demo should clearly communicate progress.

Example:

    🕷️ WEBOKU DEMO START

    Spider begins at CENTER.
    Health: 0/100

    Solving demonstration puzzle...

    ✅ Ring 1 COMPLETE
    🕷️ Spider enters Ring 1

    ✅ Ring 2 COMPLETE
    🕷️ Spider enters Ring 2

    ...

    ✅ Ring 9 COMPLETE
    🕷️ Spider reaches the outer boundary.

    💧 WATER FOUND!

    🕷️ Spider drinks the water.

    🏆 WEBOKU DEMO COMPLETE!

The actual implementation should produce these events through the
game engine rather than hard-coded fake results.

---

## 34. Input Loop

The normal game should operate through a command loop.

Conceptually:

    while game_is_running:

        display_game_state()

        command = get_player_input()

        result = process_command(command)

        display_result(result)

The actual game state and business rules remain outside the CLI.

---

## 35. CLI Error Handling

The CLI should gracefully handle:

- Empty input.
- Unknown commands.
- Incorrect command arguments.
- Invalid numbers.
- Out-of-range coordinates.
- Invalid Sudoku moves.
- Invalid save files.
- Missing save files.
- AI service failures.
- Timer expiration.

The application must not terminate unexpectedly because of ordinary
user mistakes.

---

## 36. AI Failure Handling

Ollama may not always be available.

If the AI service is unavailable:

    ⚠️ AI Master is unavailable.

    The deterministic Sudoku engine is still running normally.

The player must still be able to play the game without AI assistance.

---

## 37. Terminal Compatibility

The CLI should work in a normal terminal environment.

The implementation should avoid depending on a graphical interface.

Unicode fruit and spider symbols may be used, but the application
should handle terminals where some symbols do not render perfectly.

---

## 38. CLI Responsibility Boundary

The CLI is responsible for:

    Input
    Output
    Formatting
    Commands
    User interaction

The CLI is NOT responsible for:

    Sudoku validation
    Candidate calculation
    Spider movement
    Health calculations
    Scoring calculations
    Timer logic
    Win/lose decisions
    AI truth
    JSON persistence rules

Those responsibilities belong to the appropriate application,
domain, or service components.

---

## 39. CLI Architecture

The CLI flow is:

    User
      ↓
    CLI
      ↓
    Game/Application Service
      ↓
    Domain Components
      ↓
    Result
      ↓
    Renderer
      ↓
    Terminal

The renderer receives game state and converts it into terminal output.

---

## 40. Design Principle

The CLI should make Weboku easy to understand without changing the
underlying game rules.

The player should always be able to understand:

- Where the spider is.
- How much health remains.
- How much time remains.
- Current score.
- Active column.
- Completed structures.
- Available commands.
- What just happened.
- What action can be taken next.

The game engine remains the source of truth.
