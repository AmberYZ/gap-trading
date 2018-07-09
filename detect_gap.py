#Run this script at 9:30 am on Trading days: 
#1) Calculate the gaps and find candidate stocks of the stock
#2)	Create folds for data collection

import Robinhood
import json
import sys
import os
from datetime import date, timedelta, datetime
from collections import defaultdict
import operator
import config

tz = config.timezone

#	List of tradable stock tickers
tradable = config.tradable


#	wrapper fro the get_historical quotes functions in Robinhood
def get_data(trader,ticker, interval,span):
	return trader.get_historical_quotes(ticker,interval=interval,span=span)['results'][0]

	
if __name__ == '__main__':
	#	Login to my Robinhood Account
	#	TODO: replace username and password with raw_input once the code is ready
	username = config.username
	password = config.password
	trader =Robinhood.Robinhood()
	my_portfolio = trader.login(username=username, password=password)

	#	Today's date
	today_date = datetime.now(tz).date()
	
	print("Detecting gaps")
	######## Manually update a gap day ##########
	today_date = datetime.strptime("2018-06-04", '%Y-%m-%d').date()
	##############################################
	print('Today is: '+ str(today_date))


	#	Load all tradable stocks
	tradable_ticker = []
	with open(tradable) as f:
		for stock in f:
			ticker = stock.split(",")[0]
			tradable_ticker.append(ticker)
	
	#	Get week historicals for all tradable stocks
	gap_dict = {} #Ticker: Gap. This dictionary will be used to rank stock candidates based on the gap
	#Gap: today's first open price - yesterday's close price
	
	
	for stock in tradable_ticker:
		yesterday_close = None
		found_today = False
		today_dollar_volume = 0
		today_volume = 0
		data_last_week_json = get_data(trader,stock,'5minute','week')
		# print(data_last_week_json)
		#Calculate the gap			
		historicals = data_last_week_json['historicals']
		for entry in historicals:

			datestamp = datetime.strptime( entry['begins_at'], "%Y-%m-%dT%H:%M:%SZ" ).date()
			if datestamp == today_date and found_today == False:
				found_today = True
				today_open = entry['open_price']

				try:
					gap = (float(today_open) - float(yesterday_close)) / float(yesterday_close) * 100
				except: 
					gap = today_open

			if datestamp == today_date:
				today_dollar_volume += float(entry['volume']) * ((float(entry['high_price']) + float(entry['low_price'])) / 2)
				today_volume += float(entry['volume'])
				# print(stock, entry['begins_at'],entry['volume'])

			yesterday_close = entry['close_price']
		

		if today_dollar_volume > 10000000: 
			gap_dict[stock] = gap
			print('added', stock, gap, today_volume, today_dollar_volume)



	#Sort to get top 10 gap up and gap down
	gap_sorted = sorted(gap_dict.items(), key=operator.itemgetter(1))
	print(gap_sorted)

	#Make a folder for stocks with top gaps today

	#Root path of historical data
	data = config.data_root

	data_today = os.path.join(data, str(today_date))
	if not os.path.exists(data_today):
		os.mkdir(data_today)

	for stock_pair in gap_sorted[0:10]:
		ticker = stock_pair[0]
		data_down = os.path.join(data_today,'down',ticker)
		if not os.path.exists(data_down):
			os.makedirs(data_down)
		
	for stock_pair in gap_sorted[-10: len(gap_sorted)]:
		ticker = stock_pair[0]
		data_up = os.path.join(data_today, 'up',ticker)
		if not os.path.exists(data_up):
			os.makedirs(data_up)
				

	print("Top 10 gap down")
	print(gap_sorted[0:10])
	print("Top 10 gap up")
	print(gap_sorted[-10: len(gap_sorted)])
			
