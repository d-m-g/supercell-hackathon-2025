import os
import sys
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib.colors import LinearSegmentedColormap

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game.environment import GameEnvironment
from src.game.card import Card, CardDeck, create_sample_cards
from src.game.player import Player, AIPlayer

class GameVisualizer:
    """
    Visualizes the game state in real-time.
    """
    
    def __init__(self, game_env=None, use_ascii=True, use_matplotlib=False, delay=0.5, streamlit_mode=False):
        """
        Initialize the visualizer.
        
        Args:
            game_env: Optional GameEnvironment instance
            use_ascii: Whether to use ASCII representation
            use_matplotlib: Whether to use matplotlib for visualization
            delay: Delay between turns in seconds
            streamlit_mode: Whether to use Streamlit for visualization
        """
        self.game_env = game_env
        self.use_ascii = use_ascii and not streamlit_mode
        self.use_matplotlib = use_matplotlib
        self.delay = delay
        self.streamlit_mode = streamlit_mode
        self.fig = None
        self.ax = None
        self.current_state = {
            "turn": 0,
            "score": 0,
            "plot": None,
            "game_over": False
        }
        
        if use_matplotlib:
            if not streamlit_mode:
                plt.ion()  # Turn on interactive mode
            self.fig, self.ax = plt.subplots(figsize=(18, 4))  # Wider figure for 18x1 grid
            self.setup_plot()
    
    def setup_plot(self):
        """Set up the matplotlib plot."""
        if not self.use_matplotlib:
            return
            
        self.ax.set_xlim(-0.5, 17.5)  # Updated for 18x1 grid
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_yticks([])
        self.ax.set_xticks(range(18))  # Updated for 18x1 grid
        self.ax.set_title('Clash Royale Prototype - Game Flow')
        self.ax.grid(True, alpha=0.3)
    
    def visualize_state(self, game_env, player1=None, player2=None):
        """
        Visualize the current game state.
        
        Args:
            game_env: GameEnvironment instance
            player1: Optional Player 1 instance (None for replay visualization)
            player2: Optional Player 2 instance (None for replay visualization)
        """
        if self.use_ascii:
            self._visualize_ascii(game_env, player1, player2)
        
        if self.use_matplotlib:
            self._visualize_matplotlib(game_env, player1, player2)
            
        time.sleep(self.delay)
    
    def _visualize_ascii(self, game_env, player1=None, player2=None):
        """
        Visualize the game state using ASCII characters.
        
        Args:
            game_env: GameEnvironment instance
            player1: Optional Player 1 instance (None for replay visualization)
            player2: Optional Player 2 instance (None for replay visualization)
        """
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print turn information
        print(f"Turn: {game_env.turn_count}")
        
        # Print player decks if available
        if player1 is not None:
            print("\nPlayer 1 Deck:")
            for i, card in enumerate(player1.deck):
                status = "IN HAND" if card in player1.hand else "in deck"
                print(f"  {i+1}. {card.name}: ATK={card.attack}, HP={card.hp}, Cost={card.cost}, Range={card.range} - {status}")
        
        if player2 is not None:
            print("\nPlayer 2 Deck:")
            for i, card in enumerate(player2.deck):
                status = "IN HAND" if card in player2.hand else "in deck"
                print(f"  {i+1}. {card.name}: ATK={card.attack}, HP={card.hp}, Cost={card.cost}, Range={card.range} - {status}")
        
        print("\n" + "="*50 + "\n")  # Separator line
        
        # Count units for each player
        p1_units = sum(1 for unit in game_env.units.values() if unit['owner'] == 1)
        p2_units = sum(1 for unit in game_env.units.values() if unit['owner'] == 2)
        
        # Print elixir and unit counts if player info is available
        if player1 is not None:
            print(f"Player 1 Elixir: {player1.elixir}/{player1.max_elixir} (Units: {p1_units}/{player1.max_units})")
        else:
            print(f"Player 1 Units: {p1_units}")
            
        if player2 is not None:
            print(f"Player 2 Elixir: {player2.elixir}/{player2.max_elixir} (Units: {p2_units}/{player2.max_units})")
        else:
            print(f"Player 2 Units: {p2_units}")
        
        # Show last played cards if available
        if player1 is not None:
            if player1.last_played_card:
                print(f"Player 1 last played: {player1.last_played_card.name} (can't play again this turn)")
            else:
                print("Player 1 last played: None")
                
        if player2 is not None:
            if player2.last_played_card:
                print(f"Player 2 last played: {player2.last_played_card.name} (can't play again this turn)")
            else:
                print("Player 2 last played: None")
            
        print()
        
        # Print the grid
        grid_repr = []
        for i in range(game_env.grid_size):
            cell = game_env.grid[i]
            if cell == 'T1':
                grid_repr.append('🏰1')  # Castle emoji for Player 1's tower
            elif cell == 'T2':
                grid_repr.append('🏰2')  # Castle emoji for Player 2's tower
            elif cell == 0:
                grid_repr.append('··')  # Empty space
            else:
                # It's a unit
                unit_data = game_env.units.get(cell, {})
                owner = unit_data.get('owner', '?')
                moved = cell in game_env.moved_units  # Check if unit moved this turn
                
                if owner == 1:
                    grid_repr.append('🔵' if not moved else '🔷')  # Blue circle (solid for ready, hollow for moved)
                elif owner == 2:
                    grid_repr.append('🔴' if not moved else '🔶')  # Red circle (solid for ready, hollow for moved)
                else:
                    grid_repr.append('??')
        
        # Print the grid with indices
        print("+" + "-" * (game_env.grid_size * 3 - 1) + "+")
        print("|", end="")
        for i, cell in enumerate(grid_repr):
            print(f" {cell}", end="")
        print(" |")
        print("|", end="")
        for i in range(game_env.grid_size):
            print(f"{i:2d}", end=" ")
        print("|")
        print("+" + "-" * (game_env.grid_size * 3 - 1) + "+")
        print()
        
        # Print units with details
        print("Units on the field:")
        for unit_id, unit_data in game_env.units.items():
            card = unit_data['card']
            owner = unit_data['owner']
            position = unit_data['position']
            moved = unit_id in game_env.moved_units
            status = "MOVED (can't attack)" if moved else "READY"
            print(f"  Player {owner} - {card.name} at position {position}: HP={card.hp}, ATK={card.attack}, Range={card.range} - {status}")
        
        # Print game status
        if game_env.game_over:
            print(f"\nGame Over! Player {game_env.winner} wins!")
        
        print("\nPress Ctrl+C to exit the visualization")
        print("Note: Units that moved this turn (🔷/🔶) cannot attack until next turn")
        print("Note: Players cannot play the same card twice in a row")
        print("Note: Units can attack any enemy within their range")

    def _visualize_matplotlib(self, game_env, player1=None, player2=None):
        """
        Visualize the game state using matplotlib.
        
        Args:
            game_env: GameEnvironment instance
            player1: Optional Player 1 instance
            player2: Optional Player 2 instance
        """
        if not self.use_matplotlib:
            return
            
        self.ax.clear()
        self.setup_plot()
        
        # Update state for visualization
        self.current_state["turn"] = game_env.turn_count
        
        # Calculate score based on tower health differences
        try:
            # First try to get towers from the attribute
            if hasattr(game_env, 'towers'):
                player_tower = next((t for t in game_env.towers if t.team == 'player'), None)
                enemy_tower = next((t for t in game_env.towers if t.team == 'enemy'), None)
            # If that fails, try getting them from grid state
            elif hasattr(game_env, 'grid'):
                player_tower_cell = next((i for i, cell in enumerate(game_env.grid) if cell == 'T1'), None)
                enemy_tower_cell = next((i for i, cell in enumerate(game_env.grid) if cell == 'T2'), None)
                if player_tower_cell is not None and enemy_tower_cell is not None:
                    player_tower = {"hp": 100, "max_hp": 100}  # Using default values
                    enemy_tower = {"hp": 100, "max_hp": 100}
                else:
                    player_tower = None
                    enemy_tower = None
            else:
                player_tower = None
                enemy_tower = None
                
            if player_tower and enemy_tower:
                player_health = player_tower.hp / player_tower.max_hp if hasattr(player_tower, 'hp') else player_tower["hp"] / player_tower["max_hp"]
                enemy_health = enemy_tower.hp / enemy_tower.max_hp if hasattr(enemy_tower, 'hp') else enemy_tower["hp"] / enemy_tower["max_hp"]
                score = player_health * 100 - enemy_health * 100
            else:
                score = 0
        except Exception as e:
            print(f"Error calculating score: {e}")
            score = 0
            
        self.current_state["score"] = round(score, 1)
        self.current_state["game_over"] = True if hasattr(game_env, 'game_over') and game_env.game_over else False
        
        # Plot the grid
        for i in range(game_env.grid_size):
            cell = game_env.grid[i]
            if cell == 'T1':
                self.ax.add_patch(plt.Rectangle((i-0.4, 0.1), 0.8, 0.8, fill=True, color='blue', alpha=0.8))
                self.ax.text(i, 0.5, "T1", ha='center', va='center', color='white', fontweight='bold')
            elif cell == 'T2':
                self.ax.add_patch(plt.Rectangle((i-0.4, 0.1), 0.8, 0.8, fill=True, color='red', alpha=0.8))
                self.ax.text(i, 0.5, "T2", ha='center', va='center', color='white', fontweight='bold')
            elif cell != 0:
                # It's a unit
                unit_data = game_env.units.get(cell, {})
                owner = unit_data.get('owner', '?')
                card = unit_data.get('card', None)
                moved = cell in game_env.moved_units  # Check if unit moved this turn
                
                if owner == 1:
                    color = 'blue'
                    alpha = 0.4 if moved else 0.7  # Lower alpha if moved
                elif owner == 2:
                    color = 'red'
                    alpha = 0.4 if moved else 0.7  # Lower alpha if moved
                else:
                    color = 'gray'
                    alpha = 0.7
                
                # Draw unit as a circle
                self.ax.add_patch(plt.Circle((i, 0.5), 0.4, fill=True, color=color, alpha=alpha))
                
                # Add a dashed border if the unit moved and can't attack
                if moved:
                    self.ax.add_patch(plt.Circle((i, 0.5), 0.4, fill=False, color='black', linestyle='dashed'))
                
                # Add unit details
                if card:
                    # Show range as a semi-transparent circle
                    range_circle = plt.Circle((i, 0.5), card.range, fill=True, 
                                           color=color, alpha=0.1)
                    self.ax.add_patch(range_circle)
                    
                    # Add unit stats
                    self.ax.text(i, 0.5, f"{card.hp}", ha='center', va='center', 
                               color='white', fontweight='bold')
                    self.ax.text(i, 0.2, f"R{card.range}", ha='center', va='center',
                               color='black', fontsize=8)
        
        # Count units for each player
        p1_units = sum(1 for unit in game_env.units.values() if unit['owner'] == 1)
        p2_units = sum(1 for unit in game_env.units.values() if unit['owner'] == 2)
        
        # Add player info and decks
        # Player 1 info (left side)
        self.ax.text(1, 1.2, f"Turn: {game_env.turn_count}", ha='center', va='center', fontsize=12)
        
        if player1 is not None:
            self.ax.text(1, 1.1, f"Player 1: {player1.elixir}/{player1.max_elixir} elixir, {p1_units}/{player1.max_units} units", 
                      ha='center', va='center', color='blue')
            
            # Player 1 deck
            deck_y = 1.0
            self.ax.text(1, deck_y, "Player 1 Deck:", ha='center', va='center', color='blue', fontsize=9, fontweight='bold')
            for i, card in enumerate(player1.deck):
                status = "IN HAND" if card in player1.hand else "in deck"
                card_text = f"{card.name} (ATK:{card.attack}, HP:{card.hp}, Cost:{card.cost}, R:{card.range}) - {status}"
                self.ax.text(1, deck_y - 0.1 * (i + 1), card_text, ha='center', va='center', 
                          color='blue', fontsize=8, alpha=1.0 if card in player1.hand else 0.6)
        else:
            self.ax.text(1, 1.1, f"Player 1 Units: {p1_units}", ha='center', va='center', color='blue')
        
        # Player 2 info (right side)
        if player2 is not None:
            self.ax.text(17, 1.1, f"Player 2: {player2.elixir}/{player2.max_elixir} elixir, {p2_units}/{player2.max_units} units", 
                      ha='center', va='center', color='red')
            
            # Player 2 deck
            deck_y = 1.0
            self.ax.text(17, deck_y, "Player 2 Deck:", ha='center', va='center', color='red', fontsize=9, fontweight='bold')
            for i, card in enumerate(player2.deck):
                status = "IN HAND" if card in player2.hand else "in deck"
                card_text = f"{card.name} (ATK:{card.attack}, HP:{card.hp}, Cost:{card.cost}, R:{card.range}) - {status}"
                self.ax.text(17, deck_y - 0.1 * (i + 1), card_text, ha='center', va='center', 
                          color='red', fontsize=8, alpha=1.0 if card in player2.hand else 0.6)
        else:
            self.ax.text(17, 1.1, f"Player 2 Units: {p2_units}", ha='center', va='center', color='red')
        
        # Show last played cards if available
        if player1 is not None:
            p1_last_card = player1.last_played_card.name if player1.last_played_card else "None"
            self.ax.text(1, -0.2, f"Player 1 last played: {p1_last_card}", ha='center', va='center', color='blue', fontsize=9)
            
        if player2 is not None:
            p2_last_card = player2.last_played_card.name if player2.last_played_card else "None"
            self.ax.text(17, -0.2, f"Player 2 last played: {p2_last_card}", ha='center', va='center', color='red', fontsize=9)
        
        # Adjust y-axis limits to accommodate deck information
        max_deck_size = max(
            len(player1.deck) if player1 is not None else 0,
            len(player2.deck) if player2 is not None else 0
        )
        self.ax.set_ylim(-0.5, 1.5 + max_deck_size * 0.1)  # Adjust based on deck size
        
        # Legend for moved units and card restrictions
        legend_y = 1.2 + max_deck_size * 0.1
        self.ax.text(9, legend_y, "Note: Faded units with dashed borders have moved and can't attack", 
                 ha='center', va='center', fontsize=10, color='black')
        self.ax.text(9, legend_y - 0.1, "Note: Colored circles show unit attack ranges", 
                 ha='center', va='center', fontsize=10, color='black')
        
        if player1 is not None or player2 is not None:
            self.ax.text(9, legend_y - 0.2, "Note: Players cannot play the same card twice in a row", 
                     ha='center', va='center', fontsize=10, color='black')
            self.ax.text(9, legend_y - 0.3, "Note: Cards in hand are shown in full opacity, deck cards are faded", 
                     ha='center', va='center', fontsize=10, color='black')
        
        # Add game over message if applicable
        if game_env.game_over:
            self.ax.text(9, 0.5, f"GAME OVER! Player {game_env.winner} wins!", 
                     ha='center', va='center', fontsize=16, color='green',
                     bbox=dict(facecolor='white', alpha=0.8))
        
        if self.streamlit_mode:
            self.current_state["plot"] = self.fig
        else:
            # Update the plot
            self.fig.canvas.draw()
            plt.pause(0.01)
    
    def close(self):
        """Close the visualizer."""
        if self.use_matplotlib and self.fig:
            plt.close(self.fig)


