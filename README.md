# Clash Royale Prototype for Game Analysis

A simplified Clash Royale-inspired prototype designed to generate game replays for analysis. This project implements a 1D grid-based game with towers, character cards, and an elixir system.

## Features

- 1×10 grid gameplay with towers at each end
- Character cards with Attack, HP, and Cost attributes
- Elixir-based resource management system
- AI opponents with configurable difficulty
- Comprehensive replay recording system
- Advanced analysis and visualization tools

## Project Structure

```
clash-royale-prototype/
├── src/                  # Source code
│   ├── game/             # Core game mechanics
│   ├── replay/           # Replay recording and loading
│   ├── analysis/         # Analysis and visualization tools
│   └── main.py           # Main entry point
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

The prototype provides several commands through a command-line interface:

### Playing a Single Game

```
python src/main.py play [--player1 {human,ai}] [--player2 {human,ai}] [--turns TURNS] [--difficulty {1,2,3}]
```

Options:
- `--player1`: Type of player 1 (human or ai, default: ai)
- `--player2`: Type of player 2 (human or ai, default: ai)
- `--turns`: Maximum number of turns (default: 100)
- `--difficulty`: AI difficulty level (1: Easy, 2: Medium, 3: Hard, default: 2)

### Generating Multiple Games

```
python src/main.py batch [--count COUNT] [--all-ai] [--difficulty {1,2,3}]
```

Options:
- `--count`: Number of games to generate (default: 10)
- `--all-ai`: Set all games to be AI vs AI
- `--difficulty`: AI difficulty level (default: 2)

### Analyzing a Single Replay

```
python src/main.py analyze REPLAY_FILE
```

### Analyzing All Replays

```
python src/main.py analyze-all
```

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