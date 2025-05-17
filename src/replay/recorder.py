import json
import os
import time
from datetime import datetime

class ReplayRecorder:
    """
    Records game states for replay and analysis.
    """
    
    def __init__(self, base_dir="replays"):
        self.base_dir = base_dir
        self.states = []
        self.metadata = {
            "start_time": time.time(),
            "game_version": "0.1",
            "replay_version": "0.1"
        }
        
        # Create replays directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
    
    def record_state(self, state):
        """
        Record a game state.
        
        Args:
            state: Game state dictionary from GameEnvironment._get_state()
        """
        self.states.append(state)
    
    def add_metadata(self, key, value):
        """Add metadata to the replay."""
        self.metadata[key] = value
    
    def save(self, filename=None, batch_index=None):
        """
        Save the replay to a file.
        
        Args:
            filename: Custom filename, if None a timestamp-based name will be generated
            batch_index: Optional index for batch-generated replays
            
        Returns:
            The path to the saved replay file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if batch_index is not None:
                filename = f"replay_{timestamp}_batch{batch_index:03d}.json"
            else:
                filename = f"replay_{timestamp}.json"
        
        # Add end time to metadata
        self.metadata["end_time"] = time.time()
        self.metadata["duration"] = self.metadata["end_time"] - self.metadata["start_time"]
        self.metadata["turn_count"] = len(self.states)
        
        # Add game result to metadata
        if self.states and self.states[-1]["game_over"]:
            self.metadata["winner"] = self.states[-1]["winner"]
        
        # Add batch index to metadata if provided
        if batch_index is not None:
            self.metadata["batch_index"] = batch_index
        
        # Prepare final replay data
        replay_data = {
            "metadata": self.metadata,
            "states": self.states
        }
        
        # Save to file
        filepath = os.path.join(self.base_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(replay_data, f, indent=2)
        
        return filepath
    
    def __len__(self):
        return len(self.states)


class ReplayLoader:
    """
    Loads replay data from file for analysis or playback.
    """
    
    def __init__(self, base_dir="replays"):
        self.base_dir = base_dir
    
    def load(self, filename):
        """
        Load a replay from file.
        
        Args:
            filename: The replay filename
            
        Returns:
            Replay data dictionary or None if file not found
        """
        filepath = os.path.join(self.base_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading replay: {e}")
            return None
    
    def list_replays(self):
        """
        List all available replay files.
        
        Returns:
            List of replay filenames
        """
        try:
            return [f for f in os.listdir(self.base_dir) if f.endswith('.json')]
        except FileNotFoundError:
            return []


def get_replay_summary(replay_data):
    """
    Generate a summary of a replay.
    
    Args:
        replay_data: Loaded replay data
        
    Returns:
        Dictionary with replay summary information
    """
    if not replay_data:
        return {"error": "Invalid replay data"}
    
    metadata = replay_data.get("metadata", {})
    states = replay_data.get("states", [])
    
    summary = {
        "duration": metadata.get("duration", 0),
        "turns": len(states),
        "winner": metadata.get("winner"),
        "start_time": datetime.fromtimestamp(metadata.get("start_time", 0)).strftime("%Y-%m-%d %H:%M:%S"),
        "game_version": metadata.get("game_version", "unknown")
    }
    
    # Add more detailed statistics if states are available
    if states:
        # Count units played by each player
        units_played = {1: 0, 2: 0}
        
        # Track units on field at end of each turn
        units_over_time = []
        
        for state in states:
            # Count units by owner
            units_by_owner = {1: 0, 2: 0}
            for unit_data in state.get("units", {}).values():
                units_by_owner[unit_data["owner"]] += 1
            
            units_over_time.append(units_by_owner)
        
        # Calculate unit statistics
        summary["max_units"] = {
            1: max([u.get(1, 0) for u in units_over_time]),
            2: max([u.get(2, 0) for u in units_over_time])
        }
        
        summary["avg_units"] = {
            1: sum([u.get(1, 0) for u in units_over_time]) / len(units_over_time),
            2: sum([u.get(2, 0) for u in units_over_time]) / len(units_over_time)
        }
    
    return summary 