from flask import Flask
import threading, time, requests, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import io

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

def enviar_texto(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}, timeout=15)
        print(f"ENVIADO: {texto[:80]}", flush=True)
    except Exception as e:
        print(f"Error envio texto: {e}", flush=True)

def enviar_con_grafico(texto, precio, sl, tp1, tp2, closes, señal):
    try:
        plt.figure(figsize=(10,5))
        plt.plot(closes[-100:], color='white', linewidth=1.5)
        plt.axhline(precio, color='cyan', linestyle='--', label=f'Entrada {precio:.2f}')
        plt.axhline(sl, color='red', linestyle='--', label=f'SL {sl:.2f}')
        plt.axhline(tp1, color='green', linestyle='--', label=f'TP1 {tp1:.2f}')
        plt.axhline(tp2, color='green', linestyle='-', label=f'TP2 {tp2:.2f}')
        plt.style.use('dark_background')
        plt.legend()
        plt.title(f"ORO - {señal}")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': buf}
        data = {"chat_id": CHAT_ID, "caption": texto, "parse_mode": "Markdown"}
        requests.post(url, data=data, files=files, timeout=20)
        print("Grafico enviado", flush=True)
    except Exception as e:
        print(f"Error grafico: {e}", flush=True)
        enviar_texto(texto)

def analizar_pro():
    try:
        print("Analizando ORO...", flush=True)
        # Descarga ORO 5m
        df = yf.download("GC=F", period="2d", interval="5m", progress=False)
        if len(df) < 200:
            print("Datos insuficientes", flush=True)
            return
        
        closes = df['Close']
        precio = float(closes.iloc[-1])
        ema50 = float(closes.ewm(span=50).mean().iloc[-1])
        ema200 = float(closes.ewm(span=200).mean().iloc[-1])
        
        # RSI 14
        delta = closes.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = float(rsi.iloc[-1])

        señal = None
        if precio > ema50 and ema50 > ema200 and rsi_val > 50 and rsi_val < 70:
            señal = "COMPRAR"
            sl = precio - 4
            tp1 = precio + 2.6  # +130 pips aprox en oro
            tp2 = precio + 5.2  # +260 pips
        elif precio < ema50 and ema50 < ema200 and rsi_val < 50 and rsi_val > 30:
            señal = "VENDER"
            sl = precio + 4
            tp1 = precio - 2.6
            tp2 = precio - 5.2
        else:
            print(f"No hay señal - Precio:{precio:.2f} EMA50:{ema50:.2f} EMA200:{ema200:.2f} RSI:{rsi_val:.1f}", flush=True)
            return

        msg = f"""🚀 *{señal} ORO XAUUSD 5m* 

💰 Entrada: `{precio:.2f}`
🔴 SL: `{sl:.2f}` 
🟢 TP1: `{tp1:.2f}` (+130 pips)
🟢 TP2: `{tp2:.2f}` (+260 pips)

📊 EMA50: {ema50:.2f} | EMA200: {ema200:.2f}
📈 RSI: {rsi_val:.1f}
📉 Gráfico con niveles abajo 👇
"""
        enviar_con_grafico(msg, precio, sl, tp1, tp2, closes, señal)

    except Exception as e:
        print(f"Error analizar_pro: {e}", flush=True)

def bot_loop():
    enviar_texto("🚀 *BOT ORO V3 GRAFICO INICIADO*\n✅ EMA+RSI + Gráficos con TP/SL\n⏰ Analizando cada 60s - Hora Ecuador")
    while True:
        try:
            analizar_pro()  # PRIMERO ANALIZA
            time.sleep(60)  # LUEGO DUERME 60s
        except Exception as e:
            print(e, flush=True)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Oro V3 Grafico Activo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
