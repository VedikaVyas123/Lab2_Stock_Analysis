# Summary: This module contains the user interface and logic for a graphical user interface version of the stock manager program.

from datetime import datetime 
from os import path
from tkinter import *
from tkinter import ttk 
from tkinter import messagebox, simpledialog, filedialog
import csv
import stock_data
print("📦 Loaded stock_data module from:", stock_data.__file__) 
from stock_class import Stock, DailyData
from utilities import display_stock_chart, sortStocks 

class StockApp:
    def __init__(self):
        self.stock_list = []
        #check for database, create if not exists
        if path.exists("stocks.db") == False:
            stock_data.create_database()

 # This section creates the user interface

        # Create Window
        self.root = Tk()
        self.root.title("Vedika Stock Manager") #Replace with a suitable name for your program

        # Add Menubar
        self.menubar = Menu(self.root)

        # Add File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load data", command=self.load) 
        self.filemenu.add_command(label="Save data", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)


        # Add Web Menu 
        self.webmenu = Menu(self.menubar, tearoff=0)
        self.webmenu.add_command(label="Scrape Data from Yahoo! Finance", command=self.scrape_web_data)
        self.webmenu.add_command(label="Import CSV from Yahoo! Finance", command=self.importCSV_web_data) 
        self.menubar.add_cascade(label="Web", menu=self.webmenu) 


        # Add Chart Menu
        self.chartmenu = Menu(self.menubar, tearoff=0)
        self.chartmenu.add_command(label="Display stock chart", command=self.display_chart)
        self.menubar.add_cascade(label="Chart", menu=self.chartmenu)


        # Add menus to window   
        self.root.config(menu=self.menubar)    


        # Add heading information
        self.headingLabel = Label(self.root, text = "Welcome to Stock Manager", font=("Aptos", 14, "bold")) 
        self.headingLabel.pack(pady=10)

        # Add stock list
        self.stockList = Listbox(self.root, height=5, exportselection=False)
        self.stockList.pack()
        self.stockList.bind('<<ListboxSelect>>', self.update_data) 
        
        # Add Tabs
        self.tabControl = ttk.Notebook(self.root) 

        self.mainTab = Frame(self.tabControl)
        self.historyTab = Frame(self.tabControl) 
        self.reportTab = Frame(self.tabControl) 

        self.tabControl.add(self.mainTab, text = 'Main')
        self.tabControl.add(self.historyTab, text = 'History')
        self.tabControl.add(self.reportTab, text = 'Report')
        self.tabControl.pack(expand = 1, fill = "both")

        # Set Up Main Tab
        Label(self.mainTab, text="Symbol:").grid(row=0, column=0, padx=5, pady=5)
        self.addSymbolEntry = Entry(self.mainTab)
        self.addSymbolEntry.grid(row=0, column=1)

        Label(self.mainTab, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.addNameEntry = Entry(self.mainTab)
        self.addNameEntry.grid(row=1, column=1)

        Label(self.mainTab, text="Shares:").grid(row=2, column=0, padx=5, pady=5)
        self.addSharesEntry = Entry(self.mainTab)
        self.addSharesEntry.grid(row=2, column=1)

        Button(self.mainTab, text="Add Stock", command=self.add_stock).grid(row=3, column=0, pady=10)
        Button(self.mainTab, text="Delete Stock", command=self.delete_stock).grid(row=3, column=1, pady=10)

        Label(self.mainTab, text="Buy/Sell Shares:").grid(row=4, column=0, pady=5)
        self.updateSharesEntry = Entry(self.mainTab)
        self.updateSharesEntry.grid(row=4, column=1)

        Button(self.mainTab, text="Buy", command=self.buy_shares).grid(row=5, column=0, pady=10)
        Button(self.mainTab, text="Sell", command=self.sell_shares).grid(row=5, column=1, pady=10)

        # Setup History Tab
        self.dailyDataList = Text(self.historyTab, width=60, height=20)
        self.dailyDataList.pack(padx=10, pady=10)
        
        # Setup Report Tab
        self.stockReport = Text(self.reportTab, width=60, height=20)
        self.stockReport.pack(padx=10, pady=10)

        ## Call MainLoop
        self.root.mainloop()

# This section provides the functionality
       
    # Load stocks and history from database.
    def load(self):
        self.stockList.delete(0,END)
        stock_data.load_stock_data(self.stock_list)
        sortStocks(self.stock_list)
        for stock in self.stock_list:
            self.stockList.insert(END,stock.symbol)
        messagebox.showinfo("Load Data","Data Loaded")

    # Save stocks and history to database.
    def save(self):
        stock_data.save_stock_data(self.stock_list)
        messagebox.showinfo("Save Data","Data Saved")

    # Refresh history and report tabs
    def update_data(self, evt):
        self.display_stock_data()

    # Display stock price and volume history.
    def display_stock_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
                self.dailyDataList.delete("1.0",END)
                self.stockReport.delete("1.0",END)
                self.dailyDataList.insert(END,"- Date -   - Price -   - Volume -\n")
                self.dailyDataList.insert(END,"=================================\n")
                for daily_data in stock.DataList:
                    row = daily_data.date.strftime("%m/%d/%y") + "   " +  '${:0,.2f}'.format(daily_data.close) + "   " + str(daily_data.volume) + "\n"
                    self.dailyDataList.insert(END,row)

                #display report 
                total_value = 0 
                total_volume = 0 
                count = 0 
                for daily_data in stock.DataList:
                    total_value += daily_data.close 
                    total_volume += daily_data.volume 
                    count += 1
                
                if count > 0:
                    avg_price = total_value / count 
                    avg_volume = total_volume / count 
                else:
                    avg_price = 0
                    avg_volume = 0 

                self.stockReport.insert(END, f"Stock Report for {stock.name} ({stock.symbol})\n")
                self.stockReport.insert(END, "----------------------------------------\n")
                self.stockReport.insert(END, f"Total Days Tracked: {count}\n")
                self.stockReport.insert(END, f"Average Closing Price: ${avg_price:.2f}\n")
                self.stockReport.insert(END, f"Average Volume: {int(avg_volume)}\n")

    
    # Add new stock to track.
    def add_stock(self):
        new_stock = Stock(self.addSymbolEntry.get(),self.addNameEntry.get(),float(str(self.addSharesEntry.get())))
        self.stock_list.append(new_stock)
        self.stockList.insert(END,self.addSymbolEntry.get())
        self.addSymbolEntry.delete(0,END)
        self.addNameEntry.delete(0,END)
        self.addSharesEntry.delete(0,END)

    # Buy shares of stock.
    def buy_shares(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.buy(float(self.updateSharesEntry.get()))
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Buy Shares","Shares Purchased")
        self.updateSharesEntry.delete(0,END)

    # Sell shares of stock.
    def sell_shares(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                stock.sell(float(self.updateSharesEntry.get()))
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
        messagebox.showinfo("Sell Shares","Shares Sold")
        self.updateSharesEntry.delete(0,END)

    # Remove stock and all history from being tracked.
    def delete_stock(self):
       selection = self.stockList.curselection()
       if not selection:
           messagebox.showwarning("No Selection", "Please select a stock to delete.") 
           return 
       
       index = selection[0]
       symbol = self.stockList.get(index) 

       for stock in self.stock_list:
           if stock.symbol == symbol:
               self.stock_list.remove(stock)
               break 
           
       self.stockList.delete(self.stockList.curselection()[0]) 
       self.headingLabel.config(text="Stock deleted")
       self.dailyDataList.delete("1.0", END)
       self.stockReport.delete("1.0", END)
       messagebox.showinfo("Delete Stock", f"{symbol} removed") 

    # Get data from web scraping.
    #def scrape_web_data(self):
        #dateFrom = simpledialog.askstring("Starting Date","Enter Starting Date (m/d/yy)")
        #dateTo = simpledialog.askstring("Ending Date","Enter Ending Date (m/d/yy")
        #try:
            #stock_data.retrieve_stock_web(dateFrom,dateTo,self.stock_list)
        #except:
            #messagebox.showerror("Cannot Get Data from Web","Check Path for Chrome Driver")
            #return
        #self.display_stock_data()
        #messagebox.showinfo("Get Data From Web","Data Retrieved")
    
    def scrape_web_data(self):
        dateFrom = simpledialog.askstring("Starting Date", "Enter Starting Date (m/d/yy)")
        dateTo = simpledialog.askstring("Ending Date", "Enter Ending Date (m/d/yy)")
        try:
            print("📅 Date inputs received:", dateFrom, dateTo)
            stock_data.retrieve_stock_web(dateFrom, dateTo, self.stock_list)
            print("🟢 scrape_web_data called retrieve_stock_web")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("❌ Error inside scrape_web_data:", e)
            messagebox.showerror("Cannot Get Data from Web", "Check Path for Chrome Driver")
            return

        self.display_stock_data()
        messagebox.showinfo("Get Data From Web", "Data Retrieved")


    # Import CSV stock history file.
    def importCSV_web_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        filename = filedialog.askopenfilename(title="Select " + symbol + " File to Import",filetypes=[('Yahoo Finance! CSV','*.csv')])
        if filename != "":
            try: 

                stock_data.import_stock_web_csv(self.stock_list,symbol,filename)
                self.display_stock_data()
                messagebox.showinfo("Import Complete", symbol + " Import Complete")  
            except Exception as e: 
                messagebox.showerror("Import Failed", f"Error importing file:\n{e}")  
    
    # Display stock price chart.
    def display_chart(self):
        symbol = self.stockList.get(self.stockList.curselection())
        display_stock_chart(self.stock_list,symbol)


def main():
        app = StockApp()
        

if __name__ == "__main__":
    # execute only if run as a script
    main()