import re
import logging

from decouple import config

import telegram
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler #, MessageHandler, Filters

import metallum

BOT_TOKEN = config('BOT_TOKEN')

updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher
pm = telegram.ParseMode.MARKDOWN


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "All hail the mighty *Encyclopaedia Metallum*!!!\n\n"
            "I'm a bot designed to search for METAL bands! \U0001F918\U0001F916\n\n"
            "You can use the following commands:\n\n"
            "`/band name of the band`\n"
            "> if you want me to look for the exact name of a band (searching for _Iron_ won't find _Iron Maiden_ in this case)\n"
            ">> For example: `/band black sabbath`\n\n"
            "`/bands text to search`\n"
            "> if you want me to look for all bands that include that text in their names (be careful, this could find *A LOT* of bands)\n"
            ">> For example: `/bands hell`\n\n"
            "Try it out!"
        ),
        parse_mode=pm
    )

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

class Band:
    name: str
    location: str
    country: str
    genres: str
    url: str

    _info: str

    def __init__(self, band):
        self.name = band.name
        print(self.name)
        self.location = band.location
        print(self.location)
        self.country = band.country
        print(self.country)
        self.genres = ', '.join(band.genres)
        print(self.genres)
        self.url = r'https://metal-archives.com/' + band.url.replace('_', '\_')
        print(self.url)

    def __str__(self):
        return '\n\n'.join([f'*{self.name}*', f'_Location_: {self.location}, {self.country}', f'_Genre(s)_: {self.genres}', f'_Page_: {self.url}'])


def band(update: Update, context: CallbackContext):
    eci = update.effective_chat.id

    try:
        if not (re.search('[a-zA-Z]', context.args[0])):
            context.bot.send_message(chat_id=eci, text=f'Searching for a band with ID: *{context.args[0]}*', parse_mode=pm)

            try:
                result = metallum.band_for_id(context.args[0])
                if result.id != context.args[0]:
                    raise ValueError
                band = Band(result)
                context.bot.send_message(
                    chat_id=eci,
                    text=str(band),
                    parse_mode=pm
                )
            except ValueError:
                context.bot.send_message(chat_id=eci, text='No band was found with that ID')

        try:
            query = ' '.join(context.args).title()
            print(query)
            context.bot.send_message(chat_id=eci, text=f'Searching for bands named: *{query}*', parse_mode=pm)
            band_list = metallum.band_search(query)
            if not band_list:
                raise IndexError
            print(band_list)
            for result in band_list:
                print(result)
                band_result = result.get()
                band = Band(band_result)
                print(band)
                context.bot.send_message(
                    chat_id=eci,
                    text=str(band),
                    parse_mode=pm
                )
                print("Band finished")
        except IndexError:
            context.bot.send_message(chat_id=eci, text=u'No band was found with that name. Remember, I only know METAL bands! \U0001F918\U0001F916')

    except:
        context.bot.send_message(chat_id=eci, text='Something went wrong, please review your message and try again!')

band_handler = CommandHandler('band', band)
dispatcher.add_handler(band_handler)

updater.start_polling()
