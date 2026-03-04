from fastapi import FastAPI, Request
import requests

app = FastAPI()

EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
INSTANCE = "whatsappbot"
API_KEY = "5D0A84B47ED9-42A1-B2D2-DF565E539746"


@app.get("/")
def home():
    return {"status": "running"}


# @app.post("/webhook")
# async def webhook(request: Request):

#     data = await request.json()
#     print("Webhook received:", data)

#     try:

#         # Process only incoming messages
#         if data.get("event") != "messages.upsert":
#             return {"status": "ignored"}

#         message_data = data.get("data", {})

#         number = message_data["key"]["remoteJid"].replace("@s.whatsapp.net", "")

#         msg = message_data.get("message", {})

#         message = (
#             msg.get("conversation")
#             or msg.get("extendedTextMessage", {}).get("text")
#         )

#         print("Incoming message:", message)

#         send_message(number, "Hello 👋 I am your bot")

#     except Exception as e:
#         print("Error:", e)

#     return {"status": "received"}

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("FULL WEBHOOK DATA:", data)

    return {"status": "received"}


def send_message(number, text):

    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

    payload = {
        "number": number,
        "text": text
    }

    headers = {
        "apikey": API_KEY
    }

    r = requests.post(url, json=payload, headers=headers)

    print("Send message response:", r.text)
