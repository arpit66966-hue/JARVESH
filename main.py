
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from zoneinfo import ZoneInfo
import urllib.parse
import urllib.request
import urllib.error
import json
import os

# ================= SETTINGS =================

BASE = Path(__file__).parent

app = FastAPI(title="JARVESH")

app.mount(
    "/static",
    StaticFiles(directory=BASE / "static"),
    name="static"
)

API_KEY = os.getenv("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")
MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini"
)

# ================= COMMAND MODEL =================

class Command(BaseModel):
    command: str


# ================= AI SYSTEM =================

def ai_answer(raw):

    if not API_KEY:
        return (
            "AI connect nahi hai. "
            "Render Environment mein OPENROUTER_API_KEY set kijiye."
        )

    system_prompt = """
You are JARVESH, a friendly AI assistant created by Arpit Shukla.

LANGUAGE RULES:
1. If the user writes in Hindi, reply in Hindi.
2. If the user writes in English, reply in English.
3. If the user writes in Hinglish, reply in Hinglish.
4. Detect the language of every new message.
5. Never force every answer into Hindi.
6. Understand normal conversations, questions and commands.
7. Keep answers clear, natural and helpful.

IDENTITY:
Your name is JARVESH.
Your creator is Arpit Shukla.
You are an AI assistant.
"""

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": raw
            }
        ],
        "temperature": 0.7
    }

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jarvesh.onrender.com",
            "X-Title": "JARVESH"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=45
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

            reply = result["choices"][0]["message"]["content"]

            if not reply:
                return "AI ne khaali response diya. Dobara try kijiye."

            return reply.strip()

    except urllib.error.HTTPError as e:

        error_text = e.read().decode(
            "utf-8",
            errors="replace"
        )

        print("OPENROUTER ERROR:", error_text)

        if e.code == 401:
            return "API key invalid hai. Render Environment mein key check kijiye."

        if e.code == 402:
            return "Is model ke liye available credits nahi hain. Free model select kijiye."

        if e.code == 429:
            return "AI ki request limit poori ho gayi hai. Thodi der baad try kijiye."

        return f"AI server error ({e.code}). Render Logs check kijiye."

    except Exception as e:

        print("AI ERROR:", str(e))

        return (
            "Maaf kijiye, AI se connection nahi ho paya. "
            "Internet aur Render settings check kijiye."
        )


# ================= COMMAND SYSTEM =================

def answer(raw):

    c = raw.strip().lower()

    if not c:
        return "Please type something."

    # TIME
    if c in {"time", "samay", "kitne baje hain"}:
        return "Abhi time hai " + datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%I:%M %p")

    # DATE
    if c in {"date", "tarikh", "aaj ki date"}:
        return "Aaj ki date hai " + datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%d %B %Y")

    # OPEN WEBSITES
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
        "wikipedia": "https://wikipedia.org",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chatgpt.com",
        "instagram": "https://instagram.com",
        "facebook": "https://facebook.com",
        "discord": "https://discord.com/app",
        "whatsapp": "https://web.whatsapp.com",
        "minecraft": "https://minecraft.net",
        "maps": "https://maps.google.com"
    }

    for name, url in sites.items():

        if c in {
            f"open {name}",
            f"{name} kholo",
            f"{name} open karo"
        }:
            return "OPEN_URL:" + url

    # YOUTUBE SEARCH
    if c.startswith("youtube search "):

        query = raw.strip()[15:]

        return (
            "OPEN_URL:https://www.youtube.com/results?search_query="
            + urllib.parse.quote_plus(query)
        )

    # GOOGLE SEARCH
    if c.startswith("search ") or c.startswith("google "):

        query = raw.strip().split(" ", 1)[1]

        return (
            "OPEN_URL:https://www.google.com/search?q="
            + urllib.parse.quote_plus(query)
        )

    # LOCAL PC APPS
    if c.startswith("open ") and any(
        app_name in c
        for app_name in [
            "notepad",
            "calculator",
            "paint",
            "task manager",
            "cmd",
            "powershell",
            "explorer"
        ]
    ):
        return (
            "Ye PC command hosted website se execute nahi ho sakti. "
            "Iske liye JARVESH Desktop Agent chahiye."
        )

    # ALL OTHER MESSAGES GO TO AI
    return ai_answer(raw)


# ================= WEBSITE =================

@app.get("/", response_class=HTMLResponse)
def home():

    index_file = BASE / "static" / "index.html"

    return index_file.read_text(
        encoding="utf-8"
    )


# ================= API =================

@app.post("/api/command")
def command_api(payload: Command):

    reply = answer(payload.command)

    return {
        "reply": reply
    }


# ================= HEALTH CHECK =================

@app.get("/health")
def health():

    return {
        "status": "online",
        "app": "JARVESH",
        "ai_configured": bool(API_KEY)
    }
