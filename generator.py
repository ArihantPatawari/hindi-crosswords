import json
import requests
import pdfplumber
import grapheme
import pandas as pd
import google.generativeai as genai
import argparse

# Configuration Parameters
SPREADSHEET_ID = "1vpN74SEqSQgw3LuZHhYGrigSf7l2D6rKz09jmRI5ahg"
GEMINI_API_KEY = "AQ.Ab8RN6Jzj0-yubrzhVBXLOWqVgwslRCt8gP6TuUj0MEZmoqMvg"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxKORN7Hmovey7kPXymG_iyTJtrT4DwVcgtd3Fje4IYnbdrTYz8c7u2PDV0eyFrA5Ktow/exec"
genai.configure(api_key=GEMINI_API_KEY)


# --- 1. AUTOMATIC ID GENERATOR ---
def get_next_puzzle_id():
    """Reads the current Google Sheet registry to find the next logical ID number automatically."""
    sheet_csv_url = f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PuzzlesRegistry"
    try:
        df = pd.read_csv(sheet_csv_url)
        if df.empty or 'PuzzleID' not in df.columns:
            return 1

        # Convert to numeric values, drop errors, and find max number
        existing_ids = pd.to_numeric(df['PuzzleID'], errors='coerce').dropna().astype(int).tolist()
        if not existing_ids:
            return 1
        return max(existing_ids) + 1
    except Exception:
        # If the sheet is completely fresh and empty, start at 1
        return 1


def create_automatic_puzzle(pdf_path, book_title):
    # Fetch next sequential ID automatically
    day_number = get_next_puzzle_id()
    print(f"🔄 Auto-Assigned Puzzle ID: {day_number}")
    print(f"⏳ Extracting textbook text from your Mac for Day {day_number}...")

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= 8: break
            text += page.extract_text() or ""

    model = genai.GenerativeModel('gemini-1.5-flash')
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
    response = model.generate_content(prompt)
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    word_pairs = json.loads(clean_json)

    # Calculate 12x12 Grid Layout Locations
    grid = [[' ' for _ in range(12)] for _ in range(12)]
    placed_clues = []

    pairs = sorted(word_pairs, key=lambda x: len(list(grapheme.graphemes(x['word']))), reverse=True)
    first_letters = list(grapheme.graphemes(pairs[0]['word']))
    r, c = 5, (12 - len(first_letters)) // 2
    for i, l in enumerate(first_letters): grid[r][c + i] = l
    placed_clues.append({"id": 1, "dir": "H", "row": r, "col": c, "clue": pairs[0]['clue']})

    # Sync puzzle settings directly to Google Sheet registry tab
    requests.post(WEB_APP_URL, data={"sheetName": "PuzzlesRegistry", "rowData": json.dumps(
        [str(day_number), book_title, json.dumps(placed_clues, ensure_ascii=False)])})

    # Sync exact correct character tracking matrix paths
    for row_idx in range(12):
        for col_idx in range(12):
            if grid[row_idx][col_idx] != ' ':
                cell_key = f"cell_{row_idx}_{col_idx}"
                requests.post(WEB_APP_URL, data={"sheetName": "AnswersMatrix", "rowData": json.dumps(
                    [str(day_number), cell_key, grid[row_idx][col_idx]])})

    print(f"🎉 Success! Puzzle {day_number} ('{book_title}') is now LIVE!")
    print(f"🔗 User Link: https://streamlit.app{day_number}")


if __name__ == "__main__":
    # Change these two variables directly inside PyCharm whenever you want to generate a new puzzle
    TARGET_PDF = "chapter1.pdf"
    PUZZLE_TITLE = "इतिहास: अध्याय 1"

    create_automatic_puzzle(TARGET_PDF, PUZZLE_TITLE)
    # parser = argparse.ArgumentParser(description="Auto-incrementing Hindi Crossword Generator")
    # parser.add_argument("--pdf", required=True, help="Name of your PDF file (e.g., chapter1.pdf)")
    # parser.add_argument("--title", required=True, help="Crossword Title Header string")
    #
    # args = parser.parse_args()
    # create_automatic_puzzle(args.pdf, args.title)
