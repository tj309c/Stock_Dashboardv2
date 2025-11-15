"""
LLM-Powered Predictive Models
Uses Claude API to analyze the "digital landscape" and generate market predictions.

Features:
- Aggregate all data sources (economic, political, sentiment, technical)
- LLM analyzes correlations and hidden patterns
- Natural language explanations of predictions
- Multi-timeframe forecasting (1 day, 1 week, 1 month, 3 months)

Philosophy:
The "digital landscape" is the totality of quantifiable market data.
An LLM can discover non-obvious correlations that traditional models miss
(e.g., "rising oil prices + Fed hawkish tone + tech insider selling = tech pullback").
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class ClaudePredictor:
    """
    LLM-powered market prediction engine using Claude API.
    
    Workflow:
    1. Aggregate all available data (macro, sentiment, technical, insider)
    2. Format into structured prompt for Claude
    3. Claude analyzes patterns and generates prediction
    4. Parse response into actionable signals
    """
    
    def __init__(self):
        """Initialize Claude client with API key from secrets."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.client = None
        
        try:
            if hasattr(st, 'secrets'):
                api_key = st.secrets.get('ANTHROPIC_API_KEY')
            else:
                import os
                api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Claude API initialized successfully")
            else:
                logger.warning("Claude API key not found. Set ANTHROPIC_API_KEY in secrets.toml")
                
        except Exception as e:
            logger.error(f"Error initializing Claude API: {e}")
    
    # =========================================================================
    # Data Aggregation
    # =========================================================================
    
    def aggregate_digital_landscape_data(self, ticker: str, 
                                        economic_data: Optional[Dict] = None,
                                        political_data: Optional[Dict] = None,
                                        sentiment_data: Optional[Dict] = None,
                                        technical_data: Optional[pd.DataFrame] = None,
                                        insider_data: Optional[Dict] = None) -> Dict:
        """
        Aggregate all available data sources into unified structure.
        
        Args:
            ticker: Stock ticker symbol
            economic_data: Macro indicators (inflation, rates, GDP, etc.)
            political_data: Congressional trades, insider transactions
            sentiment_data: Reddit, news, social media sentiment
            technical_data: Price history, indicators (RSI, MACD, etc.)
            insider_data: Corporate insider buy/sell activity
            
        Returns:
            Dictionary with all data formatted for LLM consumption
        """
        landscape = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'data_sources': []
        }
        
        # Economic indicators
        if economic_data:
            landscape['economic'] = economic_data
            landscape['data_sources'].append('economic')
        
        # Political/insider activity
        if political_data:
            landscape['political'] = political_data
            landscape['data_sources'].append('political')
        
        # Social sentiment
        if sentiment_data:
            landscape['sentiment'] = sentiment_data
            landscape['data_sources'].append('sentiment')
        
        # Technical analysis
        if technical_data is not None and len(technical_data) > 0:
            latest = technical_data.iloc[-1]
            historical = technical_data.tail(30)  # Last 30 days
            
            landscape['technical'] = {
                'current_price': latest.get('Close', 0),
                'price_change_30d': ((latest.get('Close', 0) - historical.iloc[0].get('Close', 1)) / 
                                    historical.iloc[0].get('Close', 1) * 100),
                'volatility_30d': historical['Close'].pct_change().std() * np.sqrt(252) * 100,
                'volume_trend': 'increasing' if latest.get('Volume', 0) > historical['Volume'].mean() else 'decreasing',
                'support_level': historical['Low'].min(),
                'resistance_level': historical['High'].max()
            }
            landscape['data_sources'].append('technical')
        
        # Insider transactions
        if insider_data:
            landscape['insider'] = insider_data
            landscape['data_sources'].append('insider')
        
        return landscape
    
    # =========================================================================
    # LLM Prediction
    # =========================================================================
    
    def generate_prediction(self, landscape: Dict, timeframe: str = '1_week') -> Optional[Dict]:
        """
        Generate market prediction using Claude's analysis.
        
        Args:
            landscape: Aggregated data from aggregate_digital_landscape_data()
            timeframe: Prediction timeframe (1_day, 1_week, 1_month, 3_months)
            
        Returns:
            Dictionary with prediction, confidence, reasoning
        """
        if not self.client:
            st.error("🔑 Claude API not configured. Add ANTHROPIC_API_KEY to secrets.toml")
            return None
        
        try:
            # Build structured prompt
            prompt = self._build_prediction_prompt(landscape, timeframe)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",  # Latest Claude model
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent predictions
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            prediction = self._parse_prediction_response(response_text)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            return None
    
    def _build_prediction_prompt(self, landscape: Dict, timeframe: str) -> str:
        """
        Build structured prompt for Claude API.
        
        Format:
        - Clear role definition (financial analyst)
        - All relevant data in structured format
        - Specific prediction request with output format
        """
        timeframe_map = {
            '1_day': '1 trading day',
            '1_week': '1 week (5 trading days)',
            '1_month': '1 month (21 trading days)',
            '3_months': '3 months (63 trading days)'
        }
        
        timeframe_text = timeframe_map.get(timeframe, '1 week')
        ticker = landscape.get('ticker', 'UNKNOWN')
        
        prompt = f"""You are an expert quantitative analyst with deep knowledge of market dynamics, macroeconomics, and behavioral finance.

Analyze the following "digital landscape" data for {ticker} and predict the stock's price movement over the next {timeframe_text}.

DATA AVAILABLE:
{json.dumps(landscape, indent=2, default=str)}

TASK:
1. Analyze all available data sources and identify key factors influencing {ticker}
2. Look for correlations between macro indicators, sentiment, insider activity, and technical patterns
3. Provide a directional prediction (BULLISH, BEARISH, or NEUTRAL)
4. Assign a confidence level (0-100%)
5. Explain your reasoning in 2-3 concise paragraphs

OUTPUT FORMAT (JSON):
{{
    "prediction": "BULLISH | BEARISH | NEUTRAL",
    "confidence": 75,
    "target_price_change_pct": 5.2,
    "key_factors": ["factor 1", "factor 2", "factor 3"],
    "reasoning": "Full explanation here...",
    "risks": ["risk 1", "risk 2"],
    "catalysts": ["catalyst 1", "catalyst 2"]
}}

Respond ONLY with valid JSON. No additional text."""
        
        return prompt
    
    def _parse_prediction_response(self, response_text: str) -> Dict:
        """
        Parse Claude's JSON response into structured prediction.
        
        Args:
            response_text: Raw response from Claude API
            
        Returns:
            Dictionary with prediction fields
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()
            
            prediction = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['prediction', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in prediction:
                    logger.warning(f"Missing field in prediction: {field}")
                    prediction[field] = "Unknown"
            
            # Add metadata
            prediction['generated_at'] = datetime.now().isoformat()
            
            return prediction
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            
            # Return fallback structure
            return {
                'prediction': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'Error parsing LLM response',
                'raw_response': response_text,
                'error': str(e)
            }
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    @st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
    def get_full_analysis(_self, ticker: str, 
                         economic_pipeline = None,
                         political_pipeline = None,
                         market_pipeline = None) -> Dict:
        """
        One-click comprehensive analysis using all data sources.
        
        Args:
            ticker: Stock ticker symbol
            economic_pipeline: EconomicDataPipeline instance (optional)
            political_pipeline: PoliticalDataPipeline instance (optional)
            market_pipeline: MarketDataPipeline instance (optional)
            
        Returns:
            Complete prediction with all supporting data
        """
        # Aggregate data from all pipelines
        landscape = {}
        
        if economic_pipeline:
            try:
                landscape['economic'] = economic_pipeline.get_current_snapshot()
            except Exception as e:
                logger.warning(f"Failed to fetch economic data: {e}")
        
        if political_pipeline:
            try:
                landscape['political'] = political_pipeline.get_comprehensive_insider_report(ticker)
            except Exception as e:
                logger.warning(f"Failed to fetch political data: {e}")
        
        if market_pipeline:
            try:
                ticker_data = market_pipeline.get_comprehensive_ticker_data(ticker)
                landscape['technical'] = ticker_data.get('historical_data')
                landscape['fundamentals'] = ticker_data.get('info')
            except Exception as e:
                logger.warning(f"Failed to fetch market data: {e}")
        
        # Generate prediction
        prediction = _self.generate_prediction(landscape, timeframe='1_week')
        
        if prediction:
            prediction['landscape_data'] = landscape
        
        return prediction
    
    def explain_reasoning(self, prediction: Dict) -> str:
        """
        Format prediction reasoning for display in dashboard.
        
        Args:
            prediction: Prediction dictionary from generate_prediction()
            
        Returns:
            Formatted markdown string
        """
        if not prediction or 'reasoning' not in prediction:
            return "No prediction available."
        
        direction = prediction.get('prediction', 'NEUTRAL')
        confidence = prediction.get('confidence', 0)
        reasoning = prediction.get('reasoning', 'No reasoning provided')
        key_factors = prediction.get('key_factors', [])
        risks = prediction.get('risks', [])
        catalysts = prediction.get('catalysts', [])
        
        # Color code based on prediction
        color = {
            'BULLISH': '🟢',
            'BEARISH': '🔴',
            'NEUTRAL': '🟡'
        }.get(direction, '⚪')
        
        output = f"""
### {color} Prediction: {direction} ({confidence}% confidence)

**Analysis:**
{reasoning}

**Key Factors:**
{chr(10).join(f'• {factor}' for factor in key_factors)}

**Potential Risks:**
{chr(10).join(f'⚠️ {risk}' for risk in risks)}

**Catalysts to Watch:**
{chr(10).join(f'🎯 {catalyst}' for catalyst in catalysts)}
"""
        
        return output


# Convenience function
def get_claude_predictor() -> ClaudePredictor:
    """Factory function to get configured Claude predictor."""
    return ClaudePredictor()
