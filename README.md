# VerifyKaro
Agentic Scam Investigation & Response System (CSC-348 Project 1).

## Deploy on Render
- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Add environment variable `GEMINI_API_KEY` in Render.
- Optional: `GEMINI_MODEL=gemini-2.5-flash`

## Prototype tools
1. URL Inspector: extracts URLs and checks basic domain patterns without opening them.
2. Official Source Lookup: searches a curated starter knowledge base of Pakistani cyber-safety resources.

The agent chooses tools based on each submitted message and runs a separate reflection pass.
This is an educational prototype, not a guarantee of safety or fraud. It does not submit complaints.
