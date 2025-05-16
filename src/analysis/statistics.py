import json
import os
import numpy as np
from collections import Counter, defaultdict


class ReplayAnalyzer:
    """
    Analyzes replay data to extract insights and patterns.
    """
    
    def __init__(self, replay_data):
        """
        Initialize the analyzer with replay data.
        
        Args:
            replay_data: Loaded replay data dictionary
        """
        self.metadata = replay_data.get("metadata", {})
        self.states = replay_data.get("states", [])
        self.winner = self.metadata.get("winner")
        self.turn_count = len(self.states)
    
    def get_card_usage_stats(self):
        """
        Analyze card usage patterns.
        
        Returns:
            Dictionary with card usage statistics
        """
        # Track card appearances by player
        card_appearances = {1: Counter(), 2: Counter()}
        
        # Track when cards were played
        card_timings = defaultdict(list)
        
        for i, state in enumerate(self.states):
            for unit_id, unit_data in state.get("units", {}).items():
                owner = unit_data["owner"]
                # We're approximating the card name here since it's not stored in unit data
                # In a real implementation, you would store the card name in the unit data
                card_name = f"Card-{unit_data['attack']}-{unit_data['hp']}"
                card_appearances[owner][card_name] += 1
                
                # If this is the first time we're seeing this unit, assume it was just played
                if i > 0 and unit_id not in self.states[i-1].get("units", {}):
                    card_timings[card_name].append(i)
        
        # Calculate statistics
        stats = {
            "card_frequency": {
                1: dict(card_appearances[1]),
                2: dict(card_appearances[2])
            },
            "most_used_cards": {
                1: card_appearances[1].most_common(3),
                2: card_appearances[2].most_common(3)
            },
            "average_play_timing": {
                card: np.mean(timings) if timings else 0
                for card, timings in card_timings.items()
            }
        }
        
        return stats
    
    def get_elixir_efficiency(self):
        """
        Calculate elixir efficiency metrics.
        
        Note: This is a simplified version since the replay data doesn't include elixir information.
        In a real implementation, you would record elixir values in the game state.
        
        Returns:
            Dictionary with elixir efficiency metrics
        """
        # This is a placeholder for actual elixir calculation
        # In a real implementation, you would track elixir in the game state
        return {
            "player1_efficiency": 0.75,  # Placeholder
            "player2_efficiency": 0.65,  # Placeholder
        }
    
    def get_battle_flow(self):
        """
        Analyze the flow of battle over time.
        
        Returns:
            Dictionary with battle flow statistics
        """
        # Track unit counts over time
        unit_counts = []
        
        for state in self.states:
            units = state.get("units", {})
            player1_units = sum(1 for u in units.values() if u["owner"] == 1)
            player2_units = sum(1 for u in units.values() if u["owner"] == 2)
            
            unit_counts.append({
                "turn": state["turn"],
                "player1": player1_units,
                "player2": player2_units,
                "advantage": player1_units - player2_units
            })
        
        # Identify turning points (when advantage changes sign)
        turning_points = []
        for i in range(1, len(unit_counts)):
            prev_advantage = unit_counts[i-1]["advantage"]
            curr_advantage = unit_counts[i]["advantage"]
            
            if (prev_advantage > 0 and curr_advantage <= 0) or (prev_advantage < 0 and curr_advantage >= 0):
                turning_points.append({
                    "turn": unit_counts[i]["turn"],
                    "prev_advantage": prev_advantage,
                    "new_advantage": curr_advantage
                })
        
        return {
            "unit_counts": unit_counts,
            "turning_points": turning_points,
            "player1_avg_units": np.mean([uc["player1"] for uc in unit_counts]),
            "player2_avg_units": np.mean([uc["player2"] for uc in unit_counts])
        }
    
    def get_win_factors(self):
        """
        Identify factors that contributed to the victory.
        
        Returns:
            Dictionary with potential win factors
        """
        if not self.winner:
            return {"error": "No winner information available"}
        
        # Analyze the final state
        final_state = self.states[-1] if self.states else None
        if not final_state:
            return {"error": "No final state available"}
        
        # Get battle flow data
        battle_flow = self.get_battle_flow()
        
        # Calculate momentum (advantage over last 3 turns)
        momentum = 0
        if len(battle_flow["unit_counts"]) >= 3:
            last_three = battle_flow["unit_counts"][-3:]
            momentum = sum(uc["advantage"] for uc in last_three) / 3
        
        # Determine win factors
        win_factors = {
            "winner": self.winner,
            "turn_count": self.turn_count,
            "final_units": {},
            "momentum": momentum,
            "turning_points_count": len(battle_flow["turning_points"]),
        }
        
        # Count units in final state
        units = final_state.get("units", {})
        win_factors["final_units"][1] = sum(1 for u in units.values() if u["owner"] == 1)
        win_factors["final_units"][2] = sum(1 for u in units.values() if u["owner"] == 2)
        
        # Determine win type
        if self.turn_count < 10:
            win_factors["win_type"] = "quick_victory"
        elif momentum * (1 if self.winner == 1 else -1) > 2:
            win_factors["win_type"] = "momentum_based"
        elif len(battle_flow["turning_points"]) > 3:
            win_factors["win_type"] = "back_and_forth"
        else:
            win_factors["win_type"] = "steady_advance"
        
        return win_factors


def analyze_multiple_replays(replays_dir="replays", output_dir="analysis_results"):
    """
    Analyze multiple replay files and generate aggregate statistics.
    
    Args:
        replays_dir: Directory containing replay files
        output_dir: Directory to save analysis results
        
    Returns:
        Dictionary with aggregate statistics
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load all replay files
    replay_files = [f for f in os.listdir(replays_dir) if f.endswith('.json')]
    
    if not replay_files:
        return {"error": "No replay files found"}
    
    # Aggregate data
    wins = {1: 0, 2: 0}
    turn_counts = []
    win_types = Counter()
    
    for replay_file in replay_files:
        try:
            with open(os.path.join(replays_dir, replay_file), 'r') as f:
                replay_data = json.load(f)
                
            analyzer = ReplayAnalyzer(replay_data)
            
            # Count wins
            winner = analyzer.winner
            if winner in (1, 2):
                wins[winner] += 1
            
            # Record turn count
            turn_counts.append(analyzer.turn_count)
            
            # Record win type
            win_factors = analyzer.get_win_factors()
            if "win_type" in win_factors:
                win_types[win_factors["win_type"]] += 1
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error analyzing {replay_file}: {e}")
    
    # Calculate aggregate statistics
    stats = {
        "total_replays": len(replay_files),
        "wins": wins,
        "win_ratio": {
            1: wins[1] / len(replay_files) if len(replay_files) > 0 else 0,
            2: wins[2] / len(replay_files) if len(replay_files) > 0 else 0
        },
        "avg_turn_count": np.mean(turn_counts) if turn_counts else 0,
        "min_turn_count": min(turn_counts) if turn_counts else 0,
        "max_turn_count": max(turn_counts) if turn_counts else 0,
        "win_types": dict(win_types)
    }
    
    # Save aggregate statistics
    with open(os.path.join(output_dir, "aggregate_stats.json"), 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats 