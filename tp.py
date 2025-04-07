import streamlit as st
import pandas as pd
import google.generativeai as genai

# 🔹 API Key Setup (Avoid hardcoding in production)
API_KEY = "AIzaSyAW_b4mee9l8eP931cqd9xqErHV34f7OEw"
genai.configure(api_key=API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get cricket stats from Gemini
def get_cricket_stats(player_name, role):
    prompt = (
        f"Provide only the numerical cricket statistics for {player_name}, who is a {role}.\n"
        "Return strictly comma-separated values with no text or labels.\n"
        "Format:\n"
        "- Batsman: Strike Rate, Highest Score, Batting Average\n"
        "- Bowler: Average Wickets, Runs Conceded, Average Economy\n"
        "- All-rounder: Strike Rate, Batting Average, Average Economy\n\n"
        "Example: 145.2, 102, 55.4"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No data available."
    except Exception as e:
        return f"⚠️ Error fetching stats: {str(e)}"

# Parse response into DataFrame based on role
def parse_stats_to_df(stats, player_name, role):
    values = [v.strip() for v in stats.split(",") if v.strip().replace(".", "", 1).isdigit()]
    
    role_columns = {
        "Batsman": ["Strike Rate", "Highest Score", "Batting Average"],
        "Bowler": ["Average Wickets", "Runs Conceded", "Average Economy"],
        "All-rounder": ["Strike Rate", "Batting Average", "Average Economy"]
    }

    if len(values) != 3:
        return None

    try:
        columns = role_columns.get(role, ["Stat1", "Stat2", "Stat3"])
        df = pd.DataFrame([values], columns=columns)
        df.insert(0, "Player Name", player_name)
        df.insert(1, "Role", role)
        return df
    except Exception:
        return None

# --- Streamlit UI ---
st.title("🏏 Cricket Player Stats Viewer")

player_name = st.text_input("Enter Player Name:")
role = st.selectbox("Select Player Role:", ["Batsman", "Bowler", "All-rounder"])

if st.button("Get Stats") and player_name and role:
    stats = get_cricket_stats(player_name, role)

    if "⚠️" in stats or "No data" in stats or not stats.strip():
        st.warning(stats)
    else:
        df = parse_stats_to_df(stats, player_name, role)
        if df is not None:
            st.markdown(f"### 📊 Stats for `{player_name}` ({role})")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{player_name}_{role}_stats.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Could not parse stats into table format.")
