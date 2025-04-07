import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configure Gemini API
API_KEY = "AIzaSyAW_b4mee9l8eP931cqd9xqErHV34f7OEw"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_cricket_stats(player_name, role):
    if role == "Batsman":
        prompt = (
            f"Provide only the numerical cricket statistics for {player_name}. "
            "Include:\n"
            "- Number of Matches played.\n"
            "- Strike Rate, Highest Score, Batting Average.\n"
            "Respond with only the numbers separated by commas, nothing else."
        )
    elif role == "Bowler":
        prompt = (
            f"Provide only the numerical cricket statistics for {player_name}. "
            "Include:\n"
            "- Number of Matches played.\n"
            "- Average Wickets, Runs Conceded.\n"
            "Respond with only the numbers separated by commas, nothing else."
        )
    elif role == "All-rounder":
        prompt = (
            f"Provide only the numerical cricket statistics for {player_name}. "
            "Include:\n"
            "- Number of Matches played.\n"
            "- Strike Rate, Batting Average.\n"
            "Respond with only the numbers separated by commas, nothing else."
        )
    else:
        return "Invalid role"
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No data available."
    except Exception as e:
        return f"⚠️ Error fetching stats: {str(e)}"

def parse_stats_to_df(stats, player_name, role):
    values = [v.strip() for v in stats.split(",")]
    if role == "Batsman":
        if len(values) != 4:
            return None
        columns = ["Matches", "Strike Rate", "Highest Score", "Batting Average"]
    elif role == "Bowler":
        if len(values) != 3:
            return None
        columns = ["Matches", "Average Wickets", "Runs Conceded"]
    elif role == "All-rounder":
        if len(values) != 3:
            return None
        columns = ["Matches", "Strike Rate", "Batting Average"]
    else:
        return None
    try:
        df = pd.DataFrame([values], columns=columns)
        df.insert(0, "Player Name", player_name)
        df.insert(1, "Role", role)
        return df
    except Exception:
        return None

# --- Streamlit UI ---
st.title("🏏 Categorized Cricket Player Stats Viewer")
st.markdown("Enter player names for each category (one per line):")

# Separate input areas for each role
bowlers_input = st.text_area("Bowlers")
batsmen_input = st.text_area("Batsmen")
allrounders_input = st.text_area("All-rounders")

bowlers = [name.strip() for name in bowlers_input.strip().split("\n") if name.strip()] if bowlers_input else []
batsmen = [name.strip() for name in batsmen_input.strip().split("\n") if name.strip()] if batsmen_input else []
allrounders = [name.strip() for name in allrounders_input.strip().split("\n") if name.strip()] if allrounders_input else []

if st.button("🔍 Fetch Stats"):
    all_stats = []
    with st.spinner("Fetching stats..."):
        # Process Bowlers
        for name in bowlers:
            stats = get_cricket_stats(name, "Bowler")
            df = parse_stats_to_df(stats, name, "Bowler")
            if df is not None:
                all_stats.append(df)
            else:
                st.warning(f"Could not parse stats for bowler: {name}")
        # Process Batsmen
        for name in batsmen:
            stats = get_cricket_stats(name, "Batsman")
            df = parse_stats_to_df(stats, name, "Batsman")
            if df is not None:
                all_stats.append(df)
            else:
                st.warning(f"Could not parse stats for batsman: {name}")
        # Process All-rounders
        for name in allrounders:
            stats = get_cricket_stats(name, "All-rounder")
            df = parse_stats_to_df(stats, name, "All-rounder")
            if df is not None:
                all_stats.append(df)
            else:
                st.warning(f"Could not parse stats for all-rounder: {name}")
    
    if all_stats:
        final_df = pd.concat(all_stats, ignore_index=True)
        st.success(f"✅ Stats fetched for {len(final_df)} players.")
        st.dataframe(final_df, use_container_width=True)
        csv = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download All Stats as CSV",
            data=csv,
            file_name="categorized_player_stats.csv",
            mime="text/csv"
        )
    else:
        st.error("No valid stats found.")
