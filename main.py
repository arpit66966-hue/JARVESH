
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from zoneinfo import ZoneInfo
import urllib.parse
import random
import re
import io
import base64

import cv2
import numpy as np

BASE = Path(__file__).parent

app = FastAPI(title="JARVESH")

app.mount(
    "/static",
    StaticFiles(directory=BASE / "static"),
    name="static"
)


class Command(BaseModel):
    command: str


def detect_language(text):
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    words = text.lower().split()

    hinglish_words = {
        "hai", "hain", "ho", "kya", "kaise", "mera",
        "meri", "tum", "tumhara", "batao", "kar",
        "karo", "nahi", "haan", "acha", "achha",
        "kyun", "kaun", "aur", "mein", "mujhe"
    }

    if any(word in hinglish_words for word in words):
        return "hinglish"

    return "english"


def answer(raw):
    c = raw.strip().lower()
    lang = detect_language(raw)

    if not c:
        return "Please type something."

    if c in {"hi", "hello", "hey", "namaste", "hii"}:
        if lang == "hindi":
            return "नमस्ते! मैं JARVESH हूँ। बताइए, मैं आपकी क्या मदद कर सकता हूँ?"
        if lang == "hinglish":
            return "Namaste! Main JARVESH hoon. Batao, kya help chahiye?"
        return "Hello! I am JARVESH. How can I help you today?"

    if any(x in c for x in ["kaise ho", "how are you", "कैसे हो"]):
        if lang == "hindi":
            return "मैं बिल्कुल ठीक हूँ! आप कैसे हैं?"
        if lang == "hinglish":
            return "Main bilkul theek hoon! Tum kaise ho?"
        return "I am doing great! How are you?"

    if any(x in c for x in ["tumhara naam", "your name", "आपका नाम", "naam kya hai"]):
        if lang == "hindi":
            return "मेरा नाम JARVESH है।"
        if lang == "hinglish":
            return "Mera naam JARVESH hai."
        return "My name is JARVESH."

    if any(x in c for x in ["creator", "kisne banaya", "who created you", "who made you"]):
        if lang == "hindi":
            return "मुझे Arpit Shukla ने बनाया है।"
        if lang == "hinglish":
            return "Mujhe Arpit Shukla ne banaya hai."
        return "I was created by Arpit Shukla."

    if c in {"time", "samay", "time batao", "what time is it"}:
        now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p")
        if lang == "hindi":
            return "अभी समय है " + now
        if lang == "hinglish":
            return "Abhi time hai " + now
        return "The current time is " + now

    if c in {"date", "tarikh", "aaj ki date", "what is the date"}:
        now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %B %Y")
        if lang == "hindi":
            return "आज की तारीख है " + now
        if lang == "hinglish":
            return "Aaj ki date hai " + now
        return "Today's date is " + now

    if any(x in c for x in ["thank you", "thanks", "shukriya", "धन्यवाद"]):
        if lang == "hindi":
            return "आपका स्वागत है!"
        if lang == "hinglish":
            return "Koi baat nahi! Main madad ke liye yahan hoon."
        return "You're welcome! Happy to help."

    if c in {"joke", "mazak", "tell me a joke"}:
        jokes = {
            "hindi": "कंप्यूटर डॉक्टर के पास क्यों गया? क्योंकि उसे वायरस हो गया था!",
            "hinglish": "Computer doctor ke paas kyun gaya? Kyunki usko virus ho gaya tha!",
            "english": "Why did the computer go to the doctor? Because it caught a virus!"
        }
        return jokes[lang]

    if c in {"help", "commands", "/commands", "command list"}:
        return (
            "Commands: hello, kaise ho, tumhara naam, creator, "
            "time, date, joke, open youtube, open google, "
            "open github, search [query], youtube search [query]."
        )

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

    if c.startswith("youtube search "):
        query = raw.strip()[15:]
        return (
            "OPEN_URL:https://www.youtube.com/results?search_query="
            + urllib.parse.quote_plus(query)
        )

    if c.startswith("search ") or c.startswith("google "):
        query = raw.strip().split(" ", 1)[1]
        return (
            "OPEN_URL:https://www.google.com/search?q="
            + urllib.parse.quote_plus(query)
        )

    if any(x in c for x in ["what can you do", "tum kya kar sakte ho", "kya kar sakte ho"]):
        if lang == "hindi":
            return "मैं समय, तारीख, वेबसाइट खोलने और Google या YouTube पर खोजने में मदद कर सकता हूँ।"
        if lang == "hinglish":
            return "Main time, date, websites open aur Google/YouTube search kar sakta hoon."
        return "I can tell the time and date, open websites, and search Google or YouTube."

    if any(x in c for x in ["good morning", "good evening", "good night"]):
        if lang == "hindi":
            return "आपका दिन शुभ हो!"
        if lang == "hinglish":
            return "Aapka din achha rahe!"
        return "Have a wonderful day!"

    if lang == "hindi":
        return "माफ कीजिए, मैं अभी इस बात को समझ नहीं पाया। 'help' लिखकर commands देखिए।"

    if lang == "hinglish":
        return "Maaf kijiye, main abhi ye baat samajh nahi paya. 'help' likhkar commands dekhiye."

    return "Sorry, I don't understand that yet. Type 'help' to see my commands."


