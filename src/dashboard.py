import customtkinter as ctk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

plt.style.use('dark_background')

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E1E28")
        self.pack(fill=ctk.BOTH, expand=True)

        self.header_label = ctk.CTkLabel(self, text="Analysis Results", font=("Helvetica", 20, "bold"), text_color="#F25858")
        self.header_label.pack(pady=10)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        self.chart_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.chart_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.indicators_frame = ctk.CTkFrame(self.content_frame, fg_color="#2D3B45", corner_radius=10)
        self.indicators_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=20)

        self.ma_var = ctk.StringVar()
        self.rsi_var = ctk.StringVar()
        self.trend_var = ctk.StringVar()
        self.macd_var = ctk.StringVar()
        self.pct_change_var = ctk.StringVar()
        self.accuracy_var = ctk.StringVar()

        self._setup_indicators_ui()

    def _setup_indicators_ui(self):
        ctk.CTkLabel(self.indicators_frame, text="Indicator Summary", font=("Helvetica", 16, "bold"), text_color="white").pack(pady=(15,20), padx=20)

        ctk.CTkLabel(self.indicators_frame, text="Price Change:", font=("Helvetica", 12, "bold"), text_color="#A0A0A0").pack(anchor=ctk.W, padx=20)
        ctk.CTkLabel(self.indicators_frame, textvariable=self.pct_change_var, text_color="white", font=("Helvetica", 13)).pack(anchor=ctk.W, pady=(0, 15), padx=20)

        ctk.CTkLabel(self.indicators_frame, text="Moving Average:", font=("Helvetica", 12, "bold"), text_color="#A0A0A0").pack(anchor=ctk.W, padx=20)
        ctk.CTkLabel(self.indicators_frame, textvariable=self.ma_var, text_color="white", font=("Helvetica", 13)).pack(anchor=ctk.W, pady=(0, 15), padx=20)

        ctk.CTkLabel(self.indicators_frame, text="RSI:", font=("Helvetica", 12, "bold"), text_color="#A0A0A0").pack(anchor=ctk.W, padx=20)
        ctk.CTkLabel(self.indicators_frame, textvariable=self.rsi_var, text_color="white", font=("Helvetica", 13)).pack(anchor=ctk.W, pady=(0, 15), padx=20)

        ctk.CTkLabel(self.indicators_frame, text="MACD:", font=("Helvetica", 12, "bold"), text_color="#A0A0A0").pack(anchor=ctk.W, padx=20)
        ctk.CTkLabel(self.indicators_frame, textvariable=self.macd_var, text_color="white", font=("Helvetica", 13)).pack(anchor=ctk.W, pady=(0, 15), padx=20)

        ctk.CTkLabel(self.indicators_frame, text="Prediction:", font=("Helvetica", 12, "bold"), text_color="#A0A0A0").pack(anchor=ctk.W, padx=20)
        # Store label widget so we can change the color dynamically
        self.prediction_val_label = ctk.CTkLabel(self.indicators_frame, textvariable=self.trend_var, font=("Helvetica", 16, "bold"), text_color="white")
        self.prediction_val_label.pack(anchor=ctk.W, pady=(0, 15), padx=20)
        
        ctk.CTkLabel(self.indicators_frame, text="Model Accuracy:", font=("Helvetica", 12, "bold"), text_color="#A0A0A0").pack(anchor=ctk.W, padx=20)
        ctk.CTkLabel(self.indicators_frame, textvariable=self.accuracy_var, text_color="#32CD32", font=("Helvetica", 14, "bold")).pack(anchor=ctk.W, pady=(0, 15), padx=20)

    def displayChart(self, data: pd.DataFrame, symbol: str):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(4, 3), dpi=100)
        fig.tight_layout()
        fig.patch.set_facecolor('#1E1E28') 
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1E1E28')
        
        ax.spines['bottom'].set_color('#555555')
        ax.spines['top'].set_color('#555555') 
        ax.spines['right'].set_color('#555555')
        ax.spines['left'].set_color('#555555')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        close_data = data['Close']
        if isinstance(close_data, pd.DataFrame):
            close_data = close_data.iloc[:, 0]

        ax.plot(data.index, close_data, label=f"{symbol} Price", color="#4D96FF")
        if 'MA' in data.columns:
            ax.plot(data.index, data['MA'], label='Moving Average', color='#FF6B6B')
            
        ax.set_title(f"{symbol} Stock Price")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend(facecolor='#2D3B45', edgecolor="#2D3B45", labelcolor="white")
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def displayIndicators(self, ma: float, rsi: float, macd: float, pct_change: float, accuracy: float = 0.0):
        self.ma_var.set(f"{ma:.2f}")
        self.rsi_var.set(f"{rsi:.2f}")
        self.macd_var.set(f"{macd:.2f}")
        self.accuracy_var.set(f"{accuracy * 100:.2f}%")
        
        sign = "+" if pct_change > 0 else ""
        self.pct_change_var.set(f"{sign}{pct_change:.2f}%")

    def displayPrediction(self, trend: str):
        self.trend_var.set(trend)
        if trend.lower() == "uptrend":
            self.prediction_val_label.configure(text_color="#32CD32") # Green
        elif trend.lower() == "downtrend":
            self.prediction_val_label.configure(text_color="#E84545") # Red
        else:
            self.prediction_val_label.configure(text_color="white")