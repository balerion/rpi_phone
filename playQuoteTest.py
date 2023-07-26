from gtts import gTTS 
import vlc
from pathlib import Path

import requests
## function that gets the random quote
def get_random_quote():
    try:
        ## making the get request
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
    tts = gTTS(text=text, lang='en')
    filename = "abc.mp3"
    tts.save(filename)
    p = vlc.MediaPlayer(filename)#"abc.mp3"
    p.play()
    while p.get_state() != vlc.State.Ended:
        continue
    return text

getQuote()