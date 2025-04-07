import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configure Gemini API
API_KEY = "AIzaSyAW_b4mee9l8eP931cqd9xqErHV34f7OEw"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_cricket_stats(player_name):
    prompt = (
        f"Provide only the numerical cricket statistics for {player_name}. "
        "Include:\n"
        "- Number of Matches played.\n"
        "- If the player is a batsman: Strike Rate, Highest Score, Batting Average.\n"
        "- If the player is a bowler: Average Wickets, Runs Conceded.\n"
        "- If the player is an all-rounder: Number of Matches, Strike Rate, Batting Average.\n"
        "Respond with only the numbers separated by commas, nothing else."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "No data available."
    except Exception as e:
        return f"⚠️ Error fetching stats: {str(e)}"

def parse_stats_to_df(stats, player_name):
    values = [v.strip() for v in stats.split(",")]
    
    if len(values) == 4:
        columns = ["Matches", "Strike Rate", "Highest Score", "Batting Average"]
    elif len(values) == 3:
        columns = ["Matches", "Strike Rate", "Batting Average"]
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

# --- Streamlit UI ---
st.title("🏏 Bulk Cricket Player Stats Viewer")

option = st.radio("Choose input method:", ("Text Input", "Upload CSV"))

player_names = []

if option == "Text Input":
    multiline_input = st.text_area("Enter player names (one per line):")
    if multiline_input:
        player_names = [name.strip() for name in multiline_input.strip().split("\n") if name.strip()]
elif option == "Upload CSV":
    uploaded_file = st.file_uploader("Upload CSV with column 'Player Name'", type="csv")
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        if "Player Name" in df_input.columns:
            player_names = df_input["Player Name"].dropna().astype(str).tolist()
        else:
            st.error("CSV must contain a column named 'Player Name'.")

if st.button("🔍 Fetch Stats") and player_names:
    all_stats = []
    with st.spinner("Fetching stats..."):
        for i, name in enumerate(player_names):
            stats = get_cricket_stats(name)
            df = parse_stats_to_df(stats, name)
            if df is not None:
                all_stats.append(df)
            else:
                st.warning(f"Could not parse stats for: {name}")
    
    if all_stats:
        final_df = pd.concat(all_stats, ignore_index=True)
        st.success(f"✅ Stats fetched for {len(final_df)} players.")
        st.dataframe(final_df, use_container_width=True)

        csv = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download All Stats as CSV",
            data=csv,
            file_name="all_player_stats.csv",
            mime="text/csv"
        )
    else:
        st.error("No valid stats found.")
