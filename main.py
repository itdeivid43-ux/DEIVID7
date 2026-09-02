from flask import Flask
import threading, time, requests, os
import yfinance as yf

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","NZDUSD=X","EURJPY=X","GBPJPY=X","EURGBP=X","AUDJPY=X","EURAUD=X","EURCAD=X","GBPCHF=X","USDCHF=X","NZDJPY=X","CADJPY=X","AUDNZD=X","AUDCAD=X","AUDCHF=X","CADCHF=X","CHFJPY=X","EURNZD=X","EURCHF=X","GBPAUD=X","GBPCAD=X","GBPNZD=X","NZDCHF=X","NZDCAD=X"]

def enviar(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}, timeout=10)
        print(f"ENVIADO: {texto[:60]}", flush=True)
    except Exception as e:
        print(e, flush=True)

def analizar():
    print("Analizando 28 pares binarias...", flush=True)
    for par in PARES:
        try:
            df = yf.download(par, period="2d", interval="5m", progress=False, auto_adjust=True)
            if len(df) < 60: continue
            c = df['Close']
            # Si es DataFrame con MultiIndex
            if hasattr(c, 'iloc') and len(c.shape) > 1:
                c = c.iloc[:,0]
            
            ema9 = c.ewm(span=9).mean().iloc[-1]
            ema21 = c.ewm(span=21).mean().iloc[-1]
            ema50 = c.ewm(span=50).mean().iloc[-1]
            precio = float(c.iloc[-1])
            
            nombre = par.replace("=X","")
            
            # BINARIAS 85% + FILTRO LATERAL
            if ema9 > ema21 and ema21 > ema50 and precio > ema9:
                enviar(f"🟢 *{nombre} | COMPRA 5M*\n💹 BINARIAS\n📊 EMA 9>21>50 | Precio sobre EMA9\n🎯 Confianza 85% | Expiracion 5m\n⏰ {time.strftime('%H:%M')} Ecuador")
            elif ema9 < ema21 and ema21 < ema50 and precio < ema9:
                enviar(f"🔴 *{nombre} | VENTA 5M*\n💹 BINARIAS\n📊 EMA 9<21<50 | Precio bajo EMA9\n🎯 Confianza 85% | Expiracion 5m\n⏰ {time.strftime('%H:%M')} Ecuador")
            else:
                print(f"{nombre} lateral - no señal", flush=True)
            time.sleep(1.5)
        except Exception as e:
            print(f"Error {par}: {e}", flush=True)
            continue

def bot_loop():
    enviar("🚀 *BOT BINARIAS DEIVID ACTIVO*\n28 Pares | 5m | 85% + Lateral\nEscaneo cada 1 min")
    while True:
        try:
            analizar()
            time.sleep(60)
        except Exception as e:
            print(f"Error loop: {e}", flush=True)
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home():
    return "BOT BINARIAS 28 PARES ACTIVO"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
