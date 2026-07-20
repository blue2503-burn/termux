import requests
from config import DISCORD_WEBHOOK

def send(msg):
    if DISCORD_WEBHOOK.startswith('PASTE_'): return
    requests.post(DISCORD_WEBHOOK,json={'content':msg},timeout=20)
