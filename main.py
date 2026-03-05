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

# Global variable to store last few webhooks for debugging
webhook_history = []

@app.get("/")
def home():
    return {
        "status": "bot running",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "debug": "/debug (GET)",
            "test": "/test-send?number=... (GET)"
        }
    }

@app.get("/debug")
def get_debug():
    """Returns the last 5 webhooks received for manual debugging."""
    return {
        "count": len(webhook_history),
        "history": webhook_history
    }

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        logger.warning("⚠️ Received webhook with no JSON body")
        return {"status": "ignored", "reason": "Empty or invalid JSON"}

    logger.info("📥 WEBHOOK RECEIVED")

    # Store debug history
    webhook_history.insert(0, {
        "time": str(logging.datetime.datetime.now()),
        "data": data
    })

    if len(webhook_history) > 5:
        webhook_history.pop()
            
        logger.info(f"📥 WEBHOOK RECEIVED")
    except Exception as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return {"status": "error", "message": "Invalid JSON"}

    # Relaxed event check - Evolutionary API sometimes sends different event names
    event = data.get("event")
    logger.info(f"Event type: {event}")

    # Check for messages.upsert or similar
    if "messages" not in str(event).lower():
        return {"status": "ignored", "reason": f"Not a message event ({event})"}

    # Extract message data
    message_data = data.get("data", {})
    key = message_data.get("key", {})
    
    # Ignore messages sent by the bot itself
    if key.get("fromMe"):
        logger.info("ℹ️ Ignoring self message")
        return {"status": "ignored", "reason": "Self message"}

    remote_jid = key.get("remoteJid", "")
    if not remote_jid:
        return {"status": "error", "message": "No remoteJid found"}

    recipient_number = remote_jid.split("@")[0]
    
    # Extract text content - try every possible location
    msg = message_data.get("message", {})
    incoming_text = ""
    
    if msg:
        if "conversation" in msg:
            incoming_text = msg["conversation"]
        elif "extendedTextMessage" in msg:
            incoming_text = msg.get("extendedTextMessage", {}).get("text", "")
        elif "imageMessage" in msg:
            incoming_text = msg.get("imageMessage", {}).get("caption", "")
        elif "videoMessage" in msg:
            incoming_text = msg.get("videoMessage", {}).get("caption", "")
        elif "buttonsResponseMessage" in msg:
            incoming_text = msg.get("buttonsResponseMessage", {}).get("selectedButtonId", "")
        elif "listResponseMessage" in msg:
            incoming_text = msg.get("listResponseMessage", {}).get("title", "")

    if not incoming_text:
        logger.info("ℹ️ No text content found in message structure")
        return {"status": "ignored", "reason": "No text content"}

    logger.info(f"📩 MESSAGE FROM {recipient_number}: {incoming_text}")

    # Reply logic
    reply_text = f"Bot Received: {incoming_text}"
    
    # Send response
    success = send_message(recipient_number, reply_text)
    
    return {
        "status": "success" if success else "failed", 
        "event": event,
        "recipient": recipient_number
    }

@app.get("/test-send")
async def test_send(number: str):
    """Diagnostic endpoint to test Evolution API directly."""
    logger.info(f"🧪 Running diagnostic test for number: {number}")
    success = send_message(number, "Direct Test Result: SUCCESS ✅")
    if success:
        return {"status": "success", "message": f"Message sent to {number}"}
    else:
        return {"status": "failed", "message": "API call failed. Check Evolution API settings (URL/Key/Instance)."}

def send_message(number, text):
    """Sends a text message using the Evolution API with fallback logic."""
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    # Attempt 1: Standard v2 Payload
    payload = {
        "number": number,
        "text": text
    }

    try:
        logger.info(f"🚀 ATTEMPTING SEND -> {number}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info(f"📡 API STATUS: {response.status_code}")
        
        if response.status_code in [200, 201]:
            return True
        
        # Attempt 2: textMessage structure (v2 v2)
        logger.info("⚠️ Trying fallback structure...")
        v2_payload = {
            "number": number,
            "textMessage": {"text": text}
        }
        response = requests.post(url, json=v2_payload, headers=headers, timeout=10)
        logger.info(f"📡 FALLBACK STATUS: {response.status_code}")
        
        return response.status_code in [200, 201]
            
    except Exception as e:
        logger.error(f"❌ SEND ERROR: {e}")
        return False
