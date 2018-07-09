from __future__ import print_function
import time
import os
import config
from datetime import datetime
import boto
import config
import sys
#from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler



# def remove_local():
# 	pass

def run_get_news_gap():
	os.system('python get_news_gap.py')

# def sync_s3():
# 	print("Syncing s3", file=sys.stderr)
# 	access_key = config.access_key
# 	secret_key = config.secret_key
# 	cmd = 'AWS_ACCESS_KEY_ID='+access_key+' AWS_SECRET_ACCESS_KEY='+secret_key+' aws s3 sync static/ '+config.s3
# 	print(cmd)
# 	os.system(cmd)


def run_detect_gap():
	os.system('python detect_gap.py')

def run_get_data_candidate():
	os.system('python get_data_candidate.py')
	
	
def daily_update():
	run_detect_gap()
	run_get_data_candidate()
	run_get_news_gap()
# 	sync_s3()

# def test():
# 	print("here")

# print("Gaps scheduled to be deteted at 16:30 Mon - Friday")
# print("Data scheduled to be updated at 17:00 Mon - Friday")
# print("News scheduled to be collected at 17:15 Mon - Friday")
# print("Data scheduled to be synced and deleted at 17:30 Mon - Friday")

# apsched = BackgroundScheduler()
# apsched.configure({'apscheduler.timezone': 'UTC'})


# # apsched.add_job(schedule_task.run_detect_gap,'cron', day_of_week='mon-fri', hour=20, minute=30)
# # apsched.add_job(schedule_task.run_get_data_candidate, 'cron', day_of_week='mon-fri', hour=21, minute=00)
# # apsched.add_job(schedule_task.run_get_news_gap,'cron', day_of_week='mon-fri', hour=21, minute=10)
# # apsched.add_job(schedule_task.sync_s3,'cron', day_of_week='mon-fri', hour=21, minute=30)

# apsched.add_job(daily_update,'cron', day_of_week='mon-fri', hour=20, minute=15)
# apsched.add_job(test,'cron', day_of_week='mon-fri', hour=3, minute=52)


# #	For testing	#
# # #apsched.add_cron_job(schedule_task.run_detect_gap, day_of_week='mon-sun', hour=23, minute=17)
# # # apsched.add_cron_job(schedule_task.run_get_data_candidate, day_of_week='mon-fri', hour=23, minute=48)
# #apsched.add_cron_job(schedule_task.sync_s3, day_of_week='mon-sun', hour=3, minute=41)
# apsched.start()
# print("started!")



sched = BlockingScheduler()
sched.configure({'apscheduler.timezone': 'UTC'})
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=20, minute=30)
def scheduled_job():
	print("Start updating")
	daily_update()
	print("Done")

sched.start()



