from flask import Flask
import threading, time, requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensaje(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto})
        print(f"Enviado: {texto}")
    except Exception as e:
        print(e)

def bot_loop():
    enviar_mensaje("✅ BOT PRO 32 PARES INICIADO - Ya estoy analizando Deivid")
    while True:
        try:
            enviar_mensaje("🔥 SEÑAL TEST - EUR/USD - COMPRA 85% - 5 MIN")
            time.sleep(300)
        except Exception as e:
            print(e)
            time.sleep(60)

@app.route('/')
def home():
    return "BOT FUNCIONANDO"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
