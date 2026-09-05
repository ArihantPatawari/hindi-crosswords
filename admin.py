import streamlit as st
import pandas as pd

st.set_page_config(page_title="Admin Winner Core", layout="centered")
st.title("📱 एडमिन पहेली डैशबोर्ड")
st.subheader("🏆 निर्णय: पहले आओ-पहले पाओ (First Come, First Win)")

SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"
LATEST_SUBMISSIONS_CSV = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Submissions"

try:
    df = pd.read_csv(LATEST_SUBMISSIONS_CSV)
    unique_puzzles = df['PuzzleID'].unique().tolist()
except Exception:
    df = pd.DataFrame()
    unique_puzzles = []

target_filter = st.selectbox("परिणाम देखने के लिए पहेली संख्या चुनें:",
                             unique_puzzles if unique_puzzles else ["No submissions received"])

if not df.empty and target_filter != "No submissions received":
    # 1. Filter entries for the selected puzzle
    filtered_df = df[df['PuzzleID'] == target_filter].copy()

    st.metric(label="इस पहेली के कुल खिलाड़ी", value=len(filtered_df))

    # 2. Parse data vectors to enforce numerical and logical integrity
    filtered_df['Acc_Num'] = filtered_df['Accuracy'].str.rstrip('%').astype(int)
    filtered_df['Timestamp_Parsed'] = pd.to_datetime(filtered_df['Timestamp'])

    # 3. WINNER ENGINE: SORT BY SCORE (DESCENDING) THEN TIMESTAMP CLOCK (ASCENDING)
    # Page-time duration is completely ignored. Only the absolute click-time matters.
    ranked_df = filtered_df.sort_values(by=['Acc_Num', 'Timestamp_Parsed'], ascending=[False, True])

    st.subheader("🏅 लाइव लीडरबोर्ड (Rankings)")

    for idx, (_, row) in enumerate(ranked_df.iterrows(), 1):
        # Medals for the podium finishers
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "👤"

        with st.expander(f"{medal} रैंक #{idx} — {row['PlayerName']} ({row['Accuracy']})"):
            st.markdown(f"⏱️ **सबमिशन का सही समय:** `{row['Timestamp']}`")
            st.write(f"🎯 **स्कोर:** {row['Score']}")
            if idx == 1:
                st.success("🌟 वर्तमान विजेता (Highest Score + Earliest Submission)")

if st.button("🔄 डेटा रीफ्रेश करें", type="primary", use_container_width=True):
    st.rerun()
