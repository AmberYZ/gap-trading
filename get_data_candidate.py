#Run this script at 5:00 pm on trading days
#1) Get today's data yesterday's data for today's candidates
#2) Get today's data for candidates detected in today -1, -2, -3, -4 -5


import Robinhood
from datetime import datetime
import json
import sys
import os
from datetime import date, timedelta
from collections import defaultdict
import operator
import config
import json



#	List of tradable stock tickers
tradable = config.tradable

tz = config.timezone

#	wrapper fro the get_historical quotes functions in Robinhood
def get_data(trader,ticker, interval,span):
	return trader.get_historical_quotes(ticker,interval=interval,span=span)['results'][0]

	
if __name__ == '__main__':
	#	Login to my Robinhood Account
	print("Login to robinhood")
	#TODO: replace username and password with raw_input once the code is ready
	username = config.username
	password = config.password
	trader =Robinhood.Robinhood()
	my_portfolio = trader.login(username=username, password=password)


	#	Load all tradable stocks
	tradable_ticker = []
	with open(tradable) as f:
		for stock in f:
			ticker = stock.split(",")[0]
			tradable_ticker.append(ticker)



	#	Today's date
	today_date = (datetime.now(tz)).date() 
	######### Manually update a gap day ##########
	today_date = datetime.strptime("2018-06-08", '%Y-%m-%d').date()
	##############################################
	print('Today is: '+ str(today_date))
	print("Updating today's quote data for candidate stocks")

	date_list = []
	for date_str in os.listdir(config.data_root): 
		if date_str.startswith("."):
			continue
		#check to see if the folder is empty
		if os.listdir(os.path.join(config.data_root, date_str)) == []:
			continue
		date = datetime.strptime(date_str, '%Y-%m-%d').date()
		if date <= today_date:
			date_list.append(date)
	date_list = sorted(date_list)
	
	assert(date_list[-1] == today_date)

	try:
		yesterday_date = date_list[-2]
	except:
		yesterday_date = None
	
	#Retrieve data for stocks gapped (today): data for today and yesterday
	folder_today = os.path.join(config.data_root, str(today_date))

	for up_down in os.listdir(folder_today):
		if up_down == []:
			#No data were retrieved for current day, report error
			pass
		if up_down.startswith("."):
			continue
		
		#Get date of last trading day
		for stock in os.listdir(os.path.join(folder_today, up_down)):
			data_last_week_json = get_data(trader,stock,'5minute','week')
			historicals = data_last_week_json['historicals']
			data_tmp = defaultdict(list)

			for entry in historicals:
				datestamp = datetime.strptime( entry['begins_at'], "%Y-%m-%dT%H:%M:%SZ" ).date()
				data_tmp[datestamp].append(entry)
			
			
			today_data = data_tmp[today_date]
			#Today's data
			out_path = os.path.join(folder_today, up_down, stock)
			with open(os.path.join(out_path,str(today_date)+'.json'), 'w') as outfile:
				json.dump(today_data, outfile)

			# Yesterday's data
			if yesterday_date != None:
				yesterday_data = data_tmp[yesterday_date]
				yesterday_path = os.path.join(folder_today, up_down, stock, str(yesterday_date))
				with open(os.path.join(out_path,str(yesterday_date)+'.json'), 'w') as outfile:
					json.dump(yesterday_data, outfile)



	# Retrieve data for stocks gapped today -1, -2, -3, -4, -5
	for k in range(2,7):
		prev_date = date_list[-k]
		folder_prev = os.path.join(config.data_root, str(prev_date))
		for up_down in os.listdir(folder_prev):
			if up_down == []:
				#No data were retrieved for current day, report error
				pass
			if up_down.startswith("."):
				continue
	
			#Get date of last trading day
			for stock in os.listdir(os.path.join(folder_prev, up_down)):
				if stock.startswith("."):
					continue
				data_last_week_json = get_data(trader,stock,'5minute','week')
				historicals = data_last_week_json['historicals']
				today_data = []

				for entry in historicals:
					datestamp = datetime.strptime(entry['begins_at'], "%Y-%m-%dT%H:%M:%SZ" ).date()
					if datestamp == today_date:
						today_data.append(entry)
						
				#Write today_data to file
				prev_out_path = os.path.join(folder_prev, up_down, stock)


				with open(os.path.join(prev_out_path, str(today_date)+ ".json"),'w') as outfile:
					json.dump(today_data, outfile)
	print("Candidate stocks data update end")


	
	
