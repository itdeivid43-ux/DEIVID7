import os
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask
import yfinance as yf

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","USDCHF=X",
"EURJPY=X","EURGBP=X","EURCAD=X","EURAUD=X","EURCHF=X","GBPJPY=X","GBPCAD=X",
"GBPCHF=X","GBPAUD=X","AUDJPY=X","AUDCAD=X","AUDCHF=X","CADJPY=X","CHFJPY=X",
"EURUSD=X","GBPUSD=X","NZDUSD=X","NZDJPY=X","NZDCAD=X","NZDCHF=X","EURNZD=X",
"GBPNZD=X","AUDNZD=X","CADCHF=X","EURCAD=X"]

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(f"Enviado: {msg[:50]}")
    except Exception as e:
        print(f"Error telegram: {e}")

def bot_loop():
    print("BOT LOOP INICIADO 32 PARES")
    while True:
        try:
            ahora = datetime.now()
            expira = ahora + timedelta(minutes=5)
            compras = []
            ventas = []
            # aqui va tu logica RSI / señales - simplificado
            for par in PARES[:12]:
                try:
                    data = yf.download(par, period="1d", interval="5m", progress=False)
                    if len(data) < 14: continue
                    # Ejemplo señal aleatoria - tu pon tu RSI real aqui
                    r = data['Close'].iloc[-1] % 100
                    if r < 30:
                        compras.append(f"🟢 {par.replace('=X','')} - COMPRA 5M")
                    elif r > 70:
                        ventas.append(f"🔴 {par.replace('=X','')} - VENTA 5M")
                except:
                    continue

            if compras or ventas:
                msg = f" *SEÑALES 5M - {ahora.strftime('%H:%M:%S')} EC*\n"
                msg += f"⌛ Expira: {expira.strftime('%H:%M:%S')}\n\n"
                if compras:
                    msg += "*COMPRAS:*\n" + "\n".join(compras[:12]) + "\n\n"
                if ventas:
                    msg += "*VENTAS:*\n" + "\n".join(ventas[:12])
                enviar_telegram(msg)
            else:
                msg = f" *SEÑALES 5M - {ahora.strftime('%H:%M:%S')} EC* ⌛ Expira: {expira.strftime('%H:%M:%S')}\nSin señales claras, esperando..."
                enviar_telegram(msg)

        except Exception as e:
            print(f"Error loop: {e}")
        time.sleep(300)

@app.route('/')
def home():
    return "Bot Activo 32 Pares - OK"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
