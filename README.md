# JARVESH Web

Browser version of JARVESH commands.

Deploy on Render as a Python web service. Build: `pip install -r requirements.txt`. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`.

The browser stores memory locally. Voice support depends on browser permissions. Alarms work only while the page remains open. Hosted websites cannot run Windows applications on a visitor's PC; use a separate authorized desktop agent for that.