def run_visualization(player1_type="ai", player2_type="ai", delay=2.0, turns=100, difficulty=2, use_ascii=True, use_matplotlib=True, replay_data=None, seed=None):
    """
    Run a game visualization.
    
    Args:
        player1_type: Type of player 1 ("human" or "ai")
        player2_type: Type of player 2 ("human" or "ai")
        delay: Delay between turns in seconds
        turns: Maximum number of turns
        difficulty: AI difficulty (1-3)
        use_ascii: Whether to use ASCII visualization
        use_matplotlib: Whether to use matplotlib visualization
        replay_data: Optional replay data to visualize instead of running a new game
        seed: Random seed for reproducibility (optional)
    """
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Initialize game environment
    game_env = GameEnvironment(grid_size=18)  # Updated to 18x1 grid
    
    # Create visualization
    viz = GameVisualizer(use_ascii=use_ascii, use_matplotlib=use_matplotlib, delay=delay)
    
    if replay_data:
        # Visualize replay
        states = replay_data["states"]
        metadata = replay_data["metadata"]
        
        # Print replay info
        print(f"Replay Info:")
        print(f"Game Version: {metadata.get('game_version', 'unknown')}")
        print(f"Player 1 Type: {metadata.get('player1_type', 'unknown')}")
        print(f"Player 2 Type: {metadata.get('player2_type', 'unknown')}")
        print(f"Difficulty: {metadata.get('difficulty', 'unknown')}")
        if "seed" in metadata:
            print(f"Seed: {metadata['seed']}")
        print()
        
        # Visualize each state
        for i, state in enumerate(states, 1):
            print(f"\nTurn {i}")
            # Create temporary game environment for visualization
            temp_env = GameEnvironment(grid_size=18)
            temp_env._set_state(state)  # Set the state from replay
            viz.game_env = temp_env  # Update visualizer's game environment
            viz.visualize_state(temp_env, None, None)  # Pass None for players as we don't have them in replay
            if i < len(states):  # Don't delay after the last state
                time.sleep(delay)
        
        # Print final result
        if state["game_over"]:
            print(f"\nGame Over! Winner: Player {state['winner']}")
        else:
            print("\nReplay ended without a winner")
    else:
        # Create card decks for players
        sample_cards = create_sample_cards()
        random.shuffle(sample_cards)
        
        # Split cards evenly between players
        half = len(sample_cards) // 2
        player1_cards = sample_cards[:half]
        player2_cards = sample_cards[half:]
        
        # Create player decks
        player1_deck = CardDeck(player1_cards)
        player2_deck = CardDeck(player2_cards)
        
        # Create players based on type
        if player1_type.lower() == "ai":
            player1 = AIPlayer(1, player1_deck, difficulty=difficulty)
        else:
            player1 = Player(1, player1_deck)
        
        if player2_type.lower() == "ai":
            player2 = AIPlayer(2, player2_deck, difficulty=difficulty)
        else:
            player2 = Player(2, player2_deck)
        
        # Main game loop
        for turn in range(1, turns + 1):
            print(f"\nTurn {turn}")
            
            # PHASE 1: Movement
            game_env._process_movements()
            
            # PHASE 2: Unit Placement
            if isinstance(player1, AIPlayer):
                player1.make_move(game_env)
            if isinstance(player2, AIPlayer):
                player2.make_move(game_env)
            
            # PHASE 3: Attacks
            game_env._process_attacks()
            game_env._check_win_conditions()
            
            # Generate elixir
            player1.generate_elixir()
            player2.generate_elixir()
            
            # Update visualizer's game environment and visualize
            viz.game_env = game_env
            viz.visualize_state(game_env, player1, player2)
            
            # Check if game is over
            if game_env.game_over:
                print(f"\nGame Over! Winner: Player {game_env.winner}")
                break
            
            # Delay between turns
            time.sleep(delay)


