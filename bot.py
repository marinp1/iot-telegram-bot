import telegram
import config
import re
import numpy as np
from controller import EnergeniePlugController
from telegram.ext import Updater, CommandHandler, RegexHandler

plug_controller = None

plug_names = {'plug_2': 'Socket #2', 'plug_4': 'Socket #4'}
plug_values = {'plug_2' : None, 'plug_4' : None}

current_command = None
socket_to_be_renamed = None

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

    message = 'Turned all sockets ON' if socket_id == 'all' else 'Turned {} ON'.format(plug_names[socket_id])
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)

    plug_controller.on(socket_id)
    if socket_id == 'all':
        plug_values['plug_2'] = True
        plug_values['plug_4'] = True
    else:
        plug_values[socket_id] = True
    
def power_off(bot, update, socket_id):
    if not is_authorised(update):
        return False

    message = 'Turned all sockets OFF' if socket_id == 'all' else 'Turned {} OFF'.format(plug_names[socket_id])
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)

    plug_controller.off(socket_id)
    if socket_id == 'all':
        plug_values['plug_2'] = False
        plug_values['plug_4'] = False
    else:
        plug_values[socket_id] = False

def start(bot, update):
    update.message.reply_text(
        "This bot controls and monitors Patrik's IoT devices.\n\nCurrently supported commands:\n/power\n/rename_socket")

def get_keyboard_text_for_socket(socket_id):
    return 'Turn {} OFF'.format(plug_names[socket_id]) if plug_values[socket_id] else 'Turn {} ON'.format(plug_names[socket_id])

def power(bot, update):
    if not is_authorised(update):
        return False

    if plug_values['plug_2'] is None:
        plug_controller.off('all')
        plug_values['plug_2'] = False
        plug_values['plug_4'] = False

    KEYBOARD_TEXT_1 = get_keyboard_text_for_socket('plug_2')
    KEYBOARD_TEXT_2 = get_keyboard_text_for_socket('plug_4')

    custom_keyboard = [[KEYBOARD_TEXT_1, KEYBOARD_TEXT_2], 
                    ['Turn all sockets ON', 'Turn all sockets OFF']]

    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard)
    bot.send_message(chat_id=update.message.chat.id,
                    text="What would you like to do?", 
                    reply_markup=reply_markup)

def power_control_single(bot, update):
    match = re.match('^Turn (.*?) (OFF|ON)$', update.message.text)
    socket_name = match.group(1) if match else None
    cmd = match.group(2) if match else None
    socket_id = list(plug_names.keys())[list(plug_names.values()).index(socket_name)]
    if cmd == 'ON':
        power_on(bot, update, socket_id)
    elif cmd == 'OFF':
        power_off(bot, update, socket_id)

def power_control_all(bot, update):
    match = re.match('^Turn all sockets (ON|OFF)$', update.message.text)
    cmd = match.group(1) if match else None
    if cmd == 'ON':
        power_on(bot, update, 'all')
    elif cmd == 'OFF':
        power_off(bot, update, 'all')

def rename_socket(bot, update):
    is_odd = len(list(plug_names.values())) % 2 == 1
    tmp = list(plug_names.values())
    if is_odd:
        tmp.append('Temp') 
    keyboard_items = np.asarray(tmp).reshape(-1, 2).tolist()
    if is_odd:
        del keyboard_items[-1][-1]

    global current_command
    current_command = 'RENAME_SOCKET'

    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=keyboard_items)
    bot.send_message(chat_id=update.message.chat.id,
                    text="Which socket would you like to rename?", 
                    reply_markup=reply_markup)

def rename_socket_response(bot, update):
    global current_command
    global socket_to_be_renamed

    if not is_authorised(update):
        return False

    match = re.match('^(.*?)$', update.message.text)
    socket_name = match.group(1) if match else None

    try:
        socket_id = list(plug_names.keys())[list(plug_names.values()).index(socket_name)]
        socket_to_be_renamed = socket_id
        message = 'Give a new name for socket {}'.format(socket_name)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)
    except:
        current_command = None
        socket_to_be_renamed = None
        message = 'Could not match socket name with socket id'
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)

def custom_text(bot, update):
    if not update.message.text:
        return False

    def reset_custom_command():
        global socket_to_be_renamed
        global current_command
        current_command = None
        socket_to_be_renamed = None

    global plug_names
    if current_command == 'RENAME_SOCKET':
        if not socket_to_be_renamed is None:
            new_name = update.message.text.strip()
            plug_names[socket_to_be_renamed] = new_name
            reset_custom_command()
            bot.send_message(chat_id=update.message.chat.id, text="Socket name updated successfully")
        else:
            rename_socket_response(bot, update)

def run_app():
    global plug_controller
    plug_controller = EnergeniePlugController()
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=False)
    #updater = Updater(config.TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('power', power))
    updater.dispatcher.add_handler(CommandHandler('rename_socket', rename_socket))
    updater.dispatcher.add_handler(RegexHandler('^Turn all sockets (ON|OFF)$', power_control_all))
    updater.dispatcher.add_handler(RegexHandler('^Turn (.*?) (OFF|ON)$', power_control_single))
    updater.dispatcher.add_handler(RegexHandler('^(.*?)$', custom_text))
    updater.start_polling()
    updater.idle()

def main():
    try:
        run_app()
    finally:
        plug_controller.cleanup()

if __name__=='__main__':
    main()
