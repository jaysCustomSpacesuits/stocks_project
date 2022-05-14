# base for web project to extract and keep track of stocks
# based on technical indicators from Finviz screener

import requests
from bs4 import BeautifulSoup, Comment
import yfinance as yf
import pandas as pd
import sqlite3
from datetime import date
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html


# scrapes Finviz site for stocks that meet query and generates a
# returns list of the ticker symbols to use in yfinance

def get_stock_list():
    headers = {'User-Agent': 'Mozilla/5.0'}
    stocks = requests.get("https://finviz.com/screener.ashx?v=111&s=ta_p_wedgeup", headers=headers)
    stock_soup = BeautifulSoup(stocks.content, 'html.parser')
    stock_comment = str(stock_soup.find(string=lambda text: isinstance(text, Comment)))
    stock_list = stock_comment.split('\n')
    stock_list.remove(' TS')
    stock_list.remove('TE ')

    new_stock_list = [i.split('|') for i in stock_list]

    final_list = [i[0] for i in new_stock_list]

    return final_list


finviz_stock_list = get_stock_list()


# returns a list of the historical stocks pulled from historical_list csv

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

    # log_dictionary is used for adding to log csv
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

with sqlite3.connect('stocks.db') as conn:
    for i in stocks_history:
        stocks_history[i].to_sql(i, conn, if_exists='append', index=True, index_label=None)


# retrieves tables from stocks.db 

# retrieve_sql_tables function makes fetch_history function redundant

def retrieve_sql_tables():
    stock_table_list = []
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    for i in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        for x in i:
            stock_table_list.append(x)
    return stock_table_list
    
sql_tables = retrieve_sql_tables()


# pulling data from db into pandas df and plotting candlestick
# charts with plotly

stock_data_dict = {}
plotly_charts_list = []
stock_ticker_list = []

for i in range(len(sql_tables)):
    stock_data_dict[sql_tables[i]] = pd.read_sql(f'SELECT * FROM {sql_tables[i]}', conn)

for i in stock_data_dict.keys():
    stock_ticker_list.append(i)

for i in stock_data_dict:
    plotly_charts_list.append(go.Figure(data=[go.Candlestick(x=stock_data_dict[i]['Date'], open=stock_data_dict[i]['Open'], high=stock_data_dict[i]['High'], low=stock_data_dict[i]['Low'], close=stock_data_dict[i]['Close'])]))

for i, j in zip(plotly_charts_list, stock_ticker_list):
    i.update_layout(title=j)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

test_output = []

for m, n in zip(stock_ticker_list, plotly_charts_list):
    test_output.append(dcc.Graph(id=str(m), figure=n))

app.layout = html.Div(children=[
    html.H1(children='A Stock Chart Dash', style={'textAlign': 'center'}),

    html.Div(children=test_output),

])

if __name__ == '__main__':
    app.run_server(debug=True)