import streamlit as st
import sys
import os
import time
import json
import random
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from matplotlib.patches import Rectangle, Circle
from pathlib import Path

# Set matplotlib to use a lower DPI to avoid DecompressionBombError
plt.rcParams['figure.dpi'] = 72
plt.rcParams['savefig.dpi'] = 72

# Fix import paths to ensure we use the local alternative_simulation.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))

# IMPORTANT: Insert current_dir at the beginning of sys.path to prioritize it
sys.path.insert(0, current_dir)

# Import elements from alternative_simulation we'll need
try:
    # Add explicit relative import to ensure we use the local version
    import alternative_simulation
    from alternative_simulation import Tower, Troop, Player, GameState
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.info(f"Attempting to import from: {current_dir}")
    st.info("Make sure alternative_simulation.py is in the correct directory")

# Import the analysis function from formula.py after importing alternative_simulation
try:
    # Only add project_root after alternative_simulation is imported
    sys.path.append(project_root)
    from formula import analyze_replay
except ImportError:
    # Create a wrapper function if import fails
    def analyze_replay(replay_path):
        return None, "Could not import analysis module"

class StreamlitVisualizer:
    def __init__(self):
        self.colors = {
            'player': 'blue',
            'enemy': 'red',
            'background': '#f0f0f0',
            'lane': '#d0d0d0',
            'elixir': 'purple'
        }
        
        # Constants taken from original game
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.LANE_WIDTH = 120
        self.PLAYER_ELIXIR_MAX = 10
        
    def visualize_game_state(self, game_state):
        """Visualize the current game state using matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 6), dpi=72)

        # Set background
        ax.set_facecolor(self.colors['background'])
        ax.set_xlim(0, self.SCREEN_WIDTH)
        ax.set_ylim(0, self.SCREEN_HEIGHT)
    
        # Draw lane
        lane_rect = Rectangle(
            ((self.SCREEN_WIDTH - self.LANE_WIDTH) // 2, 0),
            self.LANE_WIDTH, self.SCREEN_HEIGHT,
            color=self.colors['lane']
        )
        ax.add_patch(lane_rect)
        
        # Draw towers
        for tower in game_state.towers:
            self._draw_tower(ax, tower)
        
        # Draw troops
        for troop in game_state.troops:
            self._draw_troop(ax, troop)
        
        # Remove axis ticks for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add game info as text
        if game_state.game_over:
            winner_text = "PLAYER WINS!" if game_state.winner == 'player' else "ENEMY WINS!"
            ax.text(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2, winner_text, 
                   fontsize=24, ha='center', va='center',
                   color=self.colors[game_state.winner],
                   bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def _draw_tower(self, ax, tower):
        """Draw a tower on the matplotlib axis"""
        tower_color = self.colors[tower.team]
        
        # Draw tower body
        tower_rect = Rectangle(
            (tower.position[0] - tower.width // 2, tower.position[1] - tower.height // 2),
            tower.width, tower.height,
            color=tower_color
        )
        ax.add_patch(tower_rect)
        
        # Draw health bar
        health_ratio = tower.hp / tower.max_hp
        health_bar_width = tower.width
        health_bar_height = 10
        
        # Health bar background
        health_bg = Rectangle(
            (tower.position[0] - health_bar_width // 2, tower.position[1] - tower.height // 2 - 15),
            health_bar_width, health_bar_height,
            facecolor='white', edgecolor='black'
        )
        ax.add_patch(health_bg)
        
        # Health bar fill
        if health_ratio > 0:
            health_fill = Rectangle(
                (tower.position[0] - health_bar_width // 2, tower.position[1] - tower.height // 2 - 15),
                health_bar_width * health_ratio, health_bar_height,
                facecolor='green'
            )
            ax.add_patch(health_fill)
        
        # Add HP text
        ax.text(tower.position[0], tower.position[1], f"HP: {int(tower.hp)}", 
                ha='center', va='center', color='black', fontsize=10)
    
    def _draw_troop(self, ax, troop):
        """Draw a troop on the matplotlib axis"""
        troop_color = self.colors[troop.team]
        
        # Draw troop as circle
        troop_circle = Circle(
            (troop.position[0], troop.position[1]),
            troop.size,
            color=troop_color
        )
        ax.add_patch(troop_circle)
        
        # Draw health bar
        health_ratio = troop.hp / troop.max_hp
        health_bar_width = troop.size * 2
        health_bar_height = 5
        
        # Health bar background
        health_bg = Rectangle(
            (troop.position[0] - health_bar_width // 2, troop.position[1] - troop.size - 5),
            health_bar_width, health_bar_height,
            facecolor='white', edgecolor='black'
        )
        ax.add_patch(health_bg)
        
        # Health bar fill
        if health_ratio > 0:
            health_fill = Rectangle(
                (troop.position[0] - health_bar_width // 2, troop.position[1] - troop.size - 5),
                health_bar_width * health_ratio, health_bar_height,
                facecolor='green'
            )
            ax.add_patch(health_fill)
        
        # Add troop type text above
        ax.text(troop.position[0], troop.position[1] - troop.size - 10, 
                troop.troop_type, ha='center', va='center', color='black', fontsize=8)

    def draw_elixir_bar(self, player, x_pos, y_pos, width=200, height=20):
        """Create a matplotlib figure for an elixir bar"""
        fig, ax = plt.subplots(figsize=(width/50, height/50), dpi=72)
        
        # Draw elixir background
        ax.add_patch(Rectangle((0, 0), width, height, facecolor='white', edgecolor='black'))
        
        # Draw elixir fill
        elixir_ratio = player.elixir / self.PLAYER_ELIXIR_MAX
        ax.add_patch(Rectangle((0, 0), width * elixir_ratio, height, facecolor=self.colors['elixir']))
        
        # Add text
        ax.text(width/2, height/2, f"Elixir: {int(player.elixir)}/{self.PLAYER_ELIXIR_MAX}", 
                ha='center', va='center', color='white', fontweight='bold')
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.axis('off')
        
        plt.tight_layout()
        return fig

def reset_game():
    """Reset the game state completely"""
    # Create a new game state
    st.session_state.game_state = GameState()
    
    # Preserve AI setting
    if 'player_ai' in st.session_state:
        st.session_state.game_state.player.is_ai = st.session_state.player_ai
    else:
        st.session_state.game_state.player.is_ai = False
    
    # Reset other state
    st.session_state.game_tick = 0
    st.session_state.last_update_time = time.time()
    
    # Clear any figures
    plt.close('all')

def analyze_last_game():
    """Analyze the last replay using formula.py and return the results"""
    replay_dir = os.path.join(project_root, "replays")
    if not os.path.exists(replay_dir):
        return None, "No replays directory found"
    
    # Find the most recent replay file
    replay_files = [f for f in os.listdir(replay_dir) if f.endswith('.json')]
    if not replay_files:
        return None, "No replay files found"
    
    # Sort by modification time (newest first)
    replay_files.sort(key=lambda x: os.path.getmtime(os.path.join(replay_dir, x)), reverse=True)
    latest_replay = os.path.join(replay_dir, replay_files[0])
    
    try:
        # Try to run the analysis directly by importing the function
        troop_performance = analyze_replay(latest_replay)
        return troop_performance, None
    except Exception as e:
        # Fallback: Run as subprocess
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(project_root, "formula.py"), latest_replay],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout, None
        except subprocess.CalledProcessError as e:
            return None, f"Analysis failed: {e.stderr}"
        except Exception as e:
            return None, f"Error: {str(e)}"

def run_game_simulation():
    """Run the game simulation with Streamlit integration"""
    # Initialize session state if it doesn't exist
    if 'game_state' not in st.session_state:
        st.session_state.game_state = GameState()
        # Update player to not be AI for manual control
        st.session_state.game_state.player.is_ai = False
        st.session_state.visualizer = StreamlitVisualizer()
        st.session_state.game_tick = 0
        st.session_state.last_update_time = time.time()
        st.session_state.game_speed = 1.0
        st.session_state.player_ai = False
    
    # Game speed control
    st.sidebar.title("Game Controls")
    game_speed = st.sidebar.slider("Game Speed", min_value=0.1, max_value=5.0, value=st.session_state.game_speed, step=0.1)
    st.session_state.game_speed = game_speed
    
    # AI toggle
    player_ai = st.sidebar.checkbox("AI Player", value=st.session_state.game_state.player.is_ai)
    if player_ai != st.session_state.game_state.player.is_ai:
        st.session_state.game_state.player.is_ai = player_ai
    st.session_state.player_ai = player_ai
    
    # Restart button
    if st.sidebar.button("Restart Game"):
        reset_game()
    
    # Troop selection for manual deployment (sidebar)
    st.sidebar.title("Troop Selection")
    troop_options = ["Knight", "Archer", "Giant", "Goblin"]
    selected_troop = st.sidebar.selectbox("Select Troop", troop_options, index=0)
    st.session_state.game_state.selected_troop = selected_troop
    
    # Display troop stats
    st.sidebar.subheader(f"{selected_troop} Stats")
    
    # Create a dummy troop to get stats
    dummy_troop = Troop([0, 0], selected_troop, 'player', 0)
    
    st.sidebar.text(f"HP: {dummy_troop.max_hp}")
    st.sidebar.text(f"Damage: {dummy_troop.attack_damage}")
    st.sidebar.text(f"Attack Speed: {dummy_troop.attack_speed}")
    st.sidebar.text(f"Cost: {st.session_state.game_state.get_troop_cost(selected_troop)}")
    
    # Manual deployment button (if not AI player)
    if not st.session_state.game_state.player.is_ai:
        if st.sidebar.button(f"Deploy {selected_troop}"):
            # Calculate lane center
            lane_center = st.session_state.visualizer.SCREEN_WIDTH // 2
            lane_width = st.session_state.visualizer.LANE_WIDTH
            # Random position within the lane
            lane_position = lane_center + random.randint(-lane_width//4, lane_width//4)
            
            # Try to deploy the troop
            troop = st.session_state.game_state.player.deploy_troop(
                selected_troop, 
                'player',
                lane_position
            )
            
            if troop:
                st.session_state.game_state.troops.append(troop)
                st.session_state.game_state.replay_data["troops_spawned"].append({
                    "tick": st.session_state.game_state.current_tick,
                    "troop_id": id(troop),
                    "troop_type": troop.troop_type,
                    "team": troop.team,
                    "position": troop.position.copy()
                })
            else:
                st.sidebar.warning(f"Not enough elixir! Need {st.session_state.game_state.get_troop_cost(selected_troop)}")
    
    # Update game state
    current_time = time.time()
    dt = (current_time - st.session_state.last_update_time) * st.session_state.game_speed
    
    # Only update if game is not over
    if not st.session_state.game_state.game_over:
        st.session_state.game_state.update(dt / 60.0)  # Convert to seconds and apply game speed
        st.session_state.game_tick += 1
        st.session_state.last_update_time = current_time
    
    # Visualize current game state
    fig = st.session_state.visualizer.visualize_game_state(st.session_state.game_state)
    game_container = st.container()
    game_container.pyplot(fig)
    
    # Display elixir bar
    elixir_col, _ = st.columns([1, 3])
    with elixir_col:
        elixir_fig = st.session_state.visualizer.draw_elixir_bar(
            st.session_state.game_state.player, 
            20, 
            st.session_state.visualizer.SCREEN_HEIGHT - 30
        )
        st.pyplot(elixir_fig)
    
    # Game status display
    st.title("Game Status")
    
    # Display tower health
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Player Tower HP", f"{int(st.session_state.game_state.player_tower.hp)}/{st.session_state.game_state.player_tower.max_hp}")
    with col2:
        st.metric("Enemy Tower HP", f"{int(st.session_state.game_state.enemy_tower.hp)}/{st.session_state.game_state.enemy_tower.max_hp}")
    
    # Troop information
    st.subheader("Troops on Field")
    if len(st.session_state.game_state.troops) > 0:
        troop_data = []
        for troop in st.session_state.game_state.troops:
            troop_data.append({
                "Type": troop.troop_type,
                "Team": troop.team.capitalize(),
                "HP": f"{int(troop.hp)}/{troop.max_hp}",
                "Position": f"({int(troop.position[0])}, {int(troop.position[1])})"
            })
        st.table(troop_data)
    else:
        st.info("No troops on the field")
    
    # Display replay save option if game is over
    if st.session_state.game_state.game_over:
        st.header(f"Game Over - {'Player' if st.session_state.game_state.winner == 'player' else 'Enemy'} Wins!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Replay"):
                replay_path = st.session_state.game_state.save_replay()
                st.session_state.last_replay_path = replay_path
                st.success(f"Replay saved to {replay_path}")
                
        with col2:
            if st.button("New Game"):
                reset_game()
                st.experimental_rerun()
        
        # Add analyze button if a replay was saved
        if 'last_replay_path' in st.session_state:
            if st.button("Analyze Last Game"):
                with st.spinner("Analyzing game data..."):
                    performance, error = analyze_last_game()
                    
                    if error:
                        st.error(error)
                    else:
                        st.subheader("Enemy Card Performance")
                        
                        if isinstance(performance, dict):
                            # Create a dataframe for better display
                            import pandas as pd
                            df = pd.DataFrame(performance.items(), columns=['Troop', 'Performance'])
                            df = df.sort_values('Performance', ascending=False)
                            
                            # Show as table
                            st.table(df)
                            
                            # Find the highest performing card
                            if not df.empty:
                                best_card = df.iloc[0]['Troop']
                                best_score = df.iloc[0]['Performance']
                                
                                # Show which card the player struggled against the most
                                st.markdown(f"**You struggled the most against: {best_card.capitalize()}**")
                                
                                # Add tips section if any score is above 2
                                if df['Performance'].max() > 0:
                                    st.subheader("Tips")
                                    
                                    if best_card == "giant":
                                        st.markdown("- Giants are tanky but slow. Use swarm units like Goblins to counter them efficiently.")
                                        st.markdown("- Place troops behind your tower to avoid splash damage.")
                                    elif best_card == "knight":
                                        st.markdown("- Knights are balanced units. Counter them with ranged units like Archers.")
                                        st.markdown("- Keep your distance and avoid direct confrontation.")
                                    elif best_card == "archer":
                                        st.markdown("- Archers attack from range. Use fast units like Goblins to close the gap quickly.")
                                        st.markdown("- Deploy troops close to them to minimize their advantage.")
                                    elif best_card == "goblin":
                                        st.markdown("- Goblins are cheap and fast. Use area damage or ranged units to counter them.")
                                        st.markdown("- Group your troops to prevent them from being overwhelmed.")
                        else:
                            # If string output from subprocess
                            st.text(performance)
    
    # Auto-refresh to update game state
    if not st.session_state.game_state.game_over:
        time.sleep(0.1)  # Small delay to prevent too many refreshes
        st.rerun()

def main():
    st.set_page_config(
        page_title="Clash Royale Simulation",
        page_icon="🏰",
        layout="wide"
    )
    
    st.title("Clash Royale Single Lane Simulation")
    
    run_game_simulation()

if __name__ == "__main__":
    main()