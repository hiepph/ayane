import logging
import yaml
import os
import time
import sys

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Filters
import psycopg2
import psycopg2.extras

from plugins.history import History

from modules.bilac import Bilac
from modules.quote import Quote
from modules.doggo import Doggo


logging.basicConfig(format='%(asctime)s - %(name)s \
                    - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


## Config
stream = open("config.yml", "r")
CONFIG = yaml.load(stream)

## Database
DB = CONFIG['db']
DB_CONN = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (
                           DB['host'],
                           DB['dbname'],
                           DB['user'],
                           DB['password']))
DB_CUR = DB_CONN.cursor(cursor_factory=psycopg2.extras.DictCursor)

## History tricks
history = History(DB_CONN, DB_CUR)
flag = None

## Help
HELP = """At your service, sir.

/ping - check my connection

BILAC
/elo - Check members' elo

QUOTE
/addquote - create a new quote with (author, content)
/listquotes [author] - List created quotes
/randomquote [author] - Random a quote
/getquote id - Get a quote with id
/deletequote id - Delete a quote with id
"""


## Utilities
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def get_command():
    """Get the (root, command) of flag"""
    if flag == None:
        return None, None
    return flag.split("/")


## Handlers
def restart(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Restarting...")
    time.sleep(0.2)
    os.execl(sys.executable, sys.executable, *sys.argv)

def response(bot, update):
    """For handling response of the user"""
    global flag
    root, cmd = get_command()

    if root == "addquote":
        q = Quote(DB_CONN, DB_CUR)
        if cmd == "author":
            history.remember(update.message.text, flag)
            flag = "addquote/content"
            bot.send_message(chat_id=update.message.chat_id, text="Provide me the quote.")
            return
        elif cmd == "content":
            author = history.latest()['message']

            # history.remember(update.message.text, flag)
            flag = None

            q.add_quote(author, update.message.text)
            bot.send_message(chat_id=update.message.chat_id, text=q.latest_quote(), parse_mode=telegram.ParseMode.MARKDOWN)
            return

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="¯\_(ツ) _/¯")


## Responses
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=HELP)

def helpme(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=HELP)

def ping(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Pong")

def elo(bot, update):
    rep = "\n".join(Bilac().elo())
    bot.send_message(chat_id=update.message.chat_id, text=rep)

def addquote(bot, update):
    global flag
    flag = "addquote/author"
    bot.send_message(chat_id=update.message.chat_id, text="Provide me name of the author.")

def listquotes(bot, update, args):
    q = Quote(DB_CONN, DB_CUR)
    if len(args) == 0:
        author = None
    else:
        author = " ".join(args)

    bot.send_message(chat_id=update.message.chat_id, text=q.list_quotes(author), parse_mode=telegram.ParseMode.MARKDOWN)

def randomquote(bot, update, args):
    q = Quote(DB_CONN, DB_CUR)
    if len(args) == 0:
        author = None
    else:
        author = " ".join(args)

    bot.send_message(chat_id=update.message.chat_id, text=q.random_quote(author), parse_mode=telegram.ParseMode.MARKDOWN)

def getquote(bot, update, args):
    q = Quote(DB_CONN, DB_CUR)
    if len(args) == 0:
        # bot.send_message(chat_id=update.message.chat_id, text="ERROR: /getquote id")
        return
    else:
        qid = args[0]
        bot.send_message(chat_id=update.message.chat_id, text=q.quote(qid), parse_mode=telegram.ParseMode.MARKDOWN)

def deletequote(bot, update, args):
    q = Quote(DB_CONN, DB_CUR)
    if len(args) == 0:
        # bot.send_message(chat_id=update.message.chat_id, text="ERROR: /deletequote id")
        return
    else:
        qid = args[0]
        q.delete_quote(qid)
        bot.send_message(chat_id=update.message.chat_id, text="Done.")

def listdoggos(bot, update):
    doggo = Doggo()
    bot.send_message(chat_id=update.message.chat_id, text=doggo.list())

def doggo(bot, update, args):
    doggo = Doggo()
    if len(args) == 0:
        breed = None
    else:
        breed = args[0]

    res = doggo.random(breed)
    if res == None:
        bot.send_message(chat_id=update.message.chat_id, text="Not found.")
    else:
        bot.send_photo(chat_id=update.message.chat_id, photo=doggo.random(breed))


if __name__ == '__main__':
    # Create the EventHandler and pass bot's token
    updater = Updater(token=CONFIG['token'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # On different comamnds - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', helpme))
    dispatcher.add_handler(CommandHandler('restart', restart))

    dispatcher.add_handler(CommandHandler('ping', ping))

    dispatcher.add_handler(CommandHandler('elo', elo))

    dispatcher.add_handler(CommandHandler('addquote', addquote))
    dispatcher.add_handler(CommandHandler('listquotes', listquotes, pass_args=True))
    dispatcher.add_handler(CommandHandler('randomquote', randomquote, pass_args=True))
    dispatcher.add_handler(CommandHandler('getquote', getquote, pass_args=True))
    dispatcher.add_handler(CommandHandler('deletequote', deletequote, pass_args=True))

    dispatcher.add_handler(CommandHandler('listdoggos', listdoggos))
    dispatcher.add_handler(CommandHandler('doggo', doggo, pass_args=True))

    # Message Handler
    dispatcher.add_handler(MessageHandler(Filters.text, response))

    # Handle unknown commands
    # dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    logger.info("Ayaneru is online and ready.")

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    # Disconnect all connection
    DB_CUR.close()
    DB_CONN.close()
