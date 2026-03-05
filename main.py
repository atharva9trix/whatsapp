from fastapi import FastAPI, Request
import requests
import logging

app = FastAPI()

EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
INSTANCE = "whatsappbot"
API_KEY = "4EB3C96EBCB4-4CE2-864C-0FF043FB41EC"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_message(number, text):

    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "number": number,
        "text": text
    }

    logger.info(f"SENDING MESSAGE -> {number}")
    logger.info(f"PAYLOAD -> {payload}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)

        logger.info(f"EVOLUTION STATUS -> {response.status_code}")
        logger.info(f"EVOLUTION RESPONSE -> {response.text}")

    except Exception as e:
        logger.error(f"SEND FAILED -> {e}")

@app.get("/")
def home():
    return {"status": "bot running"}


@app.post("/webhook")
async def webhook(request: Request):

    # Safely read JSON
    try:
        data = await request.json()
    except Exception:
        logger.warning("Webhook called without JSON body")
        return {"status": "ignored", "reason": "invalid json"}

    logger.info(f"Webhook data: {data}")

    event = data.get("event")

    if event != "messages.upsert":
        return {"ignored": "not message event"}

    message_data = data.get("data", {})
    key = message_data.get("key", {})

    # Prevent bot replying to itself
    if key.get("fromMe"):
        return {"ignored": "self message"}

    remote_jid = key.get("remoteJid")

    if not remote_jid:
        return {"ignored": "no jid"}

    number = remote_jid.split("@")[0]

    msg = message_data.get("message", {})
    text = ""

    # Extract text safely
    if "conversation" in msg:
        text = msg.get("conversation", "")

    elif "extendedTextMessage" in msg:
        text = msg.get("extendedTextMessage", {}).get("text", "")

    if not text:
        return {"ignored": "no text"}

    logger.info(f"Message received from {number}: {text}")

    reply = f"You said: {text}"

    send_message(number, reply)

    return {"status": "processed"}
