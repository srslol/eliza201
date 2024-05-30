import speech_recognition as sr
import pocketsphinx
from openai import OpenAI
import os
import sounddevice as sd
import soundfile as sf
from deepgram import (
    DeepgramClient,
    SpeakOptions,)
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
dg_api_key=os.getenv('DG_API_KEY')

#OpenAI
client = OpenAI()

#Recording Steps
r = sr.Recognizer()
mic = sr.Microphone()
#mic_list = sr.Microphone.list_microphone_names() # to get list of microphone devices

#personality = input("What role am I playing?")
#personality = 'You are my personal assistant'
personality = 'You are an arrogant jerk who is insulting'

messages = [{
        "role":"system",
        'content': personality
        #"content": '''You are my psychologist.''' or whatever personality or agent style you choose.
    }]

def add_messages(role,content):
    messages.append({'role':role, "content": content})

def speech2text_from_mic():
    text = ' '
    while text != '':  
        print('Listening...')  
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)#,timeout=5)
            try:
                text = r.recognize_google(audio)#, show_all=True) 
                
            except Exception as e:
                print(f"Exception: {e}")
                print("Trying second gpt.  Google is not working.")
                text = r.recognize_sphinx(audio)
        if text == '':
            return('')
        
        check_quit = text.split()
        if (check_quit[0] == 'quit') or (check_quit[0]=='finished') or (check_quit[0] == 'stop'):
            print('Goodbye.')
            quit()
            
        if (text == 'quit') or (text=='stop'):
            print('Goodbye.')
            quit()

        return(text)

def text2speech(text,filename):
    try:
        SPEAK_OPTIONS = {"text": text}
        #deepgram = DeepgramClient(api_key=os.getenv("DG_API_KEY"))
        deepgram = DeepgramClient(dg_api_key)
        options = SpeakOptions(
            model="aura-athena-en",
            encoding="linear16",
            container="wav"
            )
        deepgram.speak.v("1").save(filename, SPEAK_OPTIONS, options)  #speak from filename
        
    except Exception as e:
        print(f"Exception: {e}")

    return True

def playback(filename):
    print('Preparing Audio')
    try:
        # Extract data and sampling rate from file
        data, fs = sf.read(filename, dtype='float32')  
        sd.wait()
        sd.play(data, fs, blocking=False)
        #status = sd.wait()  # Wait until file is done playing
        sd.wait()  # Wait until file is done playing
        print('Audio Executed')
        #time.sleep(.5)
        return True
    
    except Exception as e:
        print(f"Exception: {e}")
        print('Error in playback')
        return False
    
def get_gpt(prompt):
    response = client.chat.completions.create(
        model='gpt-4',
        messages=messages
        )
    answer = response.choices[0].message.content
    return(answer)


filename = "speach_output.wav"
print('System Ready...\nSay QUIT when finished.')

while True:
    result = speech2text_from_mic()
    if result == '':
        print('Nothing yet...')
        continue

    print(f"Question: {result}")

    prompt = result+' as briefly as possible.'
    add_messages("user",prompt)
    try:
        answer = get_gpt(prompt)
        print("answer!")
        pass
    except Exception as e: 
        print(f'Error: {e}')
        #answer = 'Sorry, there was an error.'
        print("Sorry, answer not valid")
        continue
        
    add_messages('system', answer) 
    print(answer)
    text2speech(answer,filename)
    playback(filename)
    print('-')
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Exception: {e}")

