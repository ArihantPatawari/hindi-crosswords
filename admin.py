import streamlit as st
import pandas as pd

st.set_page_config(page_title="Admin Tracker Dashboard", layout="centered")
st.title("📱 एडमिन पहेली डैशबोर्ड (All Submissions)")

SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"
LATEST_SUBMISSIONS_CSV = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Submissions"

try:
    df = pd.read_csv(LATEST_SUBMISSIONS_CSV)
    # Group and view analytics details by puzzle ID values
    unique_puzzles = df['PuzzleID'].unique().tolist()
except Exception:
    df = pd.DataFrame()
    unique_puzzles = []

target_filter = st.selectbox("परिणाम देखने के लिए पहेली संख्या चुनें:",
                             unique_puzzles if unique_puzzles else ["No submissions received"])

if not df.empty and target_filter != "No submissions received":
    filtered_df = df[df['PuzzleID'] == target_filter]
    st.metric(label="इस पहेली के कुल खिलाड़ी", value=len(filtered_df))

    # Sort leaderboard by highest score accuracy percentages
    filtered_df['Acc_Num'] = filtered_df['Accuracy'].str.rstrip('%').astype(int)
    ranked_df = filtered_df.sort_values(by='Acc_Num', ascending=False)

    st.subheader("🏆 लाइव स्कोर बोर्ड रैंकिंग")
    for idx, row in ranked_df.iterrows():
        with st.expander(f"👤 {row['PlayerName']} — शुद्धता दर: {row['Accuracy']}"):
            st.write(f"⏱️ **समय:** {row['Timestamp']}")
            st.write(f"🎯 **स्कोर:** {row['Score']}")

if st.button("🔄 डेटा रीफ्रेश करें", type="primary", use_container_width=True):
    st.rerun()
