import requests
import datetime
from config import DISCORD_WEBHOOK

def send(msg):
    if DISCORD_WEBHOOK.startswith('PASTE_'): return
    ts = datetime.datetime.now().strftime('%I:%M:%S %p')
    requests.post(DISCORD_WEBHOOK,json={'content':f'🕒 {ts}\n{msg}'},timeout=20)
