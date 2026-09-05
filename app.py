import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxKORN7Hmovey7kPXymG_iyTJtrT4DwVcgtd3Fje4IYnbdrTYz8c7u2PDV0eyFrA5Ktow/exec"
# Paste your spreadsheet's unique sharing ID key string
SPREADSHEET_ID = "1vpN74SEqSQgw3LuZHhYGrigSf7l2D6rKz09jmRI5ahg"
SHEET_BASE = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet="

st.set_page_config(page_title="शब्द पहेली प्रतियोगिता", layout="centered")

# Read URL browser parameters
url_parameters = st.query_params

if "puzzle" not in url_parameters:
    st.title("⚠️ अमान्य लिंक (Invalid Link)")
    st.error("कृपया सही पहेली लिंक का उपयोग करें (उदा. ?puzzle=1)")
    st.stop()

target_puzzle_id = str(url_parameters["puzzle"])

# Fetch puzzle configs from Google Sheets
try:
    registry_df = pd.read_csv(SHEET_BASE + "PuzzlesRegistry")
    puzzle_row = registry_df[registry_df['PuzzleID'].astype(str) == target_puzzle_id]
except:
    puzzle_row = pd.DataFrame()

if puzzle_row.empty:
    st.title("🔒 पहेली उपलब्ध नहीं है")
    st.warning(f"पहेली संख्या {target_puzzle_id} अभी लाइव नहीं की गई है।")
    st.stop()

p_meta = puzzle_row.iloc
st.title(f"🧩 हिंदी शब्द पहेली — {p_meta['BookTitle']}")
st.write("🏁 *प्रतियोगिता लाइव है! सबसे पहले सही उत्तर सबमिट करने वाले खिलाड़ी विजेता बनेंगे।*")

player_name = st.text_input("अपना नाम दर्ज करें:")

clues = json.loads(p_meta['CluesJSON'])
matrix_df = pd.read_csv(SHEET_BASE + "AnswersMatrix")
active_matrix = matrix_df[matrix_df['PuzzleID'].astype(str) == target_puzzle_id]
playable_cells = set(active_matrix['CellKey'].tolist())

# Render Crossword Interface Layout
col1, col2 = st.columns(2)
with col2:
    st.subheader("📋 संकेत (Clues)")
    for c in clues:
        dtype = "Horizontal" if c['dir'] == 'H' else "Vertical"
        st.info(f"**#{c['id']} [{dtype}]:** {c['clue']}")

with col1:
    st.subheader("🔲 ग्रिड (Grid)")
    user_grid_responses = {}
    for r in range(12):
        cols = st.columns(12)
        for c in range(12):
            ckey = f"cell_{r}_{c}"
            with cols[c]:
                if ckey not in playable_cells:
                    st.markdown("<div style='background-color:#111; height:30px; border-radius:2px;'></div>",
                                unsafe_allow_html=True)
                else:
                    match = [x for x in clues if x['row'] == r and x['col'] == c]
                    label = str(match['id']) if match else " "
                    user_grid_responses[ckey] = st.text_input(label=label, max_chars=1,
                                                              key=f"p_{target_puzzle_id}_{r}_{c}").strip()

# --- SUBMISSION LOGIC ---
if st.button("📤 अपना उत्तर सबमिट करें", type="primary", use_container_width=True):
    if not player_name.strip():
        st.error("⚠️ कृपया जारी रखने के लिए अपना नाम लिखें!")
    else:
        # Calculate Score Matrix
        correct_cells = 0
        for _, row in active_matrix.iterrows():
            if user_grid_responses.get(row['CellKey'], "") == row['CorrectLetter']:
                correct_cells += 1

        accuracy_pct = int((correct_cells / len(active_matrix)) * 100)

        # Create Payload row data array (without page time tracking)
        payload = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # High precision click-timestamp
            target_puzzle_id,
            player_name,
            f"{correct_cells}/{len(active_matrix)}",
            f"{accuracy_pct}%"
        ]

        # Post directly to Google Sheet Submissions tab
        requests.post(WEB_APP_URL, data={"sheetName": "Submissions", "rowData": json.dumps(payload)})

        st.balloons()
        st.success("🎉 आपका उत्तर सफलतापूर्वक सबमिट कर दिया गया है!")
        st.info("📊 विजेता का निर्णय उच्चतम स्कोर और सबमिशन के समय (First Come, First Served) के आधार पर होगा।")
