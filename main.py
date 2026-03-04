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
        body = await request.body()
        data = json.loads(body)
        logger.info(f"📥 WEBHOOK RECEIVED: {json.dumps(data, indent=2)}")
    except Exception as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return {"status": "error", "message": "Invalid JSON"}

    # Check if it's a message event
    event = data.get("event")
    if event != "messages.upsert":
        logger.info(f"ℹ️ Ignoring event: {event}")
        return {"status": "ignored", "reason": f"Not a messages.upsert event ({event})"}

    # Extract message data
    message_data = data.get("data", {})
    key = message_data.get("key", {})
    
    # Ignore messages sent by the bot itself
    if key.get("fromMe"):
        logger.info("ℹ️ Ignoring self message")
        return {"status": "ignored", "reason": "Self message"}

    remote_jid = key.get("remoteJid", "")
    if not remote_jid:
        logger.warning("⚠️ No remoteJid found in message key")
        return {"status": "error", "message": "No remoteJid found"}

    recipient_number = remote_jid.split("@")[0]
    
    # Extract text content from various message types
    msg = message_data.get("message", {})
    if not msg:
        logger.info("ℹ️ Ignoring message with no content (reaction/status)")
        return {"status": "ignored", "reason": "No message content"}

    incoming_text = ""
    if "conversation" in msg:
        incoming_text = msg["conversation"]
    elif "extendedTextMessage" in msg:
        incoming_text = msg["extendedTextMessage"].get("text", "")
    elif "imageMessage" in msg:
        incoming_text = msg["imageMessage"].get("caption", "")
    elif "videoMessage" in msg:
        incoming_text = msg["videoMessage"].get("caption", "")
    
    if not incoming_text:
        logger.info("ℹ️ No text content found in message")
        return {"status": "ignored", "reason": "No text content"}

    logger.info(f"📩 MESSAGE FROM {recipient_number}: {incoming_text}")

    # Reply logic
    reply_text = f"Hello! 👋 I received your message: {incoming_text}"
    
    # Send response
    success = send_message(recipient_number, reply_text)
    
    if success:
        return {"status": "success", "recipient": recipient_number}
    else:
        return {"status": "failed", "recipient": recipient_number}

@app.get("/test-send")
async def test_send(number: str):
    """Diagnostic endpoint to test Evolution API directly."""
    logger.info(f"🧪 Running diagnostic test for number: {number}")
    success = send_message(number, "Test message from Dashboard 🧪")
    if success:
        return {"status": "success", "message": f"Test message sent to {number}"}
    else:
        return {"status": "failed", "message": "Failed to send test message. Check application logs."}

def send_message(number, text):
    """Sends a text message using the Evolution API with fallback logic."""
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    # Attempt 1: Standard v2 Paylod (Number and Text at top level)
    payload = {
        "number": number,
        "text": text,
        "delay": 1200,
        "linkPreview": False
    }

    try:
        logger.info(f"🚀 SENDING to {number} via {url}...")
        logger.info(f"📦 PAYLOAD: {json.dumps(payload)}")
        
        response = requests.post(url, json=payload, headers=headers)
        logger.info(f"📡 RESPONSE ({response.status_code}): {response.text}")
        
        if response.status_code in [200, 201]:
            return True
        
        # Attempt 2: textMessage structure (Some v2 versions)
        logger.info("⚠️ Attempt 1 failed, trying fallback structure (textMessage)...")
        v2_payload = {
            "number": number,
            "textMessage": {"text": text}
        }
        response = requests.post(url, json=v2_payload, headers=headers)
        logger.info(f"📡 FALLBACK RESPONSE ({response.status_code}): {response.text}")
        
        return response.status_code in [200, 201]
            
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR in send_message: {e}")
        return False
