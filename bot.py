import telegram
import config
import re
import numpy as np
from controller import EnergenieSocketController
from telegram.ext import Updater, CommandHandler, RegexHandler

socket_controller = None
sockets = []

ID_ALL_SOCKETS = 'ALL_SOCKETS'
ID_VALUE_OFF = 'OFF'
ID_VALUE_ON = 'ON'

current_command = None
socket_to_be_renamed = None

def is_authorised(update):
    if not str(update.message.from_user.id) == config.APPROVED_USER_ID:
        update.message.reply_text(
            '{}, you are not authorised to use this bot.'.format(update.message.from_user.first_name))
        return False
    if socket_controller is None:
        update.message.reply_text(
            'There seems to be a problem with  {}  code'.format(u'\U0001F50C'))
        return False
    return True

def get_socket_by_name(socket_name):
    for socket in sockets:
        if socket.get_name() == socket_name:
            return socket
    return None

def convert_list_to_sublist(original_list):
    result = original_list
    is_odd = len(result) % 2 == 1
    if is_odd:
        result.append('Temp') 
    result = np.asarray(result).reshape(-1, 2).tolist()
    if is_odd:
        del result[-1][-1]
    return result

def power_switch(bot, update, socket_name, value):
    if not is_authorised(update):
        return False

    if not value == ID_VALUE_OFF and not value == ID_VALUE_ON:
        return False

    message = None

    if socket_name == ID_ALL_SOCKETS:
        if value == ID_VALUE_ON:
            socket_controller.turn_all_off()
        else:
            socket_controller.turn_all_on()
        message = 'Turned all sockets {}'.format(value)
    else:
        socket = get_socket_by_name(socket_name)
        if socket is None:
            message = 'Could not find socket with name {}'.format(socket_name)
        else:
            if value == ID_VALUE_ON:
                socket.turn_off() 
            else:
                socket.turn_on()
            message = 'Turned socket with name {0} {1}'.format(socket_name, value)

    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)

def start(bot, update):
    update.message.reply_text(
        "This bot controls and monitors Patrik's IoT devices.\n\nCurrently supported commands:\n/power\n/rename_socket")

def power(bot, update):
    if not is_authorised(update):
        return False

    custom_keyboard = []
    for socket in sockets:
        new_value = ID_VALUE_OFF if socket.get_value() else ID_VALUE_ON
        custom_keyboard.append('Turn {0} {1}'.format(socket.get_name(), new_value))
    
    custom_keyboard = convert_list_to_sublist(custom_keyboard)
    custom_keyboard.append(['Turn all sockets ON', 'Turn all sockets OFF'])

    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard)
    bot.send_message(chat_id=update.message.chat.id,
                    text="What would you like to do?", 
                    reply_markup=reply_markup)

def power_control_single(bot, update):
    match = re.match('^Turn (.*?) (OFF|ON)$', update.message.text)
    socket_name = match.group(1) if match else None
    cmd = match.group(2) if match else None
    if cmd == ID_VALUE_ON or cmd == ID_VALUE_OFF:
        power_switch(bot, update, socket_name, cmd)

def power_control_all(bot, update):
    match = re.match('^Turn all sockets (ON|OFF)$', update.message.text)
    cmd = match.group(1) if match else None
    if cmd == ID_VALUE_ON or cmd == ID_VALUE_OFF:
        power_switch(bot, update, ID_ALL_SOCKETS, cmd)

def rename_socket(bot, update):
    custom_keyboard = []
    for socket in sockets:
        custom_keyboard.append(socket.get_name())
    custom_keyboard = convert_list_to_sublist(custom_keyboard)

    global current_command
    current_command = 'RENAME_SOCKET'

    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard)
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
    socket_to_be_renamed = get_socket_by_name(socket_name)

    if not socket_to_be_renamed is None:
        message = 'Give a new name for socket {}'.format(socket_name)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)
    else:
        current_command = None
        message = 'Could not find socket with given name'
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

    if current_command == 'RENAME_SOCKET':
        if not socket_to_be_renamed is None:
            socket_to_be_renamed.rename(update.message.text)
            reset_custom_command()
            bot.send_message(chat_id=update.message.chat.id, text="Socket name updated successfully")
        else:
            rename_socket_response(bot, update)

def run_app():
    global socket_controller
    global sockets

    socket_controller = EnergenieSocketController()
    sockets.append(socket_controller.add_socket(2))
    sockets.append(socket_controller.add_socket(4))

    updater = Updater(config.TELEGRAM_TOKEN)
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
        socket_controller.cleanup()

if __name__=='__main__':
    main()
