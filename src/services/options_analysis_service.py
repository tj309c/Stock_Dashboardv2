"""
Options Analysis Service
Pure business logic for options analysis - NO Streamlit dependencies
Returns type-safe OptionsChain and related objects
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats
import logging

from src.core.types import (
    OptionsChain,
    OptionContract,
    GreeksData,
    UnusualActivity
)
from src.core.errors import (
    DataFetchError,
    AnalysisError,
    InsufficientDataError
)

logger = logging.getLogger(__name__)


class OptionsAnalysisService:
    """
    Business logic for options analysis
    
    Key Features:
    - Zero Streamlit dependencies
    - Type-safe returns (OptionsChain, OptionContract, etc.)
    - Greeks calculation (Black-Scholes)
    - Unusual activity detection
    - Strategy recommendations
    
    Usage:
        service = OptionsAnalysisService(components)
        chain = service.analyze_options_chain("SPY")
        strategies = service.get_strategy_recommendations(chain, 450)
    """
    
    def __init__(self, components: Dict):
        """
        Initialize service with required components
        
        Args:
            components: Dict containing:
                - fetcher: MarketDataFetcher
                - options: OptionsAnalyzer (optional)
        """
        self.fetcher = components.get("fetcher")
        self.options_analyzer = components.get("options")
        
        if not self.fetcher:
            raise ValueError("Missing required component: fetcher")
    
    # ========== MAIN ANALYSIS ==========
    
    def analyze_options_chain(
        self, 
        ticker: str,
        include_greeks: bool = True,
        include_unusual: bool = True
    ) -> OptionsChain:
        """
        Fetch and analyze complete options chain
        
        Args:
            ticker: Stock ticker symbol
            include_greeks: Calculate Greeks for all contracts
            include_unusual: Detect unusual activity
        
        Returns:
            OptionsChain with all options data
        
        Raises:
            DataFetchError: If data cannot be fetched
            AnalysisError: If analysis fails
        """
        try:
            # Fetch options data
            options_data = self.fetcher.get_options_chain(ticker)
            if not options_data or "error" in options_data:
                raise DataFetchError(f"Cannot fetch options for {ticker}")
            
            # Get current stock price
            quote = self.fetcher.get_realtime_quote(ticker)
            current_price = quote.get("price", 0)
            
            if current_price == 0:
                raise DataFetchError(f"Cannot get current price for {ticker}")
            
            # Store raw data for later use
            self._raw_chains_data = options_data.get("chains", {})
            self._ticker = ticker
            self._spot_price = current_price
            
            # Extract expirations and convert to datetime
            exp_strings = list(options_data.get("chains", {}).keys())
            exp_dates = []
            for exp_str in exp_strings:
                try:
                    exp_dates.append(datetime.strptime(exp_str, "%Y-%m-%d"))
                except:
                    pass
            
            # Build OptionsChain (empty calls/puts - populated on demand)
            return OptionsChain(
                ticker=ticker,
                spot_price=current_price,
                expiration_dates=exp_dates,
                calls=[],
                puts=[]
            )
            
        except DataFetchError:
            raise
        except Exception as e:
            logger.error(f"Error analyzing options chain for {ticker}: {e}")
            raise AnalysisError(f"Failed to analyze options: {str(e)}")
    
    def get_contracts_by_expiration(
        self, 
        ticker: str,
        expiration: str,
        option_type: str = "both"
    ) -> List[OptionContract]:
        """
        Get option contracts for specific expiration
        
        Args:
            ticker: Stock ticker
            expiration: Expiration date string (YYYY-MM-DD)
            option_type: 'calls', 'puts', or 'both'
        
        Returns:
            List of OptionContract objects
        """
        contracts = []
        
        # Use cached raw data if available and matches ticker
        if hasattr(self, '_raw_chains_data') and hasattr(self, '_ticker') and self._ticker == ticker:
            chains_data = self._raw_chains_data
        else:
            # Fetch fresh data
            options_data = self.fetcher.get_options_chain(ticker)
            if not options_data or "error" in options_data:
                return contracts
            chains_data = options_data.get("chains", {})
        
        if expiration not in chains_data:
            return contracts
        
        exp_data = chains_data[expiration]
        
        # Process calls
        if option_type in ["both", "calls"] and "calls" in exp_data:
            for call_data in exp_data["calls"]:
                # Handle both dict and string types
                if isinstance(call_data, dict):
                    contracts.append(self._dict_to_contract(call_data, "call", expiration))
        
        # Process puts
        if option_type in ["both", "puts"] and "puts" in exp_data:
            for put_data in exp_data["puts"]:
                # Handle both dict and string types
                if isinstance(put_data, dict):
                    contracts.append(self._dict_to_contract(put_data, "put", expiration))
        
        return contracts
    
    # ========== GREEKS CALCULATION ==========
    
    def calculate_greeks(
        self, 
        spot_price: float,
        strike: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float = 0.045,
        option_type: str = "call"
    ) -> GreeksData:
        """
        Calculate Black-Scholes Greeks
        
        Args:
            spot_price: Current stock price
            strike: Option strike price
            time_to_expiry: Time to expiration in years
            volatility: Implied volatility (decimal, e.g., 0.25 for 25%)
            risk_free_rate: Risk-free rate (decimal)
            option_type: 'call' or 'put'
        
        Returns:
            GreeksData with delta, gamma, theta, vega, rho
        """
        try:
            if time_to_expiry <= 0:
                time_to_expiry = 1 / 365  # 1 day minimum
            
            # Black-Scholes calculation
            S = spot_price
            K = strike
            T = time_to_expiry
            r = risk_free_rate
            sigma = volatility
            
            # d1 and d2
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            # Delta
            if option_type.lower() == "call":
                delta = stats.norm.cdf(d1)
            else:
                delta = stats.norm.cdf(d1) - 1
            
            # Gamma (same for calls and puts)
            gamma = stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
            
            # Theta (daily)
            if option_type.lower() == "call":
                theta = (-(S * stats.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                        - r * K * np.exp(-r * T) * stats.norm.cdf(d2)) / 365
            else:
                theta = (-(S * stats.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                        + r * K * np.exp(-r * T) * stats.norm.cdf(-d2)) / 365
            
            # Vega (per 1% change in IV)
            vega = S * stats.norm.pdf(d1) * np.sqrt(T) / 100
            
            # Rho (per 1% change in interest rate)
            if option_type.lower() == "call":
                rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2) / 100
            else:
                rho = -K * T * np.exp(-r * T) * stats.norm.cdf(-d2) / 100
            
            return GreeksData(
                delta=delta,
                gamma=gamma,
                theta=theta,
                vega=vega,
                rho=rho
            )
            
        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")
            return GreeksData(delta=0, gamma=0, theta=0, vega=0, rho=0)
    
    # ========== UNUSUAL ACTIVITY ==========
    
    def detect_unusual_activity(
        self, 
        ticker: str,
        volume_threshold: float = 2.0,
        min_volume: int = 100
    ) -> List[UnusualActivity]:
        """
        Detect unusual options activity
        
        Args:
            ticker: Stock ticker
            volume_threshold: Volume/OI ratio threshold
            min_volume: Minimum volume to consider
        
        Returns:
            List of UnusualActivity objects
        """
        unusual = []
        
        # Get all expirations from raw data or fetch fresh
        if hasattr(self, '_raw_chains_data') and hasattr(self, '_ticker') and self._ticker == ticker:
            exp_strings = list(self._raw_chains_data.keys())
        else:
            options_data = self.fetcher.get_options_chain(ticker)
            if not options_data or "error" in options_data:
                return unusual
            exp_strings = list(options_data.get("chains", {}).keys())
        
        for expiration in exp_strings:
            contracts = self.get_contracts_by_expiration(ticker, expiration)
            
            for contract in contracts:
                # Check for unusual volume
                if contract.volume >= min_volume and contract.open_interest > 0:
                    vol_oi_ratio = contract.volume / contract.open_interest
                    
                    if vol_oi_ratio >= volume_threshold:
                        unusual.append(UnusualActivity(
                            contract=contract,
                            unusual_score=min(100, vol_oi_ratio * 20),
                            reason=f"High Vol/OI ratio: {vol_oi_ratio:.2f}x",
                            premium_value=contract.last_price * contract.volume * 100,
                            detected_at=datetime.now()
                        ))
        
        # Sort by unusual score
        unusual.sort(key=lambda x: x.unusual_score, reverse=True)
        
        return unusual[:20]  # Top 20
    
    # ========== STRATEGY RECOMMENDATIONS ==========
    
    def get_strategy_recommendations(
        self, 
        ticker: str,
        current_price: float,
        outlook: str = "neutral"
    ) -> List[Dict]:
        """
        Get options strategy recommendations
        
        Args:
            ticker: Stock ticker
            current_price: Current stock price
            outlook: 'bullish', 'bearish', or 'neutral'
        
        Returns:
            List of strategy dictionaries with details
        """
        strategies = []
        
        # Get expirations
        if hasattr(self, '_raw_chains_data') and hasattr(self, '_ticker') and self._ticker == ticker:
            exp_strings = list(self._raw_chains_data.keys())
        else:
            options_data = self.fetcher.get_options_chain(ticker)
            if not options_data or "error" in options_data:
                return strategies
            exp_strings = list(options_data.get("chains", {}).keys())
        
        if not exp_strings:
            return strategies
        
        # Get nearest expiration (usually most liquid)
        nearest_exp = exp_strings[0]
        contracts = self.get_contracts_by_expiration(ticker, nearest_exp)
        
        if outlook == "bullish":
            strategies.extend(self._bullish_strategies(contracts, current_price, nearest_exp))
        elif outlook == "bearish":
            strategies.extend(self._bearish_strategies(contracts, current_price, nearest_exp))
        else:
            strategies.extend(self._neutral_strategies(contracts, current_price, nearest_exp))
        
        return strategies
    
    def calculate_covered_call(
        self, 
        stock_price: float,
        strike: float,
        premium: float,
        shares: int = 100
    ) -> Dict:
        """
        Calculate covered call metrics
        
        Args:
            stock_price: Current stock price
            strike: Call strike price
            premium: Call premium per share
            shares: Number of shares (default 100)
        
        Returns:
            Dict with max profit, max loss, breakeven
        """
        premium_income = premium * shares
        
        return {
            "strategy": "Covered Call",
            "max_profit": (strike - stock_price) * shares + premium_income,
            "max_loss": float('inf'),  # Unlimited downside risk
            "breakeven": stock_price - premium,
            "premium_income": premium_income,
            "return_on_capital": ((strike - stock_price + premium) / stock_price) * 100 if stock_price > 0 else 0
        }
    
    def calculate_vertical_spread(
        self,
        long_strike: float,
        short_strike: float,
        long_premium: float,
        short_premium: float,
        spread_type: str = "bull_call"
    ) -> Dict:
        """
        Calculate vertical spread metrics
        
        Args:
            long_strike: Long option strike
            short_strike: Short option strike
            long_premium: Premium paid for long
            short_premium: Premium received for short
            spread_type: 'bull_call', 'bear_put', etc.
        
        Returns:
            Dict with max profit, max loss, breakeven
        """
        net_debit = (long_premium - short_premium) * 100
        spread_width = abs(long_strike - short_strike) * 100
        
        if "call" in spread_type:
            max_profit = spread_width - net_debit
            max_loss = net_debit
            breakeven = long_strike + (net_debit / 100)
        else:  # Put spread
            max_profit = spread_width - net_debit
            max_loss = net_debit
            breakeven = long_strike - (net_debit / 100)
        
        return {
            "strategy": spread_type.replace("_", " ").title(),
            "max_profit": max_profit,
            "max_loss": max_loss,
            "breakeven": breakeven,
            "net_debit": net_debit,
            "risk_reward_ratio": max_profit / max_loss if max_loss > 0 else 0
        }
    
    def calculate_iron_condor(
        self,
        put_buy_strike: float,
        put_sell_strike: float,
        call_sell_strike: float,
        call_buy_strike: float,
        put_buy_premium: float,
        put_sell_premium: float,
        call_sell_premium: float,
        call_buy_premium: float
    ) -> Dict:
        """
        Calculate iron condor metrics
        
        Returns:
            Dict with max profit, max loss, breakevens
        """
        # Net credit received
        net_credit = ((put_sell_premium - put_buy_premium) + 
                     (call_sell_premium - call_buy_premium)) * 100
        
        # Max loss (widest spread minus credit)
        put_spread_width = (put_sell_strike - put_buy_strike) * 100
        call_spread_width = (call_buy_strike - call_sell_strike) * 100
        max_loss = max(put_spread_width, call_spread_width) - net_credit
        
        return {
            "strategy": "Iron Condor",
            "max_profit": net_credit,
            "max_loss": max_loss,
            "lower_breakeven": put_sell_strike - (net_credit / 100),
            "upper_breakeven": call_sell_strike + (net_credit / 100),
            "net_credit": net_credit,
            "probability_of_profit": self._estimate_pop(
                put_sell_strike, call_sell_strike, 
                (put_buy_strike + call_buy_strike) / 2  # Approx current price
            )
        }
    
    # ========== VOLATILITY ANALYSIS ==========
    
    def calculate_iv_metrics(
        self, 
        ticker: str,
        expiration: str,
        spot_price: float
    ) -> Dict:
        """
        Calculate IV rank and percentile
        
        Args:
            ticker: Stock ticker
            expiration: Expiration date
            spot_price: Current stock price
        
        Returns:
            Dict with IV rank, percentile, skew
        """
        contracts = self.get_contracts_by_expiration(ticker, expiration)
        
        if not contracts:
            return {"error": "No contracts found"}
        
        ivs = [c.implied_volatility for c in contracts if c.implied_volatility > 0]
        
        if not ivs:
            return {"error": "No IV data"}
        
        avg_iv = np.mean(ivs)
        min_iv = np.min(ivs)
        max_iv = np.max(ivs)
        
        # IV Rank (0-100)
        iv_range = max_iv - min_iv
        iv_rank = ((avg_iv - min_iv) / iv_range * 100) if iv_range > 0 else 50
        
        return {
            "average_iv": avg_iv * 100,  # Convert to percentage
            "min_iv": min_iv * 100,
            "max_iv": max_iv * 100,
            "iv_rank": iv_rank,
            "iv_percentile": iv_rank,  # Simplified - would need historical data for true percentile
            "volatility_skew": self._calculate_skew(contracts, spot_price)
        }
    
    # ========== HELPERS ==========
    
    def _dict_to_contract(self, data: Dict, contract_type: str, expiration: str) -> OptionContract:
        """Convert dict to OptionContract"""
        return OptionContract(
            contract_type=contract_type,
            strike=data.get("strike", 0),
            expiration=expiration,
            last_price=data.get("lastPrice", 0),
            bid=data.get("bid", 0),
            ask=data.get("ask", 0),
            volume=data.get("volume", 0),
            open_interest=data.get("openInterest", 0),
            implied_volatility=data.get("impliedVolatility", 0)
        )
    
    def _bullish_strategies(self, contracts: List[OptionContract], price: float, exp: str) -> List[Dict]:
        """Generate bullish strategy recommendations"""
        strategies = []
        
        # Find slightly OTM call
        calls = [c for c in contracts if c.contract_type == "call" and c.strike > price]
        if calls:
            call = min(calls, key=lambda x: abs(x.strike - price * 1.02))
            strategies.append({
                "name": "Long Call",
                "type": "bullish",
                "strike": call.strike,
                "premium": call.last_price,
                "expiration": exp,
                "max_risk": call.last_price * 100,
                "max_reward": "Unlimited",
                "breakeven": call.strike + call.last_price
            })
        
        return strategies
    
    def _bearish_strategies(self, contracts: List[OptionContract], price: float, exp: str) -> List[Dict]:
        """Generate bearish strategy recommendations"""
        strategies = []
        
        # Find slightly OTM put
        puts = [c for c in contracts if c.contract_type == "put" and c.strike < price]
        if puts:
            put = max(puts, key=lambda x: x.strike if x.strike < price * 0.98 else 0)
            strategies.append({
                "name": "Long Put",
                "type": "bearish",
                "strike": put.strike,
                "premium": put.last_price,
                "expiration": exp,
                "max_risk": put.last_price * 100,
                "max_reward": (put.strike - put.last_price) * 100,
                "breakeven": put.strike - put.last_price
            })
        
        return strategies
    
    def _neutral_strategies(self, contracts: List[OptionContract], price: float, exp: str) -> List[Dict]:
        """Generate neutral strategy recommendations"""
        strategies = []
        
        # Find ATM call for covered call
        calls = [c for c in contracts if c.contract_type == "call"]
        if calls:
            atm_call = min(calls, key=lambda x: abs(x.strike - price))
            cc_metrics = self.calculate_covered_call(price, atm_call.strike, atm_call.last_price)
            strategies.append({
                "name": "Covered Call",
                "type": "neutral",
                "strike": atm_call.strike,
                "premium": atm_call.last_price,
                "expiration": exp,
                **cc_metrics
            })
        
        return strategies
    
    def _calculate_skew(self, contracts: List[OptionContract], spot_price: float) -> float:
        """Calculate volatility skew"""
        otm_puts = [c for c in contracts if c.contract_type == "put" and c.strike < spot_price * 0.95]
        otm_calls = [c for c in contracts if c.contract_type == "call" and c.strike > spot_price * 1.05]
        
        if otm_puts and otm_calls:
            avg_put_iv = np.mean([c.implied_volatility for c in otm_puts if c.implied_volatility > 0])
            avg_call_iv = np.mean([c.implied_volatility for c in otm_calls if c.implied_volatility > 0])
            return (avg_put_iv - avg_call_iv) * 100  # Percentage difference
        
        return 0.0
    
    def _estimate_pop(self, lower_strike: float, upper_strike: float, current_price: float) -> float:
        """Estimate probability of profit (simplified)"""
        range_width = upper_strike - lower_strike
        distance_from_center = abs(current_price - (upper_strike + lower_strike) / 2)
        
        # Simple linear approximation
        pop = max(0, min(100, (1 - distance_from_center / (range_width / 2)) * 100))
        return pop
