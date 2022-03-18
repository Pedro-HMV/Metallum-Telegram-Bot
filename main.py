import http
import logging
import re
import time
from typing import NoReturn

import metallum
from decouple import config
from flask import Flask, request
from telegram import MAX_MESSAGE_LENGTH, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Dispatcher, Updater
from telegram.utils.helpers import escape_markdown
from werkzeug.wrappers import Response

app = Flask(__name__)

BOT_TOKEN = config("BOT_TOKEN")
BASE_URL = "https://metal-archives.com/"
BAND_SEP = escape_markdown("\n\n" + "*" * 30 + "\n\n", version=2)
PM = ParseMode.MARKDOWN_V2


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def map_markdown(s: str) -> str:
    return escape_markdown(s, version=2)


class Band:
    def __init__(self, band):
        escaped_band = self.escape_band(band)
        self.name: str = escaped_band["name"]
        # print(self.name)
        self.genres: str = escaped_band["genres"]
        # print(self.genres)
        self.status: str = escaped_band["status"]
        # print(self.status)
        self.location: str = escaped_band["location"]
        # print(self.location)
        self.country: str = escaped_band["country"]
        # print(self.country)
        self.formed_in: str = escaped_band["formed_in"]
        # print(self.formed_in)
        self.themes = escaped_band["themes"]
        full_albums = band.albums.search(type="full-length")
        # print("Full albums: " + str(full_albums))
        string_albums: str = (
            "This band has no full-length albums. Check their page below"
            " for other releases."
            if full_albums == []
            else "\n".join([f"({str(a.year)}) {a.title}" for a in full_albums])
        )
        self.albums = escape_markdown(string_albums, version=2)
        # print(self.albums)
        self.url: str = escape_markdown(BASE_URL + band.url, version=2)
        # print(self.url)
        self._info: str = "\n\n".join(
            [
                f"*{self.name}*",
                f"_GENRES_: {self.genres}",
                f"_LOCATION_: {self.location}, {self.country}",
                f"_FORMED IN_: {self.formed_in}",
                f"_STATUS_: {self.status}",
                f"_THEMES_: {self.themes}",
                f"_ALBUMS_: \n{self.albums}",
                f"_PAGE_: {self.url}",
            ]
        )

    def __str__(self):
        return self._info

    def escape_band(self, band):
        escape_list = list(
            map(
                lambda x: escape_markdown(x, version=2),
                [
                    band.name,
                    ", ".join(band.genres),
                    band.status,
                    band.location,
                    band.country,
                    band.formed_in,
                    ", ".join(band.themes),
                ],
            )
        )
        escaped_band = {
            "name": escape_list[0],
            "genres": escape_list[1],
            "status": escape_list[2],
            "location": escape_list[3],
            "country": escape_list[4],
            "formed_in": escape_list[5],
            "themes": escape_list[6],
        }
        return escaped_band


