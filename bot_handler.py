#!/usr/bin/python3

import SIM800L_utils
import configparser
import sys
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from functools import wraps

class bot():
    TOKEN=0
    def __init__(self):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logging.getLogger("vlc.player").setLevel(logging.CRITICAL + 1)
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
            try:
                name=' '
                config.add_section('Admins')
                while (name):
                    name=input("enter admin name >> ")
                    number=input("enter admin id >> ")
                    if name and number:
                        config.set('Admins', name, number)
            except Exception as e:
                logging.error(str(e))
                sys.exit(1)


            with open('settings.ini', 'w') as configfile:
                config.write(configfile)

        self.numbers = dict(config['Phonebook'])
        self.TOKEN = config['Tokens']['TOKEN']
        self.admins = dict(config['Admins'])
        self.simnames = dict(config['Sims'])

    def restricted(func):
        @wraps(func)
        def wrapped(self, update, context, *args, **kwargs):
            user_id = update.effective_user.id
            if str(user_id) not in self.admins.values():
                print("Unauthorized access denied for {}.".format(user_id))
                return
            return func(self, update, context, *args, **kwargs)
        return wrapped


    # Define a few command handlers. These usually take the two arguments update and
    # context.
    def start(self, update: Update, context: CallbackContext):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        update.message.reply_markdown_v2(
            'Hi {}\!'.format(user.mention_markdown_v2()),
            reply_markup=ForceReply(selective=True),
        )


    def help_command(self, update: Update, context: CallbackContext):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')


    def echo(self, update: Update, context: CallbackContext):
        """Echo the user message."""
        update.message.reply_text(update.message.text)


    @restricted
    def sim800l_bot(self, update: Update, context: CallbackContext):
        text=update.message.text
        if (text.split()[0].lower()=='call'):
            name=text.split()[1].lower()
            if (name in self.numbers):
                update.message.reply_text('calling '+self.numbers[name])
                call = SIM800L_utils.makeCall(self.numbers[name])
                update.message.reply_text('Call success is {}'.format(call))

        if (text.split()[0].lower()=='sim'):
            simno=int(text.split()[1])
            simchange = SIM800L_utils.changeSim(simno)
            if isinstance(simchange, str):
                iccid = int(''.join(char for char in str(simchange) if str(char).isdigit()))
            else:
                iccid = simchange

            if iccid>=0:
                try:
                    simname = list(self.simnames.keys())[list(self.simnames.values()).index(str(iccid))]
                except:
                    simname = 'unknown'
                update.message.reply_text(f'changed to sim number {simno}, iccid {iccid} ({simname})')
            else:
                update.message.reply_text(f'failed to change sim (error code {simchange})')

        if (text.split()[0].lower()=='receive'):
            smstext = SIM800L_utils.receiveSMS()
            update.message.reply_text("Unread texts:")
            for ss in smstext[1:-1]:
                try:
                    if not ss.isspace():
                        update.message.reply_text(ss)
                except Exception as e:
                    logging.error(e)

        if (text.split()[0].lower()=='reset'):
            SIM800L_utils.resetRadio()
    

# TODO: add bot safety.
# needs to:
# 1) generate token and access link only in console (not via chat)
# 2) if token used or timeout elapsed, delete token and not accept it anymore
# 3) when token used, add chat id to accepted chat ids in settings
# 4) restrict sim access to users in list

    def main(self):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater(self.TOKEN)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help_command))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.sim800l_bot))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
        #SIM800L.radioOff()
        #logging.info("Turned radio off. Bye!")


if __name__ == '__main__':
    bot().main()