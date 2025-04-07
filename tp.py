import streamlit as st
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

# Streamlit UI
st.title("🏏 Cricket Player Stats Viewer")

player_name = st.text_input("Enter Player Name:")

if st.button("Get Stats") and player_name:
    stats = get_cricket_stats(player_name)
    st.markdown(f"### 📊 Stats for {player_name}")
    st.write(stats)
