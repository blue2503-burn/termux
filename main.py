import time,traceback
from config import CHECK_INTERVAL
from notifier import send
from monitor import check
while True:
    try:
        messages = check()
        for m in messages:
            print(m)
            send(m)
    except Exception:
        send('Monitor error')
        print(traceback.format_exc())
    time.sleep(CHECK_INTERVAL)
