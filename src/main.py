import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import threading
from datetime import datetime

from models import Analysis
from database import DatabaseManager
from data_fetcher import StockDataFetcher
from analyzer import StockAnalyzer
from dashboard import Dashboard

class UserInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Stock Market Analysis System")
        self.geometry("1300x750")  
        self.configure(fg_color="#1E1E28")

        self.db_manager = DatabaseManager()
        self.fetcher = StockDataFetcher()
        self.analyzer = StockAnalyzer()

        self.current_analysis: Analysis = None
        self.current_df: pd.DataFrame = None

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#14141B")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E1E28")
        self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.frames = {}
        
        self._init_sidebar()
        self._init_main_screen()
        self._init_dashboard_screen()
        self._init_past_analyses_screen()
        self._init_help_screen()
        
        self.nav_buttons = {}
        self.nav_buttons["main_screen"] = self.btn_home
        self.nav_buttons["dashboard_screen"] = self.btn_dashboard
        self.nav_buttons["past_analyses"] = self.btn_past
        self.nav_buttons["help_screen"] = self.btn_help

        self.show_frame("main_screen")
        
    def _init_sidebar(self):
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="📊", font=("Helvetica", 40))
        self.logo_label.pack(pady=(30, 20))

        nav_font = ("Helvetica", 16, "bold")
        nav_fg = "transparent"
        nav_text = "#F25858"
        hover_col = "#2D3B45"

        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="Home", font=nav_font, 
                                      fg_color=nav_fg, text_color=nav_text, hover_color=hover_col, anchor="w",
                                      command=lambda: self.show_frame("main_screen"))
        self.btn_home.pack(fill=tk.X, padx=10, pady=5)

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", font=nav_font, 
                                           fg_color=nav_fg, text_color=nav_text, hover_color=hover_col, anchor="w",
                                           command=lambda: self.show_frame("dashboard_screen"))
        self.btn_dashboard.pack(fill=tk.X, padx=10, pady=5)

        self.btn_past = ctk.CTkButton(self.sidebar_frame, text="Past Analysis", font=nav_font, 
                                      fg_color=nav_fg, text_color=nav_text, hover_color=hover_col, anchor="w",
                                      command=lambda: self.show_frame("past_analyses"))
        self.btn_past.pack(fill=tk.X, padx=10, pady=5)

        self.btn_help = ctk.CTkButton(self.sidebar_frame, text="Help / Glossary", font=nav_font, 
                                      fg_color=nav_fg, text_color=nav_text, hover_color=hover_col, anchor="w",
                                      command=lambda: self.show_frame("help_screen"))
        self.btn_help.pack(fill=tk.X, padx=10, pady=5)


    def _init_main_screen(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames["main_screen"] = frame

        title = ctk.CTkLabel(frame, text="Stock Market Analysis System", font=("Helvetica", 24, "bold"), text_color="#F25858")
        title.pack(pady=(40, 40))

        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(pady=10)

        label_font = ("Helvetica", 18)
        input_bg = "#2D3B45"

        ctk.CTkLabel(form_frame, text="Asset Category", font=label_font, text_color="#F25858").grid(row=0, column=0, padx=(0, 30), pady=20, sticky=tk.W)
        self.category_entry = ctk.CTkComboBox(form_frame, values=["Stocks", "Commodities", "Currencies (Forex/Crypto)", "Indices"], fg_color=input_bg, border_width=0, text_color="white", dropdown_fg_color=input_bg, width=150, command=self.update_symbol_dropdown)
        self.category_entry.grid(row=0, column=1, padx=5, pady=20)
        self.category_entry.set("Stocks")

        ctk.CTkLabel(form_frame, text="Symbol", font=label_font, text_color="#F25858").grid(row=1, column=0, padx=(0, 30), pady=20, sticky=tk.W)
        self.symbol_entry = ctk.CTkComboBox(form_frame, values=["AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "NVDA"], fg_color=input_bg, border_width=0, text_color="white", dropdown_fg_color=input_bg, width=150)
        self.symbol_entry.grid(row=1, column=1, padx=5, pady=20)
        self.symbol_entry.set("AAPL")

        ctk.CTkLabel(form_frame, text="Start Date", font=label_font, text_color="#F25858").grid(row=2, column=0, padx=(0, 30), pady=20, sticky=tk.W)
        self.start_date_entry = ctk.CTkEntry(form_frame, fg_color=input_bg, border_width=0, text_color="white", width=150)
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=20)
        self.start_date_entry.insert(0, "2023-01-01")

        ctk.CTkLabel(form_frame, text="End Date", font=label_font, text_color="#F25858").grid(row=3, column=0, padx=(0, 30), pady=20, sticky=tk.W)
        self.end_date_entry = ctk.CTkEntry(form_frame, fg_color=input_bg, border_width=0, text_color="white", width=150)
        self.end_date_entry.grid(row=3, column=1, padx=5, pady=20)
        self.end_date_entry.insert(0, "2023-12-31")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(50, 0))

        self.run_btn = ctk.CTkButton(btn_frame, text="Run Analysis", font=("Helvetica", 14), fg_color=input_bg, text_color="white", hover_color="#3e4f5c", corner_radius=10, command=self.getUserInput)
        self.run_btn.grid(row=0, column=0, padx=20)

        past_btn = ctk.CTkButton(btn_frame, text="View Past Analysis", font=("Helvetica", 14), fg_color=input_bg, text_color="white", hover_color="#3e4f5c", corner_radius=10, command=lambda: self.show_frame("past_analyses"))
        past_btn.grid(row=0, column=1, padx=20)

    def update_symbol_dropdown(self, choice):
        if choice == "Stocks":
            values = ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "NVDA"]
        elif choice == "Commodities":
            values = ["GC=F", "SI=F", "CL=F", "NG=F", "ZC=F"]
        elif choice == "Currencies (Forex/Crypto)":
            values = ["EURUSD=X", "GBPUSD=X", "JPY=X", "BTC-USD", "ETH-USD"]
        elif choice == "Indices":
            values = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
        else:
            values = ["AAPL"]
            
        self.symbol_entry.configure(values=values)
        self.symbol_entry.set(values[0])


    def _init_dashboard_screen(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames["dashboard_screen"] = frame

        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill=tk.X, padx=20, pady=(20, 0))

        self.dash_title = ctk.CTkLabel(top_frame, text="Dashboard", font=("Helvetica", 18, "bold"), text_color="#F25858")
        self.dash_title.pack(side=tk.LEFT)

        self.save_btn = ctk.CTkButton(top_frame, text="Save Analysis", font=("Helvetica", 12), fg_color="#2D3B45", text_color="white", hover_color="#3e4f5c", command=self.saveCurrentAnalysis)
        self.save_btn.pack(side=tk.RIGHT)

        # Dynamic container for either 1 dashboard or side-by-side comparison dashboards
        self.dash_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.dash_container.pack(fill=tk.BOTH, expand=True)

    def _init_past_analyses_screen(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames["past_analyses"] = frame

        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ctk.CTkLabel(top_frame, text="Past Analyses", font=("Helvetica", 18, "bold"), text_color="#F25858").pack(side=tk.LEFT)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2D3B45", 
                        foreground="white", 
                        fieldbackground="#2D3B45",
                        borderwidth=0,
                        rowheight=35,
                        font=("Helvetica", 12))
        style.configure("Treeview.Heading", 
                        background="#14141B", 
                        foreground="white", 
                        borderwidth=0,
                        font=("Helvetica", 14, "bold"))
        style.map('Treeview', background=[('selected', '#3e4f5c')])
        
        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        cols = ("ID", "Symbol", "Dates", "Prediction", "Accuracy")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=150 if col == "Dates" else 100, anchor=tk.CENTER)
            
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))

        view_btn = ctk.CTkButton(btn_frame, text="View", font=("Helvetica", 12), fg_color="#2D3B45", text_color="white", hover_color="#3e4f5c", command=self.viewSelectedAnalysis)
        view_btn.pack(side=tk.LEFT, padx=10)

        compare_btn = ctk.CTkButton(btn_frame, text="Compare", font=("Helvetica", 12), fg_color="#2D3B45", text_color="white", hover_color="#3e4f5c", command=self.compareSelectedAnalyses)
        compare_btn.pack(side=tk.LEFT, padx=10)

        del_btn = ctk.CTkButton(btn_frame, text="Delete", font=("Helvetica", 12), fg_color="#2D3B45", text_color="white", hover_color="#3e4f5c", command=self.deleteSelectedAnalysis)
        del_btn.pack(side=tk.LEFT, padx=10)

    def _init_help_screen(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames["help_screen"] = frame

        title = ctk.CTkLabel(frame, text="Educational Glossary", font=("Helvetica", 24, "bold"), text_color="#F25858")
        title.pack(pady=(40, 20), anchor=tk.W, padx=40)

        scroll_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        def create_card(parent, title_text, desc_text):
            card = ctk.CTkFrame(parent, fg_color="#2D3B45", corner_radius=10)
            card.pack(fill=tk.X, pady=10, padx=20)
            
            t_lbl = ctk.CTkLabel(card, text=title_text, font=("Helvetica", 16, "bold"), text_color="#F25858")
            t_lbl.pack(anchor=tk.W, padx=20, pady=(15, 5))
            
            d_lbl = ctk.CTkLabel(card, text=desc_text, font=("Helvetica", 13), text_color="white", justify=tk.LEFT, wraplength=800)
            d_lbl.pack(anchor=tk.W, padx=20, pady=(0, 15))

        create_card(scroll_frame, "RSI (Relative Strength Index)", 
                    "RSI is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100. "
                    "Typically, an RSI above 70 indicates that a stock is 'Overbought' and may fall soon. An RSI below 30 indicates "
                    "that it is 'Oversold' and might see an upcoming bounce.")
                    
        create_card(scroll_frame, "MACD (Moving Average Convergence Divergence)", 
                    "MACD tracks the relationship between two moving averages (usually 12-day and 26-day). "
                    "When the MACD is positive, momentum is generally bullish. When the short-term line crosses "
                    "above the long-term line, it's considered a Buy signal. A cross below is a Sell signal.")
                    
        create_card(scroll_frame, "Moving Average (MA)", 
                    "The Simple Moving Average smooths out price data by creating a constantly updated average price over a specific period (like 20 days). "
                    "It helps cut down the 'noise' of rapid daily price fluctuations, making it easier to see the true underlying trend.")
                    
        create_card(scroll_frame, "LSTM Neural Network Prediction", 
                    "We use a Long Short-Term Memory (LSTM) deep learning architecture instead of basic tree algorithms. "
                    "By looking at historical indicator data in 'sequences' (like 10-day overlapping windows), the LSTM retains a memory "
                    "of complex patterns leading up to today before predicting whether tomorrow will be an Uptrend or Downtrend!")
                    
        create_card(scroll_frame, "Commodities", 
                    "Physical goods that can be bought or sold. On Yahoo Finance, these often trade as futures and end with '=F'. "
                    "Examples included by default are GC=F (Gold), SI=F (Silver), CL=F (Crude Oil), NG=F (Natural Gas), and ZC=F (Corn).")
                    
        create_card(scroll_frame, "Currencies & Forex", 
                    "Forex (Foreign Exchange) represents the fluctuating exchange rates between two national currencies, typically ending in '=X'. "
                    "Examples include EURUSD=X (Euros to US Dollars) and GBPUSD=X (British Pounds to US Dollars). Cryptocurrency pairs like BTC-USD (Bitcoin) operate similarly.")

        create_card(scroll_frame, "Market Indices", 
                    "An index tracks the performance of a group of stocks representing a segment of the market, usually starting with '^'. "
                    "Examples include ^GSPC (S&P 500), ^DJI (Dow Jones), and ^IXIC (NASDAQ).")


    def show_frame(self, frame_name):
        for f in self.frames.values():
            f.pack_forget()
            
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color="#2D3B45" if name == frame_name else "transparent")

        if frame_name == "past_analyses":
            self.refresh_past_analyses_list()
            
        self.frames[frame_name].pack(fill=tk.BOTH, expand=True)

    # --- Core Workflow Methods ---

    def getUserInput(self):
        symbol = self.symbol_entry.get().strip().upper()
        category = self.category_entry.get().strip()
        start = self.start_date_entry.get().strip()
        end = self.end_date_entry.get().strip()

        # --- Category validation ---
        valid_categories = ["Stocks", "Commodities", "Currencies (Forex/Crypto)", "Indices"]
        if category not in valid_categories:
            messagebox.showerror(
                "Invalid Asset Category",
                f"'{category}' is not a recognised category.\n"
                f"Please choose one of: {', '.join(valid_categories)}."
            )
            return

        if not symbol or not start or not end:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # --- Strict allowlist validation per category ---
        valid_symbols = {
            "Stocks":                    ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "NVDA"],
            "Commodities":               ["GC=F", "SI=F", "CL=F", "NG=F", "ZC=F"],
            "Currencies (Forex/Crypto)": ["EURUSD=X", "GBPUSD=X", "JPY=X", "BTC-USD", "ETH-USD"],
            "Indices":                   ["^GSPC", "^DJI", "^IXIC", "^RUT"],
        }
        allowed = valid_symbols.get(category, [])
        if symbol not in allowed:
            messagebox.showerror(
                "Invalid Symbol",
                f"'{symbol}' is not a valid symbol for {category}.\n\n"
                f"Valid symbols are:\n  {', '.join(allowed)}\n\n"
                f"Please select or type one of the above exactly."
            )
            return

        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            if start_dt >= today and end_dt >= today:
                messagebox.showerror("Invalid Date Range", "Both dates are in the future.\nPlease choose a Start Date and End Date before the current date.")
                return
            if start_dt >= end_dt:
                messagebox.showerror("Error", "End Date must be later than Start Date.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid Date format. Please use YYYY-MM-DD.")
            return

        self.run_btn.configure(text="Loading...", state="disabled")

        def _fetch_and_analyze():
            df = self.fetcher.fetchHistoricalData(symbol, start, end)
            
            def _update_ui():
                self.run_btn.configure(text="Run Analysis", state="normal")
                
                if df is None or df.empty:
                    messagebox.showerror("Error", f"Could not retrieve data for {symbol}.")
                    return

                results = self.analyzer.analyzeStock(df)

                self.current_analysis = Analysis(
                    symbol=symbol,
                    start_date=start,
                    end_date=end,
                    moving_average=results["moving_average"],
                    rsi=results["rsi"],
                    macd=results["macd"],
                    pct_change=results["pct_change"],
                    prediction=results["prediction"],
                    accuracy=results.get("accuracy", 0.0)
                )
                self.current_df = df
                self.showDashboard()
                
            self.after(0, _update_ui)
            
        threading.Thread(target=_fetch_and_analyze, daemon=True).start()

    def showDashboard(self):
        if not self.current_analysis or self.current_df is None:
            return

        self.dash_title.configure(text=f"Dashboard: {self.current_analysis.symbol} ({self.current_analysis.start_date} to {self.current_analysis.end_date})")
        self.save_btn.configure(state="normal")
        
        for widget in self.dash_container.winfo_children():
            widget.destroy()

        dash = Dashboard(self.dash_container)
        dash.header_label.configure(text="Analysis Results")
        
        dash.displayChart(self.current_df, self.current_analysis.symbol)
        
        dash.displayIndicators(
            self.current_analysis.moving_average, 
            self.current_analysis.rsi,
            self.current_analysis.macd,
            self.current_analysis.pct_change,
            self.current_analysis.accuracy
        )
        dash.displayPrediction(self.current_analysis.prediction)

        self.show_frame("dashboard_screen")

    def refresh_past_analyses_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        analyses = self.db_manager.getPastAnalyses()
        
        for a in analyses:
            self.tree.insert("", "end", values=(
                a.id, 
                a.symbol, 
                f"{a.start_date} - {a.end_date}", 
                a.prediction,
                f"{a.accuracy * 100:.2f}%"
            ))

    def saveCurrentAnalysis(self):
        if self.current_analysis:
            self.db_manager.saveAnalysis(self.current_analysis)
            messagebox.showinfo("Success", "Analysis saved successfully.")

    def viewSelectedAnalysis(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an analysis to view.")
            return
        
        item = self.tree.item(selected[0])
        a_id = item['values'][0]
        
        analysis = self.db_manager.getAnalysisById(a_id)
        if not analysis:
            return
            
        def _fetch_view():
            df = self.fetcher.fetchHistoricalData(analysis.symbol, analysis.start_date, analysis.end_date)
            def _update():
                if df is None:
                    messagebox.showwarning("Warning", "Could not fetch historical data to display the chart for this saved analysis.")
                    return
                self.analyzer.analyzeStock(df)
                self.current_analysis = analysis
                self.current_df = df
                self.showDashboard()
            self.after(0, _update)
            
        threading.Thread(target=_fetch_view, daemon=True).start()

    def compareSelectedAnalyses(self):
        selected = self.tree.selection()
        if len(selected) != 2:
            messagebox.showwarning("Warning", "Please select exactly TWO analyses to compare (use CTRL+Click).")
            return
            
        id1 = self.tree.item(selected[0])['values'][0]
        id2 = self.tree.item(selected[1])['values'][0]
        
        a1 = self.db_manager.getAnalysisById(id1)
        a2 = self.db_manager.getAnalysisById(id2)
        
        for widget in self.dash_container.winfo_children():
            widget.destroy()

        self.dash_title.configure(text=f"Comparing: {a1.symbol} vs {a2.symbol}")
        self.save_btn.configure(state="disabled")

        dash1 = Dashboard(self.dash_container)
        dash1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=0)
        dash1.header_label.configure(text=f"Loading {a1.symbol}...")
        
        dash2 = Dashboard(self.dash_container)
        dash2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=0)
        dash2.header_label.configure(text=f"Loading {a2.symbol}...")

        self.show_frame("dashboard_screen")

        def _fetch_compare():
            df1 = self.fetcher.fetchHistoricalData(a1.symbol, a1.start_date, a1.end_date)
            df2 = self.fetcher.fetchHistoricalData(a2.symbol, a2.start_date, a2.end_date)
            
            def _update():
                if df1 is not None and not df1.empty:
                    dash1.header_label.configure(text=f"{a1.symbol} ({a1.start_date} to {a1.end_date})")
                    self.analyzer.analyzeStock(df1) 
                    dash1.displayChart(df1, a1.symbol)
                    dash1.displayIndicators(a1.moving_average, a1.rsi, a1.macd, a1.pct_change, a1.accuracy)
                    dash1.displayPrediction(a1.prediction)
                else:
                    dash1.header_label.configure(text=f"Error loading {a1.symbol}")

                if df2 is not None and not df2.empty:
                    dash2.header_label.configure(text=f"{a2.symbol} ({a2.start_date} to {a2.end_date})")
                    self.analyzer.analyzeStock(df2)
                    dash2.displayChart(df2, a2.symbol)
                    dash2.displayIndicators(a2.moving_average, a2.rsi, a2.macd, a2.pct_change, a2.accuracy)
                    dash2.displayPrediction(a2.prediction)
                else:
                    dash2.header_label.configure(text=f"Error loading {a2.symbol}")
                    
            self.after(0, _update)
            
        threading.Thread(target=_fetch_compare, daemon=True).start()
        
    def deleteSelectedAnalysis(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        for s in selected:
            item = self.tree.item(s)
            a_id = item['values'][0]
            self.db_manager.deleteAnalysis(a_id)
            self.tree.delete(s)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = UserInterface()
    app.mainloop()
