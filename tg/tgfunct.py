import telegram as bot
import telegram.ext as botext
import json


def tg_receiver():
    with open('./tg/tgconfig.json') as j:
        jsonapi = json.load(j)
    global updater
    
    updater = botext.Updater(token=jsonapi['telegram']['token'],use_context=True)
    dispatcher = updater.dispatcher
    handler_start = botext.CommandHandler('start', start)
    dispatcher.add_handler(handler_start)
    
    updater.start_polling(clean=True)
    updater.idle()

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    unknown_handler = botext.MessageHandler(botext.Filters.command, unknown)
    bot.dispatcher.add_handler(unknown_handler)

def start(update, context):
    text = update['message']['text']
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting things")
    return text

def tg_sendmessage(text):
    with open('./pyapi.json') as j:
        jsonapi = json.load(j)
        bot.send_message(chat_id=jsonapi['telegram']['token'], text=text)
