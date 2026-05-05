import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from typing import Tuple

class StockAnalyzer:
    """
    Role: Performs calculations on stock data and uses Machine Learning for forecasting.
    """
    def __init__(self):
        pass

    def analyzeStock(self, data: pd.DataFrame) -> dict:
        """
        Runs full analysis on the dataframe.
        Returns a dictionary with the results.
        """
        ma = self.calculateMovingAverage(data)
        rsi = self.calculateRSI(data)
        macd = self.calculateMACD(data)
        pct_change = self.calculatePctChange(data)
        
        # ML Prediction logic
        prediction, accuracy = self.predictTrend(data)

        return {
            "moving_average": ma,
            "rsi": rsi,
            "macd": macd,
            "pct_change": pct_change,
            "prediction": prediction,
            "accuracy": accuracy
        }

    def calculateMovingAverage(self, data: pd.DataFrame, period: int = 20) -> float:
        close_col = data['Close']
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
            
        data['MA'] = close_col.rolling(window=period).mean()
        
        latest_ma = data['MA'].iloc[-1] 
        
        if pd.isna(latest_ma):
             latest_ma = close_col.mean()
             
        if isinstance(latest_ma, pd.Series):
             latest_ma = latest_ma.iloc[0]
             
        return float(latest_ma)

    def calculateRSI(self, data: pd.DataFrame, period: int = 14) -> float:
        close_col = data['Close']
        if isinstance(close_col, pd.DataFrame):
             close_col = close_col.iloc[:, 0]
             
        close_delta = close_col.diff()
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        ma_up = up.ewm(com=period - 1, adjust=True, min_periods=period).mean()
        ma_down = down.ewm(com=period - 1, adjust=True, min_periods=period).mean()

        rsi = ma_up / ma_down
        rsi = 100 - (100 / (1 + rsi))
        data['RSI'] = rsi

        latest_rsi = rsi.iloc[-1]
        
        if pd.isna(latest_rsi):
            return 50.0
            
        if isinstance(latest_rsi, pd.Series):
            latest_rsi = latest_rsi.iloc[0]
            
        return float(latest_rsi)

    def calculateMACD(self, data: pd.DataFrame) -> float:
        close_col = data['Close']
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
            
        ema_12 = close_col.ewm(span=12, adjust=False).mean()
        ema_26 = close_col.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        
        data['MACD'] = macd_line

        latest_macd = macd_line.iloc[-1]
        if pd.isna(latest_macd):
            return 0.0
            
        if isinstance(latest_macd, pd.Series):
            latest_macd = latest_macd.iloc[0]
            
        return float(latest_macd)

    def calculatePctChange(self, data: pd.DataFrame) -> float:
        close_col = data['Close']
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
            
        # Filter NaNs or 0s if they exist at exact bounds
        valid_closes = close_col.dropna()
        if len(valid_closes) < 2: 
            return 0.0
            
        start_price = valid_closes.iloc[0]
        end_price = valid_closes.iloc[-1]
        
        if pd.isna(start_price) or start_price == 0: 
            return 0.0
            
        pct_change = ((end_price - start_price) / start_price) * 100
        return float(pct_change)

    def predictTrend(self, data: pd.DataFrame) -> Tuple[str, float]:
        df = data.copy()
        
        close_col = df['Close']
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
            
        df['Returns'] = close_col.pct_change()
        df['MA'] = close_col.rolling(window=20).mean()
        
        delta = close_col.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        rs = up.ewm(com=13, adjust=False).mean() / down.ewm(com=13, adjust=False).mean()
        df['RSI'] = 100 - (100 / (1 + rs))

        # Add MACD as a feature
        ema_12 = close_col.ewm(span=12, adjust=False).mean()
        ema_26 = close_col.ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26

        df = df.dropna()
        
        # Need at least ~50 days to construct sequences and test
        if len(df) < 50: 
            return "Insufficient Data for LSTM", 0.0

        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # Don't train on the very last row as it's the one we are predicting
        historical_data = df.iloc[:-1].copy()
        
        features = ['Returns', 'MA', 'RSI', 'MACD']
        X_raw = historical_data[features].values
        y_raw = historical_data['Target'].values
        
        # Scale data dynamically between 0 and 1
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_scaled = scaler.fit_transform(X_raw)
        
        look_back = 10
        X_seq, y_seq = [], []
        for i in range(len(X_scaled) - look_back):
            X_seq.append(X_scaled[i:(i + look_back)])
            y_seq.append(y_raw[i + look_back])
            
        X_seq = np.array(X_seq)
        y_seq = np.array(y_seq)
        
        if len(X_seq) < 20: 
            return "Insufficient Sequenced Data", 0.0
            
        # 80/20 train test split (no shuffle to maintain temporal order)
        split_idx = int(len(X_seq) * 0.8)
        X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
        y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]
        
        # Build LSTM
        model = Sequential()
        model.add(LSTM(50, return_sequences=False, input_shape=(look_back, len(features))))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        
        # Train
        model.fit(X_train, y_train, epochs=20, batch_size=16, verbose=0)
        
        # Calculate Accuracy on the test data
        loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
        
        # Predict the future directly from the original df (the actual last 'look_back' rows)
        latest_features_raw = df.iloc[-look_back:][features].values
        latest_features_scaled = scaler.transform(latest_features_raw)
        
        latest_seq = np.array([latest_features_scaled])
        prediction_prob = model.predict(latest_seq, verbose=0)[0][0]
        
        result_str = "Uptrend" if prediction_prob > 0.5 else "Downtrend"
        return result_str, float(accuracy)
