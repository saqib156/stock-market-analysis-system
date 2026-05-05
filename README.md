# stock-market-analysis-system
A Python-based desktop application for financial market analysis using technical indicators and LSTM-based trend prediction.
Stock Market Analysis System

A desktop application built using Python that allows users to analyse financial assets such as stocks, commodities, forex, and indices. The system provides technical indicators, visualisations, and AI-based trend predictions using an LSTM model.

## Features

- Historical data retrieval using Yahoo Finance API  
- Technical indicators:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Moving Average
- LSTM-based machine learning prediction (Uptrend / Downtrend)
- Interactive charts using Matplotlib
- Save, view, delete, and compare past analyses
- GUI built with CustomTkinter
- Multi-threaded processing for smooth performance

## Tech Stack: 
- Python
- Pandas, NumPy
- TensorFlow / Keras (LSTM Model)
- Scikit-learn
- Matplotlib
- CustomTkinter
- SQLite
- yfinance API 

## Installation & Setup: 
     
git clone https://github.com/your-username/stock-market-analysis-system.git             

cd stock-market-analysis-system          
    
pip install -r requirements.txt
python main.py
