from fastapi import FastAPI, Request
import requests

app = FastAPI()

EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
INSTANCE = "whatsappbot"
API_KEY = "5D0A84B47ED9-42A1-B2D2-DF565E539746"


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("Webhook received:", data)

    try:
        number = data["data"]["key"]["remoteJid"].replace("@s.whatsapp.net", "")

        message = (
            data["data"]["message"].get("conversation")
            or data["data"]["message"].get("extendedTextMessage", {}).get("text")
        )

        print("Incoming message:", message)

        send_message(number, "Hello 👋 I am your bot")

    except Exception as e:
        print("Error:", e)

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
