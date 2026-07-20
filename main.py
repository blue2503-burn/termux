import time,traceback
from config import CHECK_INTERVAL
from notifier import send
from monitor import check
while True:
    try:
        d=check();print(d)
    except Exception:
        send('Monitor error')
        print(traceback.format_exc())
    time.sleep(CHECK_INTERVAL)
