import streamlit as st
import pandas as pd

st.set_page_config(page_title="Admin Winner Hub", layout="centered")
st.title("📱 Crossword Admin Dashboard")
st.subheader("🏁 Judgment Principle: First Come, First Served")

# Paste your spreadsheet's unique sharing ID key string
SPREADSHEET_ID = "1vpN74SEqSQgw3LuZHhYGrigSf7l2D6rKz09jmRI5ahg"
LATEST_SUBMISSIONS_CSV = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Submissions"

try:
    df = pd.read_csv(LATEST_SUBMISSIONS_CSV)
    unique_puzzles = df['PuzzleID'].unique().tolist()
except Exception:
    df = pd.DataFrame()
    unique_puzzles = []

target_filter = st.selectbox("Select Puzzle ID to view results:",
                             unique_puzzles if unique_puzzles else ["No submissions received"])

if not df.empty and target_filter != "No submissions received":
    # 1. Filter entries for the selected puzzle ID
    filtered_df = df[df['PuzzleID'].astype(str) == str(target_filter)].copy()

    st.metric(label="Total Participants for this Puzzle", value=len(filtered_df))

    # 2. Parse data vectors to enforce numerical and logical integrity
    filtered_df['Acc_Num'] = filtered_df['Accuracy'].str.rstrip('%').astype(int)
    filtered_df['Timestamp_Parsed'] = pd.to_datetime(filtered_df['Timestamp'])

    # 3. WINNER ENGINE: SORT BY SCORE (DESCENDING) THEN TIMESTAMP CLOCK (ASCENDING)
    # Page-time duration is completely ignored. Only the absolute submission click-time matters.
    ranked_df = filtered_df.sort_values(by=['Acc_Num', 'Timestamp_Parsed'], ascending=[False, True])

    st.subheader("🏅 Live Leaderboard Rankings")

    for idx, (_, row) in enumerate(ranked_df.iterrows(), 1):
        # Medals for the podium finishers
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "👤"

        with st.expander(f"{medal} Rank #{idx} — {row['PlayerName']} ({row['Accuracy']})"):
            st.markdown(f"⏱️ **Submission Timestamp:** `{row['Timestamp']}`")
            st.write(f"🎯 **Final Score:** {row['Score']}")
            if idx == 1:
                st.success("🌟 Current Winner (Highest Score + Earliest Submission)")

if st.button("🔄 Refresh Live Leaderboard", type="primary", use_container_width=True):
    st.rerun()
