from __future__ import print_function
import flask
from flask import Flask
from flask import render_template, request,url_for
from flask import send_from_directory
import csv
import requests
import json
import sys
import os
from flask import Flask, render_template, jsonify
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import logging
# import schedule_task
import config
from datetime import datetime
from collections import defaultdict
from pytz import utc
import atexit

app = Flask(__name__)
app.secret_key = 'some_secret'
logging.basicConfig()


#Update day mon - fri at 4: 15 after market closes
# def daily_update():
# 	schedule_task.run_detect_gap()
# 	schedule_task.run_get_data_candidate()
# 	schedule_task.run_get_news_gap()
# 	# schedule_task.sync_s3()



# @app.before_first_request
# def initialize():
# 	print("Gaps scheduled to be deteted at 16:30 Mon - Friday")
# 	print("Data scheduled to be updated at 17:00 Mon - Friday")
# 	print("News scheduled to be collected at 17:15 Mon - Friday")
# 	print("Data scheduled to be synced and deleted at 17:30 Mon - Friday")

# 	apsched = BackgroundScheduler()
# 	apsched.configure({'apscheduler.timezone': 'UTC'})
	

# 	# apsched.add_job(schedule_task.run_detect_gap,'cron', day_of_week='mon-fri', hour=20, minute=30)
# 	# apsched.add_job(schedule_task.run_get_data_candidate, 'cron', day_of_week='mon-fri', hour=21, minute=00)
# 	# apsched.add_job(schedule_task.run_get_news_gap,'cron', day_of_week='mon-fri', hour=21, minute=10)
# 	# apsched.add_job(schedule_task.sync_s3,'cron', day_of_week='mon-fri', hour=21, minute=30)
	
# 	apsched.add_job(daily_update,'cron', day_of_week='mon-fri', hour=20, minute=15)
	

# 	#	For testing	#
# 	# #apsched.add_cron_job(schedule_task.run_detect_gap, day_of_week='mon-sun', hour=23, minute=17)
# 	# # apsched.add_cron_job(schedule_task.run_get_data_candidate, day_of_week='mon-fri', hour=23, minute=48)
# 	#apsched.add_cron_job(schedule_task.sync_s3, day_of_week='mon-sun', hour=3, minute=41)
# 	apsched.start()



# initialize()

#Return the list of stocks that gapped at day - 5
def get_stocks_for_viz(alter_day = None):
	date_list = []
	for date_str in os.listdir(config.data_root): 
		if date_str.startswith("."):
			continue
		#check to see if the folder is empty
		if os.listdir(os.path.join(config.data_root, date_str)) == []:
			continue
		today_date = (datetime.now(config.timezone)).date() 
		# today_date = datetime.strptime("2018-04-27", '%Y-%m-%d').date()
		date = datetime.strptime(date_str, '%Y-%m-%d').date()
		if date <= today_date:
			date_list.append(date)
	date_list = sorted(date_list)

	day = str(date_list[-6]) #Day of gap
	day_before = str(date_list[-7])

	try:
		if alter_day != None:
			day = (datetime.strptime(alter_day, '%Y-%m-%d').date())
			day_before = str(date_list[date_list.index(day) - 1])
			day = str(day)
	except:
		pass

	up_list = os.listdir(os.path.join(config.data_root, day, 'up'))
	down_list = os.listdir(os.path.join(config.data_root, day,'down'))

	#assert(date_list[-1] == today_date)
	return day_before, day, up_list, down_list


@app.route("/")
def prepare(alter_day = None):
	up_list_sorted = {}
	down_list_sorted = {}
	list_dict = {'up':up_list_sorted, 'down':down_list_sorted}


	day_before, day, up_list, down_list, = get_stocks_for_viz(alter_day)
	# print(day)
	if alter_day != None:
		day = alter_day

	#First, sort the up_list and down_list by the amount of gap
	for a in list_dict.keys():
		for stock in os.listdir(os.path.join(config.data_root,day, a)):
			if stock.startswith("."):
				continue
			stock_folder = os.path.join(config.data_root, day, a, stock)
			files = [f.split(".")[0] for f in os.listdir(stock_folder)]
			files.sort()
			# print("----files----")
			# print(files)
			# print("day----", day)
			for i in range(len(files)):
				if files[i].startswith(day):
					print(files[i-1])
					today = json.load(open(os.path.join(stock_folder,files[i]+".json")))[0]['open_price']
					try:
						before = json.load(open(os.path.join(stock_folder,files[i-1]+".json")))[-1]['close_price']
					except:
						before = 1


					list_dict[a][stock] =  (float(today) - float(before)) / float(before) * 100
					break

	up_list_sorted = sorted(up_list_sorted.items(), key= lambda kv: (-kv[1], kv[0]))
	down_list_sorted = sorted(down_list_sorted.items(), key= lambda kv: (-kv[1], kv[0]),reverse=True)
			
	
	path_up = defaultdict(list)
	path_down = defaultdict(list)

	up_list = [a[0] for a in up_list_sorted]
	down_list = [a[0] for a in down_list_sorted]

	for stock in up_list:
		root_path = config.data_root+ day+ '/up/'+stock
		for file in os.listdir(root_path):
			path_up[stock].append(os.path.join(root_path, file))

	for stock in down_list:
		root_path = config.data_root+ day+ '/down/'+stock
		for file in os.listdir(root_path):
			path_down[stock].append(os.path.join(root_path, file))

	#Sort the list of dates
	for d in [path_up, path_down]:
		d = [v.sort() for v in d.values()]

	#Load json files and pass to javascript
	up_all = defaultdict(list)
	down_all = defaultdict(list)
	
	for k,v in path_up.items():
		for path in v:
			up_all[k].extend(json.load(open(path)))
	
	for k,v in path_down.items():
		for path in v:
			down_all[k].extend(json.load(open(path)))


	#Pack the arguments
	return {'up':[day,up_list,path_up, up_list_sorted, up_all], 'down':[day, down_list, path_down, down_list_sorted, down_all]}



@app.route("/up")
def up():
	args = prepare()['up']
	# print(args[0])
	return render_template('gap_dashboard.html', up_down = 'up', today = args[0], stocks = args[1], path = args[2], gap_value = args[3], all_data = args[4])

@app.route("/up_<today>")
def up_alter_day(today):
	args = prepare(today)['up']
	return render_template('gap_dashboard.html', up_down = 'up', today = args[0], stocks = args[1], path = args[2], gap_value = args[3], all_data = args[4])



@app.route("/down")
def down():
	args = prepare()['down']
	return render_template('gap_dashboard.html', up_down = 'down', today = args[0], stocks = args[1], path = args[2], gap_value = args[3],all_data = args[4])

@app.route("/down_<today>")
def down_alter_day(today):
	args = prepare(today)['down']
	return render_template('gap_dashboard.html', up_down = 'down', today = args[0], stocks = args[1], path = args[2], gap_value = args[3],all_data = args[4])


if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)



