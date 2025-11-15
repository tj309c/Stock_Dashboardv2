"""
Arbitrage Detection Engine
Scans for crypto triangular arbitrage and statistical arbitrage opportunities.

Strategies:
1. Triangular Arbitrage: BTC/USDT → ETH/BTC → ETH/USDT cycles (same exchange)
2. Cross-Exchange Arbitrage: Buy on Binance, sell on Coinbase simultaneously
3. Statistical Arbitrage: Mean-reversion pairs trading (cointegrated stocks)

Dependencies:
- ccxt: Multi-exchange cryptocurrency data
- statsmodels: Cointegration testing (Engle-Granger, Johansen)
- scipy: Statistical analysis
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from itertools import combinations

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

try:
    from statsmodels.tsa.stattools import coint, adfuller
    from statsmodels.tsa.vector_ar.vecm import coint_johansen
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CryptoArbitrageScanner:
    """
    Detects crypto arbitrage opportunities across multiple exchanges.
    """
    
    def __init__(self, exchanges: List[str] = None):
        """
        Initialize with list of exchanges to monitor.
        
        Args:
            exchanges: List of ccxt exchange names (default: ['binance', 'coinbase', 'kraken'])
        """
        if not CCXT_AVAILABLE:
            raise ImportError("ccxt not installed. Run: pip install ccxt")
        
        self.exchanges = exchanges or ['binance', 'coinbase', 'kraken', 'bybit', 'okx']
        self.exchange_instances = {}
        
        for name in self.exchanges:
            try:
                exchange_class = getattr(ccxt, name)
                self.exchange_instances[name] = exchange_class()
                logger.info(f"Initialized {name} exchange")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
    
    # =========================================================================
    # Triangular Arbitrage (Same Exchange)
    # =========================================================================
    
    def calculate_triangular_arbitrage(self, exchange_name: str, base: str = 'BTC', 
                                      quote: str = 'USDT', intermediate: str = 'ETH') -> Optional[Dict]:
        """
        Calculate profit from triangular arbitrage cycle.
        
        Example cycle:
        1. Buy ETH with USDT (ETH/USDT)
        2. Buy BTC with ETH (BTC/ETH)
        3. Sell BTC for USDT (BTC/USDT)
        
        If final USDT > initial USDT (after fees), there's an arbitrage opportunity.
        
        Args:
            exchange_name: Exchange to scan
            base: Base currency (e.g., BTC)
            quote: Quote currency (e.g., USDT)
            intermediate: Intermediate currency (e.g., ETH)
            
        Returns:
            Dictionary with profit percentage, cycle details
        """
        if exchange_name not in self.exchange_instances:
            return None
        
        exchange = self.exchange_instances[exchange_name]
        
        try:
            # Fetch order books for 3 pairs
            pair1 = f"{intermediate}/{quote}"  # ETH/USDT
            pair2 = f"{base}/{intermediate}"   # BTC/ETH
            pair3 = f"{base}/{quote}"          # BTC/USDT
            
            ticker1 = exchange.fetch_ticker(pair1)
            ticker2 = exchange.fetch_ticker(pair2)
            ticker3 = exchange.fetch_ticker(pair3)
            
            # Simulate cycle with 1000 USDT
            initial_capital = 1000.0
            fee_rate = 0.001  # 0.1% per trade (typical maker fee)
            
            # Step 1: Buy intermediate with quote (e.g., buy ETH with USDT)
            step1_price = ticker1['ask']  # Buy at ask
            step1_amount = initial_capital / step1_price * (1 - fee_rate)
            
            # Step 2: Buy base with intermediate (e.g., buy BTC with ETH)
            step2_price = ticker2['ask']
            step2_amount = step1_amount / step2_price * (1 - fee_rate)
            
            # Step 3: Sell base for quote (e.g., sell BTC for USDT)
            step3_price = ticker3['bid']  # Sell at bid
            final_capital = step2_amount * step3_price * (1 - fee_rate)
            
            # Calculate profit
            profit = final_capital - initial_capital
            profit_pct = (profit / initial_capital) * 100
            
            # Arbitrage is profitable if profit > transaction costs
            is_opportunity = profit_pct > 0.1  # At least 0.1% profit to be worthwhile
            
            return {
                'exchange': exchange_name,
                'cycle': f"{quote} → {pair1} → {pair2} → {pair3} → {quote}",
                'initial_capital': initial_capital,
                'final_capital': final_capital,
                'profit': profit,
                'profit_pct': profit_pct,
                'is_opportunity': is_opportunity,
                'timestamp': datetime.now(),
                'prices': {
                    pair1: step1_price,
                    pair2: step2_price,
                    pair3: step3_price
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating triangular arbitrage on {exchange_name}: {e}")
            return None
    
    @st.cache_data(ttl=30, show_spinner=False)  # 30-second cache for arbitrage
    def scan_all_triangular_opportunities(_self, base: str = 'BTC', quote: str = 'USDT',
                                         intermediates: List[str] = None) -> List[Dict]:
        """
        Scan all exchanges for triangular arbitrage opportunities.
        
        Args:
            base: Base currency
            quote: Quote currency
            intermediates: List of intermediate currencies to test
            
        Returns:
            List of arbitrage opportunities sorted by profit percentage
        """
        if intermediates is None:
            intermediates = ['ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'MATIC']
        
        opportunities = []
        
        for exchange_name in _self.exchange_instances.keys():
            for intermediate in intermediates:
                result = _self.calculate_triangular_arbitrage(
                    exchange_name, base, quote, intermediate
                )
                
                if result and result['is_opportunity']:
                    opportunities.append(result)
        
        # Sort by profit percentage descending
        opportunities.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        return opportunities
    
    # =========================================================================
    # Cross-Exchange Arbitrage
    # =========================================================================
    
    @st.cache_data(ttl=30, show_spinner=False)
    def scan_cross_exchange_arbitrage(_self, symbol: str = 'BTC/USDT') -> List[Dict]:
        """
        Find price discrepancies for same trading pair across exchanges.
        
        Example: If BTC/USDT is $40,000 on Binance but $40,500 on Coinbase,
        buy on Binance and sell on Coinbase for $500 profit per BTC.
        
        Args:
            symbol: Trading pair to scan
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        prices = {}
        
        # Fetch prices from all exchanges
        for exchange_name, exchange in _self.exchange_instances.items():
            try:
                ticker = exchange.fetch_ticker(symbol)
                prices[exchange_name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last']
                }
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol} from {exchange_name}: {e}")
        
        if len(prices) < 2:
            return []
        
        # Compare all pairs of exchanges
        exchange_names = list(prices.keys())
        
        for buy_exchange, sell_exchange in combinations(exchange_names, 2):
            # Buy on buy_exchange at ask, sell on sell_exchange at bid
            buy_price = prices[buy_exchange]['ask']
            sell_price = prices[sell_exchange]['bid']
            
            # Assume 0.1% fee on each exchange
            fee_rate = 0.001
            buy_cost = buy_price * (1 + fee_rate)
            sell_revenue = sell_price * (1 - fee_rate)
            
            profit = sell_revenue - buy_cost
            profit_pct = (profit / buy_cost) * 100
            
            # Account for withdrawal fees (rough estimate: 0.0005 BTC = ~$20)
            withdrawal_fee = 0.0005 * buy_price
            net_profit = profit - withdrawal_fee
            net_profit_pct = (net_profit / buy_cost) * 100
            
            if net_profit_pct > 0.5:  # At least 0.5% profit after all costs
                opportunities.append({
                    'symbol': symbol,
                    'buy_exchange': buy_exchange,
                    'sell_exchange': sell_exchange,
                    'buy_price': buy_cost,
                    'sell_price': sell_revenue,
                    'profit_per_unit': profit,
                    'profit_pct': profit_pct,
                    'net_profit_pct': net_profit_pct,
                    'withdrawal_fee': withdrawal_fee,
                    'timestamp': datetime.now()
                })
        
        # Sort by net profit percentage
        opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)
        
        return opportunities


