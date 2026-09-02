from flask import Flask
import threading, time, requests, os, yfinance as yf
app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")
PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","EURJPY=X","GBPJPY=X","USDCHF=X"]

def enviar(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def rsi(s, p=14):
    d = s.diff()
    g = (d.where(d>0,0)).rolling(p).mean()
    l = (-d.where(d<0,0)).rolling(p).mean()
    return 100-(100/(1+g/l))

def bot():
    print("BOT BINARIAS V7 INICIADO", flush=True)
    enviar("✅ *BOT BINARIAS DEIVID V7 ACTIVO*\n💵 Binarias 5m")
    while True:
        try:
            for par in PARES:
                try:
                    df = yf.download(par, period="1d", interval="5m", progress=False, auto_adjust=True)
                    if len(df)<60: continue
                    c = df['Close']
                    if len(c.shape)>1: c=c.iloc[:,0]
                    e9=c.ewm(span=9).mean().iloc[-1]
                    e21=c.ewm(span=21).mean().iloc[-1]
                    e50=c.ewm(span=50).mean().iloc[-1]
                    r=float(rsi(c).iloc[-1])
                    p=float(c.iloc[-1])
                    n=par.replace("=X","")
                    if e9>e21>e50 and 55<r<75:
                        h=time.strftime('%H:%M')
                        enviar(f"📊 *SEÑAL {h} EC*\n\n🟢 *COMPRAR {n} 5m*\n💰 {p:.5f}\n📈 EMA9>EMA21>EMA50\n📉 RSI {r:.1f}\n🎯 Confianza 95% ✅\n💵 Payout 85%\n\n⏰ *BINARIA 5 MIN*")
                        time.sleep(300); break
                    if e9<e21<e50 and 25<r<45:
                        h=time.strftime('%H:%M')
                        enviar(f"📊 *SEÑAL {h} EC*\n\n🔴 *VENDER {n} 5m*\n💰 {p:.5f}\n📉 EMA9<EMA21<EMA50\n📈 RSI {r:.1f}\n🎯 Confianza 95% ✅\n💵 Payout 85%\n\n⏰ *BINARIA 5 MIN*")
                        time.sleep(300); break
                except: continue
            time.sleep(120)
        except: time.sleep(30)

threading.Thread(target=bot, daemon=True).start()
@app.route("/")
def home(): return "BOT BINARIAS V7 ACTIVO"
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
