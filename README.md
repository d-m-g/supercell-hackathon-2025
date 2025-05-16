# Clash Royale Prototype for Game Analysis

A simplified Clash Royale-inspired prototype designed to generate game replays for analysis. This project implements a 1D grid-based game with towers, character cards, and an elixir system.

## Features

- 1×10 grid gameplay with towers at each end
- Character cards with Attack, HP, and Cost attributes
- Elixir-based resource management system
- AI opponents with configurable difficulty
- Comprehensive replay recording system
- Advanced analysis and visualization tools

## Game Rules

- **Card Distribution**: Decks are randomly generated and shuffled for fair distribution
- **Card Usage**: Cards can be reused (they return to hand after being played)
- **Unit Limit**: Each player can have up to 4 units on the field at once
- **Card Placement**: Players can only place units 1-2 spaces from their tower
- **Movement & Combat**:
  - Units can either move OR attack in a turn, not both
  - Units that move cannot attack until the next turn
  - When there's a 1-cell gap between opposing units, the unit with higher HP moves forward
  - No friendly fire (units only attack enemy units)
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
│   ├── analysis/         # Analysis and visualization tools
│   └── visualize_game.py # Game visualization and main entry point
├── replays/              # Saved game replays
├── analysis_results/     # Analysis outputs and visualizations
├── DEVELOPMENT_PLAN.md   # Project development plan
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python packages (install with `pip install -r requirements.txt`):
  - numpy
  - matplotlib

### Installation

1. Clone this repository
2. Create the necessary directories:
   ```
   mkdir -p src/game src/replay src/analysis replays analysis_results
   ```
3. Install dependencies:
   ```
   pip install numpy matplotlib
   ```

## Usage

The prototype provides a command-line interface for running and visualizing games:

### Running a Game

```
python visualize.py [--player1 {human,ai}] [--player2 {human,ai}] [--delay DELAY] [--turns TURNS] [--difficulty {1,2,3}] [--ascii] [--plot]
```

Options:
- `--player1`: Type of player 1 (human or ai, default: ai)
- `--player2`: Type of player 2 (human or ai, default: ai)
- `--delay`: Delay between turns in seconds (default: 2.0)
- `--turns`: Maximum number of turns (default: 100)
- `--difficulty`: AI difficulty level (1: Easy, 2: Medium, 3: Hard, default: 1)
- `--ascii`: Use ASCII visualization (default: True)
- `--plot`: Use matplotlib visualization (default: False)

### Visualization Modes

The game can be visualized in two ways:

1. **ASCII Mode** (default):
   - Shows the game grid using ASCII characters
   - Displays unit status (moved/ready)
   - Shows last played cards for each player
   - Updates in real-time in the terminal

2. **Matplotlib Mode** (optional):
   - Provides a graphical visualization
   - Shows unit positions and health
   - Displays game statistics
   - Updates in a separate window

## Analysis Features

The analysis system provides:

1. **Card Usage Statistics**: Frequency and timing of card usage
2. **Battle Flow Analysis**: Unit advantage over time and turning points
3. **Win Factor Analysis**: Identifying key factors in victories
4. **Visualizations**:
   - Unit count over time
   - Battle flow graphs
   - Position heatmaps
   - Card usage charts

## Extending the Prototype

To add new card types, edit the `create_sample_cards` function in `src/game/card.py`. Each card needs:
- Name
- Attack value
- HP (hit points)
- Cost (elixir)

## License

This project is released under the MIT License.