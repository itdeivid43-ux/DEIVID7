from flask import Flask
import threading, time, requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN") # tu token de telegram
CHAT_ID = "5890249548"

PARES = ["EURUSD","GBPUSD","USDJPY","EURGBP","AUDUSD","USDCAD","NZDUSD","EURJPY","GBPJPY","EURCHF","USDCHF","AUDJPY","CADJPY","GBPCHF","EURAUD","GBPAUD","AUDCAD","AUDNZD","NZDCAD","NZDJPY","EURCAD","GBPCAD","EURNZD","GBPNZD","USDHKD","USDSGD","USDSEK","USDNOK","USDDKK","USDPLN","USDTRY","USDZAR"] # 32 pares

def enviar_mensaje(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto})
        print(f"Enviado: {texto}")
    except Exception as e:
        print(e)

def bot_loop():
    enviar_mensaje("✅ BOT PRO 32 PARES INICIADO EN RENDER - Ya estoy analizando")
    while True:
        try:
            # Aquí va tu lógica de análisis
            # Por ahora te mando una señal de prueba cada 5 min para que veas que funciona
            for par in PARES[:2]: # prueba
                pass
            enviar_mensaje(f"🔥 SEÑAL TEST - EUR/USD - COMPRA 🟢 - Confianza 85% - 5 MIN")
            time.sleep(300) # 5 min
        except Exception as e:
            print(e)
            time.sleep(60)

@app.route('/')
def home():
    return "BOT PRO 32 PARES FUNCIONANDO"

# Iniciar el bot en segundo plano
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
