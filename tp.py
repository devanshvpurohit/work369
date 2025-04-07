import streamlit as st
import pandas as pd
import google.generativeai as genai

# 🔹 API Key Setup (do NOT hardcode in production)
API_KEY = "AIzaSyAW_b4mee9l8eP931cqd9xqErHV34f7OEw"
genai.configure(api_key=API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_cricket_stats(player_name):
    prompt = (
        f"Provide only the cricket statistics for {player_name} in the format below.\n\n"
        "If Batsman:\n"
        "Strike Rate, Highest Score, Batting Average\n"
        "If Bowler:\n"
        "Average Wickets, Runs Conceded, Average Economy\n"
        "If All-rounder:\n"
        "Strike Rate, Batting Average, Average Economy\n\n"
        "Respond with only the numbers separated by commas. No text, labels, or units. Example: 140.5, 120, 52.3"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No data available."
    except Exception as e:
        return f"⚠️ Error fetching stats: {str(e)}"

def parse_stats_to_df(stats, player_name):
    values = [v.strip() for v in stats.split(",") if v.strip().replace(".", "", 1).isdigit()]
    col_map = {
        3: [
            ["Strike Rate", "Highest Score", "Batting Average"],
            ["Average Wickets", "Runs Conceded", "Average Economy"],
            ["Strike Rate", "Batting Average", "Average Economy"]
        ],
        2: [
            ["Strike Rate", "Batting Average"],
            ["Average Wickets", "Average Economy"]
        ]
    }

    try:
        columns = None
        if len(values) == 3:
            # Let Gemini return any of the 3-stats categories
            columns = st.selectbox("Choose stat type (since 3 values match multiple roles):", 
                                   ["Batsman", "Bowler", "All-rounder"])
            if columns == "Batsman":
                columns = col_map[3][0]
            elif columns == "Bowler":
                columns = col_map[3][1]
            else:
                columns = col_map[3][2]
        elif len(values) == 2:
            columns = st.selectbox("Choose stat type (2 values):", 
                                   ["Batsman (Strike Rate, Bat Avg)", "Bowler (Avg Wickets, Econ)"])
            if "Batsman" in columns:
                columns = col_map[2][0]
            else:
                columns = col_map[2][1]
        elif len(values) == 1:
            columns = ["Stat"]
        else:
            return None

        df = pd.DataFrame([values], columns=columns)
        df.insert(0, "Player Name", player_name)
        return df
    except Exception:
        return None

# --- Streamlit UI ---
st.title("🏏 Cricket Player Stats Viewer")

player_name = st.text_input("Enter Player Name:")

if st.button("Get Stats") and player_name:
    stats = get_cricket_stats(player_name)

    if "⚠️" in stats or "No data" in stats or not stats.strip():
        st.warning(stats)
    else:
        df = parse_stats_to_df(stats, player_name)
        if df is not None:
            st.markdown(f"### 📊 Stats for `{player_name}`")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{player_name}_stats.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Could not parse stats into table format.")
