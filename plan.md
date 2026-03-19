# Economic Sprint - Telegram Bot Plan

## 1. Project Overview
**Name:** Economic Sprint
**Goal:** Improve economic skills through quick, 2-3 minute challenge sessions.
**Platform:** Telegram Bot (Python + aiogram)
**Database:** SQLite
**Style:** Text-based, NO EMOJIS.

## 2. Architecture

### Directory Structure
```text
economic_sprint/
├── main.py              # Entry point: initializes bot and dispatcher
├── database.py          # Handles SQLite connections, user creation, and score updates
├── config.py            # Configuration (Bot Token, Admin IDs)
├── data/
│   └── questions.json   # Initial set of economic questions (Easy/Medium/Hard)
├── handlers/            # Bot logic
│   ├── __init__.py
│   ├── start.py         # /start command and registration
│   ├── menu.py          # Main menu navigation (Play, Profile, Leaderboard)
│   └── game.py          # The core game loop (Question -> Answer -> Result)
└── utils/               # Helper functions
    └── game_logic.py    # XP calculation, Leveling formulas, Streak checks
```

### Database Schema (SQLite)

**Table: `users`**
| Column | Type | Description |
| :--- | :--- | :--- |
| `user_id` | INTEGER (PK) | Telegram User ID |
| `username` | TEXT | Telegram Username |
| `xp` | INTEGER | Total Experience Points |
| `level` | INTEGER | Current Level (calculated from XP) |
| `streak` | INTEGER | Current daily streak |
| `last_played` | TEXT | Date string (YYYY-MM-DD) to track streaks |
| `best_score` | INTEGER | Highest score in a single session |

**Table: `questions`**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Unique ID |
| `text` | TEXT | The question text |
| `options` | TEXT | JSON string of options (e.g., "['A','B','C','D']") |
| `correct_index` | INTEGER | Index of the correct answer (0-3) |
| `difficulty` | INTEGER | 1 (Easy), 2 (Medium), 3 (Hard) |

## 3. Game Mechanics

### The "Sprint" (Session)
*   **Length:** 10 Questions per session.
*   **Time:** ~15 seconds per question (enforced by user pacing, or bot timeout if possible).
*   **Flow:**
    1.  User clicks "PLAY SPRINT".
    2.  Bot sends Question 1 with 4 options.
    3.  User clicks an option.
    4.  Bot edits message to show result (Correct/Wrong) briefly, then sends Question 2.
    5.  Repeat until Question 10.
    6.  Show Session Summary (Score, XP gained).

### Progression
*   **XP:**
    *   Correct Answer: +10 XP * Difficulty.
    *   Wrong Answer: +1 XP.
*   **Level Up:** `XP Needed = Current Level * 100`.
*   **Streaks:**
    *   Login daily to increase streak.
    *   Bonus XP = `Streak * 5`.

## 4. Implementation Steps
1.  **Setup:** Initialize project, virtual environment, install `aiogram`.
2.  **Database:** Create `database.py` to set up tables.
3.  **Content:** Create `questions.json` with 10-20 starter economic questions.
4.  **Bot Core:** Implement `/start` and Main Menu.
5.  **Game Loop:** Implement question serving and answer checking.
6.  **Stats:** Implement Profile and Leaderboard.