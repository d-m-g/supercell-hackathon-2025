import streamlit as st
import pandas as pd
from .charts import create_score_trend_chart, create_player_stats_chart

def create_dashboard():
    st.title("Game Dashboard")

    st.header("Score Trends")
    score_data = pd.DataFrame({
        'time': range(10),
        'score': [10, 20, 15, 30, 25, 35, 45, 40, 50, 55],
        'player': ['Player 1'] * 5 + ['Player 2'] * 5,
        'date': pd.date_range(start='2025-05-17', periods=10)
    })
    create_score_trend_chart(score_data)

    st.header("Player Statistics")
    create_player_stats_chart(score_data)  # Using the same data for now

if __name__ == "__main__":
    create_dashboard()