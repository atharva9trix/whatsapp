from fastapi import FastAPI, Request

app = FastAPI()

# @app.get("/")
# def home():
#     return {"status": "running"}

# @app.post("/webhook")
# async def webhook(request: Request):
#     data = await request.json()
#     print(data)
#     return {"status": "received"}

EVOLUTION_URL = "https://whatsapp-1-evolution-api.n0r6ff.easypanel.host/manager"
INSTANCE = "Demo1"
API_KEY = "7D3A3FE318B8-4F2D-AB6A-FCC54686DF98"


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()
    print(data)

    try:
        number = data["data"]["key"]["remoteJid"].replace("@s.whatsapp.net", "")
        message = data["data"]["message"]["conversation"]

        send_message(number, "Hello 👋 I am your bot")

    except:
        pass

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

    requests.post(url, json=payload, headers=headers)
