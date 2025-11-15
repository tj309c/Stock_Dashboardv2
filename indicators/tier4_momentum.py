"""
Tier 4 - Momentum & Volatility Indicators
Specialized momentum: BB %B/Bandwidth, ROC, TRIX, Chande, DPO, Coppock, Connors RSI, Williams %R
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MomentumIndicators:
    """Momentum and volatility indicators - Tier 4"""
    
    @staticmethod
    def calculate_roc(df: pd.DataFrame, period: int = 12) -> pd.DataFrame:
        """Rate of Change (ROC)"""
        df['ROC'] = ((df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)) * 100
        return df
    
    @staticmethod
    def calculate_trix(df: pd.DataFrame, period: int = 15) -> pd.DataFrame:
        """TRIX - Triple Exponential Average"""
        ema1 = df['Close'].ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        ema3 = ema2.ewm(span=period, adjust=False).mean()
        df['TRIX'] = ((ema3 - ema3.shift()) / ema3.shift()) * 100
        return df
    
    @staticmethod
    def calculate_chande_momentum(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Chande Momentum Oscillator"""
        delta = df['Close'].diff()
        up = delta.where(delta > 0, 0).rolling(window=period).sum()
        down = -delta.where(delta < 0, 0).rolling(window=period).sum()
        df['CMO'] = 100 * (up - down) / (up + down)
        return df
    
    @staticmethod
    def calculate_dpo(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Detrended Price Oscillator"""
        sma = df['Close'].rolling(window=period).mean()
        shift_period = int(period / 2) + 1
        df['DPO'] = df['Close'].shift(shift_period) - sma
        return df
    
    @staticmethod
    def calculate_coppock(df: pd.DataFrame, 
                         wma_period: int = 10,
                         roc1: int = 14,
                         roc2: int = 11) -> pd.DataFrame:
        """Coppock Curve"""
        roc_1 = ((df['Close'] - df['Close'].shift(roc1)) / df['Close'].shift(roc1)) * 100
        roc_2 = ((df['Close'] - df['Close'].shift(roc2)) / df['Close'].shift(roc2)) * 100
        df['Coppock'] = (roc_1 + roc_2).rolling(window=wma_period).mean()
        return df
    
    @staticmethod
    def calculate_connors_rsi(df: pd.DataFrame) -> pd.DataFrame:
        """Connors RSI (combination of RSI, UpDown Length, ROC)"""
        # Standard RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=3).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=3).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # UpDown Length RSI
        streak = pd.Series(0, index=df.index)
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                streak.iloc[i] = max(streak.iloc[i-1], 0) + 1
            elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                streak.iloc[i] = min(streak.iloc[i-1], 0) - 1
        
        streak_gain = streak.where(streak > 0, 0).rolling(window=2).mean()
        streak_loss = -streak.where(streak < 0, 0).rolling(window=2).mean()
        streak_rs = streak_gain / streak_loss
        udl_rsi = 100 - (100 / (1 + streak_rs))
        
        # ROC RSI
        roc = ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1)) * 100
        roc_rank = roc.rolling(window=100).apply(lambda x: pd.Series(x).rank().iloc[-1])
        roc_rsi = (roc_rank / 100) * 100
        
        # Connors RSI
        df['Connors_RSI'] = (rsi + udl_rsi + roc_rsi) / 3
        return df
    
    @staticmethod
    def calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Williams %R"""
        high_max = df['High'].rolling(window=period).max()
        low_min = df['Low'].rolling(window=period).min()
        df['Williams_R'] = -100 * (high_max - df['Close']) / (high_max - low_min)
        return df
    
    @staticmethod
    def calculate_all_momentum(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all momentum indicators"""
        df = MomentumIndicators.calculate_roc(df)
        df = MomentumIndicators.calculate_trix(df)
        df = MomentumIndicators.calculate_chande_momentum(df)
        df = MomentumIndicators.calculate_dpo(df)
        df = MomentumIndicators.calculate_coppock(df)
        df = MomentumIndicators.calculate_connors_rsi(df)
        df = MomentumIndicators.calculate_williams_r(df)
        return df
