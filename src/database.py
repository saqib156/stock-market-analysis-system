import sqlite3
from models import Analysis
from typing import List, Optional

class DatabaseManager:
    """
    Role: Handles database operations for saving and retrieving historical analyses.
    """
    def __init__(self, db_path="stock_analysis.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                moving_average REAL NOT NULL,
                rsi REAL NOT NULL,
                macd REAL NOT NULL,
                pct_change REAL NOT NULL,
                prediction TEXT NOT NULL
            )
        ''')
        
        # Schema migration: Add accuracy column to existing databases
        try:
            cursor.execute('ALTER TABLE analyses ADD COLUMN accuracy REAL DEFAULT 0.0')
        except sqlite3.OperationalError:
            # Column already exists, safe to ignore
            pass
            
        conn.commit()
        conn.close()

    def saveAnalysis(self, data: Analysis) -> None:
        """
        Saves a new analysis record to the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses (symbol, start_date, end_date, moving_average, rsi, macd, pct_change, prediction, accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data.symbol, data.start_date, data.end_date, data.moving_average, data.rsi, data.macd, data.pct_change, data.prediction, data.accuracy))
        conn.commit()
        conn.close()

    def getPastAnalyses(self) -> List[Analysis]:
        """
        Retrieves all past analyses from the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, symbol, start_date, end_date, moving_average, rsi, macd, pct_change, prediction, accuracy FROM analyses")
        rows = cursor.fetchall()
        conn.close()

        analyses = []
        for row in rows:
            analysis = Analysis(
                id=row[0],
                symbol=row[1],
                start_date=row[2],
                end_date=row[3],
                moving_average=row[4],
                rsi=row[5],
                macd=row[6],
                pct_change=row[7],
                prediction=row[8],
                accuracy=row[9]
            )
            analyses.append(analysis)
        return analyses

    def getAnalysisById(self, id: int) -> Optional[Analysis]:
        """
        Retrieves a specific analysis record by its ID.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, symbol, start_date, end_date, moving_average, rsi, macd, pct_change, prediction, accuracy FROM analyses WHERE id=?", (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Analysis(
                id=row[0],
                symbol=row[1],
                start_date=row[2],
                end_date=row[3],
                moving_average=row[4],
                rsi=row[5],
                macd=row[6],
                pct_change=row[7],
                prediction=row[8],
                accuracy=row[9]
            )
        return None

    def deleteAnalysis(self, id: int) -> None:
        """
        Deletes an analysis record by its ID.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id=?", (id,))
        conn.commit()
        conn.close()
