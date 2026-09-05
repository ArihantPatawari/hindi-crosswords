
from google import genai
from google.genai import types
import google.genai.errors as errors
import json
import requests
import pdfplumber
import grapheme
import pandas as pd
import os

#AQ.Ab8RN6L7O6zpk54r9PAxrwKxthmSTTe6JPwCDvlmN6GKJk50Zg
"""
  curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: AQ.Ab8RN6LcRZabDQKb-Mc8kcegNIJ0RLLjGW6PgZSAR4lkyF9APw' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
"""
# Configuration Parameters
SPREADSHEET_ID = "1vpN74SEqSQgw3LuZHhYGrigSf7l2D6rKz09jmRI5ahg"
GEMINI_API_KEY = "AQ.Ab8RN6LcRZabDQKb-Mc8kcegNIJ0RLLjGW6PgZSAR4lkyF9APw"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxKORN7Hmovey7kPXymG_iyTJtrT4DwVcgtd3Fje4IYnbdrTYz8c7u2PDV0eyFrA5Ktow/exec"
# genai.configure(api_key=GEMINI_API_KEY)
# This creates the client and automatically detects your GEMINI_API_KEY environment variable


# Change Line 9 to this format:
client = genai.Client(
    api_key="AQ.Ab8RN6LcRZabDQKb-Mc8kcegNIJ0RLLjGW6PgZSAR4lkyF9APw"
)


# =====================================================================
# FIXED OFFLINE-FALLBACK ID CALCULATOR
# =====================================================================
import urllib.request
import io
import os


# =====================================================================
# FIXED ID CALCULATOR (Correct Timeout Handling)
# =====================================================================
import os
import io
import urllib.request
import json
import pandas as pd


# =====================================================================
# FIXED NETWORK-RESILIENT AUTOMATIC COUNTER IDENTIFIER
# =====================================================================
def get_next_puzzle_id():
    """Fetches the highest cloud entry row. Resiliently falls back to local JSON if offline."""
    backup_file = "puzzle_id_tracker.json"
    sheet_csv_url = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PuzzlesRegistry"

    try:
        print("🌐 Connecting to Google Sheets database server...")
        req = urllib.request.Request(
            sheet_csv_url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        )
        # 7-second strict network connection safety window
        with urllib.request.urlopen(req, timeout=7) as response:
            csv_data = response.read().decode('utf-8')

        # Parse data vectors smoothly into data frames
        df = pd.read_csv(io.StringIO(csv_data))

        if not df.empty and 'PuzzleID' in df.columns:
            existing_ids = pd.to_numeric(df['PuzzleID'], errors='coerce').dropna().astype(int).tolist()
            if existing_ids:
                next_id = max(existing_ids) + 1

                # Write to local state backup to handle future network drops
                with open(backup_file, "w") as f:
                    json.dump({"next_id": next_id}, f)

                print(f"📊 Live Sheet Synced -> Found existing IDs: {existing_ids}. Next assigned ID is {next_id}.")
                return next_id

    except Exception as network_error:
        # Catch Errno 8 / DNS Dropouts cleanly and route to the local asset tracker
        print(f"⚠️ Network check bypassed ({network_error}). Recovering state from local track log...")

        if os.path.exists(backup_file):
            try:
                with open(backup_file, "r") as f:
                    local_data = json.load(f)
                    local_id = int(local_data.get("next_id", 1))
                    next_id = local_id + 1
                    # Pre-increment local index loop value for the next run
                    with open(backup_file, "w") as f_up:
                        json.dump({"next_id": next_id}, f_up)

                    print(f"💾 Local State Sync Successful -> Next sequential Puzzle ID is {next_id}.")
                    return next_id
            except Exception as read_err:
                print(f"⚠️ Local backup corrupted ({read_err}). Resetting tracker.")

    # Ultimate structural fallback if it's the very first time running the setup
    print("ℹ️ No previous histories detected. Starting puzzle indexing series at ID: 1")
    # Pre-increment local index loop value for the next run
    with open(backup_file, "w") as f_up:
        json.dump({"next_id": 1}, f_up)
    return 1


