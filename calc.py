import json
from mdb.dbfunct import db_connector

# modules for deep learning
from tensorflow.keras.models import load_model
from keras.models import Sequential
from keras.layers import Activation, Dense, Dropout, LSTM
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import seaborn as sns
from sklearn.metrics import mean_absolute_error


####################################################################################### PERSONAL FUNCTIONS ################

def percentage(part, whole):
  return 100 * float(part)/float(whole)

def retrieve_data(symb):
    conn = db_connector()
    cur = conn.cursor()
    cur.execute("SELECT datetime, close FROM "+symb[0]+"")
    hist = pd.DataFrame(cur.fetchall())
    hist = hist.set_index(0)
    hist.index = pd.to_datetime(hist.index, unit='s')
    conn.close()
    return hist

def db_showtables():
    conn = db_connector()
    cur = conn.cursor()
    cur.execute('SHOW TABLES')
    tables = cur.fetchall()
    conn.close()
    return tables

def db_updaterows(symb,lastupd,price,topdate,topperc,botdate,botperc):
    conn = db_connector()
    cur = conn.cursor()
    
    cur.execute("SELECT EXISTS(SELECT * FROM _assetindexes WHERE asset = '"+symb+"')")
    test = cur.fetchone()
    
    if test[0] is 0:
        cur.execute("INSERT INTO _assetindexes (asset,lastupdate,price,top_date,top_perc,bot_date,bot_perc,hold) VALUES (?,?,?,?,?,?,?,?)",(symb,lastupd,price,topdate,topperc,botdate,botperc,0))
    
    if test[0] is 1:
        cur.execute("INSERT INTO _assetindexes (asset,lastupdate,price,top_date,top_perc,bot_date,bot_perc,hold) VALUES (?,?,?,?,?,?,?,?)",(symb,))
    
    input()
    
    conn.close()

def db_create_asset_indexes():
    conn = db_connector()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS _assetindexes (asset VARCHAR(50) NOT NULL, lastupdate DATETIME NOT NULL, price FLOAT UNSIGNED NOT NULL, top_date DATETIME NOT NULL, top_perc decimal(5,2) NOT NULL, bot_date DATETIME NOT NULL, bot_perc decimal(5,2) NOT NULL, hold BOOL NOT NULL, UNIQUE KEY (asset))')
    conn.close()

####################################################################################### DEEP LEARNING FUNCTIONS ################

def train_test_split(df, test_size=0.2):
    split_row = len(df) - int(test_size * len(df))
    train_data = df.iloc[:split_row]
    test_data = df.iloc[split_row:]
    return train_data, test_data

def line_plot(line1, line2, label1=None, label2=None, title='', lw=2):
    fig, ax = plt.subplots(1, figsize=(13, 7))
    ax.plot(line1, label=label1, linewidth=lw)
    ax.plot(line2, label=label2, linewidth=lw)
    ax.set_ylabel('price [USD]', fontsize=14)
    ax.set_title(title, fontsize=16)
    ax.legend(loc='best', fontsize=16)
    plt.savefig('analysis/graphs/'+title)
    
def normalise_zero_base(df):
    return df / df.iloc[0] - 1

def normalise_min_max(df):
    return (df - df.min()) / (data.max() - df.min())

def extract_window_data(df, window_len=5, zero_base=True):
    window_data = []
    for idx in range(len(df) - window_len):
        tmp = df[idx: (idx + window_len)].copy()
        if zero_base:
            tmp = normalise_zero_base(tmp)
        window_data.append(tmp.values)
    return np.array(window_data)

### PREPARA I DATI PER ESSERE INFILATI NELLA NEURAL NETWORK ###
def prepare_data(df, target_col, window_len=10, zero_base=True, test_size=0.2):
    train_data, test_data = train_test_split(df, test_size=test_size)
    X_train = extract_window_data(train_data, window_len, zero_base)
    X_test = extract_window_data(test_data, window_len, zero_base)
    y_train = train_data[target_col][window_len:].values
    y_test = test_data[target_col][window_len:].values
    if zero_base:
        y_train = y_train / train_data[target_col][:-window_len].values - 1
        y_test = y_test / test_data[target_col][:-window_len].values - 1

    return train_data, test_data, X_train, X_test, y_train, y_test


