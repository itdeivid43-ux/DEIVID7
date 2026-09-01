import os, time, threading, requests, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(__name__)

PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD","EURGBP","EURJPY","GBPJPY","AUDJPY","EURCAD","AUDCAD","AUDNZD","CADJPY","CHFJPY","EURAUD","EURNZD","GBPAUD","GBPCAD","GBPNZD","NZDCAD","NZDJPY","AUDCHF","CADCHF","EURCHF","GBPCHF","NZDAUD","NZDCHF","USDHKD","USDSGD"]

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
        print("Mensaje enviado")
    except Exception as e:
        print(f"Error telegram: {e}")

def bot_loop():
    print("🚀 BOT 32 PARES ACTIVO")
    time.sleep(10)
    enviar_telegram("🚀 *Bot 32 Pares CONECTADO*\nHora Ecuador - Señales 5M activas")
    while True:
        try:
            tz = pytz.timezone('America/Guayaquil')
            ahora = datetime.now(tz)
            expira = ahora + timedelta(minutes=5)
            
            compras = []
            ventas = []
            for par in PARES:
                r = random.randint(1,100)
                if r > 85:
                    compras.append(f"🟢 {par} - COMPRA 5M")
                elif r < 15:
                    ventas.append(f"🔴 {par} - VENTA 5M")
            
            if compras or ventas:
                msg = f"📊 *SEÑALES 5M - {ahora.strftime('%H:%M:%S')} EC*\n"
                msg += f"⏰ Expira: {expira.strftime('%H:%M:%S')}\n\n"
                if compras:
                    msg += "*COMPRAS:*\n" + "\n".join(compras[:12]) + "\n\n"
                if ventas:
                    msg += "*VENTAS:*\n" + "\n".join(ventas[:12])
                enviar_telegram(msg)
            else:
                msg = f"📊 *SEÑALES 5M - {ahora.strftime('%H:%M:%S')} EC*\n⏰ Expira: {expira.strftime('%H:%M:%S')}\n\nSin señales claras, esperando..."
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
