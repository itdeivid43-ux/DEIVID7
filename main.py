import threading
import time
import requests
import os
from flask import Flask
import pandas as pd
import ta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

app = Flask(__name__)

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
        print(f"Enviado: {msg}")
    except Exception as e:
        print(f"Error telegram: {e}")

def get_klines(symbol, interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url, timeout=10)
    data = r.json()
    df = pd.DataFrame(data, columns=["open_time","open","high","low","close","volume","close_time","qav","trades","tbbav","tbqav","ignore"])
    df["close"] = df["close"].astype(float)
    return df

def analyze_symbol(symbol):
    df = get_klines(symbol)
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    df["ema_fast"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
    df["ema_slow"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()
    last = df.iloc[-1]
    prev = df.iloc[-2]
    rsi = last["rsi"]
    price = last["close"]
    if last["ema_fast"] > last["ema_slow"] and prev["ema_fast"] <= prev["ema_slow"] and rsi > 50:
        return f"🟢 COMPRA {symbol}\nPrecio: ${price:.2f}\nRSI: {rsi:.1f}\nCruce EMA 9 > 21"
    if last["ema_fast"] < last["ema_slow"] and prev["ema_fast"] >= prev["ema_slow"] and rsi < 50:
        return f"🔴 VENTA {symbol}\nPrecio: ${price:.2f}\nRSI: {rsi:.1f}\nCruce EMA 9 < 21"
    return None

def bot_loop():
    print("Bot Deivid iniciado...")
    if TELEGRAM_TOKEN:
        send_telegram("✅ Bot Deivid conectado y analizando cada 60 seg - BTC, ETH, SOL")
    while True:
        try:
            for symbol in SYMBOLS:
                signal = analyze_symbol(symbol)
                if signal:
                    send_telegram(signal)
                time.sleep(1)
            print(f"Chequeo OK {time.strftime('%H:%M:%S')}")
            time.sleep(60)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(10)

@app.route("/")
def home():
    return "Bot Deivid 24/7 OK"

if __name__ == "__main__":
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
