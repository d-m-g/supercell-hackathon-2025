import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_score_trend_chart(data):
    """Plot score trends over time."""
    plt.figure(figsize=(10, 5))
    plt.plot(data['time'], data['score'], marker='o')
    plt.title('Score Trends Over Time')
    plt.xlabel('Time')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def create_player_stats_chart(data):
    """Plot player statistics."""
    player_stats = data.groupby('player')['score'].mean().reset_index()
    plt.figure(figsize=(10, 5))
    plt.bar(player_stats['player'], player_stats['score'], color='skyblue')
    plt.title('Average Score by Player')
    plt.xlabel('Player')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def visualize_game_state(towers, troops):
    """Visualize current game state"""
    plt.figure(figsize=(10, 8))
    
    # Draw towers
    for tower in towers:
        color = 'blue' if tower.team == 'player' else 'red'
        plt.scatter(tower.position[0], tower.position[1], 
                   c=color, s=200, marker='s', label=f'{tower.team.title()} Tower')
        
        # Add tower health bars
        health_ratio = tower.hp / tower.max_hp
        plt.bar(tower.position[0], health_ratio * 20,
                width=50, bottom=tower.position[1] - 40,
                color='green', alpha=0.5)
    
    # Draw troops
    for troop in troops:
        color = 'blue' if troop.team == 'player' else 'red'
        marker = 'o' if troop.troop_type in ['Knight', 'Giant'] else '^'
        plt.scatter(troop.position[0], troop.position[1],
                   c=color, s=100, marker=marker,
                   label=f'{troop.team.title()} {troop.troop_type}')
    
    plt.title('Game State Visualization')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.grid(True, alpha=0.3)
    
    # Remove duplicate labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    
    st.pyplot(plt)
    plt.close()

def display_charts(data):
    """Display charts for visualizing game data."""
    st.header('Game Data Visualization')
    st.subheader('Score Trends')
    create_score_trend_chart(data)
    st.subheader('Player Statistics')
    create_player_stats_chart(data)