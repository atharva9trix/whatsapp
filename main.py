from fastapi import FastAPI, Request
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration
EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host"
INSTANCE = "whatsappbot"
API_KEY = "4EB3C96EBCB4-4CE2-864C-0FF043FB41EC"

@app.get("/")
def home():
    return {"status": "bot running"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {"status": "error", "message": "Invalid JSON"}

    logger.info(f"Webhook received: {json.dumps(data)}")

    # Check if it's a message event
    if data.get("event") != "messages.upsert":
        return {"status": "ignored", "reason": "Not a messages.upsert event"}

    # Extract message data
    message_data = data.get("data", {})
    key = message_data.get("key", {})
    
    # Ignore messages sent by the bot itself
    if key.get("fromMe"):
        logger.info("Ignoring self message")
        return {"status": "ignored", "reason": "Self message"}

    remote_jid = key.get("remoteJid", "")
    if not remote_jid:
        logger.warning("No remoteJid found in message key")
        return {"status": "error", "message": "No remoteJid found"}

    recipient_number = remote_jid.split("@")[0]
    
    # Extract text content from various message types
    msg = message_data.get("message", {})
    if not msg:
        logger.info("Ignoring empty message object (might be a status or reaction)")
        return {"status": "ignored", "reason": "No message content"}

    incoming_text = ""
    # Support multiple message types
    if "conversation" in msg:
        incoming_text = msg["conversation"]
    elif "extendedTextMessage" in msg:
        incoming_text = msg["extendedTextMessage"].get("text", "")
    elif "imageMessage" in msg:
        incoming_text = msg["imageMessage"].get("caption", "")
    elif "videoMessage" in msg:
        incoming_text = msg["videoMessage"].get("caption", "")
    
    if not incoming_text:
        logger.info("No text content found in message")
        return {"status": "ignored", "reason": "No text content"}

    logger.info(f"Incoming message from {recipient_number}: {incoming_text}")

    # Simple logic for reply
    # You can expand this logic as needed
    reply_text = "Hello! 👋 I received your message: " + incoming_text
    
    # Send response
    success = send_message(recipient_number, reply_text)
    
    if success:
        return {"status": "success", "recipient": recipient_number}
    else:
        return {"status": "failed", "recipient": recipient_number}

def send_message(number, text):
    """Sends a text message using the Evolution API."""
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    # First attempt: standard Evolution API payload
    payload = {
        "number": number,
        "text": text,
        "delay": 1200,
        "linkPreview": False
    }

    try:
        logger.info(f"Sending reply to {number} via Evolution API...")
        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"Evolution API Response ({response.status_code}): {response.text}")
        
        if response.status_code in [200, 201]:
            return True
        else:
            # Fallback for Evolution API versions that require 'textMessage' structure
            logger.info("Standard payload failed, retrying with textMessage structure (v2 style)...")
            v2_payload = {
                "number": number,
                "textMessage": {"text": text}
            }
            response = requests.post(url, json=v2_payload, headers=headers)
            logger.info(f"Evolution API v2 Response ({response.status_code}): {response.text}")
            return response.status_code in [200, 201]
            
    except Exception as e:
        logger.error(f"Critical error sending message: {e}")
        return False
