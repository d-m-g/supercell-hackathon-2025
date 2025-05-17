import os
import random
import argparse
from datetime import datetime

# Import game modules
from game.environment import GameEnvironment
from game.card import Card, CardDeck, create_sample_cards
from game.player import Player, AIPlayer

# Import replay modules
from replay.recorder import ReplayRecorder, ReplayLoader
from replay.recorder import get_replay_summary

def run_game(player1_type="human", player2_type="ai", turns=100, difficulty=2, seed=None, batch_index=None):
    """
    Run a single game between two players.
    
    Args:
        player1_type: "human" or "ai"
        player2_type: "human" or "ai"
        turns: Maximum number of turns
        difficulty: AI difficulty (1-3)
        seed: Random seed for reproducibility (optional)
        batch_index: Index for batch-generated replays (optional)
        
    Returns:
        Path to the saved replay file
    """
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Initialize game environment
    game_env = GameEnvironment(grid_size=18)  # Updated to 18x1 grid
    
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
    
    # Initialize replay recorder
    recorder = ReplayRecorder()
    recorder.add_metadata("player1_type", player1_type)
    recorder.add_metadata("player2_type", player2_type)
    recorder.add_metadata("difficulty", difficulty)
    recorder.add_metadata("grid_size", 18)
    recorder.add_metadata("player1_cards", [str(card) for card in player1_deck])
    recorder.add_metadata("player2_cards", [str(card) for card in player2_deck])
    if seed is not None:
        recorder.add_metadata("seed", seed)
    
    # Main game loop
    for turn in range(1, turns + 1):
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
        
        # Record game state
        recorder.record_state(game_env._get_state())
        
        # Check if game is over
        if game_env.game_over:
            break
    
    # Save replay
    return recorder.save(batch_index=batch_index)

def batch_generate_replays(count=10, player1_type="ai", player2_type="ai", turns=100, difficulty=2):
    """
    Generate multiple game replays.
    
    Args:
        count: Number of replays to generate
        player1_type: Type of player 1 ("human" or "ai")
        player2_type: Type of player 2 ("human" or "ai")
        turns: Maximum number of turns
        difficulty: AI difficulty level (1-3)
        
    Returns:
        List of paths to saved replay files
    """
    replay_paths = []
    
    print(f"Generating {count} replays...")
    for i in range(count):
        # Use the index as a seed for reproducibility
        replay_path = run_game(
            player1_type=player1_type,
            player2_type=player2_type,
            turns=turns,
            difficulty=difficulty,
            seed=i,
            batch_index=i
        )
        replay_paths.append(replay_path)
        print(f"Generated replay {i+1}/{count}: {os.path.basename(replay_path)}")
    
    return replay_paths

def main():
    """Main function to parse arguments and run the game."""
    parser = argparse.ArgumentParser(description="Clash Royale Prototype")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Parser for the 'play' command
    play_parser = subparsers.add_parser("play", help="Play a single game")
    play_parser.add_argument("--player1", choices=["human", "ai"], default="ai", help="Player 1 type")
    play_parser.add_argument("--player2", choices=["human", "ai"], default="ai", help="Player 2 type")
    play_parser.add_argument("--turns", type=int, default=100, help="Maximum number of turns")
    play_parser.add_argument("--difficulty", type=int, choices=[1, 2, 3], default=2, help="AI difficulty")
    play_parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    # Parser for the 'batch' command
    batch_parser = subparsers.add_parser("batch", help="Generate a batch of replays")
    batch_parser.add_argument("--count", type=int, default=10, help="Number of replays to generate")
    batch_parser.add_argument("--player1", choices=["human", "ai"], default="ai", help="Player 1 type")
    batch_parser.add_argument("--player2", choices=["human", "ai"], default="ai", help="Player 2 type")
    batch_parser.add_argument("--turns", type=int, default=100, help="Maximum number of turns")
    batch_parser.add_argument("--difficulty", type=int, choices=[1, 2, 3], default=2, help="AI difficulty")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("replays", exist_ok=True)
    
    # Handle commands
    if args.command == "play":
        replay_path = run_game(
            args.player1, 
            args.player2, 
            args.turns, 
            args.difficulty,
            args.seed
        )
        print(f"Game completed! Replay saved to: {replay_path}")
        
    elif args.command == "batch":
        replay_paths = batch_generate_replays(
            args.count,
            args.player1,
            args.player2,
            args.turns,
            args.difficulty
        )
        print(f"\nGenerated {len(replay_paths)} replays in the 'replays' directory")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 