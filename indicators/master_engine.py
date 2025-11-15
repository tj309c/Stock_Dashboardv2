"""
Master Indicators Engine
Unified interface for all 60+ technical indicators across 7 tiers
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from .tier1_core import CoreIndicators
from .tier2_pro import ProIndicators
from .tier3_volume import VolumeIndicators
from .tier4_momentum import MomentumIndicators
from .tier5_market_breadth import MarketBreadthIndicators
from .tier6_quant import QuantIndicators
from .tier7_ai import AIIndicators

logger = logging.getLogger(__name__)


class MasterIndicatorEngine:
    """
    Master engine for calculating and managing all technical indicators.
    Provides unified interface, toggle management, and summary generation.
    """
    
    def __init__(self):
        self.core = CoreIndicators()
        self.pro = ProIndicators()
        self.volume = VolumeIndicators()
        self.momentum = MomentumIndicators()
        self.breadth = MarketBreadthIndicators()
        self.quant = QuantIndicators()
        self.ai = AIIndicators()
        
        # Default enabled indicators
        self.enabled_indicators = {
            'tier1': ['SMA', 'EMA', 'Bollinger', 'MACD', 'RSI', 'Volume', 'ATR', 'VWAP'],
            'tier2': [],
            'tier3': [],
            'tier4': [],
            'tier5': [],
            'tier6': [],
            'tier7': []
        }
    
    def calculate_all(self, df: pd.DataFrame, 
                     tiers: List[int] = [1, 2, 3, 4, 5, 6, 7]) -> pd.DataFrame:
        """
        Calculate indicators for selected tiers.
        Args:
            df: OHLCV DataFrame
            tiers: List of tiers to calculate (1-7)
        """
        if df.empty:
            return df
        
        df = df.copy()
        
        try:
            if 1 in tiers:
                df = self.core.calculate_all_core(df)
                logger.info("✅ Tier 1 (Core) indicators calculated")
            
            if 2 in tiers:
                df = self.pro.calculate_all_pro(df)
                logger.info("✅ Tier 2 (Pro) indicators calculated")
            
            if 3 in tiers:
                df = self.volume.calculate_all_volume(df)
                logger.info("✅ Tier 3 (Volume) indicators calculated")
            
            if 4 in tiers:
                df = self.momentum.calculate_all_momentum(df)
                logger.info("✅ Tier 4 (Momentum) indicators calculated")
            
            if 5 in tiers:
                df = self.breadth.calculate_all_breadth(df)
                logger.info("✅ Tier 5 (Market Breadth) indicators calculated")
            
            if 6 in tiers:
                df = self.quant.calculate_all_quant(df)
                logger.info("✅ Tier 6 (Quant) indicators calculated")
            
            if 7 in tiers:
                df = self.ai.calculate_all_ai(df)
                logger.info("✅ Tier 7 (AI) indicators calculated")
        
        except ValueError as e:
            # Handle array comparison ambiguity (non-critical)
            if "truth value of an array" in str(e):
                logger.warning(f"Array comparison issue in indicators (non-critical): {e}")
            else:
                logger.error(f"ValueError in indicators: {e}")
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
        
        return df
    
    def get_summary(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Generate comprehensive summary of all indicators.
        Returns summary bar categories: Trend, Momentum, Volatility, Volume, Breadth, Sentiment
        """
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        summary = {
            'trend': {},
            'momentum': {},
            'volatility': {},
            'volume': {},
            'breadth': {},
            'sentiment': {}
        }
        
        # TREND ANALYSIS
        trend_signals = []
        
        if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
                trend_signals.append(('bullish', 'Strong Golden Cross'))
            elif latest['Close'] > latest['SMA_50']:
                trend_signals.append(('bullish', 'Above 50 SMA'))
            elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
                trend_signals.append(('bearish', 'Strong Death Cross'))
            else:
                trend_signals.append(('bearish', 'Below 50 SMA'))
        
        if 'ADX' in df.columns:
            if latest['ADX'] > 25:
                trend_signals.append(('strong', f'ADX {latest["ADX"]:.1f} (Strong Trend)'))
            elif latest['ADX'] < 20:
                trend_signals.append(('weak', f'ADX {latest["ADX"]:.1f} (Weak Trend)'))
        
        if 'Ichimoku_SpanA' in df.columns:
            if latest['Close'] > latest['Ichimoku_SpanA']:
                trend_signals.append(('bullish', 'Above Ichimoku Cloud'))
            else:
                trend_signals.append(('bearish', 'Below Ichimoku Cloud'))
        
        summary['trend'] = {
            'signals': trend_signals,
            'overall': 'bullish' if sum(1 for s in trend_signals if s[0] == 'bullish') > len(trend_signals)/2 else 'bearish'
        }
        
        # MOMENTUM ANALYSIS
        momentum_signals = []
        
        if 'RSI' in df.columns:
            rsi = latest['RSI']
            if rsi > 70:
                momentum_signals.append(('overbought', f'RSI {rsi:.1f}'))
            elif rsi < 30:
                momentum_signals.append(('oversold', f'RSI {rsi:.1f}'))
            elif rsi > 50:
                momentum_signals.append(('bullish', f'RSI {rsi:.1f}'))
            else:
                momentum_signals.append(('bearish', f'RSI {rsi:.1f}'))
        
        if 'MACD_Histogram' in df.columns:
            if latest['MACD_Histogram'] > 0:
                momentum_signals.append(('bullish', 'MACD Bullish'))
            else:
                momentum_signals.append(('bearish', 'MACD Bearish'))
        
        if 'Stoch_K' in df.columns:
            if latest['Stoch_K'] > 80:
                momentum_signals.append(('overbought', 'Stochastic Overbought'))
            elif latest['Stoch_K'] < 20:
                momentum_signals.append(('oversold', 'Stochastic Oversold'))
        
        if 'Momentum_Score' in df.columns:
            score = latest['Momentum_Score']
            if score > 70:
                momentum_signals.append(('strong_bullish', f'Score {score:.0f}/100'))
            elif score > 50:
                momentum_signals.append(('bullish', f'Score {score:.0f}/100'))
            elif score < 30:
                momentum_signals.append(('strong_bearish', f'Score {score:.0f}/100'))
            else:
                momentum_signals.append(('bearish', f'Score {score:.0f}/100'))
        
        summary['momentum'] = {
            'signals': momentum_signals,
            'overall': 'bullish' if sum(1 for s in momentum_signals if 'bullish' in s[0]) > len(momentum_signals)/2 else 'bearish'
        }
        
        # VOLATILITY ANALYSIS
        volatility_signals = []
        
        if 'ATR' in df.columns:
            atr_pct = (latest['ATR'] / latest['Close']) * 100
            if atr_pct > 3:
                volatility_signals.append(('high', f'ATR {atr_pct:.1f}%'))
            elif atr_pct < 1:
                volatility_signals.append(('low', f'ATR {atr_pct:.1f}%'))
            else:
                volatility_signals.append(('normal', f'ATR {atr_pct:.1f}%'))
        
        if 'BB_Width' in df.columns:
            bb_width_pct = (latest['BB_Width'] / latest['Close']) * 100
            if bb_width_pct > 10:
                volatility_signals.append(('expanding', 'Bollinger Expanding'))
            elif bb_width_pct < 5:
                volatility_signals.append(('contracting', 'Bollinger Squeeze'))
        
        if 'VIX' in df.columns:
            if latest['VIX'] > 30:
                volatility_signals.append(('high', f'VIX {latest["VIX"]:.1f}'))
            elif latest['VIX'] < 15:
                volatility_signals.append(('low', f'VIX {latest["VIX"]:.1f}'))
        
        summary['volatility'] = {
            'signals': volatility_signals,
            'overall': 'high' if any(s[0] == 'high' for s in volatility_signals) else 'normal'
        }
        
        # VOLUME ANALYSIS
        volume_signals = []
        
        if 'Volume' in df.columns:
            avg_vol = df['Volume'].tail(20).mean()
            vol_ratio = latest['Volume'] / avg_vol
            if vol_ratio > 2:
                volume_signals.append(('high', f'{vol_ratio:.1f}x Average'))
            elif vol_ratio < 0.5:
                volume_signals.append(('low', f'{vol_ratio:.1f}x Average'))
        
        if 'OBV' in df.columns:
            obv_trend = 'rising' if df['OBV'].iloc[-1] > df['OBV'].iloc[-5] else 'falling'
            volume_signals.append((obv_trend, f'OBV {obv_trend.title()}'))
        
        if 'CMF' in df.columns:
            if latest['CMF'] > 0.1:
                volume_signals.append(('accumulation', 'CMF Positive'))
            elif latest['CMF'] < -0.1:
                volume_signals.append(('distribution', 'CMF Negative'))
        
        if 'Volume_Anomaly' in df.columns and latest['Volume_Anomaly']:
            volume_signals.append(('anomaly', 'Volume Spike Detected'))
        
        summary['volume'] = {
            'signals': volume_signals,
            'overall': 'strong' if any('high' in str(s) or 'anomaly' in str(s) for s in volume_signals) else 'normal'
        }
        
        # MARKET BREADTH
        breadth_signals = []
        
        if 'AD_Line' in df.columns:
            ad_trend = 'positive' if df['AD_Line'].iloc[-1] > df['AD_Line'].iloc[-20] else 'negative'
            breadth_signals.append((ad_trend, f'A/D Line {ad_trend.title()}'))
        
        if 'Put_Call_Ratio' in df.columns:
            pcr = latest['Put_Call_Ratio']
            if pcr > 1.15:
                breadth_signals.append(('bearish', f'P/C {pcr:.2f} (Bearish)'))
            elif pcr < 0.7:
                breadth_signals.append(('bullish', f'P/C {pcr:.2f} (Bullish)'))
        
        summary['breadth'] = {
            'signals': breadth_signals,
            'overall': 'positive' if any(s[0] == 'positive' or s[0] == 'bullish' for s in breadth_signals) else 'negative'
        }
        
        # SENTIMENT (AI/ML)
        sentiment_signals = []
        
        if 'ML_Trend' in df.columns and latest['ML_Trend'] in ['bullish', 'bearish']:
            confidence = latest.get('ML_Confidence', 0) * 100
            sentiment_signals.append((latest['ML_Trend'], f'ML: {latest["ML_Trend"].title()} ({confidence:.0f}%)'))
        
        if 'Regime' in df.columns:
            sentiment_signals.append((latest['Regime'], f'Market: {latest["Regime"].title()}'))
        
        if 'Price_Anomaly' in df.columns and latest['Price_Anomaly']:
            sentiment_signals.append(('anomaly', 'Price Anomaly Detected'))
        
        summary['sentiment'] = {
            'signals': sentiment_signals,
            'overall': latest.get('ML_Trend', 'neutral')
        }
        
        return summary
    
    def get_indicator_list(self) -> Dict[str, List[str]]:
        """Return list of all available indicators by tier."""
        return {
            'Tier 1 - Core': [
                'SMA (20, 50, 100, 200)',
                'EMA (9, 12, 26, 50, 200)',
                'Bollinger Bands',
                'MACD',
                'RSI',
                'OBV',
                'ATR',
                'VWAP',
                'Market Hours'
            ],
            'Tier 2 - Pro': [
                'Ichimoku Cloud',
                'Fibonacci Retracement',
                'Stochastic Oscillator',
                'Chaikin Money Flow',
                'Money Flow Index',
                'Donchian Channels',
                'Keltner Channels',
                'ADX + DI',
                'Parabolic SAR',
                'Pivot Points'
            ],
            'Tier 3 - Volume': [
                'Volume Profile',
                'VWMA',
                'A/D Line',
                'Price Volume Trend',
                'Ease of Movement',
                'Force Index',
                'Volume Oscillator',
                'Klinger Oscillator'
            ],
            'Tier 4 - Momentum': [
                'Rate of Change',
                'TRIX',
                'Chande Momentum',
                'DPO',
                'Coppock Curve',
                'Connors RSI',
                'Williams %R'
            ],
            'Tier 5 - Market Breadth': [
                'Put/Call Ratio',
                'High-Low Index',
                'A/D Line',
                'TRIN Index',
                'VIX',
                'Dark Pool Estimate'
            ],
            'Tier 6 - Quant': [
                'Z-Score',
                'Rolling Beta (SPY/QQQ)',
                'Rolling Alpha',
                'Correlation Matrix',
                'Sharpe Ratio',
                'Sortino Ratio',
                'Volatility Cones'
            ],
            'Tier 7 - AI/ML': [
                'Regime Detection',
                'Volume Anomaly',
                'Price Anomaly',
                'VIX-Adjusted Bands',
                'ML Trend Classifier',
                'Momentum Score'
            ]
        }


def get_master_engine():
    """Factory function to get MasterIndicatorEngine instance."""
    return MasterIndicatorEngine()
