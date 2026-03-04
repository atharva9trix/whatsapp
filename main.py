# from fastapi import FastAPI, Request
# import requests

# app = FastAPI()

# EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
# INSTANCE = "whatsappbot"
# API_KEY = "5D0A84B47ED9-42A1-B2D2-DF565E539746"


# @app.get("/")
# def home():
#     return {"status": "running"}


# @app.post("/webhook")
# async def webhook(request: Request):

#     data = await request.json()
#     print("Webhook received:", data)

#     try:

#         if data.get("event") != "messages.upsert":
#             return {"status": "ignored"}

#         message_data = data.get("data", {})

#         # ignore messages sent by bot
#         if message_data.get("key", {}).get("fromMe"):
#             return {"status": "self message ignored"}

#         number = message_data["key"]["remoteJid"].replace("@s.whatsapp.net", "")

#         msg = message_data.get("message", {})

#         message = (
#             msg.get("conversation")
#             or msg.get("extendedTextMessage", {}).get("text")
#         )

#         print("Incoming message:", message)

#         if message:
#             send_message(number, "Hello 👋 I am your bot")

#         return {"status": "ok"}

#     except Exception as e:
#         print("Error:", e)
#         return {"status": f"failed {e}"}


# def send_message(number, text):

#     url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

#     payload = {
#         "number": number,
#         "text": text
#     }

#     headers = {
#         "apikey": API_KEY,
#         "Content-Type": "application/json"
#     }

#     r = requests.post(url, json=payload, headers=headers)

#     print("Send message response:", r.text)

# from fastapi import FastAPI, Request
# import requests
# import os

# app = FastAPI()

# # EVOLUTION_API = os.getenv("https://whatsapp-1-evolution-api.n0r6ff.easypanel.host")
# # API_KEY = os.getenv("5D0A84B47ED9-42A1-B2D2-DF565E539746")
# # INSTANCE = os.getenv("whatsappbot")

# EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
# INSTANCE = "whatsappbot"
# API_KEY = "5D0A84B47ED9-42A1-B2D2-DF565E539746"


# @app.post("/webhook")
# async def webhook(request: Request):
#     payload = await request.json()

#     try:
#         message = payload["data"]["message"]["conversation"].lower()
#         number = payload["data"]["key"]["remoteJid"].split("@")[0]
#     except Exception as e:
#         return {"ignored": True}

#     reply = "👋 Hi!\n1️⃣ Book appointment\n2️⃣ Help"

#     if "hi" in message or "hello" in message:
#         reply = "👋 Hello! What would you like to do?\n1️⃣ Book appointment\n2️⃣ Help"

#     if "help" in message:
#         reply = "ℹ️ I can help you book appointments via WhatsApp."

#     send_message(number, reply)
#     return {"status": "sent"}


# def send_message(number, text):
#     url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
#     headers = {
#         # "apikey": API_KEY,
#         "apikey": EVOLUTION_URL,
#         "Content-Type": "application/json"
#     }
#     data = {
#         "number": number,
#         "text": text
#     }
#     requests.post(url, json=data, headers=headers)

from fastapi import FastAPI, Request
import requests

app = FastAPI()

EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
INSTANCE = "whatsappbot"
API_KEY = "4EB3C96EBCB4-4CE2-864C-0FF043FB41EC"


@app.get("/")
def home():
    return {"status": "bot running"}


@app.post("/webhook")
async def webhook(request: Request):

    payload = await request.json()

    print("Webhook payload:", payload)

    if payload.get("event") != "messages.upsert":
        return {"ignored": True}

    try:

        if payload["data"]["key"]["fromMe"]:
            return {"ignored": True}

        number = payload["data"]["key"]["remoteJid"].split("@")[0]

        msg = payload.get("data", {}).get("message", {})

        message = (
            msg.get("conversation")
            or msg.get("extendedTextMessage", {}).get("text")
        )

        if not message:
            return {"ignored": True}

        message = message.lower()

        print("Incoming message:", message)

    except Exception as e:
        print("Error:", e)
        return {"ignored": True}

    reply = "👋 Hi!\n1️⃣ Book appointment\n2️⃣ Help"

    if "hi" in message or "hello" in message:
        reply = "👋 Hello! What would you like to do?\n1️⃣ Book appointment\n2️⃣ Help"

    if "help" in message:
        reply = "ℹ️ I can help you book appointments via WhatsApp."

    send_message(number, reply)

    return {"status": "sent"}


def send_message(number, text):

    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "number": number,
        "text": text
    }

    r = requests.post(url, json=data, headers=headers)

    print("Response:", r.text)
