
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from zoneinfo import ZoneInfo
import urllib.parse
import urllib.request
import json
import os

BASE = Path(__file__).parent
app = FastAPI(title="JARVESH")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class Command(BaseModel):
    command: str

def ai_answer(raw):
    if not API_KEY:
        return "AI abhi connect nahi hai. Render Environment mein OPENAI_API_KEY set kijiye."

    system_prompt = """
You are JARVESH, a friendly AI assistant created by Arpit Shukla.

IMPORTANT LANGUAGE RULES:
- If user writes in Hindi, reply in Hindi.
- If user writes in English, reply in English.
- If user writes in Hinglish, reply in Hinglish.
- Always detect and follow the language of the latest user message.
- Do not always reply in Hindi.
- Understand normal conversations and questions.
- Be helpful, clear and friendly.
"""

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw}
        ],
        "temperature": 0.7
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("AI ERROR:", str(e))
        return "Maaf kijiye, AI se connection nahi ho paya. Render logs aur API settings check kijiye."

def answer(raw):
    c = raw.strip().lower()

    if not c:
        return "Please type something."

    if c in {"time", "samay"}:
        return "Current time: " + datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%I:%M %p")

    if c in {"date", "tarikh"}:
        return "Today's date: " + datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%d %B %Y")

    if c in {"open youtube", "youtube kholo"}:
        return "OPEN_URL:https://youtube.com"

    if c in {"open google", "google kholo"}:
        return "OPEN_URL:https://google.com"

    if c in {"open github", "github kholo"}:
        return "OPEN_URL:https://github.com"

    if c.startswith("youtube search "):
        query = raw.strip()[15:]
        return "OPEN_URL:https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)

    if c.startswith("search ") or c.startswith("google "):
        query = raw.strip().split(" ", 1)[1]
        return "OPEN_URL:https://www.google.com/search?q=" + urllib.parse.quote_plus(query)

    if c.startswith("open notepad") or c.startswith("open calculator"):
        return "Ye PC command hosted website se execute nahi ho sakti."

    # Normal conversation and all other questions go to AI
    return ai_answer(raw)

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/command")
def command_api(payload: Command):
    return {"reply": answer(payload.command)}
