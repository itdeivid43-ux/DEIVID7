from flask import Flask
import threading, time, requests, os, sys
import yfinance as yf

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","GBPJPY=X","EURJPY=X","EURGBP=X","USDCAD=X"]

def log(msg):
    print(msg, flush=True)
    sys.stdout.flush()

def enviar(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def analizar():
    for par in PARES:
        try:
            log(f"Analizando {par}...")
            df = yf.download(par, period="1d", interval="5m", progress=False, auto_adjust=True, threads=False)
            if len(df) < 50:
                log(f"{par} sin datos")
                continue
            c = df['Close']
            if len(c.shape) > 1: c = c.iloc[:,0]
            ema9 = c.ewm(span=9).mean().iloc[-1]
            ema21 = c.ewm(span=21).mean().iloc[-1]
            ema50 = c.ewm(span=50).mean().iloc[-1]
            precio = float(c.iloc[-1])
            nombre = par.replace("=X","")
            
            log(f"{nombre}: P={precio:.5f} E9={ema9:.5f} E21={ema21:.5f}")

            if ema9 > ema21 and ema21 > ema50 and precio > ema9:
                enviar(f"🟢 *{nombre} COMPRA 5M*\n💹 BINARIAS 85%\n⏰ {time.strftime('%H:%M')} Ec")
                log(f"SENAL COMPRA {nombre}")
            elif ema9 < ema21 and ema21 < ema50 and precio < ema9:
                enviar(f"🔴 *{nombre} VENTA 5M*\n💹 BINARIAS 85%\n⏰ {time.strftime('%H:%M')} Ec")
                log(f"SENAL VENTA {nombre}")
            time.sleep(2)
        except Exception as e:
            log(f"Error {par}: {e}")
            time.sleep(1)

def bot_loop():
    log(">>>>>>>> BOT BINARIAS INICIADO <<<<<<<<")
    enviar("🚀 *BOT BINARIAS LITE ACTIVO*\n8 Pares principales | 5M | 85%\nYa estoy analizando...")
    while True:
        try:
            analizar()
            log("--- ciclo terminado, esperando 60s ---")
            time.sleep(60)
        except Exception as e:
            log(f"Error loop: {e}")
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home():
    return "BOT BINARIAS LITE ACTIVO - 8 PARES"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
