#!/usr/bin/env python
"""
Clash Royale Prototype Visualization Runner

This script provides a convenient way to run the game visualization or record replays.
"""

import sys
import os
from src.visualize_game import run_visualization
from src.replay.recorder import ReplayRecorder
from src.game.environment import GameEnvironment
from src.game.card import CardDeck, create_sample_cards
from src.game.player import Player, AIPlayer
import random

def run_game_recording(player1_type="ai", player2_type="ai", turns=100, difficulty=1, seed=None):
    """
    Run a game without visualization and record it as a replay.
    
    Args:
        player1_type: Type of player 1 ("human" or "ai")
        player2_type: Type of player 2 ("human" or "ai")
        turns: Maximum number of turns
        difficulty: AI difficulty level (1-3)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        Path to the saved replay file
    """
    # Set random seed if provided
    if seed is not None:
        random.seed(seed)
    
    # Initialize game environment
    game_env = GameEnvironment(grid_size=10)
    
    # Create and shuffle card decks
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
    
    # Save the replay
    return recorder.save()

def generate_batch_replays(count, player1_type="ai", player2_type="ai", turns=100, difficulty=1):
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
        replay_path = run_game_recording(
            player1_type=player1_type,
            player2_type=player2_type,
            turns=turns,
            difficulty=difficulty,
            seed=i
        )
        replay_paths.append(replay_path)
        print(f"Generated replay {i+1}/{count}: {os.path.basename(replay_path)}")
    
    return replay_paths

def main():
    """Run the visualization or recording with default settings."""
    # Check if matplotlib is available
    try:
        import matplotlib
        has_matplotlib = True
    except ImportError:
        has_matplotlib = False
        print("Note: Matplotlib is not installed. Only ASCII visualization will be used.")
    
    # Default settings
    settings = {
        "player1_type": "ai",
        "player2_type": "ai",
        "delay": 2.0,
        "turns": 100,
        "difficulty": 1,
        "use_ascii": True,
        "use_matplotlib": has_matplotlib,
        "record": False,
        "count": 1
    }
    
    # Parse command-line arguments
    args = sys.argv[1:]
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == "--record":
            settings["record"] = True
        elif arg == "--count" and i + 1 < len(args):
            try:
                count = int(args[i+1])
                if count < 1:
                    print(f"Error: Count must be at least 1, not {count}")
                    return 1
                settings["count"] = count
                i += 1
            except ValueError:
                print(f"Error: Invalid count value: {args[i+1]}")
                return 1
        elif arg == "--ascii-only":
            settings["use_matplotlib"] = False
        elif arg == "--plot-only":
            settings["use_ascii"] = False
            settings["use_matplotlib"] = has_matplotlib
        elif arg == "--both":
            settings["use_ascii"] = True
            settings["use_matplotlib"] = has_matplotlib
        elif arg == "--delay" and i + 1 < len(args):
            try:
                settings["delay"] = float(args[i+1])
                i += 1
            except ValueError:
                print(f"Error: Invalid delay value: {args[i+1]}")
                return 1
        elif arg == "--turns" and i + 1 < len(args):
            try:
                settings["turns"] = int(args[i+1])
                i += 1
            except ValueError:
                print(f"Error: Invalid turns value: {args[i+1]}")
                return 1
        elif arg == "--difficulty" and i + 1 < len(args):
            try:
                diff = int(args[i+1])
                if diff not in (1, 2, 3):
                    print(f"Error: Difficulty must be 1, 2, or 3, not {diff}")
                    return 1
                settings["difficulty"] = diff
                i += 1
            except ValueError:
                print(f"Error: Invalid difficulty value: {args[i+1]}")
                return 1
        elif arg == "--player1" and i + 1 < len(args):
            player_type = args[i+1].lower()
            if player_type not in ("human", "ai"):
                print(f"Error: Player type must be 'human' or 'ai', not {player_type}")
                return 1
            settings["player1_type"] = player_type
            i += 1
        elif arg == "--player2" and i + 1 < len(args):
            player_type = args[i+1].lower()
            if player_type not in ("human", "ai"):
                print(f"Error: Player type must be 'human' or 'ai', not {player_type}")
                return 1
            settings["player2_type"] = player_type
            i += 1
        elif arg == "--help" or arg == "-h":
            print_help()
            return 0
        else:
            print(f"Error: Unknown argument: {arg}")
            print_help()
            return 1
            
        i += 1
    
    if settings["record"]:
        # Run game recording
        print("Starting Clash Royale Prototype Recording...")
        print(f"Player 1: {settings['player1_type'].upper()}")
        print(f"Player 2: {settings['player2_type'].upper()}")
        print(f"Difficulty: {settings['difficulty']}")
        print(f"Max turns: {settings['turns']}")
        print()
        
        if settings["count"] > 1:
            replay_paths = generate_batch_replays(
                count=settings["count"],
                player1_type=settings["player1_type"],
                player2_type=settings["player2_type"],
                turns=settings["turns"],
                difficulty=settings["difficulty"]
            )
            print(f"\nGenerated {len(replay_paths)} replays in the 'replays' directory")
        else:
            replay_path = run_game_recording(
                player1_type=settings["player1_type"],
                player2_type=settings["player2_type"],
                turns=settings["turns"],
                difficulty=settings["difficulty"]
            )
            print(f"Game completed! Replay saved to: {replay_path}")
    else:
        # Run visualization
        print("Starting Clash Royale Prototype Visualization...")
        print(f"Player 1: {settings['player1_type'].upper()}")
        print(f"Player 2: {settings['player2_type'].upper()}")
        print(f"Difficulty: {settings['difficulty']}")
        print(f"Visualization: {'ASCII' if settings['use_ascii'] else ''}{' and ' if settings['use_ascii'] and settings['use_matplotlib'] else ''}{'Graphical' if settings['use_matplotlib'] else ''}")
        print(f"Delay: {settings['delay']} seconds")
        print(f"Max turns: {settings['turns']}")
        print()
        print("Press Ctrl+C to stop the visualization at any time.")
        print()
        
        run_visualization(
            player1_type=settings["player1_type"],
            player2_type=settings["player2_type"],
            delay=settings["delay"],
            turns=settings["turns"],
            difficulty=settings["difficulty"],
            use_ascii=settings["use_ascii"],
            use_matplotlib=settings["use_matplotlib"]
        )
    
    return 0


def print_help():
    """Print help information."""
    print("""
Clash Royale Prototype Visualization/Recording

Usage: python visualize.py [options]

Options:
  --record             Run game without visualization and save as replay
  --count VALUE        Number of replays to generate (default: 1)
  --ascii-only         Use only ASCII visualization (default if matplotlib not available)
  --plot-only          Use only graphical (matplotlib) visualization
  --both               Use both ASCII and graphical visualization (default)
  --delay VALUE        Set delay between turns in seconds (default: 2.0)
  --turns VALUE        Set maximum number of turns (default: 100)
  --difficulty VALUE   Set AI difficulty (1: Easy, 2: Medium, 3: Hard, default: 1)
  --player1 TYPE       Set player 1 type (human or ai, default: ai)
  --player2 TYPE       Set player 2 type (human or ai, default: ai)
  --help, -h           Show this help message and exit

Examples:
  # Generate a single replay
  python visualize.py --record --difficulty 1

  # Generate 10 replays with different random seeds
  python visualize.py --record --count 10 --difficulty 1

  # Run a visualized game
  python visualize.py --both --delay 1.0
""")


if __name__ == "__main__":
    sys.exit(main()) 