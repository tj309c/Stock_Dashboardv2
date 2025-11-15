"""
Tier 7 - AI/Derived Indicators
ML-powered indicators: Regime detection, Anomaly detection, VIX-adjusted bands, Trend classifier
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class AIIndicators:
    """AI and ML-powered indicators - Tier 7"""
    
    @staticmethod
    def detect_regime(df: pd.DataFrame, lookback: int = 60) -> pd.DataFrame:
        """
        Regime-switching indicator (Trending vs Ranging).
        Uses ADX and volatility to classify market regime.
        """
        # Calculate ADX if not present
        if 'ADX' not in df.columns:
            from .tier2_pro import ProIndicators
            df = ProIndicators.calculate_adx(df)
        
        # Calculate volatility
        returns = df['Close'].pct_change()
        volatility = returns.rolling(window=20).std() * np.sqrt(252) * 100
        
        # Regime classification
        regime = pd.Series('unknown', index=df.index)
        
        # Strong Trending: High ADX
        regime[df['ADX'] > 25] = 'trending'
        
        # Ranging: Low ADX
        regime[df['ADX'] < 20] = 'ranging'
        
        # High Volatility
        vol_threshold = volatility.quantile(0.75)
        regime[volatility > vol_threshold] = 'volatile'
        
        # Low Volatility
        vol_floor = volatility.quantile(0.25)
        regime[(volatility < vol_floor) & (df['ADX'] < 20)] = 'quiet'
        
        df['Regime'] = regime
        return df
    
    @staticmethod
    def detect_volume_anomaly(df: pd.DataFrame, 
                             std_threshold: float = 2.5) -> pd.DataFrame:
        """
        Volume anomaly detector using statistical methods.
        Flags unusual volume spikes.
        """
        # Calculate rolling z-score of volume
        vol_mean = df['Volume'].rolling(window=20).mean()
        vol_std = df['Volume'].rolling(window=20).std()
        vol_zscore = (df['Volume'] - vol_mean) / vol_std
        
        # Flag anomalies
        df['Volume_Anomaly'] = False
        df.loc[vol_zscore > std_threshold, 'Volume_Anomaly'] = True
        df['Volume_ZScore'] = vol_zscore
        
        return df
    
    @staticmethod
    def detect_price_anomaly(df: pd.DataFrame,
                            std_threshold: float = 2.5) -> pd.DataFrame:
        """
        Price anomaly detector.
        Identifies unusual price movements.
        """
        returns = df['Close'].pct_change()
        
        # Rolling z-score of returns
        ret_mean = returns.rolling(window=20).mean()
        ret_std = returns.rolling(window=20).std()
        ret_zscore = (returns - ret_mean) / ret_std
        
        # Flag anomalies
        df['Price_Anomaly'] = False
        df.loc[ret_zscore.abs() > std_threshold, 'Price_Anomaly'] = True
        df['Return_ZScore'] = ret_zscore
        
        return df
    
    @staticmethod
    def calculate_vix_adjusted_bands(df: pd.DataFrame, 
                                     vix_level: float = 20.0,
                                     period: int = 20) -> pd.DataFrame:
        """
        VIX-adjusted volatility bands.
        Widens bands during high VIX, narrows during low VIX.
        """
        # Get VIX if not present
        if 'VIX' not in df.columns:
            df['VIX'] = vix_level
        
        # Calculate base bands (Bollinger-style)
        sma = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()
        
        # Adjust std by VIX level
        vix_adjustment = df['VIX'] / 20.0  # Normalize to long-term VIX average
        
        df['VIX_Upper'] = sma + (2 * std * vix_adjustment)
        df['VIX_Lower'] = sma - (2 * std * vix_adjustment)
        df['VIX_Middle'] = sma
        
        return df
    
    @staticmethod
    def ml_trend_classifier(df: pd.DataFrame, 
                           train_period: int = 500,
                           prediction_horizon: int = 5) -> pd.DataFrame:
        """
        ML-driven trend classifier using Random Forest.
        Predicts trend direction based on technical features.
        """
        if len(df) < train_period + prediction_horizon:
            df['ML_Trend'] = 'insufficient_data'
            df['ML_Confidence'] = 0.0
            return df
        
        try:
            # Feature engineering
            features = pd.DataFrame(index=df.index)
            
            # Technical features
            features['rsi'] = df.get('RSI', 50)
            features['macd'] = df.get('MACD_Histogram', 0)
            features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
            features['atr_pct'] = df.get('ATR', 0) / df['Close'] * 100
            features['close_sma_ratio'] = df['Close'] / df['Close'].rolling(window=20).mean()
            
            # Future returns (labels)
            future_returns = df['Close'].pct_change(prediction_horizon).shift(-prediction_horizon)
            labels = (future_returns > 0).astype(int)
            
            # Prepare training data
            features = features.fillna(0)
            mask = ~(features.isnull().any(axis=1) | labels.isnull())
            
            X = features[mask].values
            y = labels[mask].values
            
            if len(X) < 50:
                df['ML_Trend'] = 'insufficient_data'
                df['ML_Confidence'] = 0.0
                return df
            
            # Train model on historical data
            train_size = min(train_period, len(X) - 10)
            X_train = X[:train_size]
            y_train = y[:train_size]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            
            # Train Random Forest
            model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Predict on all data
            X_scaled = scaler.transform(X)
            predictions = model.predict(X_scaled)
            probabilities = model.predict_proba(X_scaled)
            
            # Map predictions to dataframe
            df['ML_Trend'] = 'neutral'
            df.loc[mask, 'ML_Trend'] = ['bullish' if p == 1 else 'bearish' for p in predictions]
            
            # Confidence (probability of predicted class)
            confidence = np.max(probabilities, axis=1)
            df['ML_Confidence'] = 0.0
            df.loc[mask, 'ML_Confidence'] = confidence
            
        except Exception as e:
            logger.error(f"Error in ML trend classifier: {e}")
            df['ML_Trend'] = 'error'
            df['ML_Confidence'] = 0.0
        
        return df
    
    @staticmethod
    def calculate_momentum_score(df: pd.DataFrame) -> pd.DataFrame:
        """
        Composite momentum score (0-100) based on multiple indicators.
        """
        score = pd.Series(50.0, index=df.index)  # Start neutral
        
        # RSI contribution (0-100)
        if 'RSI' in df.columns:
            score += (df['RSI'] - 50) * 0.3
        
        # MACD contribution
        if 'MACD_Histogram' in df.columns:
            macd_norm = (df['MACD_Histogram'] / df['MACD_Histogram'].abs().max() * 10).fillna(0)
            score += macd_norm
        
        # Trend contribution (price vs MA)
        if 'SMA_50' in df.columns:
            trend = ((df['Close'] / df['SMA_50'] - 1) * 100).fillna(0)
            score += trend.clip(-10, 10)
        
        # Clip to 0-100 range
        df['Momentum_Score'] = score.clip(0, 100)
        
        return df
    
    @staticmethod
    def calculate_all_ai(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all AI indicators"""
        df = AIIndicators.detect_regime(df)
        df = AIIndicators.detect_volume_anomaly(df)
        df = AIIndicators.detect_price_anomaly(df)
        df = AIIndicators.calculate_vix_adjusted_bands(df)
        df = AIIndicators.ml_trend_classifier(df)
        df = AIIndicators.calculate_momentum_score(df)
        
        return df
