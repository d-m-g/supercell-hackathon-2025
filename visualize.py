#!/usr/bin/env python
"""
Clash Royale Prototype Visualization Runner

This script provides a convenient way to run the game visualization.
"""

import sys
import os
from src.visualize_game import run_visualization

def main():
    """Run the visualization with default settings."""
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
        "use_matplotlib": has_matplotlib
    }
    
    # Parse command-line arguments
    args = sys.argv[1:]
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == "--ascii-only":
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
    
    # Run the visualization
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
Clash Royale Prototype Visualization

Usage: python visualize.py [options]

Options:
  --ascii-only         Use only ASCII visualization (default if matplotlib not available)
  --plot-only          Use only graphical (matplotlib) visualization
  --both               Use both ASCII and graphical visualization (default)
  --delay VALUE        Set delay between turns in seconds (default: 2.0)
  --turns VALUE        Set maximum number of turns (default: 100)
  --difficulty VALUE   Set AI difficulty (1: Easy, 2: Medium, 3: Hard, default: 1)
  --player1 TYPE       Set player 1 type (human or ai, default: ai)
  --player2 TYPE       Set player 2 type (human or ai, default: ai)
  --help, -h           Show this help message and exit
""")


if __name__ == "__main__":
    sys.exit(main()) 