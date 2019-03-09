# iot-telegram-bot
Telegram bot for managing my own IoT devices.

## Features
Currently only supports turning a power socket in my home `on` or `off`.

## How it works
I have set up a Raspberry Pi with [Energenie 314-RT](https://energenie4u.co.uk/catalogue/product/ENER314-RT) controller and a radio controlled socket.

`energenie` folder has been cloned from [Energenie's own Github repository](https://github.com/Energenie/pyenergenie) and modified to work with the sockets. Currently it always turns all the connected sockets on or off as I haven't figured out a way for it to work individually.

Telegram bot uses [python-telegram-bot](https://python-telegram-bot.org/) wrapper and runs on my local machine.
