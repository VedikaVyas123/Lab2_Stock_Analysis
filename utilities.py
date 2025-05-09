#Helper Functions

import matplotlib.pyplot as plt 

from os import system, name

# Function to Clear the Screen
def clear_screen():
    if name == "nt": # User is running Windows
        _ = system('cls')
    else: # User is running Linux or Mac
        _ = system('clear')

# Function to sort the stock list (alphabetical)
def sortStocks(stock_list):
    ## Sort the stock list
    stock_list.sort(key=lambda stock:stock.symbol) 


# Function to sort the daily stock data (oldest to newest) for all stocks
def sortDailyData(stock_list):
    for stock in stock_list:
        stock.DataList.sort(key=lambda daily_data:daily_data.date) 

# Function to create stock chart
def display_stock_chart(stock_list,symbol):
    for stock in stock_list:
        if stock.symbol == symbol:
            dates = [daily_data.date for daily_data in stock.DataList] 
            prices = [daily_data.close for daily_data in stock.DataList] 

            if not dates or not prices:
                return 
            
            plt.figure(figsize=(10, 5))
            plt.plot(dates, prices, marker='o', linestyle='-', color='red')
            plt.title(f"Stock Price History for {symbol}")
            plt.xlabel("Date")
            plt.ylabel("Closing Price ($)")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()