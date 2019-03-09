from controller import EnergeniePlug
from telegram.ext import Updater, CommandHandler
import config

plug = None

def is_authorised(update):
    if not str(update.message.from_user.id) == config.APPROVED_USER_ID:
        update.message.reply_text(
            '{}, you are not authorised to use this bot.'.format(update.message.from_user.first_name))
        return False
    if plug is None:
        update.message.reply_text(
            'There seems to be a problem with  {}  code'.format(u'\U0001F50C'))
        return False
    return True

def power_on(bot, update):
    if not is_authorised(update):
        return False
    plug.on()
    update.message.reply_text(
        'Power status: ON')
    
def power_off(bot, update):
    if not is_authorised(update):
        return False
    plug.off()
    update.message.reply_text(
        'Power status: OFF')

def start(bot, update):
    update.message.reply_text(
        "This bot control and monitors Patrik's IOT devices.\n\nCurrently supported commands:\n/power_on\n/power_off")

def run_app():
    global plug
    plug = EnergeniePlug()
    updater = Updater(config.TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('power_on', power_on))
    updater.dispatcher.add_handler(CommandHandler('power_off', power_off))
    updater.start_polling()
    updater.idle()

def main():
    try:
        run_app()
    finally:
        plug.cleanup()

if __name__=='__main__':
    main()