class Bot:
    def __init__(self):
        self.updater: Updater = Updater(BOT_TOKEN)
        self.dispatcher: Dispatcher = self.updater.dispatcher
        self.flags = {}

        start_handler = CommandHandler("start", self.start, run_async=True)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler("help", self.help, run_async=True)
        self.dispatcher.add_handler(help_handler)

        band_handler = CommandHandler("band", self.band, run_async=True)
        self.dispatcher.add_handler(band_handler)

        bands_handler = CommandHandler("bands", self.bands, run_async=True)
        self.dispatcher.add_handler(bands_handler)

        stop_handler = CommandHandler("stop", self.stop, run_async=True)
        self.dispatcher.add_handler(stop_handler)

        # button_handler = CallbackQueryHandler(self.button)
        # self.updater.dispatcher.add_handler(button_handler)

        # self.updater.start_polling()
        # self.updater.idle()

    def start(self, update: Update, context: CallbackContext) -> NoReturn:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "All hail the mighty *Encyclopaedia Metallum*\\!\\!\\!\n\nI'm"
                " a bot designed to search for METAL bands\\!"
                " \U0001F918\U0001F916\n\nYou can use the following"
                " commands:\n\n`/band name of the band`\n\\> if you want me to"
                " look for the *exact* name of a band \\(searching for _Iron_"
                " won't find _Iron Maiden_ in this case\\)\n\\>\\> For"
                " example: `/band black sabbath`\n\n`/bands words in the"
                " name`\n\\> if you want me to look for all bands that include"
                " *all* of those words in their names \\(be careful, this"
                " could find *A LOT* of bands\\)\n\\>\\> For example: `/bands"
                " iron`\n\nUse `/stop` to shutdown ongoing searches\n\\>\\if"
                " you're gonna get a ton of results, but don't wanna wait, for"
                " instance\\.\\.\\. ||ain't nobody got time for that\\!||"
                "\n\nYou can also type `/help band` or `/help"
                " bands` to learn more detailed/advanced searches\\."
            ),
            parse_mode=PM,
        )

    def help(self, update: Update, context: CallbackContext) -> NoReturn:
        eci = update.effective_chat.id
        try:
            if not context.args:
                context.bot.send_message(
                    chat_id=eci,
                    text=(
                        "To learn about advanced searches, please type"
                        " ```\n/help band\n``` or ```\n/help bands\n```"
                    ),
                    parse_mode=PM,
                )
            else:
                help_command = context.args[0]
                if help_command == "band":
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "*HOW TO USE* `/band`:\n\n When using this"
                            " command, you can type the exact name of the band"
                            " you wanna find\\.\nFor instance, if you want"
                            " _Iron Maiden_, you should type `/band iron"
                            " maiden` \\(capitalization doesn't matter,"
                            " i\\.e\\., _iron maiden_ is the same as _iRoN"
                            " MAidEn_\\)\\.\nYou can get multiple bands with"
                            " this command, if they have the exact same name,"
                            " but you will be able to differentiate them by"
                            " location and genre\\(s\\) in the"
                            " results\\.\n\nWith this command, it's also"
                            " possible to look for a band by ID \\(the one"
                            " used by Encyclopaedia Metallum, which is the"
                            " number at the end of the band's page"
                            " url\\)\\.\nTo do that, you just need to type a"
                            " number \\(ID\\), instead of the name, like so:"
                            " `/band 38492` which would give you the band with"
                            " the very creative name _Inverted Pentagram_, for"
                            " instance\\.\n\nBut that's not all\\!\nIn"
                            " addition to searching for the ID, I will also"
                            " look for bands with that exact number for a name"
                            " \\(you know, just in case you're looking for the"
                            " band called _13_, instead of the band with ID"
                            " '13', for instance\\)\\.\n\nIf you include"
                            " multiple numbers, or a number followed by more"
                            " numbers and/or words, separated by spaces, I"
                            " will only look for the first number as an ID,"
                            " and then look for the whole message as a"
                            " name\\.\nFor instance, `/band 7 sins` will have"
                            " me look for the band with ID '7' \\(which would"
                            " be _Entombed_\\), but also for the band named _7"
                            " Sins_\\.\n\nSo, now you can master the `/band`"
                            " command by discovering every band with numbers"
                            " for names, or something\\.\n*Get to work,"
                            " METALHEAD\\!*\n\n\\(Remember, you can always"
                            " stop ongoings searches with `/stop`\\)"
                        ),
                        parse_mode=PM,
                    )
                elif help_command == "bands":
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "*HOW TO USE* `/bands`:\n\nThis is the crazy"
                            " command\\! Be prepared to get flooded with"
                            " bands\\.\n\nYou give this command one or more"
                            " words and I will find you all bands with all"
                            " those words in their names, no matter the"
                            " order\\!\nThat means `/bands black sabbath` will"
                            " find _Black Sabbath_ and _Sabbath Black"
                            " Heretic_\\.\n\nBut that's the *poser* way to use"
                            " it\\. The *tr00* way would be something like"
                            " `/bands hell`, which will give you upwards"
                            " of\\.\\.\\.\n||You know what, try that one for"
                            " yourself\\! \U0001F92D||\n\nBe aware that this"
                            " looks for the actual separate words in the"
                            " names, not for parts of words, meaning the above"
                            " example will find _Alyson Hell_ and even"
                            " _DisnneyHell_ \\(lmao\\), but won't find"
                            " _Helloween_\\.\n\nYou can get even more"
                            " comprehensive searches, though, with"
                            " asterisks\\(\\*\\), pipes\\(\\|\\|\\) and"
                            " dashes\\(\\-\\):\n\n`/bands hell*` will now give"
                            " you bands that contain *any* words beginning"
                            " with 'hell' \\(remember _Helloween_? You got"
                            " it\\!\\)\n`/bands *iron` will give you bands"
                            " that have words ending with 'iron', such as"
                            " _Iron Maiden_ and _Apeiron_\\.\nFinally, `/bands"
                            " *iron*` will give you bands that have 'iron' in"
                            " any part of their names, like _Ironsword_ or"
                            " _Dramatic Irony_\\.\n\n`/bands blind ||"
                            " guardian` will give you bands that have *either*"
                            " the words 'blind' *or* 'guardian' \\(*or"
                            " both*\\) in their names\\.\nNote that you can"
                            " combine that with the __asterisks\\*__ explained"
                            " above\\.\n\n`/bands black -sabbath` will give"
                            " you all bands with the word 'black', but none of"
                            " that 'sabbath' nonsense\\.\n\nFinally, and this"
                            " should be obvious, you're not limited to"
                            " two\\-word searches, so go ahead and do"
                            " something like `/bands *crazy* || *black* ||"
                            " *troll* || *from* || *hell*`, but you might"
                            " wanna disable notifications 'cause I'm gonna be"
                            " messaging you for a while\\!\n\nAnyways, now you"
                            " can discover all those ~dorky~ *EPIC* bands with"
                            " 'dragon' in their names\\. The fun is not SO FAR"
                            " AWAY\\!\n\n\\(Remember, you can always stop"
                            " ongoings searches with `/stop`\\)"
                        ),
                        parse_mode=PM,
                    )
                else:
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "I'm sorry, I can't help you with that\\!\nHave"
                            " you tried `/help band` and `/help bands`?"
                        ),
                        parse_mode=PM,
                    )
        except Exception as e:
            print(f"Exception in /help: {e}")
            context.bot.send_message(
                chat_id=eci,
                text=(
                    "YIKES! It looks like my creator did something wrong"
                    " here.\n\nI'm sorry, this error should get fixed soon!   "
                    " \U0001F91E\U0001F916"
                ),
            )

    def search_bands(
        self,
        eci,
        context: CallbackContext,
        query: str,
        strict: bool,
        page_start: int = 0,
        bot_response: str = "",
    ) -> None:
        while self.flags[f"{eci}"]:

            try:
                band_list = metallum.band_search(
                    query, strict=strict, page_start=page_start
                )
                if not band_list:
                    raise IndexError
                if page_start == 0 and band_list.result_count > 1:
                    if self.flags[f"{eci}"]:
                        context.bot.send_message(
                            chat_id=eci,
                            text=(
                                f"Found {band_list.result_count} bands\\."
                                " Please wait for all results to show up\\!"
                            )
                            + (
                                ""
                                if band_list.result_count < 15
                                else (
                                    "\n\nThis will take some time\\. Use"
                                    " `/stop` if you wanna\\.\\.\\. stop\\."
                                    " \U0001F643"
                                )
                            ),
                            parse_mode=PM,
                        )
                    if not self.flags[f"{eci}"]:
                        break
                for i in range(band_list.result_count):
                    band_result = band_list[i].get()
                    band = Band(band_result)
                    print(band)
                    band_to_add = "\n\n".join(
                        [
                            str(band),
                            f"{i+1+page_start}/{band_list.result_count}",
                        ]
                    )
                    if bot_response:
                        if (
                            len(bot_response) + len(BAND_SEP + band_to_add)
                            <= MAX_MESSAGE_LENGTH
                        ):
                            bot_response += BAND_SEP + band_to_add
                        else:
                            context.bot.send_message(
                                chat_id=eci,
                                text=bot_response,
                                parse_mode=PM,
                            )
                            bot_response = "" + band_to_add
                    else:
                        bot_response += band_to_add
                    if not self.flags[f"{eci}"]:
                        break
                    if (i + 1) % 200 == 0:
                        self.search_bands(
                            eci,
                            context,
                            query,
                            strict=strict,
                            page_start=page_start + 200,
                            bot_response=bot_response,
                        )
                        return
                if bot_response:
                    context.bot.send_message(
                        chat_id=eci, text=bot_response, parse_mode=PM
                    )
                self.flags[f"{eci}"] = False

            except IndexError:
                if self.flags[f"{eci}"]:
                    self.flags[f"{eci}"] = False
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "No band was found with that name. Remember, I"
                            " only know METAL bands! \U0001F918\U0001F916"
                        ),
                    )

    def band(self, update: Update, context: CallbackContext) -> NoReturn:
        eci = update.effective_chat.id
        if str(eci) in self.flags:
            context.bot.send_message(
                chat_id=eci,
                text=(
                    "Recalibrating from the previous"
                    " search\\.\\.\\.\n\n*Please wait a moment\\!*"
                    " \U0001F9BE\U0001F916"
                ),
                parse_mode=PM,
            )
            time.sleep(10)
        self.flags[f"{eci}"] = True

        try:
            if not context.args:
                context.bot.send_message(
                    chat_id=eci,
                    text=(
                        "Please provide at least one word after the command,"
                        " like `/band slayer`"
                    ),
                    parse_mode=PM,
                )
            else:
                if re.search(r"^\d+$", context.args[0]):
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "Searching for a band with ID:"
                            f" *{context.args[0]}*"
                        ),
                        parse_mode=PM,
                    )

                    try:
                        result = metallum.band_for_id(context.args[0])
                        if result.id != context.args[0]:
                            raise ValueError
                        band = Band(result)
                        context.bot.send_message(
                            chat_id=eci, text=str(band), parse_mode=PM
                        )
                    except ValueError as v:
                        print(f"Value error in /band: {v}")
                        context.bot.send_message(
                            chat_id=eci,
                            text="No band was found with that ID",
                        )

                try:
                    print(f"\n\nCOMMAND: /band\tARGS: {context.args}")
                    query = " ".join(context.args).lower().title()
                    print(
                        "User = "
                        + (
                            update.effective_user.username
                            if update.effective_user.username
                            else ""
                        )
                        + ", "
                        + (
                            update.effective_user.full_name
                            if update.effective_user.full_name
                            else ""
                        )
                        + f"\n Query = {query}\n\n"
                    )
                    escaped_query = escape_markdown(query, version=2)
                    context.bot.send_message(
                        chat_id=eci,
                        text=f"Searching for bands named: *{escaped_query}*",
                        parse_mode=PM,
                    )
                    self.search_bands(eci, context, query, strict=True)
                    print("\n\nBand finished")
                except IndexError as i:
                    print(f"IndexError in /band: {i}")
                    if self.flags[f"{eci}"]:
                        self.flags[f"{eci}"] = False
                        context.bot.send_message(
                            chat_id=eci,
                            text=(
                                "No band was found with that name. Remember, I"
                                " only know METAL bands! \U0001F918\U0001F916"
                            ),
                        )

        except Exception as e:
            print(f"Exception in /band: {e}")
            context.bot.send_message(
                chat_id=eci,
                text=(
                    "Something went wrong, please review your message and try"
                    " again!"
                ),
            )
        try:
            del self.flags[f"{eci}"]
        except KeyError as k:
            print(f"KeyError in /band: {k}")

    def bands(self, update: Update, context: CallbackContext) -> NoReturn:
        eci = update.effective_chat.id
        if str(eci) in self.flags and not self.flags[f"{eci}"]:
            context.bot.send_message(
                chat_id=eci,
                text=(
                    "Recalibrating from the previous search\\.\\.\\. *Please"
                    " wait a moment\\!* \U0001F9BE\U0001F916"
                ),
                parse_mode=PM,
            )
            time.sleep(10)
        self.flags[f"{eci}"] = True

        try:

            try:
                if not context.args:
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "Please provide at least one word after the"
                            " command, like `/bands slayer`"
                        ),
                        parse_mode=PM,
                    )
                else:
                    print(f"\n\nCOMMAND: /bands\tARGS: {context.args}")
                    query = " ".join(context.args).lower().title()
                    print(
                        "User = "
                        + (
                            update.effective_user.username
                            if update.effective_user.username
                            else ""
                        )
                        + ", "
                        + (
                            update.effective_user.full_name
                            if update.effective_user.full_name
                            else ""
                        )
                        + f"\n Query = {query}\n\n"
                    )
                    escaped_query = escape_markdown(query, version=2)
                    if (
                        re.search(r"\s-\S", query)
                        or re.search(
                            r"(([\w\d]\*)|(\*[\w\d])|(\*[\w\d]\*))+",
                            query,
                        )
                        or re.search(r"[\w\d]\s\|\|\s[\w\d]", query)
                    ):
                        context.bot.send_message(
                            chat_id=eci,
                            text=(
                                "Performing advanced search:"
                                f" '*{escaped_query}*'"
                            ),
                            parse_mode=PM,
                        )
                    else:
                        context.bot.send_message(
                            chat_id=eci,
                            text=(
                                "Searching for bands with"
                                f" '*{escaped_query}*'"
                                " in their name"
                            ),
                            parse_mode=PM,
                        )
                    self.search_bands(eci, context, query, strict=False)
                    print("\n\nBands finished")
            except IndexError as i:
                print(f"IndexError in /bands: {i}")
                if self.flags[f"{eci}"]:
                    self.flags[f"{eci}"] = False
                    context.bot.send_message(
                        chat_id=eci,
                        text=(
                            "No band was found with that name. Remember, I"
                            " only know METAL bands! \U0001F918\U0001F916"
                        ),
                    )

        except Exception as e:
            print(f"Exception in /bands: {e}")
            context.bot.send_message(
                chat_id=eci,
                text=(
                    "Something went wrong, please review your message and try"
                    " again!"
                ),
            )
        try:
            del self.flags[f"{eci}"]
        except KeyError as k:
            print(f"KeyError in /bands: {k}")

    def stop(self, update: Update, context: CallbackContext) -> NoReturn:
        try:
            self.flags[f"{update.effective_chat.id}"] = False
        except Exception as e:
            print(f"Exception in /stop: {e}")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "SHUTTING DOWN!    \U0001F44B\U0001F916\n\n(You may still get"
                " one more message with the results I've gathered so far.)"
            ),
        )
        print("\n\n\n------------STOPPING COMMAND------------\n\n\n")

    # def button(update: Update, context: CallbackContext):
    #     query = update.callback_query
    #     query.answer()
    #     return query.data


@app.post("/")
def index() -> Response:
    bot = Bot()
    bot.dispatcher.process_update(
        Update.de_json(request.get_json(force=True), bot)
    )

    return "", http.HTTPStatus.NO_CONTENT
