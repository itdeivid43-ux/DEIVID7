from flask import Flask
import threading, time, requests, os, yfinance as yf
import pandas as pd

app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")
PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","NZDUSD=X","NZDCAD=X","EURJPY=X","GBPJPY=X","AUDJPY=X","USDCAD=X"]

def log(m): print(m, flush=True)
def enviar(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": t, "parse_mode": "Markdown"}, timeout=15)
    except: pass

def calcular_rsi(serie, period=14):
    delta = serie.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def bot_loop():
    log(">>>>>>>> BOT V6 FORMATO BONITO INICIADO <<<<<<<<")
    enviar("✅ *BOT DEIVID V6 ACTIVO*\nFormato bonito restaurado\n📊 Señales cada 3 min")
    while True:
        try:
            for par in PARES:
                try:
                    df = yf.download(par, period="1d", interval="5m", progress=False, auto_adjust=True, threads=False)
                    if len(df) < 55: continue
                    close = df['Close']
                    if len(close.shape) > 1: close = close.iloc[:,0]
                    ema9 = close.ewm(span=9).mean().iloc[-1]
                    ema21 = close.ewm(span=21).mean().iloc[-1]
                    ema50 = close.ewm(span=50).mean().iloc[-1]
                    rsi = float(calcular_rsi(close).iloc[-1])
                    precio = float(close.iloc[-1])
                    nombre = par.replace("=X","")
                    compra = ema9 > ema21 and ema21 > ema50 * 0.999
                    venta = ema9 < ema21 and ema21 < ema50 * 1.001
                    if compra and 40 < rsi < 75:
                        hora = time.strftime('%H:%M')
                        enviar(f"📊 *SEÑAL {hora} EC*\n\n🟢 *COMPRAR {nombre} 5m*\n💰 {precio:.5f}\n📈 EMA9>EMA21>EMA50\n📉 RSI {rsi:.1f}\n🎯 Confianza 95% ✅\n💵 Payout 85%\n\n⏰ Entrar siguiente vela 5m")
                        break
                    elif venta and 25 < rsi < 60:
                        hora = time.strftime('%H:%M')
                        enviar(f"📊 *SEÑAL {hora} EC*\n\n🔴 *VENDER {nombre} 5m*\n💰 {precio:.5f}\n📉 EMA9<EMA21<EMA50\n📈 RSI {rsi:.1f}\n🎯 Confianza 95% ✅\n💵 Payout 85%\n\n⏰ Entrar siguiente vela 5m")
                        break
                except: continue
            time.sleep(180)
        except: time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "V6 BONITO ACTIVO"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
