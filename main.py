from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from zoneinfo import ZoneInfo
import urllib.parse

BASE = Path(__file__).parent
app = FastAPI(title="JARVESH")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

class Command(BaseModel):
    command: str

def answer(raw):
    c = raw.strip().lower()
    if not c: return "Koi command likhiye."
    if c in {"hello", "hi", "hey", "namaste"}: return "Namaste! Main JARVESH hoon. Bataiye, kya karna hai?"
    if "kaise ho" in c or "how are you" in c: return "Main bilkul theek hoon. Aap kaise hain?"
    if "tumhara naam" in c or "your name" in c: return "Mera naam JARVESH hai."
    if "creator" in c or "kisne banaya" in c: return "Mujhe Arpit Shukla ne banaya hai."
    if c in {"time", "samay"}: return "Abhi time hai " + datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p")
    if c in {"date", "tarikh"}: return "Aaj ki date hai " + datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %B %Y")
    if c in {"joke", "mazak"}: return "Computer doctor ke paas kyun gaya? Usko virus ho gaya tha!"
    if c in {"help", "commands", "/commands", "command list"}:
        return "Commands: hello, kaise ho, tumhara naam, creator, time, date, open youtube/google/wikipedia/gmail/github/chatgpt, search [query], youtube search [query], yaad rakho [baat], meri memory, alarm [minutes], joke, clear chat."
    sites = {"youtube":"https://youtube.com","google":"https://google.com","wikipedia":"https://wikipedia.org","gmail":"https://mail.google.com","github":"https://github.com","chatgpt":"https://chatgpt.com","instagram":"https://instagram.com","facebook":"https://facebook.com","whatsapp":"https://web.whatsapp.com","discord":"https://discord.com/app","minecraft":"https://minecraft.net","maps":"https://maps.google.com"}
    for name, url in sites.items():
        if c in {f"open {name}", f"{name} kholo"}: return "OPEN_URL:" + url
    if c.startswith("youtube search "):
        return "OPEN_URL:https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(c[14:])
    if c.startswith("search ") or c.startswith("google "):
        return "OPEN_URL:https://www.google.com/search?q=" + urllib.parse.quote_plus(c.split(" ",1)[1])
    if c.startswith("yaad rakho"):
        fact = raw.strip()[len("yaad rakho"):].strip()
        return "SAVE_MEMORY:" + fact if fact else "Kya yaad rakhna hai?"
    if c in {"meri memory", "maine kya bataya"}: return "GET_MEMORY"
    if c.startswith("alarm "):
        try:
            n = int(c.split()[1])
            if 1 <= n <= 1440: return f"SET_ALARM:{n}"
        except (ValueError, IndexError): pass
        return "Example: alarm 5 (1 se 1440 minute)."
    if c in {"clear chat", "chat clear"}: return "CLEAR_CHAT"
    if c.startswith("open ") and any(x in c for x in ["notepad","calculator","paint","task manager","cmd","powershell","control panel","explorer"]):
        return "Ye PC command hosted website se execute nahi ho sakti. Iske liye aapke PC par alag JARVESH Desktop Agent chahiye."
    return "Maaf kijiye, ye command abhi samajh nahi aayi. 'help' likhkar commands dekhiye."

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/command")
def command_api(payload: Command):
    return {"reply": answer(payload.command)}
