import time, sys, os, json, mariadb, telegram
from datetime import datetime
from binance.client import Client
from mdb.dbfunct import db_connector


def tg_dbupdater_sender(text):
    with open("./tg/tgconfig.json") as j:
        jsonapi = json.load(j)
    token = jsonapi['telegram']['token']
    chatid = jsonapi['telegram']['chatid']
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chatid, text=text)

def db_showtables():
    conn = db_connector()
    cur = conn.cursor()
    cur.execute('SHOW TABLES')
    tables = cur.fetchall()
    conn.close()
    return tables

def bin_client_key():
    with open("./exchange/binconfig.json") as j:
        jsonapi = json.load(j)
    pubkey = jsonapi['binance']['pubkey']
    privkey = jsonapi['binance']['privkey']
    # setup client connection to Binance API
    client = Client(api_key=pubkey, api_secret=privkey)
    return client

tg_dbupdater_sender("DBFiller: started")

tables = db_showtables()

conn = db_connector()
cur = conn.cursor()

for symb in tables:
    
    client = bin_client_key()
    
    print(symb[0])
    
    candles = client.get_historical_klines(symb[0], Client.KLINE_INTERVAL_1HOUR, "1 Jan, 2017")
    for v in candles:
        
        ts = float(v[0])/1000
        dt = datetime.fromtimestamp(ts)
        o = float(v[1])
        h = float(v[2])
        l = float(v[3])
        c = float(v[4])
        vol = float(v[5])
        
        #print(dt, o, h, l, c, vol)
        try:
            cur.execute("INSERT INTO "+symb[0]+" (datetime,open,high,low,close,volume) VALUES (?,?,?,?,?,?)",(dt,o,h,l,c,vol))
        except mariadb.Error as e:
            print(f"Error trying to import OHLCV data in table: {e}")
        #time.sleep(0.5)

tg_dbupdater_sender("DBFiller: finished!")
conn.close()
