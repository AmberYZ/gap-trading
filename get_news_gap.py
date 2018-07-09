#Run this script at 5:40 pm on trading days
#Get news for stocks gapped today
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
def get_news(trader,ticker):
	return trader.get_news(ticker)

	
if __name__ == '__main__':
	#	Login to my Robinhood Account
	print("Login to robinhood")
	#TODO: replace username and password with raw_input once the code is ready
	username = config.username
	password = config.password
	trader = Robinhood.Robinhood()
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
	print("Updating today's news for candidate stocks")


	#Retrieve data for stocks gapped (today): data for today and yesterday
	folder_today = os.path.join(config.data_root, str(today_date))

	for up_down in os.listdir(folder_today):
		if up_down == []:
			#No data were retrieved for current day, report error
			pass
		if up_down.startswith("."):
			continue
		
		#Make output directory
		output_root = os.path.join(config.news_root, str(today_date), up_down)
		if os.path.exists(output_root):
			pass
		else:
			os.makedirs(output_root)
		

		for stock in os.listdir(os.path.join(folder_today, up_down)):
			news = get_news(trader,stock)
			news_num = news['count']

			#Get top 3 cliked news
			if int(news_num) == 0:
				continue

			news_content = news['results']
			content_dict = {}
			for entry in news_content:
				content_dict[int(entry['num_clicks'])] = [entry['title'], entry['summary'], entry['source'],entry['relay_url']]
				
			news_content_sorted = content_dict.keys()
			news_content_sorted.sort(reverse=True)
			top_idx = news_content_sorted[0:min(3, len(news_content_sorted))]

			out_json = []
			for i in top_idx:
				select = content_dict[i]
				out_json.append({'title': select[0], 'summary':select[1], 'source':select[2], 'relay_url':select[3]})
			
			json.dump(out_json,open(os.path.join(output_root, stock+'.json'),'w'))
	print("News updating done")






	
	
