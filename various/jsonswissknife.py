# check if balance is 0 in [balances][asset]
def json_bn_stripzerobalance(jdata):
    for jdata['asset'] in jdata['balances']:
        if jdata['asset']['free'] != '0.00000000':
                print(jdata['asset'])
                ###### DA FARE APPEND E RETURN
                

def json_tg_parsemessage(jsontext):
    
    return textmessage