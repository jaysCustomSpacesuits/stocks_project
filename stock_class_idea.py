class StockBase():
    def __init__(self, stockticker):
        self.stockticker = stockticker
        self.history = None
    def check_in_logs(self):
        stock_df = pd.read_csv('stock_log.csv')
        if self.stockticker in stock_df['Ticker']:
            print('stock is in log')
        else:
            self.history = yf.Ticker(self.stockticker).history('10d')
            print('this stock was not in the log')
