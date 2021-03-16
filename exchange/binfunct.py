import json, datetime
from binance.client import Client


# retrieving keys from json
def client_key():
    with open("./binconfig.json") as j:
        jsonapi = json.load(j)
    pubkey = jsonapi['binance']['pubkey']
    privkey = jsonapi['binance']['privkey']
    # setup client connection to Binance API
    client = Client(api_key=pubkey, api_secret=privkey)
    return client


def json_account_data():
    with open("./binaccountdata.json") as j:
        jsondata = json.load(j)
    return jsondata


def sys_status():
    client = client_key()
    status = client.get_system_status()
    stat = status['status']
    return stat


# return account asset balance
def bn_account_assets():
    client = client_key()
    info = client.get_account()
    result = []
    for v in info['balances']:
        bal = float(v['free'])
        if bal == 0:
            continue
        else:
            result.append([v['asset'],v['free'],v['locked']])
    return result


# return all ticker price
def price_all_ticker():
    client = client_key()
    prices = client.get_all_tickers()
    dt = datetime.datetime.now()
    return dt, prices


def get_ex_info():
    client = client_key()
    info = client.get_exchange_info()
    return info


def get_oneday_candles():
    client = client_key()
    candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)
    return candles

symb = 'AAVEUSDT'
client = client_key()
candles = client.get_klines(symbol=symb, interval='1h')
print(candles)
input()
