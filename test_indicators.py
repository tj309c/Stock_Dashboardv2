"""
Comprehensive Test Suite for Technical Indicators
Tests all 7 tiers with real and synthetic data
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from indicators.tier1_core import CoreIndicators
from indicators.tier2_pro import ProIndicators
from indicators.tier3_volume import VolumeIndicators
from indicators.tier4_momentum import MomentumIndicators
from indicators.tier5_market_breadth import MarketBreadthIndicators
from indicators.tier6_quant import QuantIndicators
from indicators.tier7_ai import AIIndicators
from indicators.master_engine import MasterIndicatorEngine


@pytest.fixture
def sample_ohlcv_data():
    """Generate synthetic OHLCV data for testing"""
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    
    # Generate realistic price movements
    close_prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)
    close_prices = np.maximum(close_prices, 50)  # Floor at $50
    
    df = pd.DataFrame({
        'Open': close_prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
        'High': close_prices * (1 + np.random.uniform(0, 0.02, len(dates))),
        'Low': close_prices * (1 - np.random.uniform(0, 0.02, len(dates))),
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    return df


@pytest.fixture
def real_market_data():
    """Fetch real market data for integration testing"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        df = ticker.history(period='6mo')
        return df
    except:
        pytest.skip("yfinance not available or network issue")


