import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configure Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

def get_player_score(player_name):
    """Fetch player historical performance using Gemini."""
    prompt = f"Provide a summary performance score (out of 100) for the cricketer {player_name} based on historical IPL data."
    try:
        response = model.generate_content(prompt)
        score = extract_score(response.text)
        return score
    except Exception as e:
        st.error(f"Error fetching score for {player_name}: {e}")
        return 50  # Default score

# Mock function to extract score from Gemini's response
def extract_score(response_text):
    try:
        return int(response_text.split()[0])  # Assuming response starts with score
    except:
        return 50  # Default score

# Streamlit UI
st.title("IPL 2025 Team Ranking Based on Player History")

# Predefined IPL teams and players
ipl_teams = {
    "Mumbai Indians": ["Rohit Sharma", "Suryakumar Yadav", "Jasprit Bumrah", "Ishan Kishan", "Hardik Pandya"],
    "Chennai Super Kings": ["MS Dhoni", "Ravindra Jadeja", "Ruturaj Gaikwad", "Deepak Chahar", "Devon Conway"],
    "Royal Challengers Bangalore": ["Virat Kohli", "Faf du Plessis", "Glenn Maxwell", "Mohammed Siraj", "Dinesh Karthik"],
    "Kolkata Knight Riders": ["Shreyas Iyer", "Andre Russell", "Sunil Narine", "Rinku Singh", "Mitchell Starc"],
    "Delhi Capitals": ["Rishabh Pant", "David Warner", "Kuldeep Yadav", "Prithvi Shaw", "Axar Patel"],
    "Rajasthan Royals": ["Sanju Samson", "Jos Buttler", "Yuzvendra Chahal", "Trent Boult", "Shimron Hetmyer"],
    "Punjab Kings": ["Shikhar Dhawan", "Liam Livingstone", "Sam Curran", "Kagiso Rabada", "Arshdeep Singh"],
    "Sunrisers Hyderabad": ["Aiden Markram", "Bhuvneshwar Kumar", "Heinrich Klaasen", "Umran Malik", "Washington Sundar"],
    "Lucknow Super Giants": ["KL Rahul", "Quinton de Kock", "Marcus Stoinis", "Ravi Bishnoi", "Krunal Pandya"],
    "Gujarat Titans": ["Shubman Gill", "Rashid Khan", "Mohammed Shami", "Rahul Tewatia", "David Miller"]
}

# Team selection
top_teams = st.multiselect("Select 10 teams to rank", list(ipl_teams.keys()), default=list(ipl_teams.keys())[:10])

if st.button("Rank Teams"):
    team_data = []
    for team in top_teams:
        players = ipl_teams[team]
        total_score = sum(get_player_score(player) for player in players)
        team_data.append([team, total_score])
    
    ranked_teams = sorted(team_data, key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(ranked_teams, columns=["Team", "Score"])
    
    st.write("### Ranked Teams")
    st.table(df)
else:
    st.write("Select 10 teams and click Rank Teams.")
