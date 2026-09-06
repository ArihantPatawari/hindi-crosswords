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
    print(puzzle_row)
except:
    puzzle_row = pd.DataFrame()

if puzzle_row.empty:
    st.title("🔒 पहेली उपलब्ध नहीं है")
    st.warning(f"पहेली संख्या {target_puzzle_id} अभी लाइव नहीं की गई है।")
    st.stop()

# NEW UPDATED CODE (Type-Safe Fix)
p_meta = puzzle_row.iloc[0] # Explicitly fetch the first matching row entry
st.title(f"🧩 हिंदी शब्द पहेली — {str(p_meta['BookTitle'])}")
player_name = st.text_input("अपना नाम दर्ज करें:")

# st.title(f"🧩 हिंदी शब्द पहेली — {p_meta['BookTitle']}")
st.write("🏁 *प्रतियोगिता लाइव है! सबसे पहले सही उत्तर सबमिट करने वाले खिलाड़ी विजेता बनेंगे।*")

# player_name = st.text_input("अपना नाम दर्ज करें:")

# clues = json.loads(p_meta['CluesJSON'])

clues_string = str(p_meta['CluesJSON'])
clues = json.loads(clues_string)

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

#
# # ==========================================
# # 🔲 RENDER THE PLAYABLE GRID (FIXED FOR 14x14)
# # ==========================================
# GRID_SIZE = 14  # <-- CRITICAL FIX: Match the generator's grid size perfectly
#
# with col1:
#     st.subheader("🔲 ग्रिड (Grid)")
#     user_grid_responses = {}
#
#     # Loop through all 14 rows and 14 columns
#     for r in range(GRID_SIZE):
#         cols = st.columns(GRID_SIZE)
#         for c in range(GRID_SIZE):
#             cell_key = f"cell_{r}_{c}"
#             with cols[c]:
#                 if cell_key not in playable_cells:
#                     # Dark placeholder box for empty cells
#                     st.markdown(
#                         "<div style='background-color:#111; height:32px; border-radius:3px; margin-bottom:2px;'></div>",
#                         unsafe_allow_html=True)
#                 else:
#                     # Look up if a clue line begins exactly on this boundary box
#                     # Explicitly convert to integers to ensure an exact data match
#                     # match = [x for x in clues if int(x['row']) == r and int(x['col']) == c]
#                     #
#                     # if match:
#                     #     label = ",".join([str(x['id']) for x in match])
#                     # else:
#                     #     label = " "
#                     #
#                     # user_grid_responses[cell_key] = st.text_input(
#                     #     label=label,
#                     #     max_chars=1,
#                     #     key=f"p_{target_puzzle_id}_{r}_{c}"
#                     # ).strip()
#
#                     # =====================================================================
#                     # SPECIFIC FIXED GRAPHEME CELL INPUT WINDOW
#                     # =====================================================================
#                     match = [x for x in clues if int(x['row']) == r and int(x['col']) == c]
#                     label = ",".join([str(x['id']) for x in match]) if match else " "
#
#                     # 1. Expand max_chars to 3 to accommodate Devanagari matras/halants cleanly
#                     user_grid_responses[cell_key] = cols[c].text_input(
#                         label=label,
#                         max_chars=3,  # <-- Change from 1 to 3 to support composite clusters
#                         key=f"p_{target_puzzle_id}_{r}_{c}"
#                     ).strip()

# =====================================================================
# 📱 MOBILE-OPTIMIZED CUSTOM UI STYLING (Add at the very top of app.py)
# =====================================================================
st.markdown("""
    <style>
    /* Force container to allow horizontal scrolling on tiny phone screens */
    .crossword-container {
        display: flex;
        flex-direction: column;
        overflow-x: auto;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    /* Enforce a flawless 14x14 grid format that never breaks alignment */
    .crossword-grid-row {
        display: grid;
        grid-template-columns: repeat(14, minmax(28px, 1fr));
        gap: 3px;
        width: 100%;
        min-width: 420px; /* Ensures it looks like a real grid on narrow devices */
    }
    /* Styling for empty locked black grid cells */
    .black-cell {
        background-color: #111111;
        aspect-ratio: 1 / 1;
        border-radius: 4px;
        border: 1px solid #222222;
    }
    /* Target the text input blocks inside Streamlit dynamically */
    div[data-baseweb="input"] {
        border-radius: 4px !important;
    }
    input {
        text-align: center !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 0px !important;
        height: 32px !important;
    }
    /* Shrink the tiny clue labels above input fields to maximize layout space */
    label[data-testid="stWidgetLabel"] {
        font-size: 10px !important;
        color: #888888 !important;
        margin-bottom: -5px !important;
        text-align: center !important;
        display: block !important;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 🔲 RENDER THE PLAYABLE GRID (RE-ENGINEERED FOR MOBILE RESPONSIVENESS)
# =====================================================================
GRID_SIZE = 14
user_grid_responses = {}

with col1:
    st.subheader("🔲 ग्रिड (Puzzle Grid)")

    # Open the structural scrolling container wrapper
    st.markdown('<div class="crossword-container">', unsafe_allow_html=True)

    for r in range(GRID_SIZE):
        # Open a strict CSS row grid container block
        st.markdown('<div class="crossword-grid-row">', unsafe_allow_html=True)

        for c in range(GRID_SIZE):
            cell_key = f"cell_{r}_{c}"

            if cell_key not in playable_cells:
                # Render the black cells directly using fast, clean HTML
                st.markdown('<div class="black-cell"></div>', unsafe_allow_html=True)
            else:
                # Find matching clue label configurations
                match = [x for x in clues if int(x['row']) == r and int(x['col']) == c]
                label = ",".join([str(x['id']) for x in match]) if match else " "

                # Render the interactive active box cleanly inside the CSS grid
                user_grid_responses[cell_key] = st.text_input(
                    label=label,
                    max_chars=3,
                    key=f"p_{target_puzzle_id}_{r}_{c}",
                    label_visibility="visible" if match else "hidden"
                ).strip()

        # Close the row grid block container element
        st.markdown('</div>', unsafe_allow_html=True)

    # Close the scrolling horizontal container element wrapper
    st.markdown('</div>', unsafe_allow_html=True)


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
