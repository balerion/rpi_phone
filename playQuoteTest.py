from gtts import gTTS 
import os
from omxplayer.player import OMXPlayer
from pathlib import Path

import requests
## function that gets the random quote
def get_random_quote():
    try:
        ## making the get request
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
    print(text)
    tts = gTTS(text=text, lang='en')
    filename = "abc.mp3"
    tts.save(filename)
    player = OMXPlayer(Path(filename))
    while player.is_playing():
        continue
    # p = vlc.MediaPlayer(filename)"abc.mp3"
    # p.play()
    # os.system('mpg321 abc.mp3 &')
    # os.remove(filename)
    return text

