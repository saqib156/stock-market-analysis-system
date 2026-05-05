from dataclasses import dataclass
from typing import Optional

@dataclass
class Analysis:
    """
    Role: Represents one analysis record
    """
    symbol: str
    start_date: str
    end_date: str
    moving_average: float
    rsi: float
    macd: float
    pct_change: float
    prediction: str
    accuracy: float = 0.0
    id: Optional[int] = None  # Added for database retrieval
