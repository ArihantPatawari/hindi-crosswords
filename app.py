import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxKORN7Hmovey7kPXymG_iyTJtrT4DwVcgtd3Fje4IYnbdrTYz8c7u2PDV0eyFrA5Ktow/exec"
# Paste your spreadsheet's unique sharing ID key string
SPREADSHEET_ID = "1vpN74SEqSQgw3LuZHhYGrigSf7l2D6rKz09jmRI5ahg"
SHEET_BASE = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet="


# 2. Correctly formatted Sheet Base URL
#SHEET_BASE = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
# https://docs.google.com/spreadsheets/d/1vpN74SEqSQgw3LuZHhYGrigSf7l2D6rKz09jmRI5ahg/edit?usp=sharing

st.set_page_config(page_title="शब्द पहेली प्रतियोगिता", layout="centered")


# =====================================================================
# 📱 DEFINITIVE MOBILE & LAPTOP RESPONSIVE GLOBAL CSS
# =====================================================================
# =====================================================================
# 📱 RESPONSIVE NATIVE SYMMETRIC GRID CSS OVERRIDES
# =====================================================================
st.markdown("""
    <style>
    /* 1. Prevent native column stacking on mobile viewports */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        align-items: flex-start !important;
        gap: 2px !important;
        width: 100% !important;
    }

    /* 2. Enforce exact matching widths across columns */
    div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 20px !important;
        max-width: 34px !important;
    }

    /* 3. Style active input cells into clean square units */
    input {
        text-align: center !important;
        font-weight: bold !important;
        font-size: 14px !important;
        padding: 0px !important;
        height: 28px !important;
        width: 100% !important;
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #464855 !important;
        border-radius: 4px !important;
    }
    input:focus {
        border-color: #ff4b4b !important;
    }

    /* 4. Style disabled cells to render as solid black blocks */
    input:disabled {
        background-color: #0e1117 !important;
        color: #0e1117 !important;
        border: 1px solid #1c1e24 !important;
        cursor: not-allowed !important;
    }

    /* 5. Center and align clue number labels above cells */
    label[data-testid="stWidgetLabel"] {
        font-size: 8px !important;
        font-weight: bold !important;
        color: #ff4b4b !important;
        margin-bottom: -10px !important;
        text-align: center !important;
        display: block !important;
        height: 12px !important;
        line-height: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# 📋 ROUTING & METADATA LOADER
# =====================================================================
url_parameters = st.query_params
if "puzzle" not in url_parameters:
    st.title("⚠️ अमान्य लिंक (Invalid Link)")
    st.error("कृपया सही पहेली लिंक का उपयोग करें (उदा. ?puzzle=1)")
    st.stop()

target_puzzle_id = str(url_parameters["puzzle"])

try:
    registry_df = pd.read_csv(SHEET_BASE + "PuzzlesRegistry")
    puzzle_row = registry_df[registry_df['PuzzleID'].astype(str) == target_puzzle_id]
except:
    puzzle_row = pd.DataFrame()

if puzzle_row.empty:
    st.title("🔒 पहेली उपलब्ध नहीं है")
    st.warning(f"पहेली संख्या {target_puzzle_id} अभी लाइव नहीं की गई है।")
    st.stop()

# Force safe text conversions out
p_meta = puzzle_row.iloc[0]
st.title(f"🧩 हिंदी शब्द पहेली प्रतियोगिता")
st.subheader(f"📖 विषय: {str(p_meta['BookTitle'])}")

player_name = st.text_input("अपना नाम दर्ज करें (Enter Your Name):", placeholder="जैसे: अमित कुमार")
st.markdown("---")

# =====================================================================
# 📋 CARD VIEW CLUES DISPLAY PANEL (FLAWLESS LAPTOP & MOBILE SCALING)
# =====================================================================
st.subheader("📋 संकेत (Crossword Clues)")
clues = json.loads(str(p_meta['CluesJSON']))

# Group clues nicely into pure UI cards
for c in clues:
    dtype = "बाएँ से दाएँ (Horizontal)" if c['dir'] == 'H' else "ऊपर से नीचे (Vertical)"
    st.markdown(f"""
        <div style="background-color:#1e222b; padding:12px; border-radius:8px; border-left: 5px solid #ff4b4b; margin-bottom:8px;">
            <span style="color:#ff4b4b; font-weight:bold;"># {c['id']} [{dtype}]</span><br>
            <span style="color:white; font-size:15px;">{c['clue']}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================================
# 🔲 THE INTERLOCKING SYMMETRIC CROSSWORD MATRIX PLAYGROUND
# =====================================================================
matrix_df = pd.read_csv(SHEET_BASE + "AnswersMatrix")
active_matrix = matrix_df[matrix_df['PuzzleID'].astype(str) == target_puzzle_id]
playable_cells = set(active_matrix['CellKey'].tolist())

GRID_SIZE = 14
user_grid_responses = {}

st.subheader("🔲 शब्द पहेली ग्रिड (Fill the Grid)")

for r in range(GRID_SIZE):
    cols = st.columns(GRID_SIZE)
    for c in range(GRID_SIZE):
        cell_key = f"cell_{r}_{c}"

        # Look up clue numbers starting at this coordinate
        match = [x for x in clues if int(x['row']) == r and int(x['col']) == c]
        label = ",".join([str(x['id']) for x in match]) if match else " "

        with cols[c]:
            if cell_key not in playable_cells:
                # Render locked black cells as disabled input fields to maintain alignment
                st.text_input(
                    label=" ",
                    value="",
                    key=f"blk_{r}_{c}",
                    disabled=True,
                    label_visibility="visible"
                )
            else:
                # Render active playable input text fields
                user_grid_responses[cell_key] = st.text_input(
                    label=label,
                    max_chars=3,
                    key=f"p_{target_puzzle_id}_{r}_{c}",
                    label_visibility="visible"
                ).strip()

st.markdown("---")

# =====================================================================
# 📤 LOGGING SUBMISSIONS
# =====================================================================
if st.button("📤 अपना उत्तर सबमिट करें (Submit Answers)", type="primary", use_container_width=True):
    if not player_name.strip():
        st.error("⚠️ कृपया सबमिट करने से पहले अपना नाम लिखें!")
    else:
        correct_cells = 0
        for _, row in active_matrix.iterrows():
            if user_grid_responses.get(row['CellKey'], "") == row['CorrectLetter']:
                correct_cells += 1

        accuracy_pct = int((correct_cells / len(active_matrix)) * 100)

        payload = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_puzzle_id,
            player_name,
            f"{correct_cells}/{len(active_matrix)}",
            f"{accuracy_pct}%"
        ]
        requests.post(WEB_APP_URL, data={"sheetName": "Submissions", "rowData": json.dumps(payload)})

        st.balloons()
        st.success(f"🎉 बधाई हो {player_name}! आपका उत्तर सबमिट हो गया है।")
