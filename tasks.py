"""Realized task manager for "update_rate" in 10 minutes"""

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from models import XRate
import api


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=10)
def update_rate():
    print(f"Job started at {datetime.now()}")
    xrates = XRate.select()
    for rate in xrates:
        try:
            api.update_rate(rate.from_currency, rate.to_currency)
        except Exception as ex:
            print(ex)

    print(f"Job finished at {datetime.now()}")


sched.start()