class TestTier1Core:
    """Test Core Indicators (Tier 1)"""
    
    def test_sma_calculation(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_sma(sample_ohlcv_data.copy(), periods=[20, 50])
        
        assert 'SMA_20' in df.columns
        assert 'SMA_50' in df.columns
        assert df['SMA_20'].notna().sum() >= len(df) - 20
        assert df['SMA_50'].notna().sum() >= len(df) - 50
    
    def test_ema_calculation(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_ema(sample_ohlcv_data.copy(), periods=[12, 26])
        
        assert 'EMA_12' in df.columns
        assert 'EMA_26' in df.columns
        assert df['EMA_12'].notna().any()
    
    def test_bollinger_bands(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_bollinger_bands(sample_ohlcv_data.copy())
        
        assert 'BB_Middle' in df.columns
        assert 'BB_Upper' in df.columns
        assert 'BB_Lower' in df.columns
        assert 'BB_Width' in df.columns
        assert 'BB_PercentB' in df.columns  # Fixed: actual column name
        
        # Upper should always be > Lower (where not NaN)
        valid_rows = df[['BB_Upper', 'BB_Lower']].dropna()
        assert (valid_rows['BB_Upper'] > valid_rows['BB_Lower']).all()
    
    def test_macd(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_macd(sample_ohlcv_data.copy())
        
        assert 'MACD' in df.columns
        assert 'MACD_Signal' in df.columns
        assert 'MACD_Histogram' in df.columns
        
        # Histogram should equal MACD - Signal
        diff = df['MACD'] - df['MACD_Signal']
        assert np.allclose(df['MACD_Histogram'].dropna(), diff.dropna(), rtol=1e-5)
    
    def test_rsi(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_rsi(sample_ohlcv_data.copy())
        
        assert 'RSI' in df.columns
        # RSI should be between 0 and 100
        assert (df['RSI'].dropna() >= 0).all()
        assert (df['RSI'].dropna() <= 100).all()
    
    def test_atr(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_atr(sample_ohlcv_data.copy())
        
        assert 'ATR' in df.columns
        # ATR should always be positive
        assert (df['ATR'].dropna() > 0).all()
    
    def test_vwap(self, sample_ohlcv_data):
        core = CoreIndicators()
        df = core.calculate_vwap(sample_ohlcv_data.copy())
        
        assert 'VWAP' in df.columns
        # VWAP should be positive
        assert (df['VWAP'].dropna() > 0).all()
        # Note: VWAP is cumulative so it won't always be between daily high/low


class TestTier2Pro:
    """Test Professional Indicators (Tier 2)"""
    
    def test_ichimoku(self, sample_ohlcv_data):
        pro = ProIndicators()
        df = pro.calculate_ichimoku(sample_ohlcv_data.copy())
        
        assert 'Ichimoku_Tenkan' in df.columns
        assert 'Ichimoku_Kijun' in df.columns
        assert 'Ichimoku_SpanA' in df.columns
        assert 'Ichimoku_SpanB' in df.columns
        assert 'Ichimoku_Chikou' in df.columns
    
    def test_fibonacci(self, sample_ohlcv_data):
        pro = ProIndicators()
        levels = pro.calculate_fibonacci(sample_ohlcv_data.copy())
        
        assert 'retracement' in levels
        assert 'extensions' in levels
        assert len(levels['retracement']) == 7
        assert len(levels['extensions']) == 3
    
    def test_stochastic(self, sample_ohlcv_data):
        pro = ProIndicators()
        df = pro.calculate_stochastic(sample_ohlcv_data.copy())
        
        assert 'Stoch_K' in df.columns
        assert 'Stoch_D' in df.columns
        # Stochastic should be between 0 and 100
        assert (df['Stoch_K'].dropna() >= 0).all()
        assert (df['Stoch_K'].dropna() <= 100).all()
    
    def test_adx(self, sample_ohlcv_data):
        pro = ProIndicators()
        df = pro.calculate_adx(sample_ohlcv_data.copy())
        
        assert 'ADX' in df.columns
        assert 'DI_Plus' in df.columns
        assert 'DI_Minus' in df.columns
        # ADX should be between 0 and 100
        assert (df['ADX'].dropna() >= 0).all()
        assert (df['ADX'].dropna() <= 100).all()


class TestTier3Volume:
    """Test Volume Indicators (Tier 3)"""
    
    def test_volume_profile(self, sample_ohlcv_data):
        volume = VolumeIndicators()
        result = volume.calculate_volume_profile(sample_ohlcv_data.copy())
        
        assert 'poc' in result
        assert 'value_area_high' in result
        assert 'value_area_low' in result
        assert result['poc'] > 0
    
    def test_obv(self, sample_ohlcv_data):
        volume = VolumeIndicators()
        df = volume.calculate_obv(sample_ohlcv_data.copy())
        
        assert 'OBV' in df.columns
    
    def test_vwma(self, sample_ohlcv_data):
        volume = VolumeIndicators()
        df = volume.calculate_vwma(sample_ohlcv_data.copy())
        
        assert 'VWMA' in df.columns


class TestTier4Momentum:
    """Test Momentum Indicators (Tier 4)"""
    
    def test_roc(self, sample_ohlcv_data):
        momentum = MomentumIndicators()
        df = momentum.calculate_roc(sample_ohlcv_data.copy())
        
        assert 'ROC' in df.columns
    
    def test_trix(self, sample_ohlcv_data):
        momentum = MomentumIndicators()
        df = momentum.calculate_trix(sample_ohlcv_data.copy())
        
        assert 'TRIX' in df.columns
    
    def test_williams_r(self, sample_ohlcv_data):
        momentum = MomentumIndicators()
        df = momentum.calculate_williams_r(sample_ohlcv_data.copy())
        
        assert 'Williams_R' in df.columns
        # Williams %R should be between -100 and 0
        assert (df['Williams_R'].dropna() >= -100).all()
        assert (df['Williams_R'].dropna() <= 0).all()


class TestTier5MarketBreadth:
    """Test Market Breadth Indicators (Tier 5)"""
    
    def test_put_call_ratio(self, sample_ohlcv_data):
        breadth = MarketBreadthIndicators()
        df = breadth.calculate_put_call_ratio(sample_ohlcv_data.copy(), "SPY")
        
        # May be None if data unavailable
        if 'Put_Call_Ratio' in df.columns:
            assert df['Put_Call_Ratio'].notna().any()
    
    def test_high_low_index(self, sample_ohlcv_data):
        breadth = MarketBreadthIndicators()
        df = breadth.calculate_high_low_index(sample_ohlcv_data.copy())
        
        if 'High_Low_Index' in df.columns:
            # Should be between 0 and 100
            assert (df['High_Low_Index'].dropna() >= 0).all()
            assert (df['High_Low_Index'].dropna() <= 100).all()


class TestTier6Quant:
    """Test Quantitative Indicators (Tier 6)"""
    
    def test_zscore(self, sample_ohlcv_data):
        quant = QuantIndicators()
        df = quant.calculate_zscore(sample_ohlcv_data.copy())
        
        assert 'ZScore' in df.columns
    
    def test_rolling_beta(self, sample_ohlcv_data):
        quant = QuantIndicators()
        df = quant.calculate_rolling_beta(sample_ohlcv_data.copy(), "SPY")
        
        # May be None if benchmark unavailable
        if 'Beta_SPY' in df.columns:
            assert df['Beta_SPY'].notna().any()
    
    def test_sharpe_ratio(self, sample_ohlcv_data):
        quant = QuantIndicators()
        df = quant.calculate_sharpe_ratio(sample_ohlcv_data.copy())
        
        assert 'Sharpe_Ratio' in df.columns


class TestTier7AI:
    """Test AI/ML Indicators (Tier 7)"""
    
    def test_regime_detection(self, sample_ohlcv_data):
        ai = AIIndicators()
        df = ai.detect_regime(sample_ohlcv_data.copy())
        
        assert 'Regime' in df.columns
        # Should be one of the valid regimes
        valid_regimes = {'trending', 'ranging', 'volatile', 'quiet'}
        assert df['Regime'].dropna().isin(valid_regimes).all()
    
    def test_volume_anomaly(self, sample_ohlcv_data):
        ai = AIIndicators()
        df = ai.detect_volume_anomaly(sample_ohlcv_data.copy())
        
        assert 'Volume_Anomaly' in df.columns
        # Should be boolean
        assert df['Volume_Anomaly'].dtype == bool
    
    def test_ml_trend_classifier(self, sample_ohlcv_data):
        ai = AIIndicators()
        df = ai.ml_trend_classifier(sample_ohlcv_data.copy())
        
        assert 'ML_Trend' in df.columns
        assert 'ML_Confidence' in df.columns
        
        # Trend should be bullish, bearish, or neutral
        valid_trends = {'bullish', 'bearish', 'neutral'}
        assert df['ML_Trend'].dropna().isin(valid_trends).all()
        
        # Confidence should be between 0 and 1
        assert (df['ML_Confidence'].dropna() >= 0).all()
        assert (df['ML_Confidence'].dropna() <= 1).all()
    
    def test_momentum_score(self, sample_ohlcv_data):
        ai = AIIndicators()
        df = ai.calculate_momentum_score(sample_ohlcv_data.copy())
        
        assert 'Momentum_Score' in df.columns
        # Should be between 0 and 100
        assert (df['Momentum_Score'].dropna() >= 0).all()
        assert (df['Momentum_Score'].dropna() <= 100).all()


class TestMasterEngine:
    """Test Master Indicator Engine"""
    
    def test_calculate_all_tiers(self, sample_ohlcv_data):
        engine = MasterIndicatorEngine()
        df = engine.calculate_all(sample_ohlcv_data.copy(), tiers=[1, 2, 3, 4, 5, 6, 7])
        
        # Should have indicators from all tiers
        assert 'SMA_20' in df.columns  # Tier 1
        assert 'Ichimoku_Tenkan' in df.columns  # Tier 2
        assert 'OBV' in df.columns  # Tier 3
        assert 'ROC' in df.columns  # Tier 4
    
    def test_calculate_selective_tiers(self, sample_ohlcv_data):
        engine = MasterIndicatorEngine()
        df = engine.calculate_all(sample_ohlcv_data.copy(), tiers=[1, 3])
        
        # Should have Tier 1 and 3
        assert 'SMA_20' in df.columns
        assert 'OBV' in df.columns
        
        # Should NOT have Tier 2
        assert 'Ichimoku_Tenkan' not in df.columns
    
    def test_get_summary(self, sample_ohlcv_data):
        engine = MasterIndicatorEngine()
        df = engine.calculate_all(sample_ohlcv_data.copy(), tiers=[1, 2, 4, 7])
        summary = engine.get_summary(df)
        
        # Should have all 6 categories
        assert 'trend' in summary
        assert 'momentum' in summary
        assert 'volatility' in summary
        assert 'volume' in summary
        assert 'breadth' in summary
        assert 'sentiment' in summary
        
        # Each should have signals and overall
        assert 'signals' in summary['trend']
        assert 'overall' in summary['trend']
    
    def test_get_indicator_list(self):
        engine = MasterIndicatorEngine()
        indicator_list = engine.get_indicator_list()
        
        assert len(indicator_list) == 7  # 7 tiers
        assert 'Tier 1 - Core' in indicator_list
        assert 'Tier 7 - AI/ML' in indicator_list


class TestIntegration:
    """Integration tests with real market data"""
    
    def test_full_pipeline_real_data(self, real_market_data):
        """Test full pipeline with real AAPL data"""
        engine = MasterIndicatorEngine()
        
        # Calculate all tiers
        df = engine.calculate_all(real_market_data.copy(), tiers=[1, 2, 3, 4, 5, 6, 7])
        
        # Should have data
        assert not df.empty
        assert len(df) == len(real_market_data)
        
        # Get summary
        summary = engine.get_summary(df)
        
        # Should have valid overall assessments
        assert summary['trend']['overall'] in ['bullish', 'bearish', 'neutral']
        assert summary['momentum']['overall'] in ['bullish', 'bearish', 'neutral']
        assert summary['volatility']['overall'] in ['high', 'low', 'normal']
    
    def test_performance_benchmark(self, sample_ohlcv_data):
        """Benchmark calculation performance"""
        import time
        engine = MasterIndicatorEngine()
        
        start_time = time.time()
        df = engine.calculate_all(sample_ohlcv_data.copy(), tiers=[1, 2, 3, 4, 5, 6, 7])
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds for 1 year of data)
        assert elapsed < 5.0
        print(f"\n⏱️ Calculated all 7 tiers in {elapsed:.2f} seconds")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_dataframe(self):
        engine = MasterIndicatorEngine()
        df_empty = pd.DataFrame()
        
        result = engine.calculate_all(df_empty, tiers=[1])
        assert result.empty
    
    def test_insufficient_data(self):
        """Test with very limited data"""
        df_short = pd.DataFrame({
            'Open': [100, 101],
            'High': [102, 103],
            'Low': [99, 100],
            'Close': [101, 102],
            'Volume': [1000000, 1100000]
        })
        
        engine = MasterIndicatorEngine()
        # Should not crash
        result = engine.calculate_all(df_short, tiers=[1])
        assert not result.empty
    
    def test_missing_columns(self):
        """Test with incomplete OHLCV data"""
        df_incomplete = pd.DataFrame({
            'Close': [100, 101, 102],
            'Volume': [1000000, 1100000, 1200000]
        })
        
        core = CoreIndicators()
        # Should handle gracefully
        try:
            core.calculate_sma(df_incomplete)
        except Exception as e:
            assert 'Close' not in str(e)  # Should fail on missing columns, not Close


def run_all_tests():
    """Run all tests and print summary"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_all_tests()
