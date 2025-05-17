# HIHIHIHAI

AI-powered tips for Clash Royale from reinforcement learning and public information.

## Features

- Single-lane Clash Royale gameplay simulation with interactive controls
- Four troop types with unique stats: Knight, Archer, Giant, and Goblin
- Elixir-based resource management system
- AI opponent with automated decision-making
- Comprehensive replay recording system
- AI coaching that analyzes your gameplay and provides personalized tips
- Beautiful visualization of game state, troops, and towers

## Game Controls

- **Deploy Troops**: Select a troop type and click the Deploy button
- **AI Toggle**: Enable/disable AI control for the player
- **Game Speed**: Adjust simulation speed with the slider
- **Restart**: Reset the game at any time
- **Replay Analysis**: Save and analyze your gameplay after a match

## Project Structure

```
supercell-hackathon-2025/
├── streamlit-game-viz/       # Streamlit application
│   ├── src/                  # Source code
│   │   ├── app.py            # Main Streamlit application
│   │   └── alternative_simulation.py  # Game simulation logic
├── formula.py                # AI analysis of replays
├── replays/                  # Saved game replays
└── requirements.txt          # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python packages (install with `pip install -r requirements.txt`):
  - streamlit
  - matplotlib
  - numpy
  - pandas
  - pygame
  - requests

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running Locally

Start the Streamlit application:
```bash
cd streamlit-game-viz
streamlit run src/app.py
```

## How to Play

1. **Select a Troop**: Choose from Knight, Archer, Giant, or Goblin in the sidebar
2. **Deploy**: Click the "Deploy" button to place your selected troop
3. **Manage Elixir**: Each troop costs different amounts of elixir, which regenerates over time
4. **Destroy the Enemy Tower**: Guide your troops to attack and destroy the enemy tower
5. **Defend Your Tower**: Prevent enemy troops from destroying your tower

## AI Coaching Features

After each game, you can:

1. **Save Replay**: Record your gameplay for later analysis
2. **Analyze Last Game**: Get AI-powered insights about your performance
3. **View Enemy Card Performance**: See which enemy cards were most effective against you
4. **Get Personalized Tips**: Receive strategic advice to improve your gameplay

The AI coach identifies:
- Which enemy troops you struggled against the most
- Provides personalized tips based on your performance
- Offers specific countering strategies

## Deployment

The application can be deployed to Streamlit Community Cloud:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Configure settings:
   - Main file path: `streamlit-game-viz/src/app.py`
   - Python version: 3.9+

## License

This project is released under the MIT License.