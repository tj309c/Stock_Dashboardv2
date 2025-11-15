"""
Tier 1 - Core Technical Indicators
Essential indicators for all traders: SMA, EMA, Bollinger, MACD, RSI, Volume, ATR, VWAP
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CoreIndicators:
    """Core technical indicators - Tier 1"""
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, periods: list = [20, 50, 100, 200]) -> pd.DataFrame:
        """
        Simple Moving Average for multiple periods.
        Args:
            df: DataFrame with 'Close' column
            periods: List of SMA periods
        """
        for period in periods:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, periods: list = [9, 12, 26, 50, 200]) -> pd.DataFrame:
        """
        Exponential Moving Average for multiple periods.
        Args:
            df: DataFrame with 'Close' column
            periods: List of EMA periods
        """
        for period in periods:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        return df
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2.0) -> pd.DataFrame:
        """
        Bollinger Bands with middle (SMA), upper, and lower bands.
        Args:
            df: DataFrame with 'Close' column
            period: Rolling window period
            std: Number of standard deviations
        """
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()
        rolling_std = df['Close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_Middle'] + (std * rolling_std)
        df['BB_Lower'] = df['BB_Middle'] - (std * rolling_std)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_PercentB'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        return df
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        MACD (Moving Average Convergence Divergence) with histogram.
        Args:
            df: DataFrame with 'Close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        """
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        return df
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Relative Strength Index (RSI).
        Args:
            df: DataFrame with 'Close' column
            period: RSI period
        """
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """
        On-Balance Volume (OBV).
        Args:
            df: DataFrame with 'Close' and 'Volume' columns
        """
        obv = []
        obv_value = 0
        
        for i in range(len(df)):
            if i == 0:
                obv.append(df['Volume'].iloc[i])
            else:
                if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                    obv_value += df['Volume'].iloc[i]
                elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                    obv_value -= df['Volume'].iloc[i]
                obv.append(obv_value)
        
        df['OBV'] = obv
        return df
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Average True Range (ATR).
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            period: ATR period
        """
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        df['ATR'] = true_range.rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """
        Volume Weighted Average Price (VWAP).
        Args:
            df: DataFrame with 'High', 'Low', 'Close', 'Volume' columns
        """
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        return df
    
    @staticmethod
    def calculate_anchored_vwap(df: pd.DataFrame, anchor_date: Optional[str] = None) -> pd.DataFrame:
        """
        Anchored VWAP from a specific date.
        Args:
            df: DataFrame with 'High', 'Low', 'Close', 'Volume' columns
            anchor_date: Starting date for VWAP calculation (None = from beginning)
        """
        if anchor_date:
            mask = df.index >= pd.to_datetime(anchor_date)
            df_anchor = df[mask].copy()
        else:
            df_anchor = df.copy()
        
        typical_price = (df_anchor['High'] + df_anchor['Low'] + df_anchor['Close']) / 3
        df.loc[df_anchor.index, 'Anchored_VWAP'] = (
            (typical_price * df_anchor['Volume']).cumsum() / df_anchor['Volume'].cumsum()
        )
        return df
    
    @staticmethod
    def detect_market_hours(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect market hours (9:30 AM - 4:00 PM ET).
        Args:
            df: DataFrame with datetime index
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            return df
        
        # Convert to ET
        df_et = df.copy()
        if df_et.index.tz is None:
            df_et.index = df_et.index.tz_localize('US/Eastern')
        else:
            df_et.index = df_et.index.tz_convert('US/Eastern')
        
        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = df_et.index.hour > 9 or (df_et.index.hour == 9 and df_et.index.minute >= 30)
        market_close = df_et.index.hour < 16
        
        df['Market_Hours'] = market_open & market_close
        df['Pre_Market'] = df_et.index.hour < 9 or (df_et.index.hour == 9 and df_et.index.minute < 30)
        df['After_Hours'] = df_et.index.hour >= 16
        
        return df
    
    @staticmethod
    def calculate_all_core(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all core indicators at once.
        Args:
            df: DataFrame with OHLCV data
        """
        df = CoreIndicators.calculate_sma(df)
        df = CoreIndicators.calculate_ema(df)
        df = CoreIndicators.calculate_bollinger_bands(df)
        df = CoreIndicators.calculate_macd(df)
        df = CoreIndicators.calculate_rsi(df)
        df = CoreIndicators.calculate_obv(df)
        df = CoreIndicators.calculate_atr(df)
        df = CoreIndicators.calculate_vwap(df)
        df = CoreIndicators.detect_market_hours(df)
        
        return df
    
    @staticmethod
    def get_summary(df: pd.DataFrame) -> Dict[str, str]:
        """
        Get summary of core indicators for latest data point.
        """
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        summary = {}
        
        # Trend
        if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
                summary['trend'] = 'Strong Uptrend'
            elif latest['Close'] > latest['SMA_50']:
                summary['trend'] = 'Uptrend'
            elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
                summary['trend'] = 'Strong Downtrend'
            else:
                summary['trend'] = 'Downtrend'
        
        # Momentum (RSI)
        if 'RSI' in df.columns:
            rsi = latest['RSI']
            if rsi > 70:
                summary['momentum'] = 'Overbought'
            elif rsi < 30:
                summary['momentum'] = 'Oversold'
            elif rsi > 50:
                summary['momentum'] = 'Bullish'
            else:
                summary['momentum'] = 'Bearish'
        
        # MACD
        if 'MACD_Histogram' in df.columns:
            if latest['MACD_Histogram'] > 0:
                summary['macd'] = 'Bullish'
            else:
                summary['macd'] = 'Bearish'
        
        # Bollinger Position
        if 'BB_PercentB' in df.columns:
            percentb = latest['BB_PercentB']
            if percentb > 1:
                summary['bollinger'] = 'Above Upper Band'
            elif percentb < 0:
                summary['bollinger'] = 'Below Lower Band'
            else:
                summary['bollinger'] = f'Within Bands ({percentb*100:.0f}%)'
        
        return summary
