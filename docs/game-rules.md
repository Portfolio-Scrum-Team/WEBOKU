# Weboku Game Rules

## 1. Game Objective

Weboku is a CLI-based circular Sudoku game.

The player solves Sudoku cells while guiding a spider from the empty
center of the Weboku board to the outside of Ring 9.

The final objective is:

CENTER → RING 1 → RING 2 → RING 3 → RING 4 → RING 5 → RING 6 → RING 7 → RING 8 → RING 9 → OUTSIDE → WATER

The player wins when the spider reaches the outside of Ring 9 and
successfully drinks the water.

---

## 2. Board Structure

The Weboku board contains exactly 81 playable cells.

The board consists of:

- 9 concentric rings
- 9 radial columns/sectors
- 81 total cells
- 9 Sudoku regions

The center of the board is empty and is NOT a playable cell.

Internally, the board is represented as:

    board[ring][column]

There are 9 rings and 9 columns.

At the game-rule level, rings and columns are numbered from 1 to 9.

---

## 3. Sudoku Structure

Weboku follows standard 9×9 Sudoku rules.

Every:

- Ring must contain numbers 1–9 exactly once.
- Column must contain numbers 1–9 exactly once.
- Region must contain numbers 1–9 exactly once.

The 9 regions are created by grouping:

### Rings

- Rings 1–3
- Rings 4–6
- Rings 7–9

### Columns

- Columns 1–3
- Columns 4–6
- Columns 7–9

This creates nine 3×3-equivalent Sudoku regions.

---

## 4. Cell Values

The Sudoku engine stores values internally as integers 1–9.

The CLI displays those values as fruit symbols.

| Value | Fruit         |
| ----: | ------------- |
|     1 | 🍎 Apple      |
|     2 | 🍌 Banana     |
|     3 | 🍉 Watermelon |
|     4 | 🍇 Grapes     |
|     5 | 🍆 Eggplant   |
|     6 | 🥭 Mango      |
|     7 | 🍒 Cherries   |
|     8 | 🍑 Peach      |
|     9 | 🍍 Pineapple  |

The fruit symbols are a presentation layer only.

The game engine works with the numeric values 1–9.

---

## 5. Spider Position

The spider starts at the empty center of the board with 0 health.

The spider occupies a junction between a ring and a column.

The spider does NOT occupy a Sudoku cell.

A spider position is represented as:

    (ring, column)

Example:

    Ring 3 × Column 5

The corresponding Sudoku cell remains visible and available to the
player.

---

## 6. Paths

There are two types of movement paths.

### Ring Path

A ring is a circular path around the board.

### Column Path

A column/sector is a radial path from the center toward the outside.

Completed columns can therefore be used by the spider to travel
between rings.

---

## 7. Active Column

The latest completed column becomes the active column.

The active column is the radial path used for forward and backward
movement between rings.

Example:

Spider position:

    Ring 3 × Column 1

Active column:

    Column 1

If Ring 5 is completed, the spider travels:

    Ring 3 × Column 1
            ↓
    Ring 5 × Column 1

The spider stops at the Ring 5 × Column 1 junction.

---

## 8. Forward Movement

When the player completes a ring that is ahead of the spider:

- The spider moves forward.
- The active column is used as the path.
- The player receives the full movement reward.
- The spider gains health.
- The appropriate fruit reward is applied.

Example:

Spider is at Ring 3.

The player completes Ring 5.

The spider moves:

    Ring 3 → Ring 5

using the active column.

---

## 9. Backward Movement

The player may complete a ring behind the spider.

When this happens:

- The spider moves backward.
- The active column is used.
- The spider loses some health.
- The player receives half of the normal movement reward.

Example:

Spider is at Ring 5.

The player completes Ring 3.

The spider moves:

    Ring 5 → Ring 3

using the active column.

Backward movement represents a health risk.

---

## 10. Sideways Movement

When a new column is completed:

- That column becomes the active column.
- The spider moves along its current ring.
- The spider moves to the junction of the new column.
- The spider gains some health.
- The player receives half of the normal forward movement reward.

Example:

Spider position:

    Ring 3 × Column 1

Column 5 becomes completed.

The spider moves:

    Ring 3 × Column 1
            →
    Ring 3 × Column 5

Column 5 becomes the new active column.

---

## 11. Region Completion

Completing a Sudoku region awards points.

Completing a region does NOT automatically move the spider.

The spider only moves because of the defined ring or column completion
events.

---

## 12. Health

The spider has a maximum health of 100 HP.

The spider starts with:

    0 HP

The spider gains health through successful movement and fruit energy.

The spider can lose health when moving backward.

The game is lost when spider health reaches zero, unless the spider has
already reached the winning state.

---

## 13. Fruit Energy

Each successful movement can provide fruit energy.

The fruit energy values are:

