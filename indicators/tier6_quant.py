"""
Tier 6 - Quant Indicators
Quantitative analysis: Z-score, Beta, Alpha, Correlation, Sharpe, Sortino, Volatility Cones
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class QuantIndicators:
    """Quantitative indicators - Tier 6"""
    
    @staticmethod
    def calculate_zscore(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Z-score of price (standardized price)"""
        mean = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        df['ZScore'] = (df['Close'] - mean) / std
        return df
    
    @staticmethod
    def calculate_rolling_beta(df: pd.DataFrame, 
                               benchmark_ticker: str = 'SPY',
                               period: int = 60) -> pd.DataFrame:
        """
        Rolling beta vs benchmark.
        Args:
            df: Stock dataframe
            benchmark_ticker: Benchmark symbol (SPY, QQQ, etc.)
            period: Rolling window
        """
        try:
            # Fetch benchmark data
            benchmark = yf.download(benchmark_ticker, start=df.index[0], end=df.index[-1], progress=False)
            
            if len(benchmark) > 0:
                # Align dates
                stock_returns = df['Close'].pct_change()
                bench_returns = benchmark['Close'].reindex(df.index, method='ffill').pct_change()
                
                # Calculate rolling beta
                cov = stock_returns.rolling(window=period).cov(bench_returns)
                bench_var = bench_returns.rolling(window=period).var()
                
                df[f'Beta_{benchmark_ticker}'] = cov / bench_var
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            df[f'Beta_{benchmark_ticker}'] = 1.0
        
        return df
    
    @staticmethod
    def calculate_rolling_alpha(df: pd.DataFrame,
                                benchmark_ticker: str = 'SPY',
                                period: int = 60,
                                risk_free_rate: float = 0.045) -> pd.DataFrame:
        """
        Rolling alpha (excess return over benchmark).
        Alpha = Stock Return - (Risk Free Rate + Beta * (Benchmark Return - Risk Free Rate))
        """
        try:
            benchmark = yf.download(benchmark_ticker, start=df.index[0], end=df.index[-1], progress=False)
            
            if len(benchmark) > 0:
                stock_returns = df['Close'].pct_change().rolling(window=period).mean() * 252
                bench_returns = benchmark['Close'].reindex(df.index, method='ffill').pct_change().rolling(window=period).mean() * 252
                
                beta = df.get(f'Beta_{benchmark_ticker}', 1.0)
                
                df[f'Alpha_{benchmark_ticker}'] = stock_returns - (risk_free_rate + beta * (bench_returns - risk_free_rate))
        except Exception as e:
            logger.error(f"Error calculating alpha: {e}")
            df[f'Alpha_{benchmark_ticker}'] = 0.0
        
        return df
    
    @staticmethod
    def calculate_correlation_matrix(tickers: List[str], period: str = '1y') -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple tickers.
        Args:
            tickers: List of ticker symbols
            period: Time period for data
        """
        try:
            data = yf.download(tickers, period=period, progress=False)['Close']
            returns = data.pct_change().dropna()
            correlation = returns.corr()
            return correlation
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def calculate_sharpe_ratio(df: pd.DataFrame, 
                               period: int = 252,
                               risk_free_rate: float = 0.045) -> pd.DataFrame:
        """
        Rolling Sharpe Ratio.
        Sharpe = (Return - Risk Free Rate) / Std Dev of Returns
        """
        returns = df['Close'].pct_change()
        
        rolling_return = returns.rolling(window=period).mean() * 252
        rolling_std = returns.rolling(window=period).std() * np.sqrt(252)
        
        df['Sharpe_Ratio'] = (rolling_return - risk_free_rate) / rolling_std
        return df
    
    @staticmethod
    def calculate_sortino_ratio(df: pd.DataFrame,
                                period: int = 252,
                                risk_free_rate: float = 0.045) -> pd.DataFrame:
        """
        Rolling Sortino Ratio (uses downside deviation).
        Sortino = (Return - Risk Free Rate) / Downside Deviation
        """
        returns = df['Close'].pct_change()
        
        rolling_return = returns.rolling(window=period).mean() * 252
        
        # Downside deviation (only negative returns)
        downside_returns = returns.copy()
        downside_returns[downside_returns > 0] = 0
        downside_std = downside_returns.rolling(window=period).std() * np.sqrt(252)
        
        df['Sortino_Ratio'] = (rolling_return - risk_free_rate) / downside_std
        return df
    
    @staticmethod
    def calculate_volatility_cones(df: pd.DataFrame, 
                                   periods: List[int] = [10, 20, 30, 60, 90, 120]) -> Dict:
        """
        Volatility cones showing realized volatility across different periods.
        Returns percentile distribution.
        """
        returns = df['Close'].pct_change()
        
        cones = {}
        for period in periods:
            vol = returns.rolling(window=period).std() * np.sqrt(252) * 100
            
            cones[period] = {
                'current': vol.iloc[-1] if len(vol) > 0 else 0,
                'min': vol.min(),
                'p10': vol.quantile(0.10),
                'p25': vol.quantile(0.25),
                'median': vol.median(),
                'p75': vol.quantile(0.75),
                'p90': vol.quantile(0.90),
                'max': vol.max()
            }
        
        return cones
    
    @staticmethod
    def calculate_all_quant(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all quant indicators"""
        df = QuantIndicators.calculate_zscore(df)
        df = QuantIndicators.calculate_rolling_beta(df, 'SPY')
        df = QuantIndicators.calculate_rolling_beta(df, 'QQQ')
        df = QuantIndicators.calculate_rolling_alpha(df, 'SPY')
        df = QuantIndicators.calculate_sharpe_ratio(df)
        df = QuantIndicators.calculate_sortino_ratio(df)
        
        return df
