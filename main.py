import time
from config import CHECK_INTERVAL, SCAN_INTERVAL
from notifier import send
from monitor import check_for_changes, get_status_summary

time_since_last_summary = CHECK_INTERVAL  # send a summary on the very first run

while True:
    try:
        diff_msg = check_for_changes()
        if diff_msg:
            send(diff_msg)

        if time_since_last_summary >= CHECK_INTERVAL:
            send(get_status_summary())
            time_since_last_summary = 0
    except Exception as e:
        send(f'⚠️ Monitor error: {type(e).__name__}: {e}')

    time.sleep(SCAN_INTERVAL)
    time_since_last_summary += SCAN_INTERVAL
