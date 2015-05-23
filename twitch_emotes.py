import os
import json

rpath = os.path.dirname(os.path.abspath(__file__))

with open(rpath + '/global_emotes.json') as data:
    global_data = json.load(data)

with open(rpath + '/subscriber_emotes.json') as data:
    sub_data = json.load(data)

emotes = [str(em) for em in global_data['emotes'].keys()]
emotes.extend([str(em['code']) for em in sub_data['channels']['cirno_tv']['emotes']])

emote_table = dict()

for emote in emotes:
    emote_table[emote.lower()] = emote

emotes = None

def translate_emote(text):
    text = text.strip().lower()

    if text in emote_table:
        return emote_table[text]

    return text

