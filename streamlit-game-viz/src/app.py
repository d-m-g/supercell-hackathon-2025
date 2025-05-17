import streamlit as st
import sys
import os
import time
import matplotlib.pyplot as plt

# Add the project root to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import from the src directory
try:
    from src.visualize_game import GameVisualizer
    from src.game.environment import GameEnvironment
    from src.game.player import AIPlayer
    from src.game.card import create_sample_cards
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.info("Make sure you are running Streamlit from the correct directory")

def main():
    st.title("Clash Royale Prototype Visualization")

    # Sidebar controls
    st.sidebar.header("Game Settings")
    
    # Player settings
    st.sidebar.subheader("Player Configuration")
    settings = {
        "player1_type": st.sidebar.selectbox(
            "Player 1", 
            ["ai", "human"], 
            index=0,
            help="Type of player 1 (AI or Human)"
        ),
        "player2_type": st.sidebar.selectbox(
            "Player 2", 
            ["ai", "human"], 
            index=0,
            help="Type of player 2 (AI or Human)"
        ),
        "difficulty": st.sidebar.selectbox(
            "AI Difficulty", 
            [1, 2, 3], 
            index=0,
            help="Difficulty level for AI players (1: Easy, 2: Medium, 3: Hard)"
        ),
    }
    
    # Visualization settings
    st.sidebar.subheader("Visualization Settings")
    settings.update({
        "delay": st.sidebar.slider(
            "Visualization Delay", 
            0.1, 5.0, 2.0,
            help="Delay between turns in seconds"
        ),
        "turns": st.sidebar.number_input(
            "Max Turns", 
            min_value=10, 
            max_value=1000, 
            value=100,
            help="Maximum number of turns before game ends"
        ),
        "use_ascii": False,  # We'll use Streamlit's visualization instead
        "use_matplotlib": True
    })

    # Initialize or get session state
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
        st.session_state.game_env = None
        st.session_state.visualizer = None
        st.session_state.turn = 0

    # Start/Reset button
    if st.sidebar.button("Start/Reset Game"):
        # Initialize new game
        game_env = GameEnvironment()
        cards = create_sample_cards()
        
        # Create players
        player1 = AIPlayer(1, difficulty=settings["difficulty"])
        player2 = AIPlayer(2, difficulty=settings["difficulty"])
        player1.initialize_deck(cards)
        player2.initialize_deck(cards)
        
        # Create visualizer
        visualizer = GameVisualizer(
            game_env=game_env,
            use_ascii=False,
            use_matplotlib=True,
            delay=settings["delay"],
            streamlit_mode=True
        )
        
        st.session_state.game_started = True
        st.session_state.game_env = game_env
        st.session_state.player1 = player1
        st.session_state.player2 = player2
        st.session_state.visualizer = visualizer
        st.session_state.turn = 0
    
    # Display game state
    if st.session_state.game_started:
        # Game stats in a more organized layout
        st.subheader("Game Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Turn", st.session_state.turn)
        with col2:
            if st.session_state.game_env is not None:
                p1_units = len([u for u in st.session_state.game_env.units.values() if u['owner'] == 1])
                st.metric("Player 1 Units", p1_units)
        with col3:
            if st.session_state.game_env is not None:
                p2_units = len([u for u in st.session_state.game_env.units.values() if u['owner'] == 2])
                st.metric("Player 2 Units", p2_units)

        # Display current scores
        if st.session_state.game_env:
            if hasattr(st.session_state.game_env, 'calculate_scores'):
                scores = st.session_state.game_env.calculate_scores()
                st.info(f"Current Score - Player 1: {scores[1]}, Player 2: {scores[2]}")
        
        # Update game state
        if st.session_state.game_env and not st.session_state.game_env.game_over:
            # Execute one turn
            st.session_state.player1.take_turn(st.session_state.game_env)
            st.session_state.player2.take_turn(st.session_state.game_env)
            st.session_state.game_env.update()
            st.session_state.turn += 1
            
            # Visualize current state
            st.session_state.visualizer.visualize_state(
                st.session_state.game_env,
                st.session_state.player1,
                st.session_state.player2
            )
            
            # Display matplotlib plot in Streamlit
            fig = plt.gcf()
            st.pyplot(fig)
            plt.close()
            
            # Check for game over
            if st.session_state.turn >= settings["turns"]:
                st.session_state.game_env.game_over = True
                if hasattr(st.session_state.game_env, 'calculate_scores'):
                    final_scores = st.session_state.game_env.calculate_scores()
                    winner = 1 if final_scores[1] > final_scores[2] else 2
                    st.success(f"Game Over! Player {winner} wins with score {max(final_scores.values())}!")
            else:
                # Auto-rerun for next turn if not game over
                time.sleep(settings["delay"])
                st.rerun()
        elif st.session_state.game_env and st.session_state.game_env.game_over:
            st.warning("Game Over! Click Start/Reset to begin a new game.")

if __name__ == "__main__":
    main()