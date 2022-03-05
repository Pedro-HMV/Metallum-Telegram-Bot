import logging

from decouple import config

import telegram
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters

import metallum

BOT_TOKEN = config('BOT_TOKEN')

updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def bands(update: Update, context: CallbackContext):
    eci = update.effective_chat.id
    pm = telegram.ParseMode.MARKDOWN
    query = ' '.join(context.args).capitalize()
    context.bot.send_message(chat_id=eci, text=f'Searching for bands named: *{query}*', parse_mode=pm)
    bands = metallum.band_search(query)
    for band in bands:
        this_band = band.get()
        genres = ', '.join(this_band.genres)
        url_name = this_band.name.replace(' ', '\_').lower()
        band_url = f'https://www.metal-archives.com/bands/{url_name}/{this_band.id}'
        context.bot.send_message(
            chat_id=eci,
            text='\n\n'.join([f'*{this_band.name}*', f'_Location_: {this_band.location}, {this_band.country}', f'_Genre(s)_: {genres}', f'_Page_: {band_url}']),
            parse_mode=pm
        )
        # context.bot.send_message(chat_id=eci, text='Albums: ')
        # for album in this_band.albums:
        #     context.bot.send_message(chat_id=eci, text=' '*4 + f'{album.title}')

bands_handler = CommandHandler('bands', bands)
dispatcher.add_handler(bands_handler)

    

updater.start_polling()