class StatisticalArbitrageScanner:
    """
    Detects statistical arbitrage opportunities (pairs trading) in stock markets.
    
    Uses cointegration testing to find historically correlated stock pairs that
    temporarily diverge, then mean-revert.
    """
    
    def __init__(self):
        """Initialize statistical arbitrage scanner."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not installed. Run: pip install statsmodels")
    
    # =========================================================================
    # Cointegration Testing
    # =========================================================================
    
    def test_cointegration(self, price_series1: pd.Series, price_series2: pd.Series) -> Dict:
        """
        Test if two price series are cointegrated (move together in long run).
        
        Uses Engle-Granger two-step method.
        
        Args:
            price_series1: First stock's price series
            price_series2: Second stock's price series
            
        Returns:
            Dictionary with p-value, test statistic, cointegrated boolean
        """
        try:
            # Run cointegration test
            score, pvalue, _ = coint(price_series1, price_series2)
            
            # If p-value < 0.05, stocks are cointegrated
            is_cointegrated = pvalue < 0.05
            
            return {
                'test_statistic': score,
                'p_value': pvalue,
                'is_cointegrated': is_cointegrated,
                'confidence_level': '95%' if pvalue < 0.05 else 'Not Significant'
            }
            
        except Exception as e:
            logger.error(f"Error testing cointegration: {e}")
            return {'error': str(e)}
    
    def calculate_zscore(self, spread: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate z-score of spread (standardized deviation from mean).
        
        Z-score interpretation:
        - |z| > 2: Extreme divergence, expect mean reversion
        - |z| < 1: Normal relationship
        
        Args:
            spread: Price spread series (stock1 - hedge_ratio * stock2)
            window: Rolling window for mean/std calculation
            
        Returns:
            Z-score series
        """
        spread_mean = spread.rolling(window=window).mean()
        spread_std = spread.rolling(window=window).std()
        
        zscore = (spread - spread_mean) / spread_std
        
        return zscore
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def find_cointegrated_pairs(_self, tickers: List[str], price_data: Dict[str, pd.Series]) -> List[Dict]:
        """
        Test all combinations of tickers for cointegration.
        
        Args:
            tickers: List of stock tickers
            price_data: Dictionary mapping ticker -> price series
            
        Returns:
            List of cointegrated pairs sorted by strength
        """
        pairs = []
        
        for ticker1, ticker2 in combinations(tickers, 2):
            if ticker1 not in price_data or ticker2 not in price_data:
                continue
            
            series1 = price_data[ticker1].dropna()
            series2 = price_data[ticker2].dropna()
            
            # Align series
            common_idx = series1.index.intersection(series2.index)
            series1 = series1.loc[common_idx]
            series2 = series2.loc[common_idx]
            
            if len(series1) < 30:  # Need minimum data points
                continue
            
            result = _self.test_cointegration(series1, series2)
            
            if result.get('is_cointegrated'):
                # Calculate hedge ratio (beta from OLS regression)
                hedge_ratio = np.polyfit(series2, series1, 1)[0]
                
                # Calculate spread
                spread = series1 - hedge_ratio * series2
                
                # Calculate current z-score
                zscore = _self.calculate_zscore(spread)
                current_zscore = zscore.iloc[-1]
                
                pairs.append({
                    'ticker1': ticker1,
                    'ticker2': ticker2,
                    'p_value': result['p_value'],
                    'hedge_ratio': hedge_ratio,
                    'current_zscore': current_zscore,
                    'spread': spread,
                    'zscore_series': zscore
                })
        
        # Sort by p-value (lower = stronger cointegration)
        pairs.sort(key=lambda x: x['p_value'])
        
        return pairs
    
    def generate_trading_signals(self, zscore: pd.Series, entry_threshold: float = 2.0,
                                exit_threshold: float = 0.5) -> pd.DataFrame:
        """
        Generate buy/sell signals based on z-score thresholds.
        
        Strategy:
        - When z-score > +2: Short pair (sell stock1, buy stock2)
        - When z-score < -2: Long pair (buy stock1, sell stock2)
        - When |z-score| < 0.5: Exit position (mean reversion complete)
        
        Args:
            zscore: Z-score time series
            entry_threshold: Z-score threshold to enter trade
            exit_threshold: Z-score threshold to exit trade
            
        Returns:
            DataFrame with signals (-1 = short, 0 = neutral, 1 = long)
        """
        signals = pd.DataFrame(index=zscore.index)
        signals['zscore'] = zscore
        signals['signal'] = 0
        
        # Entry signals
        signals.loc[zscore > entry_threshold, 'signal'] = -1  # Short
        signals.loc[zscore < -entry_threshold, 'signal'] = 1   # Long
        
        # Exit signals (override entry)
        signals.loc[abs(zscore) < exit_threshold, 'signal'] = 0
        
        return signals
    
    def backtest_pair_strategy(self, ticker1: str, ticker2: str, 
                               price1: pd.Series, price2: pd.Series,
                               hedge_ratio: float) -> Dict:
        """
        Backtest pairs trading strategy on historical data.
        
        Args:
            ticker1: First stock ticker
            ticker2: Second stock ticker
            price1: First stock's price series
            price2: Second stock's price series
            hedge_ratio: Hedge ratio from cointegration test
            
        Returns:
            Dictionary with performance metrics
        """
        # Calculate spread and z-score
        spread = price1 - hedge_ratio * price2
        zscore = self.calculate_zscore(spread)
        
        # Generate signals
        signals = self.generate_trading_signals(zscore)
        
        # Calculate returns
        # Long pair: +return when spread increases (z-score rises)
        # Short pair: +return when spread decreases (z-score falls)
        spread_returns = spread.pct_change()
        strategy_returns = signals['signal'].shift(1) * spread_returns
        
        # Performance metrics
        total_return = (1 + strategy_returns).prod() - 1
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
        max_drawdown = (strategy_returns.cumsum().cummax() - strategy_returns.cumsum()).max()
        
        return {
            'ticker1': ticker1,
            'ticker2': ticker2,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': (signals['signal'].diff() != 0).sum(),
            'current_signal': signals['signal'].iloc[-1],
            'current_zscore': zscore.iloc[-1]
        }


# Convenience functions
def get_crypto_arbitrage_scanner(exchanges: List[str] = None) -> CryptoArbitrageScanner:
    """Factory function for crypto arbitrage scanner."""
    return CryptoArbitrageScanner(exchanges)


def get_statistical_arbitrage_scanner() -> StatisticalArbitrageScanner:
    """Factory function for statistical arbitrage scanner."""
    return StatisticalArbitrageScanner()
