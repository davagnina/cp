# importing modules
import sys, json, telegram, subprocess, telegram.ext as botext
from dbupdater import main as dbupdater
# from calc import dl_module

#from dbupdater import main


######################################################################### TELEGRAM #################################

################################################ SENDER ##########

def tg_sender(text):
    with open("./tg/tgconfig.json") as j:
        jsonapi = json.load(j)
    token = jsonapi['telegram']['token']
    chatid = jsonapi['telegram']['chatid']
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chatid, text=text)



################################################ COMMAND FUNCTIONS ##########

def tgcom_start(update, context):
    #update = update['message']['text']
    #tg_sender('Main: initializing DBUpdater...')
    procdbup = subprocess.run([sys.executable,'-c', dbupdater()])  ## WHAT TO START HERE? ##
    
    
    
def tgcom_forcesell(update, context):
    print('forcing to sell everything!')



################################################ RECEIVER ##########

def tg_receiver():
    with open('./tg/tgconfig.json') as j:
        jsonapi = json.load(j)
    
    updater = botext.Updater(token=jsonapi['telegram']['token'],use_context=True)
    dispatcher = updater.dispatcher
    handler_start = botext.CommandHandler('start', tgcom_start)
    dispatcher.add_handler(handler_start)
    
    handler_force_sell = botext.CommandHandler('forcesell', tgcom_forcesell)
    dispatcher.add_handler(handler_force_sell)
    
    print('MAIN - Telegram receiver started')
    updater.start_polling(clean=True)
    updater.idle()
    


######################################################################### LOCAL EXECUTION #################################

if __name__ == '__main__':
    
    procdbup = subprocess.run([sys.executable,'-c', dbupdater()])  ## WHAT TO START HERE? ##
    print('MAIN - Database updater started')
    
    tg_receiver()
    
    