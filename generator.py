import json
import requests
import pdfplumber
import grapheme
import google.generativeai as genai

# Configuration Parameters
GEMINI_API_KEY = "AQ.Ab8RN6Jzj0-yubrzhVBXLOWqVgwslRCt8gP6TuUj0MEZmoqMvg"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxKORN7Hmovey7kPXymG_iyTJtrT4DwVcgtd3Fje4IYnbdrTYz8c7u2PDV0eyFrA5Ktow/exec"
genai.configure(api_key=GEMINI_API_KEY)


def create_individual_day_puzzle(pdf_path, day_number, book_title):
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

    # Process and sort letters
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

    print(f"🎉 Success! Day {day_number} Crossword uploaded to your database reservoir.")


if __name__ == "__main__":
    # Example execution format: Pass the PDF path, Day number, and Title string
    create_individual_day_puzzle("chapter1.pdf", 1, "इतिहास: अध्याय 1")
