# from fastapi import FastAPI, Request
# import requests
# import logging

# app = FastAPI()

# EVOLUTION_URL = "http://whatsapp-1-evolution-api:8080"
# INSTANCE = "whatsappbot"
# API_KEY = "4EB3C96EBCB4-4CE2-864C-0FF043FB41EC"

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def send_message(number, text):

#     url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

#     headers = {
#         "apikey": API_KEY,
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "number": number,
#         "text": text
#     }

#     logger.info(f"SENDING MESSAGE -> {number}")
#     logger.info(f"PAYLOAD -> {payload}")

#     try:
#         response = requests.post(url, json=payload, headers=headers, timeout=15)

#         logger.info(f"EVOLUTION STATUS -> {response.status_code}")
#         logger.info(f"EVOLUTION RESPONSE -> {response.text}")

#     except Exception as e:
#         logger.error(f"SEND FAILED -> {e}")

# @app.get("/")
# def home():
#     return {"status": "bot running"}


# @app.post("/webhook")
# async def webhook(request: Request):

#     logger.info("WEBHOOK HIT")

#     data = await request.json()
#     logger.info(f"Payload: {data}")
#     # Safely read JSON
#     try:
#         data = await request.json()
#     except Exception:
#         logger.warning("Webhook called without JSON body")
#         return {"status": "ignored", "reason": "invalid json"}

#     logger.info(f"Webhook data: {data}")

#     event = data.get("event")

#     if "message" not in str(event).lower():
#         return {"ignored": True}

#     message_data = data.get("data", {})
#     key = message_data.get("key", {})

#     # Prevent bot replying to itself
#     if key.get("fromMe"):
#         return {"ignored": "self message"}

#     remote_jid = key.get("remoteJid")

#     if not remote_jid:
#         return {"ignored": "no jid"}

#     number = remote_jid.split("@")[0]

#     msg = message_data.get("message", {})
#     text = ""

#     # Extract text safely
#     if "conversation" in msg:
#         text = msg.get("conversation", "")

#     elif "extendedTextMessage" in msg:
#         text = msg.get("extendedTextMessage", {}).get("text", "")

#     if not text:
#         return {"ignored": "no text"}

#     logger.info(f"Message received from {number}: {text}")

#     reply = f"You said: {text}"

#     send_message(number, reply)

#     return {"status": "processed"}

from fastapi import FastAPI, Request
import requests
import logging

app = FastAPI()

# # Evolution API config
# EVOLUTION_URL = "http://whatsapp-1_evolution-api:8080"
# INSTANCE = "whatsappbot"
# API_KEY = "4EB3C96EBCB4-4CE2-864C-0FF043FB41EC"

EVOLUTION_API = os.getenv("EVOLUTION_API_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = os.getenv("INSTANCE_NAME")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to send WhatsApp message
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


# Health check
@app.get("/")
def home():
    return {"status": "WhatsApp bot running 🚀"}


# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):

    logger.info("WEBHOOK HIT")

    try:
        data = await request.json()
    except Exception:
        logger.warning("Invalid JSON received")
        return {"status": "ignored"}

    logger.info(f"Webhook payload: {data}")

    event = data.get("event", "")

    # Only process message events
    if "message" not in event.lower():
        return {"ignored": "not message event"}

    message_data = data.get("data", {})
    key = message_data.get("key", {})

    # Ignore messages sent by the bot itself
    if key.get("fromMe"):
        return {"ignored": "self message"}

    remote_jid = key.get("remoteJid")

    if not remote_jid:
        return {"ignored": "no sender"}

    # Extract phone number
    number = remote_jid.split("@")[0]

    msg = message_data.get("message", {})
    text = ""

    # Extract message text safely
    if "conversation" in msg:
        text = msg.get("conversation", "")

    elif "extendedTextMessage" in msg:
        text = msg.get("extendedTextMessage", {}).get("text", "")

    if not text:
        return {"ignored": "no text"}

    logger.info(f"Message received from {number}: {text}")

    # Bot reply
    reply = f"You said: {text}"

    send_message(number, reply)

    return {"status": "processed"}
