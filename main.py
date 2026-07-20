import time
from config import CHECK_INTERVAL
from notifier import send
from monitor import check
while True:
    try:
        messages = check()
        for m in messages:
            send(m)
    except Exception:
        send('Monitor error')
    time.sleep(CHECK_INTERVAL)
