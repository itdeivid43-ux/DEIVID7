from flask import Flask
import threading, time, requests, os

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def enviar(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto, "parse_mode":"Markdown"}, timeout=10)
        print(f"Enviado", flush=True)
    except Exception as e:
        print(e, flush=True)

def get_klines():
    try:
        # PAXG = Oro real, mismo precio que XAUUSD
        url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=200"
        r = requests.get(url, timeout=10).json()
        closes = [float(x[4]) for x in r]
        return closes
    except:
        return []

def ema(data, period):
    k = 2 / (period + 1)
    ema_val = sum(data[:period]) / period
    for price in data[period:]:
        ema_val = price * k + ema_val * (1 - k)
    return ema_val

def rsi(data, period=14):
    gains = 0
    losses = 0
    for i in range(1, period+1):
        change = data[-i] - data[-i-1]
        if change > 0:
            gains += change
        else:
            losses -= change
    if losses == 0:
        return 100
    rs = gains / losses
    return 100 - (100 / (1 + rs))

def analizar_pro():
    closes = get_klines()
    if len(closes) < 200:
        enviar("⚠️ Esperando datos del Oro...")
        return

    precio = closes[-1]
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    rsi_val = rsi(closes)

    print(f"Precio:{precio} EMA50:{ema50} EMA200:{ema200} RSI:{rsi_val}", flush=True)

    # LOGICA SEGURA
    señal = None
    if ema50 > ema200 and rsi_val > 50 and rsi_val < 70:
        señal = "COMPRA 📈"
    elif ema50 < ema200 and rsi_val < 50 and rsi_val > 30:
        señal = "VENTA 📉"

    if not señal:
        print("Sin señal clara, esperando...", flush=True)
        return

    if "COMPRA" in señal:
        sl = precio - 10
        tp1 = precio + 12
        tp2 = precio + 25
    else:
        sl = precio + 10
        tp1 = precio - 12
        tp2 = precio - 25

    msg = f"""🔥 *SEÑAL PRO ORO - XAUUSD*

📊 *{señal}*
💰 Precio actual: `{precio:.2f}`
📈 EMA50: `{ema50:.2f}` | EMA200: `{ema200:.2f}`
📊 RSI: `{rsi_val:.1f}`

🛑 SL: `{sl:.2f}`
🎯 TP1: `{tp1:.2f}`
🎯 TP2: `{tp2:.2f}`

✅ Confirmado por tendencia + RSI
⏰ 5M - Mantener 30-60 min
"""
    enviar(msg)

def bot_loop():
    enviar("✅ *BOT ORO PRO V2 INICIADO*\n📊 EMA 50/200 + RSI 14\nEsperando señal segura Deivid...")
    while True:
        try:
            time.sleep(300) # analiza cada 5 min
            analizar_pro()
        except Exception as e:
            print(f"Error: {e}", flush=True)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Oro Pro V2 Activo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