# ==========================================
# 🧱 THE INTERLOCKING CROSSWORD ENGINE
# ==========================================
class ProperCrosswordGenerator:
    def __init__(self, size=14):
        self.size = size
        # Create an empty blank grid canvas
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.placed_words = []  # Tracks detailed stats of successfully linked nodes

    def get_letters(self, word):
        """Breaks Hindi words down into human-perceived Devanagari grapheme units."""
        return list(grapheme.graphemes(word))

    def check_fit(self, letters, r, c, direction):
        """Verifies if a word can sit safely without overlapping or breaking grid rules."""
        w_len = len(letters)

        # 1. Verify canvas bounds
        if direction == 'H' and (c + w_len > self.size or c < 0): return False
        if direction == 'V' and (r + w_len > self.size or r < 0): return False

        # 2. Inspect path coordinates
        for i, char in enumerate(letters):
            curr_r = r if direction == 'H' else r + i
            curr_c = c + i if direction == 'H' else c

            # Check for conflict with existing characters
            if self.grid[curr_r][curr_c] != ' ' and self.grid[curr_r][curr_c] != char:
                return False

        return True

    def place_word_on_grid(self, word, clue, r, c, direction, clue_id):
        """Stamps the validated graphemes into the two-dimensional matrix array."""
        letters = self.get_letters(word)
        for i, char in enumerate(letters):
            curr_r = r if direction == 'H' else r + i
            curr_c = c + i if direction == 'H' else c
            self.grid[curr_r][curr_c] = char

        self.placed_words.append({
            "id": clue_id,
            "word": word,
            "clue": clue,
            "row": r,
            "col": c,
            "dir": direction
        })


    def build_interlocking_matrix(self, word_clue_pairs):
        """Iterates over words to build an interlocking network grid with proper incremental IDs."""
        sorted_pairs = sorted(word_clue_pairs, key=lambda x: len(self.get_letters(x['word'])), reverse=True)
        if not sorted_pairs: return

        # Place the first and longest word right across the middle horizontally
        first_word = sorted_pairs[0]['word']
        first_letters = self.get_letters(first_word)
        start_row = self.size // 2
        start_col = (self.size - len(first_letters)) // 2

        # First clue gets ID 1
        self.place_word_on_grid(first_word, sorted_pairs[0]['clue'], start_row, start_col, 'H', 1)

        # CRITICAL FIX: Initialize clue counter strictly OUTSIDE all loops
        clue_counter = 2

        for pair in sorted_pairs[1:]:
            word = pair['word']
            clue = pair['clue']
            letters = self.get_letters(word)
            placed_successfully = False

            for placed in self.placed_words:
                placed_letters = self.get_letters(placed['word'])

                for curr_idx, curr_char in enumerate(letters):
                    for pl_idx, pl_char in enumerate(placed_letters):
                        if curr_char == pl_char:
                            if placed['dir'] == 'H':
                                r_try = placed['row'] - curr_idx
                                c_try = placed['col'] + pl_idx
                                dir_try = 'V'
                            else:
                                r_try = placed['row'] + pl_idx
                                c_try = placed['col'] - curr_idx
                                dir_try = 'H'

                            if self.check_fit(letters, r_try, c_try, dir_try):
                                # Stamp with the unique counter ID
                                self.place_word_on_grid(word, clue, r_try, c_try, dir_try, clue_counter)

                                # INCREMENT THE COUNTER IMMEDIATELY AFTER A SUCCESSFUL PLACEMENT
                                clue_counter += 1

                                placed_successfully = True
                                break
                    if placed_successfully: break
                if placed_successfully: break


# ==========================================
# 🚀 CORE AUTOMATION PIPELINE RUNNER
# ==========================================
def create_automatic_puzzle(pdf_path, book_title):
    # Fetch next sequential ID automatically
    day_number = get_next_puzzle_id()
    print(f"🔄 Auto-Assigned Puzzle ID: {day_number}")
    print(f"⏳ Extracting textbook text from PDF...")

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= 8: break
            text += page.extract_text() or ""


    prompt = f"""
    Analyze the text. Extract 4 unique keywords in pure Hindi Devanagari script (no spaces).
    Create a crossword clue for each in Hindi.
    Output strictly as a valid JSON array without markdown blocks:
    [
        {{"word": "इतिहास", "clue": "पुरानी घटनाओं का अध्ययन।"}},
        {{"word": "नायक", "clue": "कहानी का मुख्य पात्र।"}}
    ]
    Text: {text[:4000]}
    """
    # response = client.models.generate_content(
    #     model='gemini-3.8-flash', #'gemini-flash-latest',  # Highly recommended current stable flash model
    #     contents=prompt,
    # )

    try:
        # First attempt with the target model
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
    except errors.ServerError as e:
        if "503" in str(e):
            print("⚠️ Model busy! Falling back to backup model...")
            # Fallback option if primary model has high demand spikes
            response = client.models.generate_content(
                model='gemini-3.6-pro',
                contents=prompt,
            )
        else:
            raise e

    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    word_pairs = json.loads(clean_json)

    # Calculate Proper Interlocking Layout
    engine = ProperCrosswordGenerator(size=14)
    engine.build_interlocking_matrix(word_pairs)

    # Sync puzzle settings directly to Google Sheet registry tab
    requests.post(WEB_APP_URL, data={"sheetName": "PuzzlesRegistry", "rowData": json.dumps(
        [str(day_number), book_title, json.dumps(engine.placed_words, ensure_ascii=False)])})

    # Sync exact correct character tracking matrix paths
    for row_idx in range(14):
        for col_idx in range(14):
            if engine.grid[row_idx][col_idx] != ' ':
                cell_key = f"cell_{row_idx}_{col_idx}"
                requests.post(WEB_APP_URL, data={"sheetName": "AnswersMatrix", "rowData": json.dumps(
                    [str(day_number), cell_key, engine.grid[row_idx][col_idx]])})

    print(f"\n🎉 Success! Interlocking Puzzle {day_number} ('{book_title}') is now LIVE!")
    print(f"🔗 Distributed User Link: https://hindi-crosswords-gjv5rjuerdnpb2ccunbkg9.streamlit.app/?puzzle={day_number}")


if __name__ == "__main__":
    # Change these two variables directly inside PyCharm whenever you want to generate a new puzzle
    TARGET_PDF = "Jain Vidya Bhag 1 Hindi.pdf"
    PUZZLE_TITLE = "Jain Vidya Bhag 1 Hindi 1"

    create_automatic_puzzle(TARGET_PDF, PUZZLE_TITLE)
    # parser = argparse.ArgumentParser(description="Auto-incrementing Hindi Crossword Generator")
    # parser.add_argument("--pdf", required=True, help="Name of your PDF file (e.g., chapter1.pdf)")
    # parser.add_argument("--title", required=True, help="Crossword Title Header string")
    #
    # args = parser.parse_args()
    # create_automatic_puzzle(args.pdf, args.title)
