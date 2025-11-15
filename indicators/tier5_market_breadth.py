"""
Tier 5 - Market Breadth & Institutional Tools
Market-wide indicators: Put/Call, High-Low Index, A/D Line, TRIN, TICK, VIX
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class MarketBreadthIndicators:
    """Market breadth and institutional indicators - Tier 5"""
    
    @staticmethod
    def fetch_put_call_ratio() -> float:
        """Fetch current Put/Call ratio from CBOE"""
        try:
            # Approximate using VIX options volume
            vix = yf.Ticker("^VIX")
            options = vix.option_chain()
            put_volume = options.puts['volume'].sum()
            call_volume = options.calls['volume'].sum()
            return put_volume / call_volume if call_volume > 0 else 1.0
        except:
            return 1.0  # Neutral default
    
    @staticmethod
    def calculate_high_low_index(df: pd.DataFrame, constituents: list, period: int = 10) -> pd.DataFrame:
        """
        High-Low Index (for index constituents).
        Args:
            df: DataFrame for index
            constituents: List of ticker symbols
            period: Period for new highs/lows
        """
        try:
            new_highs = 0
            new_lows = 0
            
            for ticker in constituents[:50]:  # Sample for performance
                try:
                    data = yf.Ticker(ticker).history(period=f"{period}d")
                    if len(data) > 0:
                        # Use float() to ensure scalar comparison
                        if float(data['Close'].iloc[-1]) == float(data['High'].max()):
                            new_highs += 1
                        if float(data['Close'].iloc[-1]) == float(data['Low'].min()):
                            new_lows += 1
                except:
                    continue
            
            total = new_highs + new_lows
            df['High_Low_Index'] = (new_highs / total * 100) if total > 0 else 50
        except:
            df['High_Low_Index'] = 50  # Neutral
        
        return df
    
    @staticmethod
    def calculate_advance_decline_line(df: pd.DataFrame, market_data: Dict = None) -> pd.DataFrame:
        """
        Advance/Decline Line for market breadth.
        Args:
            df: DataFrame for index
            market_data: Dict with 'advances' and 'declines' counts
        """
        if market_data:
            advances = market_data.get('advances', 0)
            declines = market_data.get('declines', 0)
            ad_diff = advances - declines
            
            if 'AD_Line' not in df.columns:
                df['AD_Line'] = ad_diff
            else:
                df['AD_Line'] = df['AD_Line'].iloc[-1] + ad_diff
        else:
            # Estimate from price action
            df['AD_Line'] = (df['Close'].pct_change() > 0).cumsum()
        
        return df
    
    @staticmethod
    def calculate_trin(advancing: int, declining: int, 
                      adv_volume: float, dec_volume: float) -> float:
        """
        TRIN Index (Arms Index).
        TRIN = (Advancing / Declining) / (Adv Volume / Dec Volume)
        """
        if declining == 0 or dec_volume == 0:
            return 1.0
        
        ad_ratio = advancing / declining
        volume_ratio = adv_volume / dec_volume
        
        return ad_ratio / volume_ratio if volume_ratio > 0 else 1.0
    
    @staticmethod
    def fetch_vix(df: pd.DataFrame) -> pd.DataFrame:
        """Fetch VIX (volatility index) data"""
        try:
            vix = yf.download("^VIX", period="1y", progress=False)
            if len(vix) > 0:
                # Align VIX with main dataframe
                df['VIX'] = vix['Close'].reindex(df.index, method='ffill')
        except:
            df['VIX'] = 20.0  # Long-term average
        
        return df
    
    @staticmethod
    def estimate_dark_pool_volume(df: pd.DataFrame) -> pd.DataFrame:
        """
        Estimate dark pool volume (requires special data feed).
        Using volume spikes as proxy.
        """
        avg_volume = df['Volume'].rolling(window=20).mean()
        volume_ratio = df['Volume'] / avg_volume
        
        # Estimate: volume spikes without price movement = potential dark pool
        price_change = df['Close'].pct_change().abs()
        
        df['Dark_Pool_Estimate'] = volume_ratio * (1 - price_change * 100)
        df['Dark_Pool_Estimate'] = df['Dark_Pool_Estimate'].clip(lower=0)
        
        return df
    
    @staticmethod
    def calculate_all_breadth(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all market breadth indicators"""
        df = MarketBreadthIndicators.fetch_vix(df)
        df = MarketBreadthIndicators.estimate_dark_pool_volume(df)
        df = MarketBreadthIndicators.calculate_advance_decline_line(df)
        
        # Add Put/Call ratio as constant (fetch separately)
        try:
            df['Put_Call_Ratio'] = MarketBreadthIndicators.fetch_put_call_ratio()
        except:
            df['Put_Call_Ratio'] = 1.0
        
        return df
