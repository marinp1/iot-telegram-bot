import telegram
import config
from controller import EnergeniePlugController
from telegram.ext import Updater, CommandHandler, RegexHandler

plug_controller = None

plug_names = {'plug_2': 'Socket #2', 'plug_4': 'Socket #4'}
plug_values = {'plug_2' : None, 'plug_4' : None}

def is_authorised(update):
    if not str(update.message.from_user.id) == config.APPROVED_USER_ID:
        update.message.reply_text(
            '{}, you are not authorised to use this bot.'.format(update.message.from_user.first_name))
        return False
    if plug_controller is None:
        update.message.reply_text(
            'There seems to be a problem with  {}  code'.format(u'\U0001F50C'))
        return False
    return True

def power_on(bot, update, socket_id):
    if not is_authorised(update):
        return False
    plug_controller.on(socket_id)
    if socket_id == 'all':
        plug_values['plug_2'] = True
        plug_values['plug_4'] = True
    else:
        plug_values[socket_id] = True
    message = 'Turned all sockets ON' if socket_id == 'all' else 'Turned {} ON'.format(plug_names[socket_id])
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)
    
def power_off(bot, update, socket_id):
    if not is_authorised(update):
        return False
    plug_controller.off(socket_id)
    if socket_id == 'all':
        plug_values['plug_2'] = False
        plug_values['plug_4'] = False
    else:
        plug_values[socket_id] = False
    message = 'Turned all sockets OFF' if socket_id == 'all' else 'Turned {} OFF'.format(plug_names[socket_id])
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)

def start(bot, update):
    update.message.reply_text(
        "This bot control and monitors Patrik's IOT devices.\n\nCurrently supported commands:\n/power_on\n/power_off")

def power(bot, update):
    if not is_authorised(update):
        return False

    if plug_values['plug_2'] is None:
        plug_controller.off('all')
        plug_values['plug_2'] = False
        plug_values['plug_4'] = False

    KEYBOARD_TEXT_1 = 'Turn {} OFF'.format(plug_names['plug_2']) if plug_values['plug_2'] else 'Turn {} OFF'.format(plug_names['plug_2'])
    KEYBOARD_TEXT_2 = 'Turn {} OFF'.format(plug_names['plug_4']) if plug_values['plug_4'] else 'Turn {} OFF'.format(plug_names['plug_4'])

    custom_keyboard = [[KEYBOARD_TEXT_1, KEYBOARD_TEXT_2], 
                    ['Turn all sockets OFF', 'Turn all sockets ON']]

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat.id,
                    text="Socket control", 
                    reply_markup=reply_markup)

def power_control(bot, update):
    bot.send_message(chat_id=update.message.chat.id,
                    text="Test")

def run_app():
    global plug_controller
    plug_controller = EnergeniePlugController()
    updater = Updater(config.TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('power', power))
    updater.dispatcher.add_handler(RegexHandler('^Turn ', power_control))
    updater.start_polling()
    updater.idle()

def main():
    try:
        run_app()
    finally:
        plug_controller.cleanup()

if __name__=='__main__':
    main()