def main():
    """Parse command line arguments and run the visualization."""
    parser = argparse.ArgumentParser(description="Clash Royale Prototype Visualization")
    
    parser.add_argument("--player1", choices=["human", "ai"], default="ai", 
                       help="Player 1 type (default: ai)")
    parser.add_argument("--player2", choices=["human", "ai"], default="ai", 
                       help="Player 2 type (default: ai)")
    parser.add_argument("--delay", type=float, default=2.0, 
                       help="Delay between turns in seconds (default: 2.0)")
    parser.add_argument("--turns", type=int, default=100, 
                       help="Maximum number of turns (default: 100)")
    parser.add_argument("--difficulty", type=int, choices=[1, 2, 3], default=2, 
                       help="AI difficulty (1: Easy, 2: Medium, 3: Hard, default: 2)")
    parser.add_argument("--ascii", action="store_true", default=True,
                       help="Use ASCII visualization (default: True)")
    parser.add_argument("--plot", action="store_true", default=True,
                       help="Use matplotlib visualization (default: True)")
    
    args = parser.parse_args()
    
    # Run the visualization
    run_visualization(
        player1_type=args.player1,
        player2_type=args.player2,
        delay=args.delay,
        turns=args.turns,
        difficulty=args.difficulty,
        use_ascii=args.ascii,
        use_matplotlib=args.plot
    )


if __name__ == "__main__":
    main()