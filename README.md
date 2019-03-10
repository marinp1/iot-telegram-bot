# iot-telegram-bot
Telegram bot for managing my own IoT devices.

## Features
Currently only supports turning power sockets in my home `on` or `off`.
Also supports giving them more human-friendly names within the bot.

## How it works
I have set up a Raspberry Pi with [Energenie 314-RT](https://energenie4u.co.uk/catalogue/product/ENER314-RT) controller and two radio controlled sockets.

`energenie` folder has been cloned from [Energenie's own Github repository](https://github.com/Energenie/pyenergenie).

Telegram bot uses [python-telegram-bot](https://python-telegram-bot.org/) wrapper and runs on my local machine.
