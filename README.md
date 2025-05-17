# Clash Royale Prototype

A simplified Clash Royale-inspired prototype designed to generate game replays. This project implements a 1D grid-based game with towers, character cards, and an elixir system.

## Features

- 1×18 grid gameplay with towers at each end
- Character cards with Attack, HP, Cost, and Range attributes
- Elixir-based resource management system (1/3 elixir per turn)
- AI opponents with configurable difficulty
- Comprehensive replay recording system

## Game Rules

- **Card Distribution**: Decks are randomly generated and shuffled for fair distribution
- **Card Usage**: Cards can be reused (they return to hand after being played)
- **Unit Limit**: Each player can have up to 3 units on the field at once
- **Card Placement**: Players can only place units 1-2 spaces from their tower
- **Movement & Combat**:
  - Units can either move OR attack in a turn, not both
  - Units that move cannot attack until the next turn
  - When there's a 1-cell gap between opposing units, the unit with higher HP moves forward
  - No friendly fire (units only attack enemy units)
  - Units can attack from a distance based on their range attribute
- **Card Restrictions**: Players cannot play the same card twice in a row
- **Turn Phases**:
  1. Movement Phase: All units move first
  2. Placement Phase: Players can place new units
  3. Attack Phase: Units that didn't move can attack

## Project Structure

```
clash-royale-prototype/
├── src/                  # Source code
│   ├── game/             # Core game mechanics
│   │   ├── card.py       # Card definitions and deck management
│   │   ├── environment.py # Game grid and core mechanics
│   │   └── player.py     # Player and AI logic
│   ├── replay/           # Replay recording and loading
│   │   └── recorder.py   # Replay recording functionality
│   └── visualize_game.py # Game visualization
├── replays/              # Saved game replays
├── main.py              # Main script for running games and recording replays
├── visualize.py         # Script for game visualization
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python packages (install with `pip install -r requirements.txt`):
  - numpy
  - matplotlib (optional, for graphical visualization)

### Installation

1. Clone this repository
2. Create the necessary directories:
   ```
   mkdir -p src/game src/replay replays
   ```
3. Install dependencies:
   ```
   pip install numpy matplotlib
   ```

## Usage

The prototype provides two main ways to run games:

### 1. Visualized Gameplay

Run a game with real-time visualization:
```bash
python visualize.py [options]
```

Options:
- `--player1`: Type of player 1 (human or ai, default: ai)
- `--player2`: Type of player 2 (human or ai, default: ai)
- `--delay`: Delay between turns in seconds (default: 2.0)
- `--turns`: Maximum number of turns (default: 100)
- `--difficulty`: AI difficulty level (1: Easy, 2: Medium, 3: Hard, default: 1)
- `--ascii-only`: Use only ASCII visualization
- `--plot-only`: Use only graphical (matplotlib) visualization
- `--both`: Use both ASCII and graphical visualization (default)

Examples:
```bash
# Run with both ASCII and graphical visualization
python visualize.py --both --delay 1.0

# Run with only ASCII visualization
python visualize.py --ascii-only --difficulty 2

# Run with only graphical visualization
python visualize.py --plot-only --player1 human
```

### 2. Replay Recording

Run games and record replays using the main script:
```bash
python src/main.py [command] [options]
```

Commands:
- `play`: Run a single game and record it
- `batch`: Generate multiple game replays

Options for `play` command:
- `--player1`: Type of player 1 (human or ai, default: ai)
- `--player2`: Type of player 2 (human or ai, default: ai)
- `--turns`: Maximum number of turns (default: 100)
- `--difficulty`: AI difficulty level (1: Easy, 2: Medium, 3: Hard, default: 2)
- `--seed`: Random seed for reproducibility (optional)

Options for `batch` command:
- `--count`: Number of replays to generate (default: 10)
- `--player1`: Type of player 1 (human or ai, default: ai)
- `--player2`: Type of player 2 (human or ai, default: ai)
- `--turns`: Maximum number of turns (default: 100)
- `--difficulty`: AI difficulty level (1: Easy, 2: Medium, 3: Hard, default: 2)

Examples:
```bash
# Generate a single replay
python src/main.py play --player1 ai --player2 ai --difficulty 2

# Generate a replay with a specific seed
python src/main.py play --seed 42 --difficulty 2

# Generate 10 replays with different random seeds
python src/main.py batch --count 10 --difficulty 2

# Generate 50 replays with custom settings
python src/main.py batch --count 50 --player1 ai --player2 ai --turns 200 --difficulty 3
```

Each replay is saved as a JSON file in the `replays` directory and includes:
- Game metadata (player types, difficulty, card distributions, seed)
- Complete game state history
- Unit information (card names, stats, positions, ranges)
- Turn-by-turn actions and outcomes

## Visualization Modes

The game can be visualized in two ways:

1. **ASCII Mode** (default):
   - Shows the game grid using ASCII characters
   - Displays unit status (moved/ready)
   - Shows last played cards for each player
   - Updates in real-time in the terminal

2. **Matplotlib Mode** (optional):
   - Provides a graphical visualization
   - Shows unit positions, health, and attack ranges
   - Displays game statistics
   - Updates in a separate window

## Extending the Prototype

To add new card types, edit the `create_sample_cards` function in `src/game/card.py`. Each card needs:
- Name
- Attack value
- HP (hit points)
- Cost (elixir)
- Range (attack range in grid cells)

## License

This project is released under the MIT License.