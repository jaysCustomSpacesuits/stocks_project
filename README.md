#Stock Tracker

This repo contains a small Dash app for tracking stock performance based on stocks that meet a number of criteria which can be selected at: 

https://finviz.com/screener.ashx


**stock_class_idea.py can be ignored**

type 'python3 stocks.py' to run

It is intended to be run each day in order to catch all new stocks that meet the given criteria and add them to a database. Each new stock has the past 30 days of data pulled. Each consecutive day after that the previous days data is retrieved and appended to each respective table. It will also graph the price history for each stock as a candlestick chart.

The app primarily revolves around four functions.

	•	get_stock_list()
	•	get_historical_list()
	•	fetch_history()
	•	retreieve_sql_tables()

get_stock_list()

- this function scrapes the results from the finviz site based on the query url and returns a list of stock tickers

get_historical_list()

- all new stocks are added to a csv file for easy record keeping. this function retrieves the stocks which are already contained in the database and returns the tickers as a list.

fetch_history()

-  fetch history function uses yfinance to get the price history of all stocks. 30 days for stocks seen for the first time, 1 day for stocks already contained in database. it returns this info as a dictionary with the ticker as the key and the price history as the value.

retrieve_sql_tables()

- this function returns a list of all the tickers (tables) in the database. it is somewhat redundant also having get_historical_list() but is currently used for the sql query that follows on line 115. could be swapped/combined with get_historical_list() for simplification


The remainder of the stocks.py contains the code for the Dash app and the graphs which are read from the database and plotted with plotly.graph_objects

to do:
- [] put lines 111 through 125 into a function
- [] put functions into modules and break out dash app into its own file