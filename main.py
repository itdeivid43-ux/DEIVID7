from flask import Flask
import threading, time, requests, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def enviar_texto(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto, "parse_mode":"Markdown"}, timeout=10)
    except Exception as e:
        print(e, flush=True)

def enviar_con_grafico(texto, precio, sl, tp1, tp2, closes, señal):
    try:
        plt.figure(figsize=(10,5))
        plt.plot(closes[-100:], color='white', linewidth=1.5)
        plt.axhline(precio, color='#00FF00', linestyle='--', label=f'Entrada {precio:.2f}')
        plt.axhline(sl, color='#FF0000', linestyle='--', label=f'SL {sl:.2f}')
        plt.axhline(tp1, color='#00BFFF', linestyle='--', label=f'TP1 {tp1:.2f}')
        plt.axhline(tp2, color='#FFD700', linestyle='--', label=f'TP2 {tp2:.2f}')
        plt.title(f'XAUUSD - {señal} - ORO PRO V3', color='white')
        plt.legend()
        plt.style.use('dark_background')
        plt.tight_layout()
        plt.savefig('/tmp/chart.png', dpi=150)
        plt.close()

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open('/tmp/chart.png', 'rb') as f:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": texto, "parse_mode":"Markdown"}, files={"photo": f}, timeout=20)
        print("Grafico enviado", flush=True)
    except Exception as e:
        print(f"Error grafico: {e}", flush=True)
        enviar_texto(texto)

def get_klines():
    try:
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
    gains = losses = 0
    for i in range(1, period+1):
        change = data[-i] - data[-i-1]
        if change > 0: gains += change
        else: losses -= change
    if losses == 0: return 100
    rs = gains / losses
    return 100 - (100 / (1 + rs))

def analizar_pro():
    closes = get_klines()
    if len(closes) < 200: return
    precio = closes[-1]
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    rsi_val = rsi(closes)

    señal = None
    if ema50 > ema200 and 50 < rsi_val < 68: señal = "COMPRA 📈"
    elif ema50 < ema200 and 32 < rsi_val < 50: señal = "VENTA 📉"

    if not señal:
        print(f"Sin señal - RSI:{rsi_val:.1f}", flush=True)
        return

    if "COMPRA" in señal:
        sl, tp1, tp2 = precio - 10, precio + 13, precio + 26
    else:
        sl, tp1, tp2 = precio + 10, precio - 13, precio - 26

    msg = f"""🔥 *SEÑAL PRO ORO V3 - XAUUSD*

📊 *{señal}*
💰 Entrada: `{precio:.2f}`
🛑 SL: `{sl:.2f}` (-100 pips)
🎯 TP1: `{tp1:.2f}` (+130 pips)
🎯 TP2: `{tp2:.2f}` (+260 pips)

📈 EMA50: {ema50:.2f} | EMA200: {ema200:.2f}
📊 RSI: {rsi_val:.1f}
✅ Gráfico con niveles abajo 👇
"""
    enviar_con_grafico(msg, precio, sl, tp1, tp2, closes, señal)

def bot_loop():
    enviar_texto("✅ *BOT ORO V3 GRAFICO INICIADO*\n📊 EMA+RSI + Gráficos con TP/SL\nEsperando señal segura Deivid...")
    while True:
        try:
            time.sleep(300)
            analizar_pro()
        except Exception as e:
            print(e, flush=True)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Oro V3 Grafico Activo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
