import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 🔍 Search Cricbuzz for the player and get profile URL
def search_cricbuzz_player(player_name):
    search_url = f"https://www.cricbuzz.com/search/cricbuzz?q={urllib.parse.quote(player_name)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find first profile link
    links = soup.select('a.cb-col.cb-col-100.cb-lst-itm.cb-txt-link')
    for link in links:
        href = link.get('href', '')
        if 'profiles' in href:
            return "https://www.cricbuzz.com" + href
    return None

# 🌐 Scrape Cricbuzz Stats
def get_cricbuzz_stats(player_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(player_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all("table", class_="table cb-col-100 cb-plyr-thead")
        if not tables:
            return "⚠️ No stats table found."

        batting_table = tables[0]
        bowling_table = tables[1] if len(tables) > 1 else None

        def parse_table(table):
            stats = {}
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = [td.text.strip() for td in row.find_all("td")]
                if cols and cols[0] in ["T20I", "IPL", "ODI", "TEST"]:
                    stats[cols[0]] = cols[1:]
            return stats

        batting_stats = parse_table(batting_table)
        bowling_stats = parse_table(bowling_table) if bowling_table else {}

        return {"batting": batting_stats, "bowling": bowling_stats}
    except Exception as e:
        return f"⚠️ Error: {e}"

# 📊 Convert to DataFrame
def parse_stats_to_df(data, player_name):
    dfs = []

    for dtype, stats in data.items():
        for format_, values in stats.items():
            df = pd.DataFrame([values])
            df.insert(0, "Format", format_)
            df.insert(0, "Stat Type", dtype.capitalize())
            df.insert(0, "Player Name", player_name)
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True) if dfs else None

# 🖥️ Streamlit UI
st.title("🏏 Cricbuzz Player Stats Viewer (Name Only)")

player_name = st.text_input("Enter Player Name (e.g., Virat Kohli)")

if st.button("Fetch Stats") and player_name:
    with st.spinner("Searching Cricbuzz..."):
        profile_url = search_cricbuzz_player(player_name)

    if not profile_url:
        st.error("❌ Could not find player on Cricbuzz.")
    else:
        with st.spinner(f"Fetching stats from Cricbuzz profile..."):
            stats = get_cricbuzz_stats(profile_url)

        if isinstance(stats, str) and "⚠️" in stats:
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
                    file_name=f"{player_name.replace(' ', '_')}_stats.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Could not parse stats into table format.")
