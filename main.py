import logging
from queue import Empty
import metallum
import re
import telegram
from typing import NoReturn
from decouple import config
from telegram import MAX_MESSAGE_LENGTH, Update
from telegram.ext import Updater, CallbackContext, CommandHandler  # , MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

BOT_TOKEN = config('BOT_TOKEN')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def map_markdown(s: str) -> str:
    return escape_markdown(s, version=2)

class Band:
    name: str
    location: str
    country: str
    genres: str
    status: str
    formed_in: str
    url: str

    _base_url: str = 'https://metal-archives.com/'

    _info: str

    def __init__(self, band: metallum.Search):
        escaped_band = list(map(map_markdown,
            [
                band.name,
                ', '.join(band.genres),
                band.status,
                band.location,
                band.country,
                band.formed_in
            ]
        ))
        self.name = escaped_band[0]
        print(self.name)
        self.genres = escaped_band[1]
        print(self.genres)
        self.status = escaped_band[2]
        print(self.status)
        self.location = escaped_band[3]
        print(self.location)
        self.country = escaped_band[4]
        print(self.country)        
        self.formed_in = escaped_band[5]
        print(self.formed_in)
        self.url = escape_markdown(self._base_url + band.url, version=2)
        print(self.url)
        self._info = '\n\n'.join(
            [
                f'*{self.name}*',
                f'_GENRE\(S\)_: {self.genres}',
                f'_LOCATION_: {self.location},{self.country}',                
                f'_FORMED IN_: {self.formed_in}',
                f'_STATUS_: {self.status}',
                f'_PAGE_: {self.url}'
            ]
        )

    def __str__(self):
        return self._info

