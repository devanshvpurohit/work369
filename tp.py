import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

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
    for player in players_df["Player Name"].tolist():
        stats = get_cricket_stats(player)
        stats_list = stats.split(",")
        
        if len(stats_list) == 3:
            stats_data.append([player, stats_list[0], stats_list[1], stats_list[2]])
        elif len(stats_list) == 2:
            stats_data.append([player, stats_list[0], stats_list[1], "N/A"])
        else:
            stats_data.append([player, "N/A", "N/A", "N/A"])
    
    stats_df = pd.DataFrame(stats_data, columns=["Player Name", "Strike Rate / Avg Wickets", "Highest Score / Runs Conceded", "Batting Average"])
    
    # Download button for CSV
    csv_buffer = io.StringIO()
    stats_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Player Stats CSV",
        data=csv_buffer.getvalue(),
        file_name="player_stats.csv",
        mime="text/csv"
    )
    
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
