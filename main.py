
import requests, pandas as pd, ta, time, threading, os
from flask import Flask
from datetime import datetime, timedelta
import pytz
app = Flask(__name__)

PARES = ["AUDCAD","AUDCHF","AUDJPY","AUDNZD","AUDUSD","BRENT","CADCHF","CADJPY","CHFJPY","EURAUD","EURCAD","EURCHF","EURGBP","EURJPY","EURNZD","EURUSD","GBPAUD","GBPCAD","GBPCHF","GBPJPY","GBPNZD","GBPUSD","NZDCAD","NZDCHF","NZDJPY","NZDUSD","US100","US500","USDCAD","USDCHF","USDJPY","XAUUSD"]

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ZONA = pytz.timezone('America/Guayaquil')

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e: print(e)

def get_data(s):
    mapa = {"XAUUSD":"GC=F","BRENT":"BZ=F","US100":"^NDX","US500":"^GSPC","EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X","USDJPY":"JPY=X","AUDUSD":"AUDUSD=X","USDCAD":"CAD=X","USDCHF":"CHF=X","EURJPY":"EURJPY=X","EURGBP":"EURGBP=X","EURCHF":"EURCHF=X","EURAUD":"EURAUD=X","EURCAD":"EURCAD=X","EURNZD":"EURNZD=X","GBPAUD":"GBPAUD=X","GBPCAD":"GBPCAD=X","GBPCHF":"GBPCHF=X","GBPJPY":"GBPJPY=X","GBPNZD":"GBPNZD=X","AUDCAD":"AUDCAD=X","AUDCHF":"AUDCHF=X","AUDJPY":"AUDJPY=X","AUDNZD":"AUDNZD=X","CADCHF":"CADCHF=X","CADJPY":"CADJPY=X","CHFJPY":"CHFJPY=X","NZDCAD":"NZDCAD=X","NZDCHF":"NZDCHF=X","NZDJPY":"NZDJPY=X","NZDUSD":"NZDUSD=X"}
    ys = mapa.get(s.upper(), s)
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ys}?interval=5m&range=1d", headers={'User-Agent':'Mozilla/5.0'}, timeout=10).json()
        c = r['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(c, columns=['close']).dropna()
        return df
    except: return None

def analizar_todos():
    ahora = datetime.now(ZONA)
    expira = ahora + timedelta(minutes=5)
    hora_str = ahora.strftime("%H:%M:%S")
    expira_str = expira.strftime("%H:%M:%S")

    compras = []
    ventas = []

    for par in PARES:
        df = get_data(par)
        if df is None or len(df)<50: continue
        df['EMA9']=ta.trend.ema_indicator(df['close'],9)
        df['EMA21']=ta.trend.ema_indicator(df['close'],21)
        df['RSI']=ta.momentum.rsi(df['close'],14)
        u=df.iloc[-1]; a=df.iloc[-2]

        if a['EMA9']<a['EMA21'] and u['EMA9']>u['EMA21'] and u['RSI']>50:
            compras.append(f"🟢 {par} - COMPRA 5M")
        elif a['EMA9']>a['EMA21'] and u['EMA9']<u['EMA21'] and u['RSI']<50:
            ventas.append(f"🔴 {par} - VENTA 5M")

    mensaje = f"📊 *SEÑALES 5M - {hora_str} EC* 📊\n⏰ Expira: {expira_str}\n\n"
    if compras:
        mensaje += "*COMPRAS:*\n" + "\n".join(compras) + "\n\n"
    if ventas:
        mensaje += "*VENTAS:*\n" + "\n".join(ventas) + "\n\n"
    if not compras and not ventas:
        mensaje += "⏳ Sin señales claras ahora, esperando cruce EMA...\n\n"

    mensaje += f"_Total analizados: {len(PARES)} pares_"
    return mensaje

def loop():
    enviar("🚀 *BOT 32 PARES ACTIVO* ✅\nTe mandaré todas las señales cada 5 min con hora precisa EC")
    while True:
        try:
            msg = analizar_todos()
            enviar(msg)
        except Exception as e:
            print(e)
        time.sleep(300) # 5 minutos

@app.route('/')
def home(): return "BOT 32 PARES CON HORA PRECISA ACTIVO"
@app.route('/<s>')
def manual(s):
    return analizar_todos()

threading.Thread(target=loop, daemon=True).start()
if __name__ == '__main__': app.run(host='0.0.0.0', port=10000)
