import sys
import logging
import requests
import time
from SIM800L import SIM800L
import RPi.GPIO as GPIO

from gtts import gTTS 
from pathlib import Path
import vlc

COMPORT_NAME = "/dev/serial0"
filename = "quote.mp3"

timeout_seconds = 10

GPIO.setwarnings(False)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logging.getLogger("vlc.player").setLevel(logging.CRITICAL + 1)


## function that gets the random quote
def get_random_quote():
    try:
        ## making the get request
        # response = requests.get("https://quote-garden.herokuapp.com/api/v3/quotes/random?genre=anger")
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            ## extracting the core data
            json_data = response.json()
            data = json_data['content']
            ## getting the quote from the data
            return (data)
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
    logging.info('getting quote, making call...')
    logging.info(print(getQuote()))

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
            player.play()
            while player.get_state() != vlc.State.Ended:
                continue
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

    if "+CPIN: READY" in sim800l.sendAtCommand(command="AT+CFUN=1"):
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            time.sleep(0.1)
            ret = sim800l.attemptRead()
            logging.info(ret)

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        time.sleep(0.5)
        reg = sim800l.checkRegistration()
        if "0,5" in reg[1]:
            break
    else:
        # This block is executed when the loop naturally exits without a break
        logging.info("could not register to network")

    
    sim800l.closeComPort()
    return 0

def changeSim(simno):
    GPIO.setmode(GPIO.BCM)
    gpios=(12,16,20)
    enable=21
    GPIO.setup(enable, GPIO.OUT)
    GPIO.output(enable, 0)
    for gpio in gpios:
        GPIO.setup(gpio, GPIO.OUT)

    bits = bin(simno)[2:]

    for bitno,gpio in enumerate(gpios):
        try:
            GPIO.output(gpio, int(bits[bitno]))
        except IndexError:
            GPIO.output(gpio, 0)

    resetRadio()
    # TODO: check for "Call ready" and CCID and CREG = 0,5


def main():
    # print(getQuote())
    try:
        player = vlc.MediaPlayer(Path(filename))
        logging.info(f'Playing?:{player.is_playing()}')
        player.play()
        while player.get_state() != vlc.State.Ended:
            continue

    except Exception as err: 
        logging.error(str(err))
    



if __name__ == "__main__":
    main()
    print("End of module")
# EOF
