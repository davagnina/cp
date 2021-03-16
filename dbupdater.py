import sched, time, json, re, telegram, mariadb
from datetime import datetime
from binance.client import Client
from mdb.dbfunct import db_connector

##########################  UTILITIES  ##########################

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

def all_prices():
    #print('retrieving symbols...')
    client = bin_client_key()
    prices = client.get_all_tickers()
    return prices

def tg_dbupdater_sender(text):
    with open("./tg/tgconfig.json") as j:
        jsonapi = json.load(j)
    token = jsonapi['telegram']['token']
    chatid = jsonapi['telegram']['chatid']
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chatid, text=text)



##########################  REAL FUNCTIONS  ##########################

def create_tables_for_symbols(prices):
    #print('create tables...')
    conn = db_connector()
    cur = conn.cursor()
    
    for symbol in prices:
        symb = symbol['symbol']
        if re.match(r'^.*USDT$', symb):
            try:
                #Column name date_time, open, high, low, close, volume
                cur.execute('CREATE TABLE IF NOT EXISTS '+symb+' (datetime DATETIME NOT NULL, open FLOAT UNSIGNED, high FLOAT UNSIGNED, low FLOAT UNSIGNED, close FLOAT UNSIGNED, volume FLOAT UNSIGNED, UNIQUE KEY (datetime))')
            except mariadb.Error as e:
                tg_dbupdater_sender(f"Error creating OHLCV table: {e}")
        else:
            continue
    conn.close()



#######  DA FINIRE  #######
def scavenge_data_from_tables(symb):
    today = datetime.now()
    oneyear = today.replace(month=today.month, hour=0, minute=0, second=0, microsecond=0)
    twoyear = today.replace(month=today.month - 1, hour=0, minute=0, second=0, microsecond=0)
    symb = symb.upper()
    
    conn = db_connector()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM '+symb+' WHERE datetime BETWEEN '+'"'+str(twoyear)+'"'+' AND '+'"'+str(oneyear)+'" GROUP BY datetime')
    t = cur.fetchall()
    print(t)
    conn.close()



def fill_ohlcv_data(symb):
    
    print('start to fill data...')
    ### CONNECT TO DB
    conn = db_connector()
    cur = conn.cursor()
    symb = symb.upper()
    
    ### QUERY BINANCE
    client = bin_client_key()
    candles = client.get_klines(symbol=symb, interval='1h')
    
    ### GET LAST DATETIME FROM TABLE
    cur.execute("SELECT MAX(datetime), close FROM "+symb)
    lastdate, jollything = cur.fetchone()
    #print(lastdate)
    
    for v in candles:
        ### FORMAT BINANCE
        if v is None:
            continue
        try:
            ts = float(v[0])/1000
            dt = datetime.fromtimestamp(ts)
            if dt <= lastdate:
                continue
            o = float(v[1])
            h = float(v[2])
            l = float(v[3])
            c = float(v[4])
            vol = float(v[5])
            print(symb+' - dt='+str(dt)+', o='+str(o)+', h='+str(h)+', l='+str(l)+', c='+str(c)+', v='+str(vol))
            ### TRY TO WRITE TO DATABASE
            try:
                cur.execute("INSERT INTO "+symb+" (datetime,open,high,low,close,volume) VALUES (?,?,?,?,?,?)",(dt,o,h,l,c,vol))
            except mariadb.Error as e:
                print(f"Error trying to import OHLCV data in table: {e}")
        except:
            print('DBUpdater: Error trying to insert a value!')
            
    
    conn.close()



##########################  MAIN  ##########################

def main():
    tg_dbupdater_sender("DBUpdater: started")
    s = sched.scheduler(time.time, time.sleep)
    
    def scheduler(sc):
        tg_dbupdater_sender("DBUpdater: filling up data in DB...")
        tickers = all_prices()
        create_tables_for_symbols(tickers)
        tables = db_showtables()
        for v in tables:
            
            underscorecheck = v[0].startswith('_')
            if underscorecheck is True:
                continue
        
            fill_ohlcv_data(v[0])
            time.sleep(2)
        tg_dbupdater_sender("DBUpdater: finished to fill data.")
        
        s.enter(14400, 1, scheduler, (sc,))
    s.enter(14400, 1, scheduler, (s,))
    s.run()


if __name__ == '__main__':
    main()