import matplotlib.pyplot as plt
import numpy as np
import os
import json
from matplotlib.colors import LinearSegmentedColormap


class ReplayVisualizer:
    """
    Visualizes replay data for analysis.
    """
    
    def __init__(self, replay_data, output_dir="analysis_results"):
        """
        Initialize the visualizer with replay data.
        
        Args:
            replay_data: Loaded replay data dictionary
            output_dir: Directory to save visualizations
        """
        self.metadata = replay_data.get("metadata", {})
        self.states = replay_data.get("states", [])
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_unit_count_over_time(self, filename="unit_count_over_time.png"):
        """
        Plot the number of units for each player over time.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved plot
        """
        # Extract turn number and unit counts
        turns = []
        player1_units = []
        player2_units = []
        
        for state in self.states:
            turns.append(state["turn"])
            
            # Count units by player
            p1_count = 0
            p2_count = 0
            for unit_data in state.get("units", {}).values():
                if unit_data["owner"] == 1:
                    p1_count += 1
                elif unit_data["owner"] == 2:
                    p2_count += 1
            
            player1_units.append(p1_count)
            player2_units.append(p2_count)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(turns, player1_units, 'b-', label='Player 1')
        plt.plot(turns, player2_units, 'r-', label='Player 2')
        plt.xlabel('Turn')
        plt.ylabel('Unit Count')
        plt.title('Unit Count Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save the plot
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        plt.close()
        
        return filepath
    
    def plot_battle_flow(self, filename="battle_flow.png"):
        """
        Plot the battle flow showing the advantage over time.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved plot
        """
        # Extract turn number and advantage
        turns = []
        advantage = []
        
        for state in self.states:
            turns.append(state["turn"])
            
            # Calculate advantage (player1 units - player2 units)
            p1_count = 0
            p2_count = 0
            for unit_data in state.get("units", {}).values():
                if unit_data["owner"] == 1:
                    p1_count += 1
                elif unit_data["owner"] == 2:
                    p2_count += 1
            
            advantage.append(p1_count - p2_count)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.plot(turns, advantage, 'g-')
        
        # Shade the regions
        plt.fill_between(turns, advantage, 0, where=(np.array(advantage) > 0), 
                         interpolate=True, color='blue', alpha=0.3, label='Player 1 Advantage')
        plt.fill_between(turns, advantage, 0, where=(np.array(advantage) < 0), 
                         interpolate=True, color='red', alpha=0.3, label='Player 2 Advantage')
        
        plt.xlabel('Turn')
        plt.ylabel('Advantage (P1 - P2)')
        plt.title('Battle Flow')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save the plot
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        plt.close()
        
        return filepath
    
    def plot_heatmap(self, filename="grid_heatmap.png"):
        """
        Plot a heatmap showing the frequency of unit positions.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved plot
        """
        # Initialize heatmap data for each player
        grid_size = 10  # Assuming a 10x1 grid
        p1_heatmap = np.zeros(grid_size)
        p2_heatmap = np.zeros(grid_size)
        
        # Count unit positions
        for state in self.states:
            for unit_data in state.get("units", {}).values():
                position = unit_data["position"]
                owner = unit_data["owner"]
                
                if 0 <= position < grid_size:
                    if owner == 1:
                        p1_heatmap[position] += 1
                    elif owner == 2:
                        p2_heatmap[position] += 1
        
        # Normalize the data
        max_count = max(np.max(p1_heatmap), np.max(p2_heatmap))
        if max_count > 0:
            p1_heatmap = p1_heatmap / max_count
            p2_heatmap = p2_heatmap / max_count
        
        # Create a combined heatmap (positive for player 1, negative for player 2)
        combined_heatmap = p1_heatmap - p2_heatmap
        
        # Create a custom colormap for the combined heatmap
        colors = [(0.0, 0.0, 1.0), (1.0, 1.0, 1.0), (1.0, 0.0, 0.0)]  # Blue -> White -> Red
        cmap = LinearSegmentedColormap.from_list('player_cmap', colors, N=100)
        
        # Create the heatmap plot
        plt.figure(figsize=(12, 3))
        
        # Plot the actual 1D heatmap
        plt.imshow([combined_heatmap], cmap=cmap, aspect='auto', vmin=-1, vmax=1)
        
        # Add a colorbar
        cbar = plt.colorbar(orientation='horizontal')
        cbar.set_label('Player Dominance (Blue: P1, Red: P2)')
        
        # Add grid positions
        plt.xticks(range(grid_size))
        plt.yticks([])  # Hide y-axis ticks since it's a 1D grid
        
        # Add labels and title
        plt.xlabel('Grid Position')
        plt.title('Grid Position Heatmap')
        
        # Add tower indicators
        plt.text(0, 0, 'T1', ha='center', va='center', color='green', fontweight='bold')
        plt.text(grid_size-1, 0, 'T2', ha='center', va='center', color='green', fontweight='bold')
        
        # Save the plot
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        plt.close()
        
        return filepath
    
    def plot_card_usage(self, filename="card_usage.png"):
        """
        Plot card usage statistics.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved plot
        """
        # Count card appearances by approximating from attack and hp values
        card_counts = {1: {}, 2: {}}
        
        for state in self.states:
            for unit_data in state.get("units", {}).values():
                owner = unit_data["owner"]
                attack = unit_data["attack"]
                hp = unit_data["hp"]
                
                # Use attack and HP as a card identifier
                card_id = f"ATK:{attack},HP:{hp}"
                
                if card_id not in card_counts[owner]:
                    card_counts[owner][card_id] = 0
                
                card_counts[owner][card_id] += 1
        
        # Prepare data for plotting
        p1_cards = list(card_counts[1].keys())
        p1_counts = list(card_counts[1].values())
        p2_cards = list(card_counts[2].keys())
        p2_counts = list(card_counts[2].values())
        
        # Create the plot (side by side bar charts)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Player 1 card usage
        if p1_cards:
            ax1.bar(p1_cards, p1_counts, color='blue')
            ax1.set_title('Player 1 Card Usage')
            ax1.set_xlabel('Card Type')
            ax1.set_ylabel('Count')
            ax1.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax1.set_title('Player 1 Card Usage')
        
        # Player 2 card usage
        if p2_cards:
            ax2.bar(p2_cards, p2_counts, color='red')
            ax2.set_title('Player 2 Card Usage')
            ax2.set_xlabel('Card Type')
            ax2.set_ylabel('Count')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax2.set_title('Player 2 Card Usage')
        
        plt.tight_layout()
        
        # Save the plot
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath)
        plt.close()
        
        return filepath
    
    def generate_all_visualizations(self):
        """
        Generate all visualizations for a replay.
        
        Returns:
            Dictionary of visualization filenames
        """
        visualizations = {}
        
        visualizations["unit_count"] = self.plot_unit_count_over_time()
        visualizations["battle_flow"] = self.plot_battle_flow()
        visualizations["heatmap"] = self.plot_heatmap()
        visualizations["card_usage"] = self.plot_card_usage()
        
        # Create a summary JSON with paths to all visualizations
        summary = {
            "replay_metadata": self.metadata,
            "visualizations": visualizations
        }
        
        summary_path = os.path.join(self.output_dir, "visualization_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return visualizations 