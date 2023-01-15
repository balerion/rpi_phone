import sys
import logging
import requests
from SIM800L import SIM800L

from gtts import gTTS 
from pathlib import Path
import vlc

COMPORT_NAME = "/dev/serial0"
filename = "quote.mp3"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logging.getLogger("vlc.player").setLevel(logging.CRITICAL + 1)


## function that gets the random quote
def get_random_quote():
    try:
        ## making the get request
        # response = requests.get("https://quote-garden.herokuapp.com/api/v3/quotes/random?genre=anger")
        response = requests.get("https://quote-garden.herokuapp.com/api/v3/quotes/random")
        if response.status_code == 200:
            ## extracting the core data
            json_data = response.json()
            data = json_data['data']

            ## getting the quote from the data
            return (data[0]['quoteText'])
        else:
            return ("Error while getting quote")
    except:
        return ("Something went wrong! Try Again!")


def getQuote():
    text=get_random_quote()
    tts = gTTS(text=text, lang='it')
    tts.save(filename)
    return text


def receiveSMS():
    sim800l = SIM800L(portName=COMPORT_NAME)
    sim800l.openComPort()
    sim800l.sendAtCommand(command="AT+CMGF=1")
    allsms = sim800l.sendAtCommand(command="AT+CMGL=\"REC UNREAD\"")
    sim800l.closeComPort()
    return allsms


def makeCall(number):
    print('making call...')
    print(getQuote())

    # logging.basicConfig(level=logging.DEBUG)

    sim800l = SIM800L(portName=COMPORT_NAME)
    sim800l.openComPort()

    if not sim800l.checkCommunication():
        logging.error("Couldn't communicate with module")
        sys.exit()
    if not  sim800l.initATSettings():
        logging.error("Couldn't initialize settings")
    success=sim800l.call(number,timeout=30,duration=-1)
    
    if success==2:
        try:
            player = vlc.MediaPlayer(Path(filename))
            logging.info(f'Playing?:{player.is_playing()}')
            player.play_sync()
        except Exception as e: 
            logging.error("Error: " + str(e))
        # os.remove(filename)

    if not sim800l.sendAtCommand("ATH"):
        logging.error("To send AT command: ATH")
    else:
        print("Successfully ended call")
    sim800l.closeComPort()

    return success

def resetRadio():
    sim800l = SIM800L(portName=COMPORT_NAME)
    sim800l.openComPort()
    sim800l.sendAtCommand(command="AT+CFUN=0")
    sim800l.sendAtCommand(command="AT+CFUN=1")
    sim800l.closeComPort()
    return 1


def main():
    # print(getQuote())
    try:
        player = vlc.MediaPlayer(Path(filename))
        logging.info(f'Playing?:{player.is_playing()}')
        player.play_sync()
    except Exception as err: 
        logging.error(str(err))
    



if __name__ == "__main__":
    main()
    print("End of module")
# EOF
