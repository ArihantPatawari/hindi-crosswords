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
# 📱 DYNAMIC FLEXBOX WORD-BLOCK DESIGN OVERRIDES
# =====================================================================
st.markdown("""
    <style>
    /* 1. Eliminate the huge 14x14 grid footprint entirely */
    div[data-testid="stHorizontalBlock"] {
        display: none !important; /* Disables standard Streamlit grid wrappers */
    }

    /* 2. Custom flex row styling exclusively for our text input tracks */
    .crossword-flex-row {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 4px !important;
        margin-bottom: 15px !important;
        width: 100% !important;
    }

    /* 3. Style only the playable text cells to render as solid square blocks */
    .crossword-cell-wrapper {
        width: 32px !important;
        max-width: 32px !important;
    }

    input {
        text-align: center !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 0px !important;
        height: 32px !important;
        width: 32px !important;
        background-color: #262730 !important;
        color: white !important;
        border: 2px solid #464855 !important;
        border-radius: 6px !important;
    }
    input:focus {
        border-color: #ff4b4b !important;
    }

    /* 4. Style clue indices resting directly over active squares */
    label[data-testid="stWidgetLabel"] {
        font-size: 9px !important;
        font-weight: bold !important;
        color: #ff4b4b !important;
        margin-bottom: -6px !important;
        text-align: center !important;
        display: block !important;
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
# 🛠️ DYNAMIC STRUCTURAL EXTRACTION ENGINE (ZERO DEAD BLOCKS RENDERING)
# =====================================================================
matrix_df = pd.read_csv(SHEET_BASE + "AnswersMatrix")
active_matrix = matrix_df[matrix_df['PuzzleID'].astype(str) == target_puzzle_id]
clues = json.loads(str(p_meta['CluesJSON']))

user_grid_responses = {}

st.subheader("🔲 शब्द पहेली (Fill the Words)")

# Iterate over the generated puzzle configurations directly
for item in clues:
    clue_id = item['id']
    direction = item['dir']
    start_r = int(item['row'])
    start_c = int(item['col'])

    # 1. Break the Hindi keyword into clean Devanagari cluster lengths natively
    letters_count = len(list(grapheme.graphemes(item['word'])))

    dtype_label = "लेटे हुए (Horizontal)" if direction == 'H' else "खड़े (Vertical)"
    st.caption(f"**संकेत #{clue_id} [{dtype_label}]:** {item['clue']}")

    # 2. Open a custom responsive horizontal flex track wrapper natively
    st.markdown('<div class="crossword-flex-row">', unsafe_allow_html=True)

    # Render ONLY the exact letter spaces needed for this word block
    for i in range(letters_count):
        curr_r = start_r if direction == 'H' else start_r + i
        curr_c = start_c + i if direction == 'H' else start_c
        cell_key = f"cell_{curr_r}_{curr_c}"

        # Only render a unique input widget if it hasn't been drawn yet
        if cell_key not in user_grid_responses:
            # Set the indicator label to show on the starting boundary square
            box_label = str(clue_id) if i == 0 else " "

            # Encapsulate directly within our customized CSS styling class tags
            st.markdown('<div class="crossword-cell-wrapper">', unsafe_allow_html=True)

            user_grid_responses[cell_key] = st.text_input(
                label=box_label,
                max_chars=3,
                key=f"cell_input_{target_puzzle_id}_{curr_r}_{curr_c}"
            ).strip()

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

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
