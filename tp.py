import streamlit as st
import google.generativeai as genai
import pandas as pd

# 🔹 Quick Fix: Hardcode the API key (Not recommended for production)
API_KEY = "AIzaSyBmETEzYBcKH6hhBUrX2XwkNZLA9Js_YLA"

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Define the model (using Gemini 1.5 Flash)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_cricket_stats(player_name):
    prompt = (
        f"Provide only the numerical cricket statistics for {player_name}. "
        "Include:\n"
        "- If the player is a batsman: Strike Rate, Highest Score, Batting Average.\n"
        "- If the player is a bowler: Average Wickets, Runs Conceded.\n"
        "- If the player is an all-rounder: Strike Rate, Batting Average.\n"
        "Respond with only the numbers separated by commas, nothing else."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No data available."
    except Exception as e:
        return f"⚠️ Error fetching stats: {str(e)}"

# Load player names from CSV
players_df = pd.read_csv("players.csv")  # Ensure you have a CSV file with a 'Player Name' column

# Streamlit UI
st.title("🏏 Cricket Player Stats Viewer")

selected_player = st.selectbox("Select a Player:", players_df["Player Name"].tolist())

if st.button("Get Stats") and selected_player:
    stats = get_cricket_stats(selected_player)
    st.markdown(f"### 📊 Stats for {selected_player}")
    
    # Convert stats to a table format
    stats_list = stats.split(",")
    columns = ["Stat Type", "Value"]
    if len(stats_list) == 3:
        data = [
            ["Strike Rate", stats_list[0]],
            ["Highest Score", stats_list[1]],
            ["Batting Average", stats_list[2]]
        ]
    elif len(stats_list) == 2:
        data = [
            ["Average Wickets", stats_list[0]],
            ["Runs Conceded", stats_list[1]]
        ]
    else:
        data = [["Data", stats]]
    
    df = pd.DataFrame(data, columns=columns)
    st.table(df)
