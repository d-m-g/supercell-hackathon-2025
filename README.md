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

The AI tracks your match history and using game analysis determines, if there is a card you are havin particularly hard time against. If that is the case, it will nudge you towards straategies commonly used byt the community.

The AI coach identifies:
- Which enemy troops you struggle against the most
- If necessary, rovides personalized tips based on your performance
- If that's not enough, offers specific countering strategies

## Deployment

The application can be deployed to Streamlit Community Cloud:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Configure settings:
   - Main file path: `streamlit-game-viz/src/app.py`
   - Python version: 3.9+

## Demo

The demo website is currently not running te finetuned QLoRA, since keeping it running constantly for possibly multiple people to use at the same time posed problems. In case you are interested in testing the QLoRA, please clone the repo and run it localy.

When testinting the evaluation:
- Play multiple games to get sufficien data of the troops. Keep in mind, that the game is very simlified and the results you get might not be very realistic.
  - You can also make both of the players play random cards and make the game speed multiplier 10 te got data faster.
- Run the formula.py file to get analysis reslts

## License

This project is released under the MIT License.
