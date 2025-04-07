import streamlit as st
import pandas as pd
import google.generativeai as genai

# 🔹 Quick Fix: Hardcode the API key (Not recommended for production)
API_KEY = "AIzaSyAW_b4mee9l8eP931cqd9xqErHV34f7OEw"

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

def parse_stats_to_df(stats, player_name):
    columns = []
    values = stats.split(",")
    # Guess columns based on count
    if len(values) == 3:
        columns = ["Strike Rate", "Highest Score", "Batting Average"]
    elif len(values) == 2:
        columns = ["Average Wickets", "Runs Conceded"]
    elif len(values) == 1:
        columns = ["Stat"]
    else:
        return None

    try:
        df = pd.DataFrame([values], columns=columns)
        df.insert(0, "Player Name", player_name)
        return df
    except Exception:
        return None

# Streamlit UI
st.title("🏏 Cricket Player Stats Viewer")

player_name = st.text_input("Enter Player Name:")

if st.button("Get Stats") and player_name:
    stats = get_cricket_stats(player_name)
    
    if "⚠️" in stats or "No data" in stats:
        st.warning(stats)
    else:
        df = parse_stats_to_df(stats, player_name)
        if df is not None:
            st.markdown(f"### 📊 Stats for `{player_name}`")
            st.dataframe(df, use_container_width=True)
            
            # Provide CSV download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{player_name}_stats.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Could not parse stats into table format.")
