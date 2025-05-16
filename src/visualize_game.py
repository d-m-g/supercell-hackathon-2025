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

# Seed the random number generator for reproducibility (optional)
random.seed()

class GameVisualizer:
    """
    Visualizes the game state in real-time.
    """
    
    def __init__(self, use_ascii=True, use_matplotlib=False, delay=0.5):
        """
        Initialize the visualizer.
        
        Args:
            use_ascii: Whether to use ASCII representation
            use_matplotlib: Whether to use matplotlib for visualization
            delay: Delay between turns in seconds
        """
        self.use_ascii = use_ascii
        self.use_matplotlib = use_matplotlib
        self.delay = delay
        self.fig = None
        self.ax = None
        
        if use_matplotlib:
            plt.ion()  # Turn on interactive mode
            self.fig, self.ax = plt.subplots(figsize=(12, 4))
            self.setup_plot()
    
    def setup_plot(self):
        """Set up the matplotlib plot."""
        if not self.use_matplotlib:
            return
            
        self.ax.set_xlim(-0.5, 9.5)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_yticks([])
        self.ax.set_xticks(range(10))
        self.ax.set_title('Clash Royale Prototype - Game Flow')
        self.ax.grid(True, alpha=0.3)
    
    def visualize_state(self, game_env, player1, player2):
        """
        Visualize the current game state.
        
        Args:
            game_env: GameEnvironment instance
            player1: Player 1 instance
            player2: Player 2 instance
        """
        if self.use_ascii:
            self._visualize_ascii(game_env, player1, player2)
        
        if self.use_matplotlib:
            self._visualize_matplotlib(game_env, player1, player2)
            
        time.sleep(self.delay)
    
    def _visualize_ascii(self, game_env, player1, player2):
        """
        Visualize the game state using ASCII characters.
        
        Args:
            game_env: GameEnvironment instance
            player1: Player 1 instance
            player2: Player 2 instance
        """
        # Clear the console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print turn information
        print(f"Turn: {game_env.turn_count}")
        print(f"Player 1 Elixir: {player1.elixir}/{player1.max_elixir}")
        print(f"Player 2 Elixir: {player2.elixir}/{player2.max_elixir}")
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
                if owner == 1:
                    grid_repr.append('🔵')  # Blue circle for Player 1's units
                elif owner == 2:
                    grid_repr.append('🔴')  # Red circle for Player 2's units
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
            print(f" {i:1d}", end=" ")
        print("|")
        print("+" + "-" * (game_env.grid_size * 3 - 1) + "+")
        print()
        
        # Print units with details
        print("Units on the field:")
        for unit_id, unit_data in game_env.units.items():
            card = unit_data['card']
            owner = unit_data['owner']
            position = unit_data['position']
            print(f"  Player {owner} - {card.name} at position {position}: HP={card.hp}, ATK={card.attack}")
        
        # Print game status
        if game_env.game_over:
            print(f"\nGame Over! Player {game_env.winner} wins!")
        
        print("\nPress Ctrl+C to exit the visualization")
    
    def _visualize_matplotlib(self, game_env, player1, player2):
        """
        Visualize the game state using matplotlib.
        
        Args:
            game_env: GameEnvironment instance
            player1: Player 1 instance
            player2: Player 2 instance
        """
        if not self.use_matplotlib:
            return
            
        self.ax.clear()
        self.setup_plot()
        
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
                
                if owner == 1:
                    color = 'blue'
                elif owner == 2:
                    color = 'red'
                else:
                    color = 'gray'
                
                # Draw unit as a circle
                self.ax.add_patch(plt.Circle((i, 0.5), 0.4, fill=True, color=color, alpha=0.7))
                
                # Add unit details
                if card:
                    self.ax.text(i, 0.5, f"{card.hp}", ha='center', va='center', color='white', fontweight='bold')
        
        # Add player info
        self.ax.text(0.5, 1.2, f"Turn: {game_env.turn_count}", ha='center', va='center', fontsize=12)
        self.ax.text(0.5, 1.1, f"Player 1 Elixir: {player1.elixir}/{player1.max_elixir}", ha='center', va='center', color='blue')
        self.ax.text(9.5, 1.1, f"Player 2 Elixir: {player2.elixir}/{player2.max_elixir}", ha='center', va='center', color='red')
        
        # Add game over message if applicable
        if game_env.game_over:
            self.ax.text(5, 0.5, f"GAME OVER! Player {game_env.winner} wins!", 
                     ha='center', va='center', fontsize=16, color='green',
                     bbox=dict(facecolor='white', alpha=0.8))
        
        # Update the plot
        self.fig.canvas.draw()
        plt.pause(0.01)
    
    def close(self):
        """Close the visualizer."""
        if self.use_matplotlib and self.fig:
            plt.close(self.fig)


