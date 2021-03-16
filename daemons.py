import sched, time, json, telegram.ext as botext
from exchange import binfunct


def load_config():
    with open("./pymain.json") as j:
        jsonmain = json.load(j)
    stablecoin = jsonmain['config']['stablecoin']
    maxusableamount = jsonmain['config']['maxusableamount']




# function start bot engine
def start_engine(jsontg, blackhole):
    print('loading config...')
    
    load_config()
    #print('starting heartbeat daemon...')
    #daemon_heartbeat()
    #print('starting table compiler daemon...')
    #daemon_table_compiler()
    #print('initializing commander...')
    #orchestrator()


# function schedule heartbeat (1min)
def daemon_heartbeat():
    s = sched.scheduler(time.time, time.sleep)
    def scheduler(sc): 
        print("pymain -- heartbeat")
        
        # do your stuff
        stat = sys_status()
        if stat == 1:
            print('Binance system is down!')
        
        s.enter(60, 1, scheduler, (sc,))
    
    s.enter(60, 1, scheduler, (s,))
    s.run()


def daemon_table_compiler():
    return 0