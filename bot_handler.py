#!/usr/bin/python3

import SIM800L_call
import configparser
import sys
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("omxplayer.player").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger(__name__)


# load configuration
config = configparser.ConfigParser()
try:
    config.read_file(open('settings.ini'))
except FileNotFoundError:
    try:
        tk=input("Insert telegram token >> ")
        if tk:
            config['Tokens'] = {'TOKEN':tk}
        else:
            logging.error('No telegram token given')
            sys.exit(1)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
    try:
        name=' '
        config.add_section('Phonebook')
        while (name):
            name=input("enter name >> ")
            number=input("enter number >> ")
            if name and number:
                config.set('Phonebook', name, number)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

numbers = config['Phonebook']
TOKEN = config['Tokens']['TOKEN']



# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        'Hi {}\!'.format(user.mention_markdown_v2()),
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def call(update: Update, context: CallbackContext):
    """Echo the user message."""
    text=update.message.text
    if (text.split()[0].lower()=='call'):
        name=text.split()[1].lower()
        if (name in numbers):
            update.message.reply_text('calling '+numbers[name])
            call = SIM800L_call.makeCall(numbers[name])
            update.message.reply_text('Call success is {}'.format(call))
    # update.message.reply_text(update.message.text)


def main():

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, call))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()