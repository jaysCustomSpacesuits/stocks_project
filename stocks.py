# base for web project to extract and keep track of stocks
# based on technical indicators from Finviz screener

import requests
from bs4 import BeautifulSoup, Comment
import yfinance as yf
import pandas as pd
import sqlite3
from datetime import date


# scrapes Finviz site for stocks that meet query and generates a
# list of the ticker symbols for use in yfinance

def get_stock_list():
    headers = {'User-Agent': 'Mozilla/5.0'}
    stocks = requests.get("https://finviz.com/screener.ashx?v=111&f=ta_changeopen_u,ta_sma20_cross200a,ta_sma50_pca&ft=3&o=-volume", headers=headers)
    stock_soup = BeautifulSoup(stocks.content, 'html.parser')
    stock_comment = str(stock_soup.find(string=lambda text: isinstance(text, Comment)))
    stock_list = stock_comment.split('\n')
    stock_list.remove(' TS')
    stock_list.remove('TE ')

    new_stock_list = [i.split('|') for i in stock_list]

    final_list = [i[0] for i in new_stock_list]

    return final_list


finviz_stock_list = get_stock_list()


# returns a list of the historical stocks pulled from
# get stock list function above 

def get_historical_list():
    historical_df = pd.read_csv('historical_list.csv')
    historical_list = list(historical_df['Ticker'].array)
    return historical_list


historical_stock_list = get_historical_list()

# retrieves price history for all stocks. if the stock is
# seen for the first time then the last 30 days is pulled.
# stocks in historical list have last 1 day retrieved.
# also adds new stocks to histrical list csv for record keeping.

def fetch_history():

    historical_df = pd.read_csv('historical_list.csv', index_col=0)

    stock_dict = {}

    # log_dictionary is used for logging and adding to log csv
    log_dictionary = {'Ticker': [], 'Date_Added': []}

    for tick in historical_stock_list:
        if tick not in finviz_stock_list:
            stock_dict[tick] = yf.Ticker(tick).history(period='1d')

    for tick in finviz_stock_list:
        if tick not in historical_stock_list:
            stock_dict[tick] = yf.Ticker(tick).history(period='1mo')
            log_dictionary['Ticker'].append(tick)
            log_dictionary['Date_Added'].append(date.today())
            new_stock_df = pd.DataFrame(data=log_dictionary)
            newest_stock_df = historical_df.append(new_stock_df, ignore_index=True)
            newest_stock_df.to_csv('historical_list.csv')

    return stock_dict


stocks_history = fetch_history()

# creates tables from stock price history for all stocks and adds
# to the database.
# i think this should be changed to using a single table for all stocks
# and using the ticker sybol as index.

with sqlite3.connect('stocks.db') as conn:
    for i in stocks_history:
        stocks_history[i].to_sql(i, conn, if_exists='append', index=True, index_label=None)

# use pd.read_sql here to pull price info from database
# use plotly to create candlestick charts.
# flask or dash for quick visualizations
