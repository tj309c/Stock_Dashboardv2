"""
Tier 3 - Volume & Order Flow Indicators
Volume analysis: Profile, VWMA, A/D Line, PVT, EOM, Force Index, Volume Oscillator
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class VolumeIndicators:
    """Volume and order flow indicators - Tier 3"""
    
    @staticmethod
    def calculate_volume_profile(df: pd.DataFrame, 
                                 bins: int = 50,
                                 period: str = 'full') -> pd.DataFrame:
        """
        Volume Profile (VRVP - Visible Range Volume Profile).
        Args:
            df: DataFrame with 'Close', 'Volume' columns
            bins: Number of price bins
            period: 'full', 'session', or number of bars
        """
        if period == 'full':
            data = df
        elif period == 'session':
            # Use last session (today)
            data = df[df.index.date == df.index[-1].date()]
        elif isinstance(period, int):
            data = df.tail(period)
        else:
            data = df
        
        # Create price bins
        price_min = data['Close'].min()
        price_max = data['Close'].max()
        price_range = np.linspace(price_min, price_max, bins)
        
        # Calculate volume at each price level
        volume_profile = []
        for i in range(len(price_range) - 1):
            mask = (data['Close'] >= price_range[i]) & (data['Close'] < price_range[i+1])
            volume_at_level = data.loc[mask, 'Volume'].sum()
            volume_profile.append({
                'price': (price_range[i] + price_range[i+1]) / 2,
                'volume': volume_at_level
            })
        
        profile_df = pd.DataFrame(volume_profile)
        
        # Find POC (Point of Control) - price level with highest volume
        if not profile_df.empty:
            poc_idx = profile_df['volume'].idxmax()
            poc_price = profile_df.loc[poc_idx, 'price']
            df['Volume_POC'] = poc_price
            
            # Value Area (70% of volume)
            total_volume = profile_df['volume'].sum()
            profile_df = profile_df.sort_values('volume', ascending=False)
            cumsum = profile_df['volume'].cumsum()
            value_area = profile_df[cumsum <= 0.7 * total_volume]
            
            df['Volume_VAH'] = value_area['price'].max()  # Value Area High
            df['Volume_VAL'] = value_area['price'].min()  # Value Area Low
        
        return df
    
    @staticmethod
    def calculate_vwma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Volume Weighted Moving Average (VWMA).
        Args:
            df: DataFrame with 'Close', 'Volume' columns
            period: VWMA period
        """
        df['VWMA'] = (df['Close'] * df['Volume']).rolling(window=period).sum() / \
                     df['Volume'].rolling(window=period).sum()
        return df
    
    @staticmethod
    def calculate_accumulation_distribution(df: pd.DataFrame) -> pd.DataFrame:
        """
        Accumulation/Distribution Line (A/D Line).
        Args:
            df: DataFrame with OHLCV data
        """
        mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        mfm = mfm.fillna(0)
        mfv = mfm * df['Volume']
        df['AD_Line'] = mfv.cumsum()
        
        return df
    
    @staticmethod
    def calculate_pvt(df: pd.DataFrame) -> pd.DataFrame:
        """
        Price Volume Trend (PVT).
        Args:
            df: DataFrame with 'Close', 'Volume' columns
        """
        price_change = df['Close'].pct_change()
        pvt = (price_change * df['Volume']).cumsum()
        df['PVT'] = pvt
        
        return df
    
    @staticmethod
    def calculate_eom(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Ease of Movement (EOM).
        Args:
            df: DataFrame with OHLCV data
            period: Smoothing period
        """
        distance = (df['High'] + df['Low']) / 2 - (df['High'].shift() + df['Low'].shift()) / 2
        box_ratio = (df['Volume'] / 1000000) / (df['High'] - df['Low'])
        
        emv = distance / box_ratio
        df['EOM'] = emv.rolling(window=period).mean()
        
        return df
    
    @staticmethod
    def calculate_force_index(df: pd.DataFrame, period: int = 13) -> pd.DataFrame:
        """
        Force Index.
        Args:
            df: DataFrame with 'Close', 'Volume' columns
            period: EMA smoothing period
        """
        force = df['Close'].diff() * df['Volume']
        df['Force_Index'] = force.ewm(span=period, adjust=False).mean()
        
        return df
    
    @staticmethod
    def calculate_volume_oscillator(df: pd.DataFrame, 
                                    short_period: int = 5,
                                    long_period: int = 10) -> pd.DataFrame:
        """
        Volume Oscillator.
        Args:
            df: DataFrame with 'Volume' column
            short_period: Short EMA period
            long_period: Long EMA period
        """
        short_ema = df['Volume'].ewm(span=short_period, adjust=False).mean()
        long_ema = df['Volume'].ewm(span=long_period, adjust=False).mean()
        
        df['Volume_Oscillator'] = ((short_ema - long_ema) / long_ema) * 100
        
        return df
    
    @staticmethod
    def calculate_klinger_oscillator(df: pd.DataFrame,
                                     short: int = 34,
                                     long: int = 55,
                                     signal: int = 13) -> pd.DataFrame:
        """
        Klinger Oscillator.
        Args:
            df: DataFrame with OHLCV data
        """
        # Trend direction
        hlc = (df['High'] + df['Low'] + df['Close']) / 3
        trend = pd.Series(0, index=df.index)
        trend[hlc > hlc.shift()] = 1
        trend[hlc < hlc.shift()] = -1
        
        # Volume Force
        dm = df['High'] - df['Low']
        cm = dm.cumsum()
        vf = df['Volume'] * trend * np.abs(2 * dm / cm - 1) * 100
        
        # Klinger Oscillator
        ko = vf.ewm(span=short, adjust=False).mean() - vf.ewm(span=long, adjust=False).mean()
        df['Klinger_Oscillator'] = ko
        df['Klinger_Signal'] = ko.ewm(span=signal, adjust=False).mean()
        
        return df
    
    @staticmethod
    def calculate_all_volume(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all volume indicators at once."""
        df = VolumeIndicators.calculate_volume_profile(df)
        df = VolumeIndicators.calculate_vwma(df)
        df = VolumeIndicators.calculate_accumulation_distribution(df)
        df = VolumeIndicators.calculate_pvt(df)
        df = VolumeIndicators.calculate_eom(df)
        df = VolumeIndicators.calculate_force_index(df)
        df = VolumeIndicators.calculate_volume_oscillator(df)
        df = VolumeIndicators.calculate_klinger_oscillator(df)
        
        return df