# ==========================
# 🌿 JARVESH PLANT DOCTOR
# ==========================

@app.post("/api/plant-scan")
async def plant_scan(file: UploadFile = File(...)):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image.")

    raw_image = await file.read()

    if len(raw_image) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image is too large. Maximum 8 MB.")

    image_array = np.frombuffer(raw_image, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image.")

    # Resize image for faster processing
    h, w = img.shape[:2]
    max_dimension = 1200

    if max(h, w) > max_dimension:
        scale = max_dimension / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Yellow leaf area
    yellow_mask = cv2.inRange(
        hsv,
        np.array([15, 35, 40]),
        np.array([40, 255, 255])
    )

    # Brown area
    brown_mask = cv2.inRange(
        hsv,
        np.array([5, 40, 20]),
        np.array([25, 255, 180])
    )

    masks = [
        ("YELLOW AREA", yellow_mask, (0, 255, 255)),
        ("BROWN / SPOTS", brown_mask, (0, 0, 255))
    ]

    annotated = img.copy()
    observations = []
    total_marked = 0

    for label, mask, color in masks:

        # Reduce small noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        count = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < 250:
                continue

            x, y, cw, ch = cv2.boundingRect(contour)

            cv2.rectangle(
                annotated,
                (x, y),
                (x + cw, y + ch),
                color,
                3
            )

            cv2.putText(
                annotated,
                label,
                (x, max(y - 10, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA
            )

            count += 1

        if count:
            observations.append(f"{label}: {count} area(s)")
            total_marked += count

    if total_marked == 0:
        observations.append(
            "No large yellow or brown color regions were detected."
        )

    report = {
        "title": "JARVESH Plant Doctor Report",
        "date": datetime.now(ZoneInfo("Asia/Kolkata")).strftime(
            "%d-%m-%Y %I:%M %p"
        ),
        "observations": observations,
        "note": (
            "This is a color-based visual scan, not a confirmed disease diagnosis. "
            "Yellow or brown colors may be natural or caused by lighting."
        ),
        "care_tips": [
            "Check soil moisture before watering.",
            "Ensure the pot has drainage.",
            "Inspect the underside of leaves for pests.",
            "Observe whether discoloration spreads."
        ]
    }

    # Encode marked image as JPEG
    success, buffer = cv2.imencode(".jpg", annotated)

    if not success:
        raise HTTPException(status_code=500, detail="Could not create scan image.")

    marked_image = base64.b64encode(buffer).decode("utf-8")

    return {
        "report": report,
        "marked_image": "data:image/jpeg;base64," + marked_image
    }


@app.get("/", response_class=HTMLResponse)
def home():
    return (
        BASE / "static" / "index.html"
    ).read_text(encoding="utf-8")


@app.post("/api/command")
def command_api(payload: Command):
    return {"reply": answer(payload.command)}


@app.get("/health")
def health():
    return {
        "status": "online",
        "app": "JARVESH",
        "ai_required": False,
        "plant_doctor": True
    }
