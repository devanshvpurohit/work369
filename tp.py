import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import time

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

# Streamlit UI
st.title("🏏 Cricket Player Stats Viewer")

# File uploader for CSV or Excel
uploaded_file = st.file_uploader("Upload CSV or Excel file with player names", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        players_df = pd.read_csv(uploaded_file)
    else:
        players_df = pd.read_excel(uploaded_file, engine="openpyxl")
    
    # Generate stats for all players
    stats_data = []
    progress_bar = st.progress(0)
    total_players = len(players_df)
    
    for index, player in enumerate(players_df["Player Name"].tolist()):
        stats = get_cricket_stats(player)
        stats_list = stats.split(",")
        
        if len(stats_list) == 3:
            stats_data.append([player, stats_list[0], stats_list[1], stats_list[2]])
        elif len(stats_list) == 2:
            stats_data.append([player, stats_list[0], stats_list[1], "N/A"])
        else:
            stats_data.append([player, "N/A", "N/A", "N/A"])
        
        # Update progress bar
        progress_bar.progress((index + 1) / total_players)
        time.sleep(0.5)  # Adding delay to simulate processing time
    
    # Display stats only after processing all players
    st.success("✅ All player stats have been generated!")
    stats_df = pd.DataFrame(stats_data, columns=["Player Name", "Strike Rate / Avg Wickets", "Highest Score / Runs Conceded", "Batting Average"])
    st.dataframe(stats_df)
    
    # Download button for CSV
    csv_buffer = io.StringIO()
    stats_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Player Stats CSV",
        data=csv_buffer.getvalue(),
        file_name="player_stats.csv",
        mime="text/csv"
    )
