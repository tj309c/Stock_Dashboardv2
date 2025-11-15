"""
Tier 2 - Pro Trader Standard Indicators
Advanced indicators: Ichimoku, Fibonacci, Stochastic, CMF, MFI, Donchian, Keltner, ADX, SAR, Pivots
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ProIndicators:
    """Professional trading indicators - Tier 2"""
    
    @staticmethod
    def calculate_ichimoku(df: pd.DataFrame, 
                          tenkan: int = 9, 
                          kijun: int = 26, 
                          senkou: int = 52) -> pd.DataFrame:
        """
        Ichimoku Cloud (Ichimoku Kinko Hyo).
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            tenkan: Conversion line period
            kijun: Base line period
            senkou: Leading span B period
        """
        # Tenkan-sen (Conversion Line)
        high_tenkan = df['High'].rolling(window=tenkan).max()
        low_tenkan = df['Low'].rolling(window=tenkan).min()
        df['Ichimoku_Tenkan'] = (high_tenkan + low_tenkan) / 2
        
        # Kijun-sen (Base Line)
        high_kijun = df['High'].rolling(window=kijun).max()
        low_kijun = df['Low'].rolling(window=kijun).min()
        df['Ichimoku_Kijun'] = (high_kijun + low_kijun) / 2
        
        # Senkou Span A (Leading Span A)
        df['Ichimoku_SpanA'] = ((df['Ichimoku_Tenkan'] + df['Ichimoku_Kijun']) / 2).shift(kijun)
        
        # Senkou Span B (Leading Span B)
        high_senkou = df['High'].rolling(window=senkou).max()
        low_senkou = df['Low'].rolling(window=senkou).min()
        df['Ichimoku_SpanB'] = ((high_senkou + low_senkou) / 2).shift(kijun)
        
        # Chikou Span (Lagging Span)
        df['Ichimoku_Chikou'] = df['Close'].shift(-kijun)
        
        return df
    
    @staticmethod
    def calculate_fibonacci_retracement(df: pd.DataFrame, 
                                       lookback: int = 100) -> pd.DataFrame:
        """
        Fibonacci Retracement levels.
        Args:
            df: DataFrame with 'High', 'Low' columns
            lookback: Period to find swing high/low
        """
        if len(df) < lookback:
            lookback = len(df)
        
        recent_high = df['High'].tail(lookback).max()
        recent_low = df['Low'].tail(lookback).min()
        diff = recent_high - recent_low
        
        # Retracement levels
        df['Fib_0'] = recent_high
        df['Fib_236'] = recent_high - (0.236 * diff)
        df['Fib_382'] = recent_high - (0.382 * diff)
        df['Fib_500'] = recent_high - (0.500 * diff)
        df['Fib_618'] = recent_high - (0.618 * diff)
        df['Fib_786'] = recent_high - (0.786 * diff)
        df['Fib_100'] = recent_low
        
        # Extensions
        df['Fib_Ext_1272'] = recent_high + (0.272 * diff)
        df['Fib_Ext_1618'] = recent_high + (0.618 * diff)
        df['Fib_Ext_2618'] = recent_high + (1.618 * diff)
        
        return df
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, 
                            k_period: int = 14, 
                            d_period: int = 3,
                            smooth: int = 3) -> pd.DataFrame:
        """
        Stochastic Oscillator (%K and %D).
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            k_period: %K period
            d_period: %D smoothing period
            smooth: %K smoothing
        """
        # Raw Stochastic
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        
        stoch_k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        
        # Smooth %K
        df['Stoch_K'] = stoch_k.rolling(window=smooth).mean()
        
        # %D (signal line)
        df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()
        
        return df
    
    @staticmethod
    def calculate_cmf(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Chaikin Money Flow (CMF).
        Args:
            df: DataFrame with OHLCV data
            period: CMF period
        """
        mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        mfm = mfm.fillna(0)
        mfv = mfm * df['Volume']
        
        df['CMF'] = mfv.rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()
        return df
    
    @staticmethod
    def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Money Flow Index (MFI).
        Args:
            df: DataFrame with OHLCV data
            period: MFI period
        """
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        # Positive and negative money flow
        positive_flow = pd.Series(0.0, index=df.index)
        negative_flow = pd.Series(0.0, index=df.index)
        
        for i in range(1, len(df)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                negative_flow.iloc[i] = money_flow.iloc[i]
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        df['MFI'] = mfi
        
        return df
    
    @staticmethod
    def calculate_donchian(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Donchian Channels.
        Args:
            df: DataFrame with 'High', 'Low' columns
            period: Lookback period
        """
        df['Donchian_Upper'] = df['High'].rolling(window=period).max()
        df['Donchian_Lower'] = df['Low'].rolling(window=period).min()
        df['Donchian_Middle'] = (df['Donchian_Upper'] + df['Donchian_Lower']) / 2
        
        return df
    
    @staticmethod
    def calculate_keltner(df: pd.DataFrame, 
                         ema_period: int = 20, 
                         atr_period: int = 10,
                         multiplier: float = 2.0) -> pd.DataFrame:
        """
        Keltner Channels.
        Args:
            df: DataFrame with OHLCV data
            ema_period: EMA period for middle line
            atr_period: ATR period
            multiplier: ATR multiplier for bands
        """
        # Calculate EMA
        df['Keltner_Middle'] = df['Close'].ewm(span=ema_period, adjust=False).mean()
        
        # Calculate ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=atr_period).mean()
        
        # Bands
        df['Keltner_Upper'] = df['Keltner_Middle'] + (multiplier * atr)
        df['Keltner_Lower'] = df['Keltner_Middle'] - (multiplier * atr)
        
        return df
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Average Directional Index (ADX) with +DI and -DI.
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            period: ADX period
        """
        # True Range
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        # Directional Movement
        up_move = df['High'] - df['High'].shift()
        down_move = df['Low'].shift() - df['Low']
        
        plus_dm = pd.Series(0.0, index=df.index)
        minus_dm = pd.Series(0.0, index=df.index)
        
        plus_dm[up_move > down_move] = up_move
        plus_dm[up_move < 0] = 0
        
        minus_dm[down_move > up_move] = down_move
        minus_dm[down_move < 0] = 0
        
        # Smoothed TR and DM
        atr = true_range.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        df['ADX'] = adx
        df['Plus_DI'] = plus_di
        df['Minus_DI'] = minus_di
        
        return df
    
    @staticmethod
    def calculate_parabolic_sar(df: pd.DataFrame, 
                               af_start: float = 0.02, 
                               af_increment: float = 0.02,
                               af_max: float = 0.2) -> pd.DataFrame:
        """
        Parabolic SAR (Stop and Reverse).
        Args:
            df: DataFrame with 'High', 'Low', 'Close' columns
            af_start: Initial acceleration factor
            af_increment: AF increment
            af_max: Maximum AF
        """
        sar = []
        ep = 0
        af = af_start
        trend = 1  # 1 for uptrend, -1 for downtrend
        
        for i in range(len(df)):
            if i == 0:
                sar.append(df['Low'].iloc[i])
                ep = df['High'].iloc[i]
            else:
                # Calculate new SAR
                new_sar = sar[-1] + af * (ep - sar[-1])
                
                # Check for trend reversal
                if trend == 1:
                    if df['Low'].iloc[i] < new_sar:
                        trend = -1
                        new_sar = ep
                        ep = df['Low'].iloc[i]
                        af = af_start
                    else:
                        if df['High'].iloc[i] > ep:
                            ep = df['High'].iloc[i]
                            af = min(af + af_increment, af_max)
                else:
                    if df['High'].iloc[i] > new_sar:
                        trend = 1
                        new_sar = ep
                        ep = df['High'].iloc[i]
                        af = af_start
                    else:
                        if df['Low'].iloc[i] < ep:
                            ep = df['Low'].iloc[i]
                            af = min(af + af_increment, af_max)
                
                sar.append(new_sar)
        
        df['PSAR'] = sar
        return df
    
    @staticmethod
    def calculate_pivot_points(df: pd.DataFrame, 
                              pivot_type: str = 'classic') -> pd.DataFrame:
        """
        Pivot Points (Classic, Fibonacci, Camarilla).
        Args:
            df: DataFrame with OHLC data
            pivot_type: 'classic', 'fibonacci', or 'camarilla'
        """
        # Use previous day's data
        prev_high = df['High'].shift(1)
        prev_low = df['Low'].shift(1)
        prev_close = df['Close'].shift(1)
        
        # Pivot Point
        pivot = (prev_high + prev_low + prev_close) / 3
        
        if pivot_type == 'classic':
            df['Pivot'] = pivot
            df['R1'] = 2 * pivot - prev_low
            df['R2'] = pivot + (prev_high - prev_low)
            df['R3'] = prev_high + 2 * (pivot - prev_low)
            df['S1'] = 2 * pivot - prev_high
            df['S2'] = pivot - (prev_high - prev_low)
            df['S3'] = prev_low - 2 * (prev_high - pivot)
            
        elif pivot_type == 'fibonacci':
            df['Pivot'] = pivot
            df['R1'] = pivot + 0.382 * (prev_high - prev_low)
            df['R2'] = pivot + 0.618 * (prev_high - prev_low)
            df['R3'] = pivot + 1.000 * (prev_high - prev_low)
            df['S1'] = pivot - 0.382 * (prev_high - prev_low)
            df['S2'] = pivot - 0.618 * (prev_high - prev_low)
            df['S3'] = pivot - 1.000 * (prev_high - prev_low)
            
        elif pivot_type == 'camarilla':
            df['Pivot'] = prev_close
            df['R1'] = prev_close + 1.1 * (prev_high - prev_low) / 12
            df['R2'] = prev_close + 1.1 * (prev_high - prev_low) / 6
            df['R3'] = prev_close + 1.1 * (prev_high - prev_low) / 4
            df['R4'] = prev_close + 1.1 * (prev_high - prev_low) / 2
            df['S1'] = prev_close - 1.1 * (prev_high - prev_low) / 12
            df['S2'] = prev_close - 1.1 * (prev_high - prev_low) / 6
            df['S3'] = prev_close - 1.1 * (prev_high - prev_low) / 4
            df['S4'] = prev_close - 1.1 * (prev_high - prev_low) / 2
        
        return df
    
    @staticmethod
    def calculate_all_pro(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all pro indicators at once."""
        df = ProIndicators.calculate_ichimoku(df)
        df = ProIndicators.calculate_fibonacci_retracement(df)
        df = ProIndicators.calculate_stochastic(df)
        df = ProIndicators.calculate_cmf(df)
        df = ProIndicators.calculate_mfi(df)
        df = ProIndicators.calculate_donchian(df)
        df = ProIndicators.calculate_keltner(df)
        df = ProIndicators.calculate_adx(df)
        df = ProIndicators.calculate_parabolic_sar(df)
        df = ProIndicators.calculate_pivot_points(df, 'classic')
        
        return df
