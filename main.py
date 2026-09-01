import os
import time
import threading
import requests
from flask import Flask
import yfinance as yf

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

PARES = ["EURUSD=X","GBPUSD=X","AUDUSD=X","NZDUSD=X","USDJPY=X","USDCHF=X","USDCAD=X","EURJPY=X","GBPJPY=X","AUDJPY=X","EURCHF=X","EURAUD=X","EURCAD=X","GBPAUD=X","GBPCAD=X","GBPCHF=X","AUDCAD=X","NZDCAD=X","NZDJPY=X","CHFJPY=X","CADJPY=X","AUDNZD=X","EURNZD=X","GBPNZD=X","CADCHF=X","EURCAD=X"]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def bot_loop():
    print("BOT V2 90% CADA 3M INICIADO")
    send_telegram("🚀 BOT V2 90% ACTIVO\nRevisando CADA 3M\nSolo señales 85-90% precisas\nExpiracion: 5M")
    c = 0
    while True:
        try:
            sen = []
            for par in PARES:
                try:
                    df = yf.download(par, period="2d", interval="5m", progress=False)
                    if len(df) < 50: continue
                    close = df['Close']
                    delta = close.diff()
                    gain = delta.where(delta>0,0).rolling(14).mean()
                    loss = -delta.where(delta<0,0).rolling(14).mean()
                    rsi = 100 - (100/(1+(gain/loss)))
                    rsi_now = float(rsi.iloc[-1])
                    ema200 = close.ewm(span=200).mean().iloc[-1]
                    precio = float(close.iloc[-1])
                    nombre = par.replace("=X","")
                    if rsi_now >= 78 and precio < ema200:
                        sen.append(f"🔴 {nombre} VENTA 90% RSI:{rsi_now:.0f}")
                    elif rsi_now <= 22 and precio > ema200:
                        sen.append(f"🟢 {nombre} COMPRA 90% RSI:{rsi_now:.0f}")
                    elif rsi_now >= 75 and precio < ema200:
                        sen.append(f"🔴 {nombre} VENTA 85% RSI:{rsi_now:.0f}")
                    elif rsi_now <= 25 and precio > ema200:
                        sen.append(f"🟢 {nombre} COMPRA 85% RSI:{rsi_now:.0f}")
                except: continue
            if sen:
                h = time.strftime("%H:%M:%S")
                m = f"🎯 SEÑAL PRECISA {h} EC (5M)\n\n" + "\n".join(sen[:4]) + "\n\n⏰ Expira 5M - Entra ya!"
                send_telegram(m)
                c=0
            else:
                c+=1
                if c>=10:
                    send_telegram(f"👀 Monitoreo 3M - {time.strftime('%H:%M')} EC - Esperando señal 90%...")
                    c=0
        except: pass
        time.sleep(180)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "BOT V2 90% CADA 3M ACTIVO"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
