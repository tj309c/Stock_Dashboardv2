"""
Stocks Analysis Service
Pure business logic for stock analysis - NO Streamlit dependencies
Returns type-safe StockAnalysisResult objects
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from src.core.types import (
    StockPrice,
    TechnicalIndicators,
    FundamentalMetrics,
    RiskMetrics,
    ValuationResult,
    TradeSignal,
    StockAnalysisResult,
    Signal,
    Trend,
    ValuationMethod
)
from src.core.errors import (
    DataFetchError,
    AnalysisError,
    ValuationError,
    InsufficientDataError
)

logger = logging.getLogger(__name__)


class StocksAnalysisService:
    """
    Business logic for stock analysis
    
    Key Features:
    - Zero Streamlit dependencies
    - Type-safe returns (StockAnalysisResult)
    - Comprehensive error handling
    - Testable with mock data
    
    Usage:
        service = StocksAnalysisService(components)
        result = service.analyze_stock("AAPL")
        signals = service.calculate_buy_signals(result)
    """
    
    def __init__(self, components: Dict):
        """
        Initialize service with required components
        
        Args:
            components: Dict containing:
                - fetcher: MarketDataFetcher
                - valuation: ValuationEngine
                - technical: TechnicalAnalysis
                - goodbuy: GoodBuyAnalyzer (optional)
                - sentiment: SentimentAnalyzer (optional)
        """
        self.fetcher = components.get("fetcher")
        self.valuation_engine = components.get("valuation")
        self.technical_engine = components.get("technical")
        self.goodbuy_analyzer = components.get("goodbuy")
        self.sentiment_analyzer = components.get("sentiment")
        
        if not self.fetcher or not self.valuation_engine or not self.technical_engine:
            raise ValueError("Missing required components: fetcher, valuation, technical")
    
    # ========== MAIN ANALYSIS ==========
    
    def analyze_stock(self, ticker: str, include_sentiment: bool = True) -> StockAnalysisResult:
        """
        Perform comprehensive stock analysis
        
        Args:
            ticker: Stock ticker symbol
            include_sentiment: Whether to include sentiment analysis
        
        Returns:
            StockAnalysisResult with all analysis data
        
        Raises:
            DataFetchError: If data cannot be fetched
            AnalysisError: If analysis fails
        """
        try:
            # Fetch market data
            data = self._fetch_stock_data(ticker, include_sentiment)
            
            # Extract components
            info = data["stock_data"].get("info", {})
            df = data.get("df", pd.DataFrame())
            quote = data.get("quote", {})
            fundamentals = data.get("fundamentals", {})
            
            # Build type-safe objects
            price = self._extract_stock_price(info, quote)
            technical = self._calculate_technical_indicators(df, info)
            fundamental = self._extract_fundamentals(info, fundamentals)
            risk = self._calculate_risk_metrics(df, info, fundamental)
            valuation = self._calculate_valuation(fundamentals, info)
            signals = self._generate_trade_signals(price, technical, fundamental, valuation, info, df)
            
            return StockAnalysisResult(
                ticker=ticker,
                timestamp=datetime.now(),
                price=price,
                technical=technical,
                fundamentals=fundamental,
                risk=risk,
                valuation=valuation,
                signals=signals,
                metadata={"raw_data": data}  # Store raw data in metadata
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            raise AnalysisError(f"Failed to analyze {ticker}: {str(e)}")
    
    def calculate_buy_signals(self, analysis: StockAnalysisResult) -> List[TradeSignal]:
        """
        Extract buy/sell signals from analysis
        
        Args:
            analysis: StockAnalysisResult object
        
        Returns:
            List of TradeSignal objects
        """
        return analysis.signals
    
    def get_technical_summary(self, analysis: StockAnalysisResult) -> Dict:
        """
        Get technical analysis summary
        
        Args:
            analysis: StockAnalysisResult object
        
        Returns:
            Dict with technical summary
        """
        technical = analysis.technical
        
        return {
            "trend": technical.get_trend().value,
            "momentum_score": technical.get_momentum_score(),
            "is_overbought": technical.is_overbought(),
            "is_oversold": technical.is_oversold(),
            "rsi": technical.rsi,
            "macd_signal": "BULLISH" if technical.macd > technical.macd_signal else "BEARISH",
            "sma_alignment": self._get_sma_alignment(technical),
            "strength": "STRONG" if technical.adx > 25 else "WEAK"
        }
    
    def get_valuation_summary(self, analysis: StockAnalysisResult) -> Dict:
        """
        Get valuation summary
        
        Args:
            analysis: StockAnalysisResult object
        
        Returns:
            Dict with valuation summary
        """
        valuation = analysis.valuation
        
        return {
            "recommendation": valuation.get_recommendation().value,
            "is_undervalued": valuation.is_undervalued(),
            "fair_value": valuation.fair_value,
            "current_price": analysis.price.current,
            "upside_percent": valuation.upside_pct,
            "confidence": valuation.confidence,
            "method": valuation.method.value
        }
    
    def get_overall_score(self, analysis: StockAnalysisResult) -> float:
        """
        Get overall investment score
        
        Args:
            analysis: StockAnalysisResult object
        
        Returns:
            Score from 0-100
        """
        return analysis.get_overall_score()
    
    # ========== DATA FETCHING ==========
    
    def _fetch_stock_data(self, ticker: str, include_sentiment: bool) -> Dict:
        """Fetch comprehensive stock data"""
        try:
            # Basic stock data
            stock_data = self.fetcher.get_stock_data(ticker)
            if not stock_data or "error" in stock_data:
                raise DataFetchError(f"Cannot fetch data for {ticker}")
            
            # Real-time quote
            quote = self.fetcher.get_realtime_quote(ticker)
            
            # Fundamentals
            fundamentals = self.fetcher.get_fundamentals(ticker)
            
            # Build DataFrame
            df = pd.DataFrame()
            if "history" in stock_data:
                df = pd.DataFrame(stock_data["history"])
                if not df.empty:
                    df.index = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
            
            data = {
                "ticker": ticker,
                "timestamp": datetime.now().isoformat(),
                "stock_data": stock_data,
                "quote": quote,
                "fundamentals": fundamentals,
                "df": df
            }
            
            # Optional: sentiment data
            if include_sentiment and self.sentiment_analyzer:
                try:
                    data["sentiment"] = {
                        "stocktwits": self.sentiment_analyzer.get_stocktwits_sentiment(ticker),
                        "news": self.sentiment_analyzer.get_news_sentiment(ticker)
                    }
                except Exception as e:
                    logger.warning(f"Sentiment fetch failed for {ticker}: {e}")
                    data["sentiment"] = {}
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {e}")
            raise DataFetchError(f"Failed to fetch data for {ticker}: {str(e)}")
    
    # ========== PRICE EXTRACTION ==========
    
    def _extract_stock_price(self, info: Dict, quote: Dict) -> StockPrice:
        """Extract StockPrice from raw data"""
        try:
            current = quote.get("price", info.get("currentPrice", info.get("regularMarketPrice", 0)))
            open_price = quote.get("open", info.get("open", current))
            high = quote.get("high", info.get("dayHigh", current))
            low = quote.get("low", info.get("dayLow", current))
            volume = quote.get("volume", info.get("volume", 0))
            market_cap = info.get("marketCap", 0)
            
            prev_close = info.get("previousClose", current)
            day_change = current - prev_close
            day_change_pct = (day_change / prev_close * 100) if prev_close > 0 else 0
            
            week_52_high = info.get("fiftyTwoWeekHigh", current)
            week_52_low = info.get("fiftyTwoWeekLow", current)
            
            return StockPrice(
                current=current,
                open=open_price,
                high=high,
                low=low,
                close=current,  # Use current as close for intraday
                volume=volume,
                market_cap=market_cap,
                day_change=day_change,
                day_change_percent=day_change_pct,
                week_52_high=week_52_high,
                week_52_low=week_52_low
            )
            
        except Exception as e:
            logger.error(f"Error extracting stock price: {e}")
            raise AnalysisError(f"Failed to extract price data: {str(e)}")
    
    # ========== TECHNICAL INDICATORS ==========
    
    def _calculate_technical_indicators(self, df: pd.DataFrame, info: Dict) -> TechnicalIndicators:
        """Calculate TechnicalIndicators from price data"""
        try:
            if df.empty:
                raise InsufficientDataError("No historical data available")
            
            # Use technical engine
            tech_data = self.technical_engine.analyze(df) if self.technical_engine else {}
            
            # Extract values with safe defaults (TechnicalAnalyzer returns nested dicts)
            rsi_data = tech_data.get("rsi", {})
            rsi = rsi_data.get("value", 50.0) if isinstance(rsi_data, dict) else rsi_data
            
            macd_data = tech_data.get("macd", {})
            macd = macd_data.get("macd", 0.0) if isinstance(macd_data, dict) else 0.0
            macd_signal = macd_data.get("signal", 0.0) if isinstance(macd_data, dict) else 0.0
            macd_hist = macd_data.get("histogram", 0.0) if isinstance(macd_data, dict) else 0.0
            
            # Bollinger Bands
            bb_data = tech_data.get("bollinger", {})
            bollinger_high = bb_data.get("upper", 0.0) if isinstance(bb_data, dict) else 0.0
            bollinger_mid = bb_data.get("middle", 0.0) if isinstance(bb_data, dict) else 0.0
            bollinger_low = bb_data.get("lower", 0.0) if isinstance(bb_data, dict) else 0.0
            
            # SMAs from price_action
            price_action = tech_data.get("price_action", {})
            sma_20 = price_action.get("sma_20", 0.0) if isinstance(price_action, dict) else 0.0
            sma_50 = price_action.get("sma_50", 0.0) if isinstance(price_action, dict) else 0.0
            sma_200 = price_action.get("sma_200", 0.0) if isinstance(price_action, dict) else 0.0
            
            # Additional indicators
            adx_data = tech_data.get("adx", {})
            adx = adx_data.get("value", 20.0) if isinstance(adx_data, dict) else 20.0
            
            obv = tech_data.get("obv", 0.0)
            atr = tech_data.get("atr", 0.0)
            
            return TechnicalIndicators(
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                macd_histogram=macd_hist,
                bollinger_high=bollinger_high,
                bollinger_mid=bollinger_mid,
                bollinger_low=bollinger_low,
                sma_20=sma_20,
                sma_50=sma_50,
                sma_200=sma_200,
                ema_12=tech_data.get("ema_12", 0.0),
                ema_26=tech_data.get("ema_26", 0.0),
                adx=adx,
                obv=obv,
                atr=atr
            )
            
        except InsufficientDataError:
            raise
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            # Return neutral indicators on error
            return TechnicalIndicators(
                rsi=50.0, macd=0.0, macd_signal=0.0, macd_histogram=0.0,
                bollinger_high=0.0, bollinger_mid=0.0, bollinger_low=0.0,
                sma_20=0.0, sma_50=0.0, sma_200=0.0,
                ema_12=0.0, ema_26=0.0,
                adx=20.0, obv=0.0, atr=0.0
            )
    
    # ========== FUNDAMENTALS ==========
    
    def _extract_fundamentals(self, info: Dict, fundamentals: Dict) -> FundamentalMetrics:
        """Extract FundamentalMetrics from raw data"""
        try:
            pe_ratio = info.get("trailingPE", info.get("forwardPE"))
            pb_ratio = info.get("priceToBook")
            eps = info.get("trailingEps", info.get("forwardEps"))
            revenue_growth = info.get("revenueGrowth")
            eps_growth = info.get("earningsGrowth")
            
            roe = info.get("returnOnEquity")
            roa = info.get("returnOnAssets")
            debt_to_equity = info.get("debtToEquity")
            current_ratio = info.get("currentRatio")
            
            profit_margin = info.get("profitMargins")
            operating_margin = info.get("operatingMargins")
            
            return FundamentalMetrics(
                pe_ratio=pe_ratio,
                pb_ratio=pb_ratio,
                eps=eps,
                revenue_growth=revenue_growth,
                eps_growth=eps_growth,
                roe=roe,
                roa=roa,
                debt_to_equity=debt_to_equity,
                current_ratio=current_ratio,
                profit_margin=profit_margin,
                operating_margin=operating_margin
            )
            
        except Exception as e:
            logger.error(f"Error extracting fundamentals: {e}")
            return FundamentalMetrics()
    
    # ========== RISK METRICS ==========
    
    def _calculate_risk_metrics(self, df: pd.DataFrame, info: Dict, fundamentals: FundamentalMetrics) -> RiskMetrics:
        """Calculate RiskMetrics from data"""
        try:
            # Calculate from historical data if available
            if not df.empty and "Close" in df.columns:
                returns = df["Close"].pct_change().dropna()
                
                # Volatility (annualized)
                volatility = returns.std() * np.sqrt(252)
                
                # Max drawdown
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                max_drawdown = drawdown.min()
                
                # Sharpe ratio (simplified)
                risk_free_rate = 0.04  # 4% annual
                excess_returns = returns.mean() * 252 - risk_free_rate
                sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
            else:
                volatility = info.get("beta", 1.0) * 0.16  # Estimate from beta
                max_drawdown = -0.2  # Default estimate
                sharpe_ratio = 0.5  # Neutral
            
            beta = info.get("beta", 1.0)
            alpha = info.get("alpha", 0.0)
            
            # VaR 95% (simplified)
            var_95 = volatility * 1.645  # 95% confidence
            
            return RiskMetrics(
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                volatility=volatility,
                beta=beta,
                alpha=alpha,
                var_95=var_95
            )
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return RiskMetrics(
                sharpe_ratio=0.5,
                max_drawdown=-0.2,
                volatility=0.2,
                beta=1.0,
                alpha=None,
                var_95=0.329
            )
    
    # ========== VALUATION ==========
    
    def _calculate_valuation(self, fundamentals: Dict, info: Dict) -> ValuationResult:
        """Calculate ValuationResult from data"""
        try:
            # Use valuation engine
            val_data = self.valuation_engine.calculate_valuation(fundamentals, info)
            
            if "error" in val_data:
                raise ValuationError(val_data["error"])
            
            fair_value = val_data.get("fair_value", 0)
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            upside = ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0
            
            # Determine method
            method_str = val_data.get("method", "DCF")
            if "DCF" in method_str or "Cash Flow" in method_str:
                method = ValuationMethod.DCF
            elif "Multiple" in method_str or "P/E" in method_str:
                method = ValuationMethod.MULTIPLES
            elif "DDM" in method_str or "Dividend" in method_str:
                method = ValuationMethod.DDM
            else:
                method = ValuationMethod.DCF
            
            # Confidence based on data quality
            confidence = self._calculate_valuation_confidence(val_data, fundamentals, info)
            
            # Scenarios
            scenarios = val_data.get("scenarios", {
                "conservative": fair_value * 0.85,
                "base": fair_value,
                "optimistic": fair_value * 1.15
            })
            
            return ValuationResult(
                fair_value=fair_value,
                current_price=current_price,
                upside_pct=upside,
                method=method,
                confidence=confidence,
                scenarios=scenarios
            )
            
        except ValuationError:
            raise
        except Exception as e:
            logger.error(f"Error calculating valuation: {e}")
            raise ValuationError(f"Valuation calculation failed: {str(e)}")
    
    def _calculate_valuation_confidence(self, val_data: Dict, fundamentals: Dict, info: Dict) -> float:
        """Calculate confidence score for valuation"""
        confidence = 50.0  # Base
        
        # Boost confidence if we have good data
        if "cash_flow" in fundamentals and fundamentals["cash_flow"]:
            confidence += 15
        if info.get("sharesOutstanding", 0) > 0:
            confidence += 10
        if info.get("beta") is not None:
            confidence += 10
        if val_data.get("method") == "DCF":
            confidence += 15
        
        return min(confidence, 95.0)  # Cap at 95%
    
    # ========== TRADE SIGNALS ==========
    
    def _generate_trade_signals(
        self, 
        price: StockPrice, 
        technical: TechnicalIndicators,
        fundamental: FundamentalMetrics,
        valuation: ValuationResult,
        info: Dict,
        df: pd.DataFrame
    ) -> List[TradeSignal]:
        """Generate TradeSignal objects"""
        signals = []
        
        try:
            # Use goodbuy analyzer if available
            if self.goodbuy_analyzer and not df.empty:
                buy_analysis = self.goodbuy_analyzer.analyze_buy_opportunity(
                    info.get("symbol", ""),
                    valuation.to_dict() if hasattr(valuation, 'to_dict') else {},
                    technical.to_dict() if hasattr(technical, 'to_dict') else {},
                    {},  # sentiment
                    info,
                    df
                )
                
                # Primary signal
                primary_signal = self._determine_primary_signal(
                    buy_analysis, valuation, technical, fundamental
                )
                
                signals.append(TradeSignal(
                    signal=primary_signal,
                    confidence=buy_analysis.get("total_score", 50) / 100,
                    reasoning=buy_analysis.get("confidence", "Neutral"),
                    entry_price=buy_analysis.get("buy_range", {}).get("low", price.current),
                    stop_loss=buy_analysis.get("buy_range", {}).get("low", price.current) * 0.95,
                    take_profit=buy_analysis.get("target_price", price.current * 1.2)
                ))
            else:
                # Fallback: simple signal generation
                signals.append(self._generate_simple_signal(price, technical, valuation))
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trade signals: {e}")
            return [TradeSignal(
                signal=Signal.HOLD,
                confidence=0.5,
                reasoning="Error generating signals",
                entry_price=price.current,
                stop_loss=price.current * 0.95,
                take_profit=price.current * 1.1
            )]
    
    def _determine_primary_signal(
        self, 
        buy_analysis: Dict, 
        valuation: ValuationResult,
        technical: TechnicalIndicators,
        fundamental: FundamentalMetrics
    ) -> Signal:
        """Determine primary buy/sell/hold signal"""
        score = buy_analysis.get("total_score", 50)
        
        # Strong buy
        if score >= 70 and valuation.is_undervalued() and not technical.is_overbought():
            return Signal.STRONG_BUY
        
        # Buy
        if score >= 55 and valuation.upside_pct > 10:
            return Signal.BUY
        
        # Sell
        if score < 40 or technical.is_overbought() or valuation.upside_pct < -20:
            return Signal.SELL
        
        # Hold
        return Signal.HOLD
    
    def _generate_simple_signal(
        self, 
        price: StockPrice, 
        technical: TechnicalIndicators, 
        valuation: ValuationResult
    ) -> TradeSignal:
        """Generate simple signal without goodbuy analyzer"""
        # Score components
        valuation_score = 1.0 if valuation.is_undervalued() else 0.0
        technical_score = 1.0 if technical.get_momentum_score() > 60 else 0.5 if technical.get_momentum_score() > 40 else 0.0
        
        combined_score = (valuation_score + technical_score) / 2
        
        if combined_score >= 0.7:
            signal = Signal.BUY
            reasoning = "Undervalued with positive momentum"
        elif combined_score <= 0.3:
            signal = Signal.SELL
            reasoning = "Overvalued or weak momentum"
        else:
            signal = Signal.HOLD
            reasoning = "Neutral outlook"
        
        return TradeSignal(
            signal=signal,
            confidence=combined_score,
            reasoning=reasoning,
            entry_price=price.current,
            stop_loss=price.current * 0.95,
            take_profit=price.current * (1 + valuation.upside_pct / 100 * 0.8)
        )
    
    # ========== HELPERS ==========
    
    def _get_sma_alignment(self, technical: TechnicalIndicators) -> str:
        """Get SMA alignment status"""
        if technical.sma_20 > technical.sma_50 > technical.sma_200:
            return "BULLISH_ALIGNED"
        elif technical.sma_20 < technical.sma_50 < technical.sma_200:
            return "BEARISH_ALIGNED"
        else:
            return "MIXED"