class Bot:    
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    pm = telegram.ParseMode.MARKDOWN_V2

    def start(self, update: Update, context: CallbackContext) -> NoReturn:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="All hail the mighty *Encyclopaedia Metallum*\!\!\!\n\n"
                "I'm a bot designed to search for METAL bands\! \U0001F918\U0001F916\n\n"
                "You can use the following commands:\n\n"
                "`/band name of the band`\n"
                "\> if you want me to look for the *exact* name of a band \(searching for _Iron_ won't find _Iron Maiden_ in this case\)\n"
                "\>\> For example: `/band black sabbath`\n\n"
                "`/bands words in the name`\n"
                "\> if you want me to look for all bands that include *all* of those words in their names \(be careful, this could find *A LOT* of bands\)\n"
                "\>\> For example: `/bands iron`\n\n"
                "You can also type `/help band` or `/help bands` to learn more detailed/advanced searches\.",
            parse_mode=self.pm
        )

    def help(self, update: Update, context: CallbackContext) -> NoReturn:
        eci = update.effective_chat.id
        help_command = context.args[0]
        if help_command == 'band':
            context.bot.send_message(
                chat_id=eci,
                text="*HOW TO USE* `/band`:\n\n"
                    "When using this command, you can type the exact name of the band you wanna find\.\n"
                    "For instance, if you want _Iron Maiden_, you should type "
                    "`/band iron maiden` \(capitalization doesn't matter, i\.e\., _iron maiden_ is the same as _iRoN MAidEn_\)\.\n"
                    "You can get multiple bands with this command, if they have the exact same name, "
                    "but you will be able to differentiate them by location and genre\(s\) in the results\.\n\n"
                    "With this command, it's also possible to look for a band by ID "
                    "\(the one used by Encyclopaedia Metallum, which is the number at the end of the band's page url\)\.\n"
                    "To do that, you just need to type a number \(ID\), instead of the name, like so: `/band 38492` "
                    "which would give you the band with the very creative name _Inverted Pentagram_, for instance\.\n\n"
                    "But that's not all\!\nIn addition to searching for the ID, I will also look for bands with that exact number for a name "
                    "\(you know, just in case you're looking for the band called _13_, instead of the band with ID '13', for instance\)\.\n\n"
                    "If you include multiple numbers, or a number followed by more numbers and/or words, separated by spaces, I will only look for the first number as an ID, "
                    "and then look for the whole message as a name\.\n"
                    "For instance, `/band 7 sins` will have me look for the band with ID '7' \(which would be _Entombed_\), but also for the band named _7 Sins_\.\n\n"
                    "So, now you can master the `/band` command by discovering every band with numbers for names, or something\.\n*Get to work, METALHEAD\!*",
                parse_mode=self.pm
            )
        elif help_command == 'bands':
            context.bot.send_message(
                chat_id=eci,
                text="*HOW TO USE* `/bands`:\n\n"
                    "This is the crazy command\! Be prepared to get flooded with bands\.\n\n"
                    "You give this command one or more words and I will find you all bands with all those words in their names, no matter the order\!\n"
                    "That means `/bands black sabbath` will find _Black Sabbath_ and _Sabbath Black Heretic_\.\n\n"
                    "But that's the *poser* way to use it\. The *tr00* way would be something like `/bands hell`, which will give you upwards of\.\.\.\n"
                    "You know what, try that one for yourself\! \U0001F92D \n\n"
                    "Be aware that this looks for the actual separate words in the names, not for parts of words, meaning the above example "
                    "will find _Alyson Hell_ and even _DisnneyHell_ \(lmao\), but won't find _Helloween_\.\n\n"
                    "You can get even more comprehensive searches, though, with asterisks\(\*\), pipes\(\|\|\) and dashes\(\-\):\n\n"
                    "`/bands hell*` will now give you bands that contain *any* words beginning with 'hell' \(remember _Helloween_? You got it\!\)\n"
                    "`/bands *iron` will give you bands that have words ending with 'iron', such as _Iron Maiden_ and _Apeiron_\.\n"
                    "Finally, `/bands *iron*` will give you bands that have 'iron' in any part of their names, like _Ironsword_ or _Dramatic Irony_\.\n\n"
                    "`/bands blind || guardian` will give you bands that have *either* the words 'blind' *or* 'guardian' \(*or both*\) in their names\.\n"
                    "Note that you can combine that with the __asterisks\*__ explained above\.\n\n"
                    "`/bands black -sabbath` will give you all bands with the word 'black', but none of that 'sabbath' nonsense\.\n\n"
                    "Finally, and this should be obvious, you're not limited to two\-word searches, so go ahead and do something like "
                    "`/bands *crazy* || *black* || *troll* || *from* || *hell*`, but you might wanna disable notifications "
                    "'cause I'm gonna be messaging you for a while\!\n\n"
                    "Anyways, now you can discover all those ~dorky~ *EPIC* bands with 'dragon' in their names\. The fun is not SO FAR AWAY\!",
                parse_mode=self.pm
            )
        else:
            context.bot.send_message(chat_id=eci,
                                     text="I'm sorry, I can't help you with that!\nHave you tried `/help band` and `/help bands`?",
                                     parse_mode=self.pm)

    def search_bands(self, update: Update, context: CallbackContext, query: str, strict: bool, page_start: int = 0, bot_response: str = '') -> None:
        eci = update.effective_chat.id
        print('User = ' + update.effective_user.username + ', ' + update.effective_user.full_name + '\n Query = ' + query)

        try:
            band_list = metallum.band_search(query, strict=strict, page_start=page_start)
            if not band_list:
                raise IndexError            
            for i in range(band_list.result_count):
                band_result = band_list[i].get()
                band = Band(band_result)
                band_to_add = '\n\n'.join([str(band), f'{i+1+page_start}/{band_list.result_count}'])
                if bot_response:
                    if len(bot_response) + len('**********************\n\n' + band_to_add) <= MAX_MESSAGE_LENGTH:
                        bot_response += escape_markdown('\n\n**********************\n\n', version=2) + band_to_add
                    else:
                        context.bot.send_message(
                            chat_id=eci,
                            text=bot_response,
                            parse_mode=self.pm
                            )
                        bot_response = ''
                else:
                    bot_response += band_to_add           
                # print(bot_response)
                
                print('ok')
                if (i+1) % 200 == 0:                    
                    self.search_bands(update, context, query, strict=strict, page_start=page_start+200, bot_response=bot_response)
                    return
            if bot_response:
                context.bot.send_message(
                        chat_id=eci,
                        text=bot_response,
                        parse_mode=self.pm
                    )
                # if i < band_list.result_count and i % 10 == 0:
                #     keyboard = [
                #         [
                #             InlineKeyboardButton("Yes", callback_data='yes'),
                #             InlineKeyboardButton("No", callback_data='no')
                #         ]
                #     ]
                #     reply_markup = InlineKeyboardMarkup(keyboard)
                #     context.bot.send_message(
                #         chat_id=eci,
                #         text='Do you wish to go on?', reply_markup=reply_markup
                #     )
                #     if reply_markup == 'no':
                #         return
        except IndexError:
            context.bot.send_message(chat_id=eci, text='No band was found with that name. Remember, I only know METAL bands! \U0001F918\U0001F916')

    def band(self, update: Update, context: CallbackContext) -> NoReturn:
        eci = update.effective_chat.id

        try:
            if not context.args:
                context.bot.send_message(chat_id=eci, text='Please provide at least one word after the command, like `/band slayer`', parse_mode=self.pm)
            else:
                if re.search(r'^\d+$', context.args[0]):
                    context.bot.send_message(chat_id=eci, text=f'Searching for a band with ID: *{context.args[0]}*', parse_mode=self.pm)

                    try:
                        result = metallum.band_for_id(context.args[0])
                        if result.id != context.args[0]:
                            raise ValueError
                        band = Band(result)
                        context.bot.send_message(
                            chat_id=eci,
                            text=str(band),
                            parse_mode=self.pm
                        )
                    except ValueError as v:
                        print(v)
                        context.bot.send_message(chat_id=eci, text='No band was found with that ID')

                try:
                    query = ' '.join(context.args).lower().title()
                    escaped_query = escape_markdown(query, version=2)
                    context.bot.send_message(chat_id=eci, text=f'Searching for bands named: *{escaped_query}*', parse_mode=self.pm)
                    self.search_bands(update, context, query, True)
                    print("\n\nBand finished")
                except IndexError as i:
                    print(i)
                    context.bot.send_message(chat_id=eci, text='No band was found with that name. Remember, I only know METAL bands! \U0001F918\U0001F916')

        except Exception as e:
            print(e)
            context.bot.send_message(chat_id=eci, text='Something went wrong, please review your message and try again!')



    def bands(self, update: Update, context: CallbackContext) -> NoReturn:
        eci = update.effective_chat.id

        try:

            try:
                if not context.args:
                    context.bot.send_message(chat_id=eci, text='Please provide at least one word after the command, like `/bands slayer`', parse_mode=self.pm)
                else:
                    query = ' '.join(context.args).lower().title()
                    escaped_query = escape_markdown(query, version=2).replace('\|\|','or').replace('\-',', but not ')
                    context.bot.send_message(chat_id=eci, text=f"Searching for bands with '*{escaped_query}*' in their name", parse_mode=self.pm)
                    self.search_bands(update, context, query, False)
                            # if i < band_list.result_count and i % 10 == 0:
                            #     keyboard = [
                            #         [
                            #             InlineKeyboardButton("Yes", callback_data='yes'),
                            #             InlineKeyboardButton("No", callback_data='no')
                            #         ]
                            #     ]
                            #     reply_markup = InlineKeyboardMarkup(keyboard)
                            #     context.bot.send_message(
                            #         chat_id=eci,
                            #         text='Do you wish to go on?',
                            #         reply_markup=reply_markup
                            #     )
                            #     choice = input(reply_markup)
                            #     if choice == 'no':
                            #         return
                    print("Bands finished")
            except IndexError as i:
                print(i)
                context.bot.send_message(chat_id=eci, text='No band was found. Remember, I only know METAL bands! \U0001F918\U0001F916')

        except Exception as e:
            print(e)
            context.bot.send_message(chat_id=eci, text='Something went wrong, please review your message and try again!')

# def button(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
#     return query.data

    def __init__(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)
        
        band_handler = CommandHandler('band', self.band)
        self.dispatcher.add_handler(band_handler)

        bands_handler = CommandHandler('bands', self.bands)
        self.dispatcher.add_handler(bands_handler)

        # button_handler = CallbackQueryHandler(self.button)
        # self.updater.dispatcher.add_handler(button_handler)

        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    print('Starting')
    bot = Bot()