| Fruit         | Energy |
| ------------- | -----: |
| 🍒 Cherries   |  +1 HP |
| 🍑 Peach      |  +2 HP |
| 🍇 Grapes     |  +3 HP |
| 🍎 Apple      |  +4 HP |
| 🍌 Banana     |  +5 HP |
| 🍆 Eggplant   |  +6 HP |
| 🍍 Pineapple  |  +7 HP |
| 🥭 Mango      |  +8 HP |
| 🍉 Watermelon | +10 HP |

Health cannot exceed the maximum health of 100 HP.

The exact balance may be adjusted during playtesting.

---

## 14. Scoring

Completing Sudoku structures awards points.

### Ring completion

A completed ring awards the normal ring-completion reward.

### Column completion

A completed column awards the normal column-completion reward.

### Region completion

A completed region awards a region-completion reward.

### Movement rewards

Forward movement receives the full movement reward.

Sideways movement receives half of the normal forward movement reward.

Backward movement receives half of the normal forward movement reward.

Backward movement also causes a health penalty.

The exact numerical scoring values are configurable and may be
adjusted during balancing.

---

## 15. Timer

The game uses a countdown timer.

The player must solve the Sudoku challenge before the timer expires.

The game is lost when the timer reaches zero.

Different levels may use different time limits.

The timer must be fair and balanced through playtesting.

---

## 16. Completing Structures

A structure becomes complete when its Sudoku rules are satisfied.

The game must detect completion of:

- Rings
- Columns
- Regions

When a structure becomes complete:

- The player receives the appropriate reward.
- The CLI displays a completion message.
- The structure receives a distinct visual indication.

Completed structures must remain visually distinguishable from
incomplete structures.

---

## 17. Player Freedom

The player does not have to solve cells in a fixed order.

The player may solve any available cell anywhere on the board.

For example, the player may solve:

    Ring 6 × Column 4

before:

    Ring 2 × Column 1

The Sudoku engine validates every move according to the Sudoku rules.

Completing structures independently is allowed.

---

## 18. Sudoku Move Validation

Every player move must be validated before being accepted.

A move is valid only when the selected value does not violate:

- The ring
- The column
- The region

Invalid moves must not modify the board.

The CLI must display a clear error message when a move is invalid.

---

## 19. AI Assistance

Weboku may use Ollama to provide optional hints and warnings.

The AI may explain:

- Sudoku hints
- Possible deductions
- Health warnings
- Time warnings
- Spider movement information
- Blocked movement

Example:

    Hint:
    Look at Ring 6, Column 4.
    Only 🍉 can fit here because the other symbols already appear
    in its column and region.

The deterministic Python game engine remains the source of truth.

Ollama must NOT decide whether a Sudoku move is valid.

Ollama must NOT directly modify game state.

---

## 20. Win Condition

The player wins when:

1. Ring 9 is completed.
2. The spider reaches the outside of Ring 9.
3. The water objective is reached.
4. The spider drinks the water.

The final game state becomes:

    WON

The final sequence is:

    CENTER
       ↓
    RING 1
       ↓
    RING 2
       ↓
    RING 3
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

---

## 21. Lose Conditions

The player loses when either:

- Spider health reaches zero.
- The timer reaches zero.

The final game state becomes:

    LOST

The CLI must clearly explain why the player lost.

---

## 22. Level Progression

Weboku contains multiple levels.

Later levels should increase the challenge through combinations of:

- More difficult Sudoku deduction patterns
- Different clue layouts
- Time pressure
- Health pressure
- Different starting conditions
- More demanding gameplay decisions

Difficulty should not depend only on having fewer missing values.

Completing a level unlocks the next level.

---

## 23. Demo Mode

Weboku must include a deterministic demo mode.

The demo is started with:

    python main.py --demo

The demo must show a complete successful game.

The demonstration should show:

1. Game start
2. Spider at the center
3. Sudoku interaction
4. Valid moves
5. Ring completion
6. Column completion
7. Active-column changes
8. Spider movement
9. Health changes
10. Fruit rewards
11. Score changes
12. Region completion
13. Timer/progress information
14. Ring 9 completion
15. Spider reaching the outside
16. Water objective
17. Victory screen

The demo must use predetermined valid data.

The demo must be deterministic so that it produces a reliable
presentation every time.

The demo must use the same game engine and rules as normal gameplay.

The demo must NOT simply print a fake victory message while bypassing
the game engine.

---

## 24. Final Game Flow

The complete Weboku flow is:

    START
      ↓
    CENTER
      ↓
    Sudoku puzzle
      ↓
    Player solves cells
      ↓
    Structures become complete
      ↓
    Rewards are calculated
      ↓
    Spider movement occurs when applicable
      ↓
    Health / score / timer updated
      ↓
    Continue solving
      ↓
    Ring 9 completed
      ↓
    Spider reaches OUTSIDE
      ↓
    💧 WATER
      ↓
    🏆 WEBOKU COMPLETE
      ↓
    Unlock next level