def run_visualization(player1_type="ai", player2_type="ai", delay=2.0, turns=100, 
                     difficulty=1, use_ascii=True, use_matplotlib=False):
    """
    Run a visualization of the game.
    
    Args:
        player1_type: Type of player 1 ("human" or "ai")
        player2_type: Type of player 2 ("human" or "ai")
        delay: Delay between turns in seconds (default: 2.0)
        turns: Maximum number of turns
        difficulty: AI difficulty level (default: 1)
        use_ascii: Whether to use ASCII visualization
        use_matplotlib: Whether to use matplotlib visualization
    """
    # Initialize game environment
    game_env = GameEnvironment(grid_size=10)
    
    # Create card decks for players
    sample_cards = create_sample_cards()
    
    # Shuffle the cards for fair distribution
    random.shuffle(sample_cards)
    
    # Split cards evenly between players after shuffling
    half = len(sample_cards) // 2
    player1_cards = sample_cards[:half]
    player2_cards = sample_cards[half:]
    
    # Ensure both players have cards with a good mix of attributes
    player1_deck = CardDeck(player1_cards)
    player2_deck = CardDeck(player2_cards)
    
    # Print card distribution for debugging (optional)
    print("Player 1 cards:", ", ".join(str(card) for card in player1_deck))
    print("Player 2 cards:", ", ".join(str(card) for card in player2_deck))
    print()
    
    # Create players based on type
    if player1_type.lower() == "ai":
        player1 = AIPlayer(1, player1_deck, difficulty=difficulty)
    else:
        player1 = Player(1, player1_deck)
    
    if player2_type.lower() == "ai":
        player2 = AIPlayer(2, player2_deck, difficulty=difficulty)
    else:
        player2 = Player(2, player2_deck)
    
    # Create visualizer
    visualizer = GameVisualizer(use_ascii=use_ascii, use_matplotlib=use_matplotlib, delay=delay)
    
    try:
        # Main game loop
        for turn in range(1, turns + 1):
            # Process player actions
            if isinstance(player1, AIPlayer):
                player1.make_move(game_env)
            
            if isinstance(player2, AIPlayer):
                player2.make_move(game_env)
            
            # Process turn in game environment
            state = game_env.process_turn()
            
            # Generate elixir for players
            player1.generate_elixir()
            player2.generate_elixir()
            
            # Visualize the current state
            visualizer.visualize_state(game_env, player1, player2)
            
            # Check if game is over
            if state["game_over"]:
                # Show the final state a bit longer
                time.sleep(2 * delay)
                break
                
    except KeyboardInterrupt:
        print("\nVisualization stopped by user.")
    
    finally:
        visualizer.close()


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
    parser.add_argument("--difficulty", type=int, choices=[1, 2, 3], default=1, 
                       help="AI difficulty (1: Easy, 2: Medium, 3: Hard, default: 1)")
    parser.add_argument("--ascii", action="store_true", default=True,
                       help="Use ASCII visualization (default: True)")
    parser.add_argument("--plot", action="store_true", default=False,
                       help="Use matplotlib visualization (default: False)")
    
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