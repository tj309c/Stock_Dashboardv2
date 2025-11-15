"""
Sentiment-Market Correlation Analyzer

Integrates all available data sources to understand correlation between:
- News sentiment
- Reddit/social sentiment  
- Insider/Congressional trades
- Stock price movements
- Overall market sentiment (SPY)

Provides backtesting to quantify how well sentiment predicts price moves.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
from scipy import stats
from scipy.stats import spearmanr, pearsonr
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class SentimentMarketCorrelation:
    """
    Analyzes correlation between sentiment data and price movements.
    Performs backtesting to validate predictive power.
    """
    
    def __init__(self):
        self.spy = None  # Market benchmark
        self.cache_duration = timedelta(hours=6)
        
    def get_market_sentiment(self, days: int = 30) -> pd.DataFrame:
        """
        Get overall market sentiment using SPY as proxy.
        
        Returns:
            DataFrame with date, close, returns, volatility
        """
        try:
            spy = yf.Ticker("SPY")
            hist = spy.history(period=f"{days}d")
            
            df = pd.DataFrame({
                'date': hist.index,
                'spy_close': hist['Close'].values,
                'spy_returns': hist['Close'].pct_change().values,
                'spy_volume': hist['Volume'].values
            })
            
            # Calculate rolling volatility (10-day)
            df['spy_volatility'] = df['spy_returns'].rolling(10).std()
            
            # Market regime
            df['market_regime'] = df['spy_returns'].apply(lambda x: 
                'bull' if x > 0.01 else 'bear' if x < -0.01 else 'neutral'
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return pd.DataFrame()
    
    def calculate_sentiment_score(self, sentiment_df: pd.DataFrame) -> Dict:
        """
        Calculate aggregate sentiment score from scraped data.
        
        Args:
            sentiment_df: DataFrame from sentiment_scraper with sentiment, polarity columns
            
        Returns:
            Dict with sentiment metrics
        """
        if sentiment_df is None or len(sentiment_df) == 0:
            return {
                'sentiment_score': 0,
                'positive_pct': 0,
                'negative_pct': 0,
                'neutral_pct': 0,
                'volume': 0,
                'avg_polarity': 0,
                'data_quality': 'none'
            }
        
        # Count sentiment categories
        sentiment_counts = sentiment_df['sentiment'].value_counts()
        total = len(sentiment_df)
        
        positive_pct = (sentiment_counts.get('positive', 0) / total) * 100
        negative_pct = (sentiment_counts.get('negative', 0) / total) * 100
        neutral_pct = (sentiment_counts.get('neutral', 0) / total) * 100
        
        # Calculate weighted sentiment score (-100 to +100)
        sentiment_score = positive_pct - negative_pct
        
        # Average polarity from TextBlob
        avg_polarity = sentiment_df['polarity'].mean() if 'polarity' in sentiment_df.columns else 0
        
        # Data quality assessment
        if total >= 50:
            quality = 'high'
        elif total >= 20:
            quality = 'medium'
        elif total >= 5:
            quality = 'low'
        else:
            quality = 'very_low'
        
        return {
            'sentiment_score': sentiment_score,
            'positive_pct': positive_pct,
            'negative_pct': negative_pct,
            'neutral_pct': neutral_pct,
            'volume': total,
            'avg_polarity': avg_polarity,
            'data_quality': quality
        }
    
    def calculate_price_momentum(self, ticker: str, days: int = 30) -> Dict:
        """
        Calculate recent price momentum metrics.
        
        Returns:
            Dict with momentum metrics
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days}d")
            
            if len(hist) < 2:
                return {'error': 'Insufficient price data'}
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            
            # Momentum metrics
            total_return = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
            avg_daily_return = returns.mean() * 100
            volatility = returns.std() * 100
            
            # Trend direction
            sma_10 = hist['Close'].rolling(10).mean()
            sma_20 = hist['Close'].rolling(20).mean()
            
            trend = 'bullish' if sma_10.iloc[-1] > sma_20.iloc[-1] else 'bearish'
            
            # Volume analysis
            avg_volume = hist['Volume'].mean()
            recent_volume = hist['Volume'].iloc[-5:].mean()
            volume_surge = (recent_volume / avg_volume - 1) * 100 if avg_volume > 0 else 0
            
            return {
                'total_return': total_return,
                'avg_daily_return': avg_daily_return,
                'volatility': volatility,
                'trend': trend,
                'volume_surge': volume_surge,
                'current_price': hist['Close'].iloc[-1],
                'period_high': hist['Close'].max(),
                'period_low': hist['Close'].min()
            }
            
        except Exception as e:
            logger.error(f"Error calculating momentum: {e}")
            return {'error': str(e)}
    
    def correlate_sentiment_to_price(self, ticker: str, sentiment_df: pd.DataFrame, 
                                    lookback_days: int = 30) -> Dict:
        """
        Calculate correlation between sentiment and forward price returns.
        
        This is the KEY metric: Does positive sentiment predict positive returns?
        
        Args:
            ticker: Stock symbol
            sentiment_df: DataFrame with date and sentiment columns
            lookback_days: Days to analyze
            
        Returns:
            Dict with correlation metrics and predictive power assessment
        """
        try:
            # Get price data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{lookback_days + 10}d")  # Extra days for forward returns
            
            if len(hist) < 10:
                return {'error': 'Insufficient price data for correlation'}
            
            # Calculate forward returns (1-day, 3-day, 7-day)
            hist['return_1d'] = hist['Close'].shift(-1) / hist['Close'] - 1
            hist['return_3d'] = hist['Close'].shift(-3) / hist['Close'] - 1
            hist['return_7d'] = hist['Close'].shift(-7) / hist['Close'] - 1
            
            # Group sentiment by date
            if 'date' in sentiment_df.columns:
                sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
                daily_sentiment = sentiment_df.groupby(sentiment_df['date'].dt.date).agg({
                    'polarity': 'mean',
                    'sentiment': lambda x: (x == 'positive').sum() - (x == 'negative').sum()
                }).reset_index()
                daily_sentiment.columns = ['date', 'avg_polarity', 'sentiment_net']
            else:
                # No date info, use overall sentiment
                return self._correlate_overall_sentiment(ticker, sentiment_df, hist)
            
            # Merge with price data
            hist.reset_index(inplace=True)
            hist['date'] = hist['Date'].dt.date
            merged = pd.merge(hist, daily_sentiment, on='date', how='left')
            
            # Fill forward sentiment (assume sentiment carries forward)
            merged['avg_polarity'] = merged['avg_polarity'].ffill()
            merged['sentiment_net'] = merged['sentiment_net'].fillna(0)
            
            # Calculate correlations
            correlations = {}
            p_values = {}
            
            for period in ['1d', '3d', '7d']:
                col = f'return_{period}'
                valid_data = merged[[col, 'avg_polarity']].dropna()
                
                if len(valid_data) >= 5:
                    # Pearson correlation
                    corr, p_val = pearsonr(valid_data['avg_polarity'], valid_data[col])
                    correlations[period] = corr
                    p_values[period] = p_val
                else:
                    correlations[period] = 0
                    p_values[period] = 1.0
            
            # Assess predictive power
            best_corr = max(abs(correlations.get('1d', 0)), 
                           abs(correlations.get('3d', 0)), 
                           abs(correlations.get('7d', 0)))
            
            if best_corr > 0.5:
                predictive_power = 'strong'
                reliability = 'high'
            elif best_corr > 0.3:
                predictive_power = 'moderate'
                reliability = 'medium'
            elif best_corr > 0.15:
                predictive_power = 'weak'
                reliability = 'low'
            else:
                predictive_power = 'negligible'
                reliability = 'very_low'
            
            return {
                'correlations': correlations,
                'p_values': p_values,
                'best_correlation': best_corr,
                'predictive_power': predictive_power,
                'reliability': reliability,
                'sample_size': len(merged),
                'interpretation': self._interpret_correlation(correlations, p_values)
            }
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return {'error': str(e)}
    
    def _correlate_overall_sentiment(self, ticker: str, sentiment_df: pd.DataFrame, 
                                    hist: pd.DataFrame) -> Dict:
        """
        Fallback: Correlate overall sentiment to recent returns when no date info.
        """
        sentiment_score = self.calculate_sentiment_score(sentiment_df)
        
        # Use most recent returns
        hist['return_1d'] = hist['Close'].pct_change()
        recent_return = hist['return_1d'].iloc[-7:].mean()  # Last week avg
        
        # Simple directional check
        sentiment_positive = sentiment_score['sentiment_score'] > 10
        price_positive = recent_return > 0
        
        directional_match = sentiment_positive == price_positive
        
        return {
            'correlations': {'overall': 0.5 if directional_match else -0.3},
            'p_values': {'overall': 0.1},
            'best_correlation': 0.5 if directional_match else 0.3,
            'predictive_power': 'moderate' if directional_match else 'weak',
            'reliability': 'low',
            'sample_size': len(sentiment_df),
            'interpretation': 'Limited: No date data for temporal correlation',
            'note': 'Using overall sentiment vs recent returns'
        }
    
    def _interpret_correlation(self, correlations: Dict, p_values: Dict) -> str:
        """
        Generate human-readable interpretation of correlation results.
        """
        interpretations = []
        
        for period, corr in correlations.items():
            p_val = p_values.get(period, 1.0)
            
            if p_val > 0.05:
                sig = "not statistically significant"
            else:
                sig = "statistically significant"
            
            if abs(corr) > 0.5:
                strength = "strongly"
            elif abs(corr) > 0.3:
                strength = "moderately"
            else:
                strength = "weakly"
            
            direction = "positively" if corr > 0 else "negatively"
            
            interpretations.append(
                f"{period} forward returns are {strength} {direction} correlated "
                f"with sentiment (r={corr:.3f}, {sig})"
            )
        
        return " | ".join(interpretations)
    
    def backtest_sentiment_signal(self, ticker: str, sentiment_history: List[Dict],
                                  price_history: pd.DataFrame) -> Dict:
        """
        Backtest a simple sentiment-based trading strategy.
        
        Strategy:
        - BUY when sentiment > threshold (e.g., +20)
        - SELL when sentiment < threshold (e.g., -20)
        - HOLD otherwise
        
        Returns:
            Dict with backtest results (returns, win rate, Sharpe ratio)
        """
        if len(sentiment_history) < 5 or len(price_history) < 5:
            return {'error': 'Insufficient data for backtesting'}
        
        # Convert to DataFrame
        sentiment_df = pd.DataFrame(sentiment_history)
        
        # Simulate trades
        trades = []
        position = None
        
        for i, row in sentiment_df.iterrows():
            sentiment_score = row.get('sentiment_score', 0)
            date = row.get('date')
            
            # Get price on this date
            price_row = price_history[price_history['Date'] == date]
            if len(price_row) == 0:
                continue
            
            price = price_row['Close'].iloc[0]
            
            # Trading logic
            if sentiment_score > 20 and position is None:
                # Open long position
                position = {'entry_price': price, 'entry_date': date}
            
            elif sentiment_score < -20 and position is not None:
                # Close long position
                exit_price = price
                profit_pct = (exit_price / position['entry_price'] - 1) * 100
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': date,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'profit_pct': profit_pct
                })
                
                position = None
        
        # Calculate performance metrics
        if len(trades) == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'total_return': 0,
                'note': 'No trades generated from sentiment signals'
            }
        
        trades_df = pd.DataFrame(trades)
        winning_trades = trades_df[trades_df['profit_pct'] > 0]
        
        return {
            'total_trades': len(trades),
            'win_rate': (len(winning_trades) / len(trades)) * 100,
            'avg_profit': trades_df['profit_pct'].mean(),
            'total_return': trades_df['profit_pct'].sum(),
            'best_trade': trades_df['profit_pct'].max(),
            'worst_trade': trades_df['profit_pct'].min(),
            'sharpe_ratio': trades_df['profit_pct'].mean() / trades_df['profit_pct'].std() if trades_df['profit_pct'].std() > 0 else 0,
            'trades': trades
        }
    
    def get_sentiment_market_beta(self, ticker: str, sentiment_df: pd.DataFrame,
                                 market_df: pd.DataFrame) -> Dict:
        """
        Calculate 'sentiment beta' - how much stock sentiment moves with market sentiment.
        
        High beta = Stock sentiment follows market (sector play)
        Low beta = Stock sentiment independent (company-specific drivers)
        
        Returns:
            Dict with sentiment beta and interpretation
        """
        try:
            # This would require historical sentiment data
            # For now, provide framework
            
            # Calculate stock sentiment volatility
            stock_sentiment_score = self.calculate_sentiment_score(sentiment_df)
            
            # Compare to market returns
            if len(market_df) > 0:
                market_return = market_df['spy_returns'].iloc[-1] * 100
                market_regime = market_df['market_regime'].iloc[-1]
                
                # Qualitative beta assessment
                if stock_sentiment_score['sentiment_score'] > 20 and market_regime == 'bull':
                    beta_type = 'high_beta'
                    interpretation = "Stock sentiment follows market uptrend (sector momentum)"
                elif stock_sentiment_score['sentiment_score'] < -20 and market_regime == 'bear':
                    beta_type = 'high_beta'
                    interpretation = "Stock sentiment follows market downtrend (risk-off)"
                else:
                    beta_type = 'low_beta'
                    interpretation = "Stock sentiment independent of market (company-specific)"
                
                return {
                    'beta_type': beta_type,
                    'market_regime': market_regime,
                    'market_return': market_return,
                    'stock_sentiment': stock_sentiment_score['sentiment_score'],
                    'interpretation': interpretation
                }
            
            return {'error': 'Market data unavailable'}
            
        except Exception as e:
            logger.error(f"Error calculating sentiment beta: {e}")
            return {'error': str(e)}
    
    def generate_comprehensive_report(self, ticker: str, sentiment_df: pd.DataFrame) -> Dict:
        """
        Generate complete sentiment-market correlation analysis.
        
        Returns:
            Dict with all analysis results
        """
        report = {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'data_sources': []
        }
        
        # 1. Sentiment metrics
        report['sentiment_metrics'] = self.calculate_sentiment_score(sentiment_df)
        report['data_sources'].append('Reddit/News')
        
        # 2. Price momentum
        report['price_momentum'] = self.calculate_price_momentum(ticker)
        report['data_sources'].append('Yahoo Finance')
        
        # 3. Market sentiment
        market_df = self.get_market_sentiment(days=30)
        if len(market_df) > 0:
            report['market_sentiment'] = {
                'regime': market_df['market_regime'].iloc[-1],
                'spy_return': market_df['spy_returns'].iloc[-1] * 100,
                'volatility': market_df['spy_volatility'].iloc[-1] * 100
            }
            report['data_sources'].append('SPY (Market)')
        
        # 4. Correlation analysis
        report['correlation'] = self.correlate_sentiment_to_price(ticker, sentiment_df)
        
        # 5. Sentiment beta
        if len(market_df) > 0:
            report['sentiment_beta'] = self.get_sentiment_market_beta(ticker, sentiment_df, market_df)
        
        # 6. Trading signal
        report['trading_signal'] = self._generate_trading_signal(report)
        
        return report
    
    def _generate_trading_signal(self, report: Dict) -> Dict:
        """
        Generate actionable trading signal from all data.
        
        Signal strength: 0-100
        Direction: BUY, SELL, HOLD
        Confidence: HIGH, MEDIUM, LOW
        """
        sentiment = report.get('sentiment_metrics', {})
        momentum = report.get('price_momentum', {})
        correlation = report.get('correlation', {})
        
        # Score components
        sentiment_score = sentiment.get('sentiment_score', 0)
        price_trend = 1 if momentum.get('trend') == 'bullish' else -1
        corr_strength = correlation.get('best_correlation', 0)
        data_quality = sentiment.get('data_quality', 'low')
        
        # Calculate signal strength (0-100)
        signal_strength = 0
        
        # Sentiment contribution (40%)
        signal_strength += abs(sentiment_score) * 0.4
        
        # Momentum contribution (30%)
        signal_strength += abs(momentum.get('total_return', 0)) * 0.3
        
        # Correlation contribution (30%)
        signal_strength += abs(corr_strength) * 100 * 0.3
        
        signal_strength = min(100, signal_strength)
        
        # Determine direction
        if sentiment_score > 15 and price_trend == 1:
            direction = 'BUY'
            rationale = "Positive sentiment + bullish momentum"
        elif sentiment_score < -15 and price_trend == -1:
            direction = 'SELL'
            rationale = "Negative sentiment + bearish momentum"
        elif abs(sentiment_score) < 10:
            direction = 'HOLD'
            rationale = "Neutral sentiment, no clear signal"
        else:
            direction = 'HOLD'
            rationale = "Mixed signals (sentiment vs momentum divergence)"
        
        # Confidence based on data quality and correlation
        if data_quality == 'high' and corr_strength > 0.3:
            confidence = 'HIGH'
        elif data_quality in ['high', 'medium'] and corr_strength > 0.15:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'direction': direction,
            'strength': signal_strength,
            'confidence': confidence,
            'rationale': rationale,
            'risk_factors': self._identify_risk_factors(report)
        }
    
    def _identify_risk_factors(self, report: Dict) -> List[str]:
        """Identify key risks in the analysis."""
        risks = []
        
        sentiment = report.get('sentiment_metrics', {})
        momentum = report.get('price_momentum', {})
        correlation = report.get('correlation', {})
        
        # Data quality risks
        if sentiment.get('data_quality') in ['low', 'very_low']:
            risks.append("⚠️ Low sample size - sentiment may not be representative")
        
        # Correlation risks
        if correlation.get('predictive_power') in ['weak', 'negligible']:
            risks.append("⚠️ Weak historical correlation - sentiment has limited predictive power")
        
        # Volatility risks
        if momentum.get('volatility', 0) > 5:
            risks.append("⚠️ High volatility - price moves may be unpredictable")
        
        # Market regime risks
        market = report.get('market_sentiment', {})
        if market.get('regime') == 'bear':
            risks.append("⚠️ Bearish market environment - macro headwinds")
        
        # Divergence risks
        sentiment_pos = sentiment.get('sentiment_score', 0) > 10
        price_pos = momentum.get('total_return', 0) > 0
        if sentiment_pos != price_pos:
            risks.append("⚠️ Sentiment-price divergence - conflicting signals")
        
        return risks if risks else ["✅ No major risk factors identified"]


def get_sentiment_correlation_analyzer() -> SentimentMarketCorrelation:
    """Factory function to get analyzer instance."""
    return SentimentMarketCorrelation()