### CREA IL MODELLO NEURAL NETWORK ###
def build_lstm_model(input_data, output_size, neurons=100, activ_func='linear', dropout=0.2, loss='mse', optimizer='adam'):
    model = Sequential()
    model.add(LSTM(neurons, input_shape=(input_data.shape[1], input_data.shape[2])))
    model.add(Dropout(dropout))
    model.add(Dense(units=output_size))
    model.add(Activation(activ_func))
    model.compile(loss=loss, optimizer=optimizer)
    return model


########################################### DEEP LEARNING MODEL CREATOR ###########
def deeplearning_module(symb):
    
    hist = retrieve_data(symb)
    target_col = 1
    train, test = train_test_split(hist, test_size=0.2)
    
    #line_plot(train[target_col], test[target_col], 'training', 'test', title=symb+' data')
    
    ### COSE DA USARE PIù TARDI ###
    np.random.seed(42)
    window_len = 5
    test_size = 0.2
    zero_base = True
    lstm_neurons = 100
    epochs = 20
    batch_size = 32
    loss = 'mse'
    dropout = 0.2
    optimizer = 'adam'
    
    ### TRAIN THE MODEL ###
    train, test, X_train, X_test, y_train, y_test = prepare_data(
        hist, target_col, window_len=window_len, zero_base=zero_base, test_size=test_size)
    model = build_lstm_model(
        X_train, output_size=1, neurons=lstm_neurons, dropout=dropout, loss=loss,
        optimizer=optimizer)
    history = model.fit(
        X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, shuffle=True)
    
    model.save('analysis/.model.h5')
    
    ### CHECK CON MAE ERROR ###
    targets = test[target_col][window_len:]
    preds = model.predict(X_test).squeeze()
    
    mean_absolute_error(preds, y_test)
    
    ### PLOT PREDICTIONS ###
    preds = test[target_col].values[:-window_len] * (preds + 1)
    preds = pd.Series(index=targets.index, data=preds)
    #line_plot(targets, preds, 'actual', 'prediction', title=symb+' results', lw=3)


def dl_module(symb):
    
    print('step one')
    hist = retrieve_data(symb)
    target_col = 1
    train, test = train_test_split(hist, test_size=0.2)

    ### COSE DA USARE PIù TARDI ###
    np.random.seed(42)
    window_len = 5
    test_size = 0.2
    zero_base = True
    
    print('step two')
    ### TRAIN THE MODEL ###
    train, test, X_train, X_test, y_train, y_test = prepare_data(
        hist, target_col, window_len=window_len, zero_base=zero_base, test_size=test_size)
    
    print('step three')
    model = load_model("analysis/.model.h5")
    
    print('step four')
    ### CHECK CON MAE ERROR ###
    targets = test[target_col][window_len:]
    preds = model.predict(X_test).squeeze()
    
    mean_absolute_error(preds, y_test)
    
    ### PLOT PREDICTIONS ###
    preds = test[target_col].values[:-window_len] * (preds + 1)
    preds = pd.Series(index=targets.index, data=preds)
    
    preds.to_json(symb[0]+' result.json')
    line_plot(targets, preds, 'actual', 'prediction', title=symb[0]+' results', lw=3)
    
    
    ############################# MODIFICHE MIE ##########
    ### FILL THE DATABASE ###
    lastupd = preds.index[-1]
    
    lastprc = preds[-1]
    
    topval = preds.max(axis=0)
    topperc = percentage(lastprc,topval)
    topdate = preds.idxmax(axis=1)
    
    botval = preds.min(axis=0)
    botperc = percentage(lastprc,botval)
    botdate = preds.idxmin(axis=1)
    
    print(symb[0],lastupd,lastprc,topdate,topperc,botdate,botperc)
    
    #db_updaterows(symb[0],lastupd,lastprc,topdate,topperc,botdate,botperc)
    

if __name__ == '__main__':
    symb = 'BTCUSDT'
    dl_module(symb)
    #db_updaterows(symb)
    
    
    #db_create_asset_indexes()
    #tables = db_showtables()
    #for symb in tables:
    #    dl_module(symb)
        
            
    #to create a new model
    #deeplearning_module(symb)