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

def run_game(player1_type="human", player2_type="ai", turns=100, difficulty=2):
    """
    Run a single game between two players.
    
    Args:
        player1_type: "human" or "ai"
        player2_type: "human" or "ai"
        turns: Maximum number of turns
        difficulty: AI difficulty (1-3)
        
    Returns:
        Path to the saved replay file
    """
    # Initialize game environment
    game_env = GameEnvironment(grid_size=10)
    
    # Create card decks for players
    sample_cards = create_sample_cards()
    
    # Shuffle cards for variety
    random.shuffle(sample_cards)
    player1_deck = CardDeck(sample_cards[:3])  # Each player gets 3 cards
    
    random.shuffle(sample_cards)
    player2_deck = CardDeck(sample_cards[:3])
    
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
        
        # Record state
        recorder.record_state(state)
        
        # Check if game is over
        if state["game_over"]:
            break
    
    # Save replay
    replay_path = recorder.save()
    
    return replay_path

def batch_generate_replays(count=10, all_ai=True, difficulty=2):
    """
    Generate a batch of replays.
    
    Args:
        count: Number of replays to generate
        all_ai: Whether all games should be AI vs AI
        difficulty: AI difficulty level
        
    Returns:
        List of paths to generated replay files
    """
    replay_paths = []
    
    for i in range(count):
        print(f"Generating replay {i+1}/{count}...")
        
        if all_ai:
            player1_type = "ai"
            player2_type = "ai"
        else:
            # Randomly decide player types for variety
            player1_type = random.choice(["human", "ai"])
            player2_type = random.choice(["human", "ai"])
        
        # For "human" player, AI will actually play, just logging as human for analysis
        replay_path = run_game(player1_type, player2_type, difficulty=difficulty)
        replay_paths.append(replay_path)
    
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
    
    # Parser for the 'batch' command
    batch_parser = subparsers.add_parser("batch", help="Generate a batch of replays")
    batch_parser.add_argument("--count", type=int, default=10, help="Number of replays to generate")
    batch_parser.add_argument("--all-ai", action="store_true", help="All games are AI vs AI")
    batch_parser.add_argument("--difficulty", type=int, choices=[1, 2, 3], default=2, help="AI difficulty")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("replays", exist_ok=True)
    
    # Handle commands
    if args.command == "play":
        replay_path = run_game(args.player1, args.player2, args.turns, args.difficulty)
        print(f"Game completed! Replay saved to: {replay_path}")
        
    elif args.command == "batch":
        replay_paths = batch_generate_replays(args.count, args.all_ai, args.difficulty)
        print(f"Generated {len(replay_paths)} replays in the 'replays' directory.")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 