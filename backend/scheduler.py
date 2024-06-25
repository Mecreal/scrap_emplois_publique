import schedule
import time
from scraper import update_data

def schedule_updates():
    schedule.every(6).hours.do(update_data)

    try:
        update_data()  # Initial run

        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script interrupted by user. Exiting.")
