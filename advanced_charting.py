"""
Advanced Interactive Charting with ALL Yahoo Finance Indicators
Comprehensive technical analysis overlays and comparison tools
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from app_utils import plotly_full_width
from mode_config import get_cache_ttl


# ===== STRATEGY PRESET CONFIGURATION =====
STRATEGY_PRESETS = {
    'clean_chart': {
        'name': 'Clean Chart',
        'emoji': '📊',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Minimal view with just volume bars - pure price action',
        'best_for': 'Price action traders who prefer clean charts without indicator clutter',
        'timeframe': 'Any',
        'complexity': 'Beginner',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': False, 'sma50': False, 'sma100': False, 'sma200': False,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': False, 'ema26': False, 'ema50': False,
            'bb': False, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': False, 'stoch': False, 'willr': False, 'macd': False, 'adx': False, 'cci': False, 'obv': False, 'mfi': False
        },
        'tutorial': {
            'what': 'A minimal chart showing only price candles and volume bars.',
            'why': 'Removes all indicator noise to focus purely on price action, support/resistance levels, and candlestick patterns.',
            'when': 'Use when you want to analyze raw price movements, identify chart patterns, or avoid over-reliance on indicators.'
        }
    },
    'scalping': {
        'name': 'Scalping',
        'emoji': '⚡',
        'category': 'SHORT-TERM TRADING',
        'description': 'Ultra short-term trades (seconds to minutes) - lightning fast',
        'best_for': 'High-frequency traders seeking quick profits on small price movements',
        'timeframe': '1m - 5m',
        'complexity': 'Advanced',
        'indicators': {
            'sma5': True, 'sma10': True, 'sma20': False, 'sma50': False, 'sma100': False, 'sma200': False,
            'ema5': True, 'ema10': True, 'ema12': True, 'ema20': False, 'ema26': False, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': True, 'vwap': True, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': False, 'macd': False, 'adx': False, 'cci': True, 'obv': False, 'mfi': True
        },
        'tutorial': {
            'what': 'Rapid-fire trading setup with fast EMAs (5,10,12), Bollinger Bands, PSAR, VWAP, RSI, Stochastic, CCI, and MFI.',
            'why': 'Fast indicators respond quickly to price changes. VWAP provides institutional reference. Volume and money flow confirm liquidity for quick entries/exits.',
            'when': 'Use in high-liquidity assets during market hours. Requires tight stop-losses and quick decision-making.'
        }
    },
    'day_trading': {
        'name': 'Day Trading',
        'emoji': '🏃',
        'category': 'SHORT-TERM TRADING',
        'description': 'Intraday trades closed before market close',
        'best_for': 'Active traders monitoring positions throughout the day',
        'timeframe': '5m - 1h',
        'complexity': 'Intermediate',
        'indicators': {
            'sma5': True, 'sma10': True, 'sma20': True, 'sma50': False, 'sma100': False, 'sma200': False,
            'ema5': True, 'ema10': True, 'ema12': True, 'ema20': False, 'ema26': True, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': True, 'vwap': True, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': False, 'macd': True, 'adx': False, 'cci': False, 'obv': False, 'mfi': True
        },
        'tutorial': {
            'what': 'Balanced setup with short-term MAs (5,10,20), PSAR, VWAP, MACD, RSI, Stochastic, and MFI.',
            'why': 'Combines trend indicators (MAs, PSAR) with momentum (RSI, Stoch, MACD) for intraday opportunities. VWAP shows institutional pricing.',
            'when': 'Use when actively monitoring charts. Best for liquid stocks with clear intraday trends.'
        }
    },
    'swing_trading': {
        'name': 'Swing Trading',
        'emoji': '🎯',
        'category': 'MEDIUM-TERM TRADING',
        'description': 'Multi-day to multi-week position holds',
        'best_for': 'Part-time traders capturing medium-term trends',
        'timeframe': '1h - Daily',
        'complexity': 'Intermediate',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': True, 'sma50': True, 'sma100': True, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': True, 'ema26': False, 'ema50': True,
            'bb': True, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': True, 'stoch': False, 'willr': False, 'macd': True, 'adx': True, 'cci': False, 'obv': True, 'mfi': False
        },
        'tutorial': {
            'what': 'Medium-term MAs (20,50,100,200), EMA(20,50), BB, MACD, RSI, ADX, and OBV.',
            'why': 'Identifies multi-day trends using longer MAs and ADX. MACD/RSI time entries within the trend.',
            'when': 'Use for holding 3-10 days. Works best when market has clear directional trends.'
        }
    },
    'trend_following': {
        'name': 'Trend Following',
        'emoji': '📈',
        'category': 'MEDIUM-TERM TRADING',
        'description': 'Ride established trends until they reverse',
        'best_for': 'Traders who profit from sustained directional moves',
        'timeframe': 'Daily - Weekly',
        'complexity': 'Intermediate',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': True, 'sma50': True, 'sma100': False, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': False, 'ema26': False, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': False, 'stoch': False, 'willr': False, 'macd': True, 'adx': True, 'cci': False, 'obv': False, 'mfi': False
        },
        'tutorial': {
            'what': 'Core trend indicators: SMA(20,50,200), Bollinger Bands, MACD, and ADX.',
            'why': 'ADX confirms trend strength. MAs define trend direction. MACD signals entries/exits within the trend.',
            'when': 'Use when ADX > 25 (strong trend). Stay in trades until MAs cross or ADX weakens.'
        }
    },
    'breakout_trading': {
        'name': 'Breakout Trading',
        'emoji': '🔄',
        'category': 'MEDIUM-TERM TRADING',
        'description': 'Enter positions as price breaks key levels',
        'best_for': 'Traders who capitalize on volatility expansion and range breakouts',
        'timeframe': '1h - Daily',
        'complexity': 'Advanced',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': True, 'sma50': True, 'sma100': False, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': True, 'ema26': False, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': False, 'willr': False, 'macd': False, 'adx': False, 'cci': True, 'obv': True, 'mfi': False
        },
        'tutorial': {
            'what': 'Volatility indicators (BB), key MAs (20,50,200), volume analysis, and momentum (RSI, CCI, OBV).',
            'why': 'BB identifies squeeze periods before breakouts. Volume confirms breakout validity. RSI/CCI show momentum.',
            'when': 'Use when price consolidates near resistance/support. Wait for volume surge confirming the breakout.'
        }
    },
    'deep_value': {
        'name': 'Deep Value',
        'emoji': '💎',
        'category': 'LONG-TERM INVESTING',
        'description': 'Long-term fundamentally undervalued positions',
        'best_for': 'Patient investors seeking undervalued assets for multi-month holds',
        'timeframe': 'Daily - Monthly',
        'complexity': 'Beginner',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': False, 'sma50': True, 'sma100': True, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': False, 'ema26': False, 'ema50': True,
            'bb': False, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': True, 'stoch': False, 'willr': False, 'macd': False, 'adx': False, 'cci': False, 'obv': True, 'mfi': False
        },
        'tutorial': {
            'what': 'Long-term MAs (50,100,200), EMA(50), RSI for oversold conditions, and OBV for accumulation.',
            'why': 'MAs identify long-term support levels. RSI < 30 flags oversold conditions. OBV shows smart money accumulation.',
            'when': 'Use for fundamentally strong stocks trading below intrinsic value. Buy when RSI oversold near key MA support.'
        }
    },
    'position_trading': {
        'name': 'Position Trading',
        'emoji': '📊',
        'category': 'LONG-TERM INVESTING',
        'description': 'Multi-month positions based on major trends',
        'best_for': 'Long-term traders holding through market noise',
        'timeframe': 'Weekly - Monthly',
        'complexity': 'Beginner',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': False, 'sma50': True, 'sma100': True, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': False, 'ema26': False, 'ema50': True,
            'bb': False, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': False, 'stoch': False, 'willr': False, 'macd': True, 'adx': True, 'cci': False, 'obv': True, 'mfi': False
        },
        'tutorial': {
            'what': 'Major MAs (50,100,200), MACD for long-term momentum, ADX for trend strength, OBV for volume analysis.',
            'why': 'Focuses on macro trends ignoring short-term volatility. MAs define trend, MACD times entries, ADX confirms strength.',
            'when': 'Use for 3-12 month holds. Enter when price above SMA200 with rising OBV and ADX > 25.'
        }
    },
    'income_dividend': {
        'name': 'Income/Dividend',
        'emoji': '💰',
        'category': 'LONG-TERM INVESTING',
        'description': 'Buy quality dividend stocks at attractive prices',
        'best_for': 'Income-focused investors seeking yield with capital preservation',
        'timeframe': 'Daily - Monthly',
        'complexity': 'Beginner',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': False, 'sma50': True, 'sma100': True, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': False, 'ema26': False, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': True, 'stoch': False, 'willr': False, 'macd': False, 'adx': False, 'cci': False, 'obv': False, 'mfi': False
        },
        'tutorial': {
            'what': 'Key MAs (50,100,200), Bollinger Bands for value zones, and RSI for entry timing.',
            'why': 'Buy dividend stocks at attractive prices (lower BB band, RSI < 40) near MA support for better yield.',
            'when': 'Use for dividend aristocrats/kings. Buy when price pulls back to SMA50/100 with RSI showing oversold.'
        }
    },
    'momentum_trading': {
        'name': 'Momentum Trading',
        'emoji': '📉',
        'category': 'SHORT-TERM TRADING',
        'description': 'Follow strong price momentum and relative strength',
        'best_for': 'Aggressive traders chasing high-momentum moves',
        'timeframe': '15m - 1h',
        'complexity': 'Advanced',
        'indicators': {
            'sma5': True, 'sma10': True, 'sma20': True, 'sma50': False, 'sma100': False, 'sma200': False,
            'ema5': True, 'ema10': True, 'ema12': True, 'ema20': True, 'ema26': False, 'ema50': False,
            'bb': False, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': True, 'macd': True, 'adx': True, 'cci': True, 'obv': False, 'mfi': True
        },
        'tutorial': {
            'what': 'Fast MAs, all momentum oscillators (RSI, Stoch, Williams %R, CCI, MFI), MACD, ADX, and volume.',
            'why': 'Identifies and rides explosive momentum. Multiple oscillators confirm strength. ADX validates trend power.',
            'when': 'Use when ADX > 30, RSI > 60, and price above all EMAs. Exit when momentum oscillators diverge.'
        }
    },
    'options_trading': {
        'name': 'Options Trading',
        'emoji': '🎲',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Volatility and directional bias for options strategies',
        'best_for': 'Options traders needing IV, support/resistance, and trend analysis',
        'timeframe': '1h - Daily',
        'complexity': 'Advanced',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': True, 'sma50': True, 'sma100': False, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': True, 'ema26': False, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': False, 'macd': True, 'adx': False, 'cci': False, 'obv': False, 'mfi': False
        },
        'tutorial': {
            'what': 'Volatility indicators (BB width), key MAs (20,50,200), RSI, Stochastic, MACD, and volume.',
            'why': 'BB width indicates IV changes (sell premium when wide, buy when narrow). MAs define support/resistance for strikes.',
            'when': 'Use for options strategies: sell premium at BB extremes, buy directional when BB squeezes with rising volume.'
        }
    },
    'institutional': {
        'name': 'Institutional',
        'emoji': '🏦',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Hedge fund / institutional-grade multi-timeframe analysis',
        'best_for': 'Professional traders using comprehensive technical analysis',
        'timeframe': '1h - Weekly',
        'complexity': 'Expert',
        'indicators': {
            'sma5': False, 'sma10': True, 'sma20': True, 'sma50': True, 'sma100': True, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': True, 'ema20': True, 'ema26': True, 'ema50': True,
            'bb': True, 'ichi': True, 'psar': False, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': False, 'macd': True, 'adx': True, 'cci': True, 'obv': True, 'mfi': True
        },
        'tutorial': {
            'what': 'Comprehensive setup: All major MAs, Ichimoku Cloud, BB, full oscillator suite (RSI, Stoch, MACD, ADX, CCI), volume analysis.',
            'why': 'Multi-timeframe confluence analysis. Ichimoku for trend/momentum, MAs for structure, oscillators for timing.',
            'when': 'Use for thorough analysis before large positions. Wait for alignment across indicators and timeframes.'
        }
    },
    'mean_reversion': {
        'name': 'Mean Reversion',
        'emoji': '⚖️',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Buy oversold, sell overbought - price returns to mean',
        'best_for': 'Counter-trend traders in ranging markets',
        'timeframe': '1h - Daily',
        'complexity': 'Intermediate',
        'indicators': {
            'sma5': False, 'sma10': False, 'sma20': True, 'sma50': True, 'sma100': False, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': False, 'ema20': True, 'ema26': False, 'ema50': False,
            'bb': True, 'ichi': False, 'psar': False, 'vol': True, 'vol_sma': False,
            'rsi': True, 'stoch': True, 'willr': True, 'macd': False, 'adx': False, 'cci': True, 'obv': False, 'mfi': True
        },
        'tutorial': {
            'what': 'Mean indicators (SMA20,50,200, BB), extreme oscillators (RSI, Stoch, Williams %R, CCI, MFI).',
            'why': 'BB identifies overbought/oversold extremes. Multiple oscillators confirm mean reversion setup. MAs define the mean.',
            'when': 'Use in range-bound markets (ADX < 20). Buy at lower BB with RSI < 30. Sell at upper BB with RSI > 70.'
        }
    },
    'crypto_volatile': {
        'name': 'Crypto/Volatile Assets',
        'emoji': '🌐',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'High volatility assets - crypto, penny stocks, meme stocks',
        'best_for': 'Traders in highly volatile, 24/7 markets like crypto',
        'timeframe': '15m - 4h',
        'complexity': 'Advanced',
        'indicators': {
            'sma5': True, 'sma10': True, 'sma20': True, 'sma50': True, 'sma100': False, 'sma200': False,
            'ema5': True, 'ema10': True, 'ema12': True, 'ema20': True, 'ema26': True, 'ema50': True,
            'bb': True, 'ichi': False, 'psar': True, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': True, 'macd': True, 'adx': False, 'cci': True, 'obv': True, 'mfi': True
        },
        'tutorial': {
            'what': 'Fast-reacting setup: Short/medium EMAs, BB, PSAR, all momentum indicators, heavy volume analysis.',
            'why': 'High volatility requires responsive indicators. Multiple confirmations reduce false signals in choppy action.',
            'when': 'Use for crypto, penny stocks, or meme stocks. Tighten stops due to volatility. Confirm moves with volume spikes.'
        }
    },
    'full_analysis': {
        'name': 'Full Analysis',
        'emoji': '🌊',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Everything enabled - comprehensive technical overview',
        'best_for': 'Deep-dive analysis when you need to see every indicator',
        'timeframe': 'Any',
        'complexity': 'Expert',
        'indicators': {
            'sma5': False, 'sma10': True, 'sma20': True, 'sma50': True, 'sma100': True, 'sma200': True,
            'ema5': False, 'ema10': False, 'ema12': True, 'ema20': True, 'ema26': True, 'ema50': True,
            'bb': True, 'ichi': True, 'psar': True, 'vol': True, 'vol_sma': True,
            'rsi': True, 'stoch': True, 'willr': True, 'macd': True, 'adx': True, 'cci': True, 'obv': True, 'mfi': True
        },
        'tutorial': {
            'what': 'All available indicators enabled for maximum information density.',
            'why': 'Comprehensive view for educational purposes or when performing thorough multi-indicator analysis.',
            'when': 'Use for learning, backtesting strategies, or when you need complete technical picture. Can be overwhelming for beginners.'
        }
    }
}


def apply_preset(preset_key):
    """Apply a preset configuration to session state"""
    if preset_key in STRATEGY_PRESETS:
        preset = STRATEGY_PRESETS[preset_key]
        st.session_state.update(preset['indicators'])
        st.session_state['active_preset'] = preset_key
        return True
    return False


def get_preset_categories():
    """Get presets organized by category"""
    categories = {}
    for key, preset in STRATEGY_PRESETS.items():
        category = preset['category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'key': key,
            'display': f"{preset['emoji']} {preset['name']}",
            **preset
        })
    return categories


@st.cache_data(ttl=get_cache_ttl("medium"))
def calculate_all_indicators(df):
    """Calculate ALL technical indicators"""

    # Moving Averages
    for period in [5, 10, 12, 20, 26, 50, 100, 200]:
        df[f'SMA{period}'] = df['Close'].rolling(window=period).mean()
        df[f'EMA{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

    # Bollinger Bands (20, 2)
    sma20 = df['Close'].rolling(window=20).mean()
    std20 = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = sma20 + (std20 * 2)
    df['BB_Middle'] = sma20
    df['BB_Lower'] = sma20 - (std20 * 2)

    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # MACD Crossovers (Convergence)
    df['MACD_Bullish_Cross'] = ((df['MACD'] > df['MACD_Signal']) &
                                 (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)))
    df['MACD_Bearish_Cross'] = ((df['MACD'] < df['MACD_Signal']) &
                                 (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)))

    # Stochastic Oscillator (14, 3, 3)
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()

    # ADX (14) - Average Directional Index
    high = df['High']
    low = df['Low']
    close = df['Close']

    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    tr = pd.concat([tr1, tr2, tr3], axis=1, join='inner').max(axis=1)
    atr = tr.rolling(14).mean()

    plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1/14).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    df['ADX'] = dx.ewm(alpha=1/14).mean()
    df['Plus_DI'] = plus_di
    df['Minus_DI'] = minus_di

    # CCI (20) - Commodity Channel Index
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['CCI'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())

    # Williams %R (14)
    df['Williams_R'] = -100 * ((high_14 - df['Close']) / (high_14 - low_14))

    # OBV - On Balance Volume
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

    # Ichimoku Cloud
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Ichimoku_Tenkan'] = (high_9 + low_9) / 2

    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Ichimoku_Kijun'] = (high_26 + low_26) / 2

    df['Ichimoku_SpanA'] = ((df['Ichimoku_Tenkan'] + df['Ichimoku_Kijun']) / 2).shift(26)

    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Ichimoku_SpanB'] = ((high_52 + low_52) / 2).shift(26)

    # Parabolic SAR
    df['PSAR'] = _calculate_psar(df)

    # ATR - Average True Range
    df['ATR'] = atr

    # Money Flow Index (MFI) - 14 period (vectorized)
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    raw_money_flow = typical_price * df['Volume']

    # Vectorized approach - no Python loop!
    price_diff = typical_price.diff()
    positive_flow = raw_money_flow.where(price_diff > 0, 0)
    negative_flow = raw_money_flow.where(price_diff < 0, 0).abs()

    positive_mf = positive_flow.rolling(14).sum()
    negative_mf = negative_flow.rolling(14).sum()
    mfi = 100 - (100 / (1 + positive_mf / negative_mf))
    df['MFI'] = mfi

    # Volume SMA
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()

    # VWAP - Volume-Weighted Average Price (critical for institutional trading)
    # VWAP resets daily in production, but for historical analysis we'll use cumulative
    # For intraday data, this should reset at market open each day
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()

    # Volume color coding (for visualization)
    df['Volume_Color'] = df['Close'] >= df['Open']  # True = green (up), False = red (down)

    # Volume spike detection (volume > 2x the 20-day average)
    df['Volume_Spike'] = df['Volume'] > (df['Volume_SMA'] * 2)

    # Detect MACD Divergences
    df = _detect_macd_divergence(df, lookback=14)

    return df


@st.cache_data(ttl=get_cache_ttl("medium"))
def _detect_chart_patterns(df):
    """
    Detect all major chart patterns in the price data

    Returns dict with pattern detections and metadata
    """
    patterns_found = {
        'head_and_shoulders': [],
        'inverse_head_and_shoulders': [],
        'double_top': [],
        'double_bottom': [],
        'triple_top': [],
        'triple_bottom': [],
        'ascending_triangle': [],
        'descending_triangle': [],
        'symmetrical_triangle': [],
        'bullish_flag': [],
        'bearish_flag': [],
        'bullish_pennant': [],
        'bearish_pennant': [],
        'cup_and_handle': [],
        'wedge_rising': [],
        'wedge_falling': [],
        'channel_up': [],
        'channel_down': []
    }

    # Head and Shoulders Pattern
    for i in range(30, len(df) - 10):
        window = df.iloc[i-30:i+10]
        if len(window) < 40:
            continue

        # Find potential shoulders and head
        high_points = window.nlargest(5, 'High')
        if len(high_points) >= 3:
            sorted_highs = high_points.sort_index()

            # Check if middle point is highest (head)
            if len(sorted_highs) >= 3:
                left_shoulder = sorted_highs.iloc[0]['High']
                head = sorted_highs.iloc[1]['High']
                right_shoulder = sorted_highs.iloc[2]['High']

                # Head should be higher than shoulders
                if (head > left_shoulder * 1.02 and head > right_shoulder * 1.02 and
                    abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                    patterns_found['head_and_shoulders'].append({
                        'date': df.index[i],
                        'price': head,
                        'confidence': 'High' if head > left_shoulder * 1.05 else 'Medium'
                    })

    # Inverse Head and Shoulders
    for i in range(30, len(df) - 10):
        window = df.iloc[i-30:i+10]
        if len(window) < 40:
            continue

        low_points = window.nsmallest(5, 'Low')
        if len(low_points) >= 3:
            sorted_lows = low_points.sort_index()

            if len(sorted_lows) >= 3:
                left_shoulder = sorted_lows.iloc[0]['Low']
                head = sorted_lows.iloc[1]['Low']
                right_shoulder = sorted_lows.iloc[2]['Low']

                if (head < left_shoulder * 0.98 and head < right_shoulder * 0.98 and
                    abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                    patterns_found['inverse_head_and_shoulders'].append({
                        'date': df.index[i],
                        'price': head,
                        'confidence': 'High' if head < left_shoulder * 0.95 else 'Medium'
                    })

    # Double Top
    for i in range(20, len(df) - 5):
        window = df.iloc[i-20:i+5]
        high_points = window.nlargest(3, 'High')

        if len(high_points) >= 2:
            sorted_highs = high_points.sort_index()
            peak1 = sorted_highs.iloc[0]['High']
            peak2 = sorted_highs.iloc[1]['High']

            # Peaks should be similar height with valley between
            if abs(peak1 - peak2) / peak1 < 0.03:
                valley_between = window.loc[sorted_highs.index[0]:sorted_highs.index[1], 'Low'].min()
                if valley_between < peak1 * 0.95:
                    patterns_found['double_top'].append({
                        'date': df.index[i],
                        'price': peak2,
                        'confidence': 'High' if abs(peak1 - peak2) / peak1 < 0.015 else 'Medium'
                    })

    # Double Bottom
    for i in range(20, len(df) - 5):
        window = df.iloc[i-20:i+5]
        low_points = window.nsmallest(3, 'Low')

        if len(low_points) >= 2:
            sorted_lows = low_points.sort_index()
            bottom1 = sorted_lows.iloc[0]['Low']
            bottom2 = sorted_lows.iloc[1]['Low']

            if abs(bottom1 - bottom2) / bottom1 < 0.03:
                peak_between = window.loc[sorted_lows.index[0]:sorted_lows.index[1], 'High'].max()
                if peak_between > bottom1 * 1.05:
                    patterns_found['double_bottom'].append({
                        'date': df.index[i],
                        'price': bottom2,
                        'confidence': 'High' if abs(bottom1 - bottom2) / bottom1 < 0.015 else 'Medium'
                    })

    # Ascending Triangle (bullish)
    for i in range(30, len(df) - 5):
        window = df.iloc[i-30:i+5]

        # Check for flat resistance and rising support
        recent_highs = window['High'].tail(15)
        recent_lows = window['Low'].tail(15)

        # Flat top (resistance)
        high_volatility = recent_highs.std() / recent_highs.mean()

        # Rising lows (support)
        low_trend = np.polyfit(range(len(recent_lows)), recent_lows.values, 1)[0]

        if high_volatility < 0.02 and low_trend > 0:
            patterns_found['ascending_triangle'].append({
                'date': df.index[i],
                'price': recent_highs.mean(),
                'confidence': 'High' if high_volatility < 0.01 else 'Medium'
            })

    # Descending Triangle (bearish)
    for i in range(30, len(df) - 5):
        window = df.iloc[i-30:i+5]

        recent_highs = window['High'].tail(15)
        recent_lows = window['Low'].tail(15)

        # Flat bottom (support)
        low_volatility = recent_lows.std() / recent_lows.mean()

        # Falling highs (resistance)
        high_trend = np.polyfit(range(len(recent_highs)), recent_highs.values, 1)[0]

        if low_volatility < 0.02 and high_trend < 0:
            patterns_found['descending_triangle'].append({
                'date': df.index[i],
                'price': recent_lows.mean(),
                'confidence': 'High' if low_volatility < 0.01 else 'Medium'
            })

    # Bullish Flag (continuation)
    for i in range(25, len(df) - 5):
        if i < 25:  # Need at least 25 bars for this pattern
            continue

        window = df.iloc[i-15:i+5]
        prev_window = df.iloc[i-20:i-10]

        # Check we have enough data
        if len(prev_window) < 10 or len(window) < 15:
            continue

        # Strong uptrend before flag
        prev_close_vals = prev_window['Close'].values
        if len(prev_close_vals) != 10:
            continue
        prev_trend = np.polyfit(range(len(prev_close_vals)), prev_close_vals, 1)[0]

        # Consolidation (flag)
        flag_window = window['Close'].tail(10)
        if len(flag_window) < 10:
            continue
        flag_volatility = flag_window.std() / flag_window.mean()
        flag_vals = flag_window.values
        flag_trend = np.polyfit(range(len(flag_vals)), flag_vals, 1)[0]

        if prev_trend > 0 and flag_volatility < 0.03 and flag_trend < 0:
            patterns_found['bullish_flag'].append({
                'date': df.index[i],
                'price': window['Close'].iloc[-1],
                'confidence': 'High' if flag_volatility < 0.02 else 'Medium'
            })

    # Bearish Flag (continuation)
    for i in range(25, len(df) - 5):
        if i < 25:  # Need at least 25 bars for this pattern
            continue

        window = df.iloc[i-15:i+5]
        prev_window = df.iloc[i-20:i-10]

        # Check we have enough data
        if len(prev_window) < 10 or len(window) < 15:
            continue

        # Strong downtrend before flag
        prev_close_vals = prev_window['Close'].values
        if len(prev_close_vals) != 10:
            continue
        prev_trend = np.polyfit(range(len(prev_close_vals)), prev_close_vals, 1)[0]

        # Consolidation (flag)
        flag_window = window['Close'].tail(10)
        if len(flag_window) < 10:
            continue
        flag_volatility = flag_window.std() / flag_window.mean()
        flag_vals = flag_window.values
        flag_trend = np.polyfit(range(len(flag_vals)), flag_vals, 1)[0]

        if prev_trend < 0 and flag_volatility < 0.03 and flag_trend > 0:
            patterns_found['bearish_flag'].append({
                'date': df.index[i],
                'price': window['Close'].iloc[-1],
                'confidence': 'High' if flag_volatility < 0.02 else 'Medium'
            })

    # Cup and Handle
    for i in range(60, len(df) - 10):
        window = df.iloc[i-60:i+10]

        if len(window) < 50:
            continue

        # Find U-shaped cup
        left_third = window.iloc[:20]['Close'].mean()
        middle_third = window.iloc[20:40]['Close'].mean()
        right_third = window.iloc[40:]['Close'].mean()

        # Cup: middle lower than sides
        if (middle_third < left_third * 0.95 and middle_third < right_third * 0.95 and
            abs(left_third - right_third) / left_third < 0.05):

            # Handle: small consolidation on right
            handle_volatility = window.iloc[-10:]['Close'].std() / window.iloc[-10:]['Close'].mean()

            if handle_volatility < 0.03:
                patterns_found['cup_and_handle'].append({
                    'date': df.index[i],
                    'price': window['Close'].iloc[-1],
                    'confidence': 'High' if handle_volatility < 0.02 else 'Medium'
                })

    return patterns_found


def _detect_macd_divergence(df, lookback=14):
    """
    Detect MACD divergences (price vs MACD momentum)

    Returns DataFrame with divergence signals added
    """
    df['MACD_Bullish_Div'] = False
    df['MACD_Bearish_Div'] = False

    for i in range(lookback, len(df)):
        # Get recent window
        price_window = df['Close'].iloc[i-lookback:i+1]
        macd_window = df['MACD'].iloc[i-lookback:i+1]

        # Find local extrema
        price_min_idx = price_window.idxmin()
        price_max_idx = price_window.idxmax()
        macd_min_idx = macd_window.idxmin()
        macd_max_idx = macd_window.idxmax()

        # Bullish Divergence: Price makes lower low, MACD makes higher low
        if (price_min_idx == price_window.index[-1] and  # Recent price low
            macd_min_idx != macd_window.index[-1] and    # MACD low is earlier
            price_window.iloc[-1] < price_window.iloc[0] and  # Price lower
            macd_window.iloc[-1] > macd_window.min()):    # MACD higher
            df.loc[df.index[i], 'MACD_Bullish_Div'] = True

        # Bearish Divergence: Price makes higher high, MACD makes lower high
        if (price_max_idx == price_window.index[-1] and  # Recent price high
            macd_max_idx != macd_window.index[-1] and    # MACD high is earlier
            price_window.iloc[-1] > price_window.iloc[0] and  # Price higher
            macd_window.iloc[-1] < macd_window.max()):    # MACD lower
            df.loc[df.index[i], 'MACD_Bearish_Div'] = True

    return df


def _calculate_psar(df, iaf=0.02, maxaf=0.2):
    """Calculate Parabolic SAR"""
    length = len(df)
    psar = df['Close'].copy()
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    hp = df['High'].iloc[0]
    lp = df['Low'].iloc[0]

    for i in range(2, length):
        if bull:
            psar.iloc[i] = psar.iloc[i - 1] + af * (hp - psar.iloc[i - 1])
        else:
            psar.iloc[i] = psar.iloc[i - 1] + af * (lp - psar.iloc[i - 1])

        reverse = False

        if bull:
            if df['Low'].iloc[i] < psar.iloc[i]:
                bull = False
                reverse = True
                psar.iloc[i] = hp
                lp = df['Low'].iloc[i]
                af = iaf
        else:
            if df['High'].iloc[i] > psar.iloc[i]:
                bull = True
                reverse = True
                psar.iloc[i] = lp
                hp = df['High'].iloc[i]
                af = iaf

        if not reverse:
            if bull:
                if df['High'].iloc[i] > hp:
                    hp = df['High'].iloc[i]
                    af = min(af + iaf, maxaf)
                if df['Low'].iloc[i - 1] < psar.iloc[i]:
                    psar.iloc[i] = df['Low'].iloc[i - 1]
                if df['Low'].iloc[i - 2] < psar.iloc[i]:
                    psar.iloc[i] = df['Low'].iloc[i - 2]
            else:
                if df['Low'].iloc[i] < lp:
                    lp = df['Low'].iloc[i]
                    af = min(af + iaf, maxaf)
                if df['High'].iloc[i - 1] > psar.iloc[i]:
                    psar.iloc[i] = df['High'].iloc[i - 1]
                if df['High'].iloc[i - 2] > psar.iloc[i]:
                    psar.iloc[i] = df['High'].iloc[i - 2]

        if bull:
            psarbull[i] = psar.iloc[i]
        else:
            psarbear[i] = psar.iloc[i]

    return psar


def render_advanced_chart(ticker, price_data):
    """
    Render fully interactive chart with ALL indicators
    Matching Yahoo Finance Advanced Charts functionality
    """

    st.markdown(f"### 📊 {ticker} - Advanced Interactive Chart")
    st.markdown("*All Yahoo Finance indicators available below*")

    # Session state caching for ultra-fast repeat visits
    # Create unique cache key based on ticker, period, and data length
    if 'chart_period' not in st.session_state:
        st.session_state.chart_period = "6M"

    cache_key = f"{ticker}_{st.session_state.chart_period}_{len(price_data)}"

    # Check if indicators are already cached in session state
    if f'indicators_{cache_key}' not in st.session_state:
        # Calculate indicators (with function-level caching)
        st.session_state[f'indicators_{cache_key}'] = calculate_all_indicators(price_data.copy())

    chart_data = st.session_state[f'indicators_{cache_key}']

    # ===== CONTROLS =====
    st.markdown("---")

    # Row 1: Chart Type and Time Range
    control_col1, control_col2 = st.columns([1, 3])

    with control_col1:
        chart_type = st.radio(
            "Chart Type",
            ["Candlestick", "Line", "Area", "OHLC", "Hollow Candlestick"],
            horizontal=False
        )

    with control_col2:
        st.markdown("**Time Range:**")
        t1, t2, t3, t4, t5, t6, t7, t8 = st.columns(8)

        if 'chart_period' not in st.session_state:
            st.session_state.chart_period = "6M"

        if t1.button("1D"): st.session_state.chart_period = "1D"
        if t2.button("5D"): st.session_state.chart_period = "5D"
        if t3.button("1M"): st.session_state.chart_period = "1M"
        if t4.button("3M"): st.session_state.chart_period = "3M"
        if t5.button("6M"): st.session_state.chart_period = "6M"
        if t6.button("1Y"): st.session_state.chart_period = "1Y"
        if t7.button("5Y"): st.session_state.chart_period = "5Y"
        if t8.button("Max"): st.session_state.chart_period = "Max"

    # Filter data by period
    period_map = {"1D": 1, "5D": 5, "1M": 22, "3M": 66, "6M": 126, "1Y": 252, "5Y": 1260, "Max": None}
    period_days = period_map[st.session_state.chart_period]
    if period_days:
        chart_data = chart_data.iloc[-min(period_days, len(chart_data)):]

    st.markdown("---")

    # ===== PROFESSIONAL TOOLBAR LAYOUT =====

    # Enhanced Indicator Presets
    st.markdown("### 🎯 Quick Indicator Presets")

    # Get organized presets
    preset_categories = get_preset_categories()

    # Create categorized options for selectbox
    preset_options = []
    preset_keys_map = {}  # Map display string to preset key

    category_order = [
        'SHORT-TERM TRADING',
        'MEDIUM-TERM TRADING',
        'LONG-TERM INVESTING',
        'SPECIALIZED STRATEGIES'
    ]

    for category in category_order:
        if category in preset_categories:
            preset_options.append(f"━━━ {category} ━━━")
            preset_keys_map[f"━━━ {category} ━━━"] = None  # Header, not selectable

            for preset in preset_categories[category]:
                display_text = preset['display']
                preset_options.append(f"  {display_text}")
                preset_keys_map[f"  {display_text}"] = preset['key']

    # Layout: Dropdown + Info Button + Active Badge
    preset_ui_col1, preset_ui_col2, preset_ui_col3 = st.columns([3, 1, 2])

    with preset_ui_col1:
        # Initialize session state for selected preset display
        if 'preset_selection_display' not in st.session_state:
            st.session_state.preset_selection_display = "  🎯 Swing Trading"

        selected_display = st.selectbox(
            "Select Trading Strategy:",
            options=preset_options,
            index=preset_options.index(st.session_state.preset_selection_display) if st.session_state.preset_selection_display in preset_options else 0,
            key="preset_selector",
            label_visibility="collapsed"
        )

        # Apply preset if selection changed and it's not a category header
        selected_key = preset_keys_map.get(selected_display)
        if selected_key:
            # Check if this is a new selection
            if st.session_state.get('active_preset') != selected_key:
                apply_preset(selected_key)
                st.session_state.preset_selection_display = selected_display
                st.rerun()

    with preset_ui_col2:
        # Inline help button with popover
        with st.popover("ℹ️ Help"):
            active_preset_key = st.session_state.get('active_preset', 'swing_trading')
            if active_preset_key in STRATEGY_PRESETS:
                preset_info = STRATEGY_PRESETS[active_preset_key]
                st.markdown(f"### {preset_info['emoji']} {preset_info['name']}")
                st.markdown(f"**Description:** {preset_info['description']}")
                st.markdown(f"**Best For:** {preset_info['best_for']}")
                st.markdown(f"**Timeframe:** {preset_info['timeframe']}")
                st.markdown(f"**Complexity:** {preset_info['complexity']}")

                st.markdown("---")
                st.markdown("#### 📚 Tutorial")
                st.markdown(f"**What:** {preset_info['tutorial']['what']}")
                st.markdown(f"**Why:** {preset_info['tutorial']['why']}")
                st.markdown(f"**When:** {preset_info['tutorial']['when']}")

    with preset_ui_col3:
        # Active preset indicator badge
        active_preset_key = st.session_state.get('active_preset', 'swing_trading')
        if active_preset_key in STRATEGY_PRESETS:
            active_preset = STRATEGY_PRESETS[active_preset_key]
            st.markdown(
                f"""<div style='background-color: #4CAF50; color: white; padding: 8px 12px;
                border-radius: 5px; text-align: center; font-weight: bold; margin-top: 0px;'>
                ✓ Active: {active_preset['emoji']} {active_preset['name']}
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Preset Comparison View (expandable)
    with st.expander("📊 **COMPARE ALL STRATEGIES** - View side-by-side strategy comparison", expanded=False):
        st.markdown("**Compare all 15 trading strategies to find the best fit for your style:**")

        # Build comparison dataframe
        comparison_data = []
        for key in ['scalping', 'day_trading', 'momentum_trading', 'swing_trading',
                    'trend_following', 'breakout_trading', 'deep_value', 'position_trading',
                    'income_dividend', 'options_trading', 'institutional', 'mean_reversion',
                    'crypto_volatile', 'full_analysis', 'clean_chart']:
            if key in STRATEGY_PRESETS:
                preset = STRATEGY_PRESETS[key]
                comparison_data.append({
                    'Strategy': f"{preset['emoji']} {preset['name']}",
                    'Category': preset['category'],
                    'Timeframe': preset['timeframe'],
                    'Complexity': preset['complexity'],
                    'Best For': preset['best_for']
                })

        comparison_df = pd.DataFrame(comparison_data)
        from app_utils import display_dataframe_full_width
        display_dataframe_full_width(comparison_df, hide_index=True)

        st.markdown("**💡 Tip:** Click the ℹ️ Help button above after selecting a strategy to see detailed tutorial and indicator configuration.")

    st.markdown("---")

    # Comparison symbols in compact layout
    comp_col1, comp_col2 = st.columns([2, 3])
    with comp_col1:
        st.markdown("**📊 Compare With:**")
    with comp_col2:
        compare_symbols = st.text_input("Comparison Symbols", placeholder="e.g., SPY, QQQ, TSLA", key="compare_syms", label_visibility="collapsed")

    comparison_data = {}
    if compare_symbols:
        symbols = [s.strip().upper() for s in compare_symbols.split(",") if s.strip()]
        for symbol in symbols:
            try:
                comp_ticker = yf.Ticker(symbol)
                period_str = "1d" if st.session_state.chart_period == "1D" else \
                            "5d" if st.session_state.chart_period == "5D" else \
                            "1mo" if st.session_state.chart_period == "1M" else \
                            "3mo" if st.session_state.chart_period == "3M" else \
                            "6mo" if st.session_state.chart_period == "6M" else \
                            "1y" if st.session_state.chart_period == "1Y" else \
                            "5y" if st.session_state.chart_period == "5Y" else "max"
                comp_data = comp_ticker.history(period=period_str)
                if not comp_data.empty:
                    comparison_data[symbol] = comp_data
            except:
                pass

    # Compact Indicator Selector
    with st.expander("🔧 **INDICATOR TOOLBOX** - Click to customize indicators", expanded=False):

        # Overlays section
        st.markdown("#### 📈 Overlays & Moving Averages")
        overlay_col1, overlay_col2, overlay_col3 = st.columns(3)

        with overlay_col1:
            st.markdown("**📊 Simple Moving Averages**")
            show_sma5 = st.checkbox("SMA 5", value=st.session_state.get('sma5', False), key="sma5")
            show_sma10 = st.checkbox("SMA 10", value=st.session_state.get('sma10', False), key="sma10")
            show_sma20 = st.checkbox("SMA 20", value=st.session_state.get('sma20', False), key="sma20")
            show_sma50 = st.checkbox("SMA 50", value=st.session_state.get('sma50', True), key="sma50")
            show_sma100 = st.checkbox("SMA 100", value=st.session_state.get('sma100', False), key="sma100")
            show_sma200 = st.checkbox("SMA 200", value=st.session_state.get('sma200', True), key="sma200")

        with overlay_col2:
            st.markdown("**⚡ Exponential Moving Averages**")
            show_ema5 = st.checkbox("EMA 5", value=st.session_state.get('ema5', False), key="ema5")
            show_ema10 = st.checkbox("EMA 10", value=st.session_state.get('ema10', False), key="ema10")
            show_ema12 = st.checkbox("EMA 12", value=st.session_state.get('ema12', False), key="ema12")
            show_ema20 = st.checkbox("EMA 20", value=st.session_state.get('ema20', False), key="ema20")
            show_ema26 = st.checkbox("EMA 26", value=st.session_state.get('ema26', False), key="ema26")
            show_ema50 = st.checkbox("EMA 50", value=st.session_state.get('ema50', False), key="ema50")

        with overlay_col3:
            st.markdown("**🎯 Bands & Other**")
            show_bb = st.checkbox("Bollinger Bands", value=st.session_state.get('bb', False), key="bb")
            show_ichimoku = st.checkbox("Ichimoku Cloud", value=st.session_state.get('ichi', False), key="ichi")
            show_psar = st.checkbox("Parabolic SAR", value=st.session_state.get('psar', False), key="psar")
            show_vwap = st.checkbox("VWAP (Institutional)", value=st.session_state.get('vwap', False), key="vwap",
                                   help="Volume-Weighted Average Price - institutional benchmark for 'fair value'")
            st.markdown("**📊 Volume**")
            show_volume = st.checkbox("Volume Bars", value=st.session_state.get('vol', True), key="vol")
            show_volume_sma = st.checkbox("Volume SMA", value=st.session_state.get('vol_sma', False), key="vol_sma")

        st.markdown("---")

        # Oscillators section
        st.markdown("#### 📉 Oscillators & Indicators")
        osc_col1, osc_col2, osc_col3 = st.columns(3)

        with osc_col1:
            st.markdown("**💪 Momentum**")
            show_rsi = st.checkbox("RSI (14)", value=st.session_state.get('rsi', False), key="rsi")
            show_stoch = st.checkbox("Stochastic", value=st.session_state.get('stoch', False), key="stoch")
            show_williams = st.checkbox("Williams %R", value=st.session_state.get('willr', False), key="willr")
            st.markdown("**📊 MACD**")
            show_macd = st.checkbox("MACD", value=st.session_state.get('macd', False), key="macd")

        with osc_col2:
            st.markdown("**📈 Trend Strength**")
            show_adx = st.checkbox("ADX (14)", value=st.session_state.get('adx', False), key="adx")
            show_cci = st.checkbox("CCI (20)", value=st.session_state.get('cci', False), key="cci")

        with osc_col3:
            st.markdown("**💰 Volume & Money Flow**")
            show_obv = st.checkbox("OBV", value=st.session_state.get('obv', False), key="obv")
            show_mfi = st.checkbox("MFI (14)", value=st.session_state.get('mfi', False), key="mfi")

    st.markdown("---")

    # ===== PATTERN DETECTION CONTROL =====
    pattern_col1, pattern_col2 = st.columns([3, 2])

    with pattern_col1:
        show_pattern_detection = st.checkbox(
            "🔍 Enable Chart Pattern Detection",
            value=False,
            help="Analyze chart for technical patterns (head & shoulders, double tops/bottoms, triangles, etc.). This is an optional feature that provides deeper technical analysis."
        )

    with pattern_col2:
        if st.button("❓ What are Chart Patterns?"):
            st.session_state['show_pattern_tutorial'] = not st.session_state.get('show_pattern_tutorial', False)

    # Tutorial expander (shown when button clicked)
    if st.session_state.get('show_pattern_tutorial', False):
        with st.expander("📚 Chart Pattern Detection Tutorial", expanded=True):
            st.markdown("""
            ### What are Chart Patterns?

            Chart patterns are recognizable formations in price movements that traders use to predict future price direction.
            These patterns are based on historical price behavior and technical analysis principles.

            #### 🔴 **Reversal Patterns** (Indicate potential trend changes)
            - **Head & Shoulders**: Bearish reversal pattern with three peaks (middle highest)
            - **Inverse Head & Shoulders**: Bullish reversal pattern with three troughs (middle lowest)
            - **Double Top/Bottom**: Two peaks/troughs at similar price levels
            - **Triple Top/Bottom**: Three peaks/troughs confirming strong resistance/support

            #### 🟢 **Continuation Patterns** (Suggest trend will continue)
            - **Bullish Flag**: Brief consolidation after strong uptrend
            - **Bearish Flag**: Brief consolidation after strong downtrend
            - **Pennants**: Small symmetrical triangles during trends

            #### 🔵 **Breakout Patterns** (Price consolidation before breakout)
            - **Ascending Triangle**: Flat resistance + rising support (bullish)
            - **Descending Triangle**: Flat support + falling resistance (bearish)
            - **Cup & Handle**: U-shaped recovery with small consolidation (bullish)

            #### 🎯 **Confidence Levels**
            - **High**: Pattern meets strict criteria with strong signal strength
            - **Medium**: Pattern partially formed with moderate signal strength

            #### ⚠️ **Important Notes**
            - Patterns are **probabilistic**, not guaranteed predictions
            - Use patterns alongside other indicators (RSI, MACD, volume)
            - Consider overall market context and fundamentals
            - Pattern detection works best on longer timeframes (6M, 1Y, 5Y)

            **To use**: Check the "Enable Chart Pattern Detection" box above to scan the chart for these patterns.
            """)

    st.markdown("---")

    # ===== BUILD CHART =====

    # Determine number of subplots
    num_rows = 1  # Main price chart
    row_map = {"price": 1}

    oscillators_to_show = []
    if show_volume:
        num_rows += 1
        row_map["volume"] = num_rows

    if show_rsi:
        oscillators_to_show.append("RSI")
    if show_macd:
        oscillators_to_show.append("MACD")
    if show_stoch:
        oscillators_to_show.append("Stochastic")
    if show_williams:
        oscillators_to_show.append("Williams %R")
    if show_adx:
        oscillators_to_show.append("ADX")
    if show_cci:
        oscillators_to_show.append("CCI")
    if show_obv:
        oscillators_to_show.append("OBV")
    if show_mfi:
        oscillators_to_show.append("MFI")

    # Create subplot for each selected oscillator
    for osc in oscillators_to_show:
        num_rows += 1
        row_map[osc] = num_rows

    # ===== TECHNICAL SUMMARY (MOVED TO TOP) =====
    st.markdown("---")
    st.markdown("### 📊 Technical Summary")
    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

    latest = chart_data.iloc[-1]

    with sum_col1:
        st.metric("Close", f"${latest['Close']:.2f}")
        if 'SMA50' in chart_data.columns:
            sma50_val = latest['SMA50']
            st.metric("SMA50", f"${sma50_val:.2f}",
                     f"{((latest['Close'] / sma50_val - 1) * 100):.2f}%" if sma50_val > 0 else "N/A")

    with sum_col2:
        if 'RSI' in chart_data.columns:
            rsi_val = latest['RSI']
            rsi_signal = "🔴 Overbought" if rsi_val > 70 else "🟢 Oversold" if rsi_val < 30 else "⚪ Neutral"
            st.metric("RSI", f"{rsi_val:.1f}", rsi_signal)

    with sum_col3:
        if 'MACD' in chart_data.columns:
            macd_val = latest['MACD']
            signal_val = latest['MACD_Signal']

            # Check for recent crossovers and divergences
            recent_data = chart_data.tail(5)  # Last 5 periods
            has_bullish_cross = recent_data['MACD_Bullish_Cross'].any()
            has_bearish_cross = recent_data['MACD_Bearish_Cross'].any()
            has_bullish_div = recent_data['MACD_Bullish_Div'].any()
            has_bearish_div = recent_data['MACD_Bearish_Div'].any()

            if has_bullish_div:
                macd_signal = "⭐ Bullish Divergence"
            elif has_bearish_div:
                macd_signal = "⭐ Bearish Divergence"
            elif has_bullish_cross:
                macd_signal = "🟢 Bullish Cross"
            elif has_bearish_cross:
                macd_signal = "🔴 Bearish Cross"
            elif macd_val > signal_val:
                macd_signal = "🟢 Bullish"
            else:
                macd_signal = "🔴 Bearish"

            st.metric("MACD", f"{macd_val:.2f}", macd_signal)

    with sum_col4:
        if 'ADX' in chart_data.columns:
            adx_val = latest['ADX']
            adx_signal = "💪 Strong Trend" if adx_val > 25 else "📊 Weak Trend"
            st.metric("ADX", f"{adx_val:.1f}", adx_signal)

    st.markdown("---")

    # Calculate row heights dynamically
    if num_rows == 1:
        row_heights = [1.0]
    elif num_rows == 2:
        row_heights = [0.7, 0.3]
    elif num_rows == 3:
        row_heights = [0.6, 0.2, 0.2]
    else:
        # Main chart gets 60%, others split remaining 40%
        row_heights = [0.6] + [0.4 / (num_rows - 1)] * (num_rows - 1)

    # Create figure
    fig = make_subplots(
        rows=num_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights
    )

    # ===== MAIN PRICE CHART =====
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=chart_data.index,
            open=chart_data['Open'],
            high=chart_data['High'],
            low=chart_data['Low'],
            close=chart_data['Close'],
            name=ticker,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ), row=1, col=1)

    elif chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['Close'],
            name=ticker,
            line=dict(color='#2962ff', width=2),
            mode='lines'
        ), row=1, col=1)

    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['Close'],
            name=ticker,
            fill='tozeroy',
            fillcolor='rgba(41, 98, 255, 0.2)',
            line=dict(color='#2962ff', width=2),
            mode='lines'
        ), row=1, col=1)

    elif chart_type == "OHLC":
        fig.add_trace(go.Ohlc(
            x=chart_data.index,
            open=chart_data['Open'],
            high=chart_data['High'],
            low=chart_data['Low'],
            close=chart_data['Close'],
            name=ticker
        ), row=1, col=1)

    # Add comparison symbols (normalized to percentage change)
    if comparison_data:
        base_price = chart_data['Close'].iloc[0]
        for symbol, comp_df in comparison_data.items():
            if not comp_df.empty and len(comp_df) > 0:
                # Normalize to percentage change
                comp_base = comp_df['Close'].iloc[0]
                normalized_comp = ((comp_df['Close'] / comp_base) - 1) * 100
                main_normalized = ((chart_data['Close'] / base_price) - 1) * 100

                fig.add_trace(go.Scatter(
                    x=comp_df.index,
                    y=normalized_comp,
                    name=f"{symbol} (%)",
                    mode='lines',
                    line=dict(width=1.5, dash='dot'),
                    yaxis="y2"
                ), row=1, col=1)

    # Add selected overlays
    sma_colors = {'SMA5': '#FF6B6B', 'SMA10': '#4ECDC4', 'SMA20': '#FFD93D', 'SMA50': '#6BCB77', 'SMA100': '#9B59B6', 'SMA200': '#E74C3C'}
    ema_colors = {'EMA5': '#F39C12', 'EMA10': '#3498DB', 'EMA12': '#1ABC9C', 'EMA20': '#E67E22', 'EMA26': '#9B59B6', 'EMA50': '#C0392B'}

    if show_sma5:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA5'], name='SMA 5', line=dict(color=sma_colors['SMA5'], width=1)), row=1, col=1)
    if show_sma10:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA10'], name='SMA 10', line=dict(color=sma_colors['SMA10'], width=1)), row=1, col=1)
    if show_sma20:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA20'], name='SMA 20', line=dict(color=sma_colors['SMA20'], width=1.2)), row=1, col=1)
    if show_sma50:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA50'], name='SMA 50', line=dict(color=sma_colors['SMA50'], width=1.5)), row=1, col=1)
    if show_sma100:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA100'], name='SMA 100', line=dict(color=sma_colors['SMA100'], width=1.5)), row=1, col=1)
    if show_sma200:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA200'], name='SMA 200', line=dict(color=sma_colors['SMA200'], width=2)), row=1, col=1)

    if show_ema5:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['EMA5'], name='EMA 5', line=dict(color=ema_colors['EMA5'], width=1, dash='dot')), row=1, col=1)
    if show_ema10:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['EMA10'], name='EMA 10', line=dict(color=ema_colors['EMA10'], width=1, dash='dot')), row=1, col=1)
    if show_ema12:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['EMA12'], name='EMA 12', line=dict(color=ema_colors['EMA12'], width=1, dash='dot')), row=1, col=1)
    if show_ema20:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['EMA20'], name='EMA 20', line=dict(color=ema_colors['EMA20'], width=1, dash='dot')), row=1, col=1)
    if show_ema26:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['EMA26'], name='EMA 26', line=dict(color=ema_colors['EMA26'], width=1, dash='dot')), row=1, col=1)
    if show_ema50:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['EMA50'], name='EMA 50', line=dict(color=ema_colors['EMA50'], width=1.5, dash='dot')), row=1, col=1)

    if show_bb:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Upper'], name='BB Upper', line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Lower'], name='BB Lower', line=dict(color='rgba(128,128,128,0.5)', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)

    if show_ichimoku:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Ichimoku_SpanA'], name='Ichi Span A', line=dict(color='#00bcd4', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Ichimoku_SpanB'], name='Ichi Span B', line=dict(color='#ff9800', width=1), fill='tonexty', fillcolor='rgba(0,188,212,0.1)'), row=1, col=1)

    if show_psar:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['PSAR'], name='PSAR', mode='markers', marker=dict(size=2, color='purple')), row=1, col=1)

    # Add VWAP - Volume-Weighted Average Price (institutional benchmark)
    if show_vwap:
        fig.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['VWAP'],
            name='VWAP',
            line=dict(color='#FFA726', width=2, dash='dot'),
            hovertemplate='VWAP: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)

    # Add Volume with enhanced coloring
    if show_volume and "volume" in row_map:
        # Color-code volume bars: red (down day), green (up day), yellow (high volume spike)
        colors = []
        for i in range(len(chart_data)):
            if chart_data['Volume_Spike'].iloc[i]:
                # High volume spike - bright yellow for attention
                colors.append('#FFD700')
            elif chart_data['Close'].iloc[i] < chart_data['Open'].iloc[i]:
                # Down day - red
                colors.append('#ef5350')
            else:
                # Up day - green
                colors.append('#26a69a')

        fig.add_trace(go.Bar(
            x=chart_data.index,
            y=chart_data['Volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False,
            hovertemplate='Volume: %{y:,.0f}<br>%{x}<extra></extra>'
        ), row=row_map["volume"], col=1)

        if show_volume_sma:
            fig.add_trace(go.Scatter(
                x=chart_data.index,
                y=chart_data['Volume_SMA'],
                name='Vol SMA (20)',
                line=dict(color='orange', width=1.5),
                hovertemplate='Vol SMA: %{y:,.0f}<extra></extra>'
            ), row=row_map["volume"], col=1)

    # Add Oscillators
    if "RSI" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['RSI'], name='RSI', line=dict(color='purple', width=1.5)),
                      row=row_map["RSI"], col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=0.5, row=row_map["RSI"], col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=0.5, row=row_map["RSI"], col=1)
        fig.update_yaxes(title_text="RSI", row=row_map["RSI"], col=1)

    if "MACD" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MACD'], name='MACD', line=dict(color='blue', width=1)),
                      row=row_map["MACD"], col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MACD_Signal'], name='Signal', line=dict(color='orange', width=1)),
                      row=row_map["MACD"], col=1)
        fig.add_trace(go.Bar(x=chart_data.index, y=chart_data['MACD_Hist'], name='Histogram', marker_color='gray', showlegend=False),
                      row=row_map["MACD"], col=1)

        # Add MACD Crossover markers
        bullish_crosses = chart_data[chart_data['MACD_Bullish_Cross']]
        bearish_crosses = chart_data[chart_data['MACD_Bearish_Cross']]

        if not bullish_crosses.empty:
            fig.add_trace(go.Scatter(
                x=bullish_crosses.index,
                y=bullish_crosses['MACD'],
                mode='markers',
                name='Bullish Cross',
                marker=dict(size=10, color='green', symbol='triangle-up'),
                showlegend=True
            ), row=row_map["MACD"], col=1)

        if not bearish_crosses.empty:
            fig.add_trace(go.Scatter(
                x=bearish_crosses.index,
                y=bearish_crosses['MACD'],
                mode='markers',
                name='Bearish Cross',
                marker=dict(size=10, color='red', symbol='triangle-down'),
                showlegend=True
            ), row=row_map["MACD"], col=1)

        # Add MACD Divergence markers
        bullish_divs = chart_data[chart_data['MACD_Bullish_Div']]
        bearish_divs = chart_data[chart_data['MACD_Bearish_Div']]

        if not bullish_divs.empty:
            fig.add_trace(go.Scatter(
                x=bullish_divs.index,
                y=bullish_divs['MACD'],
                mode='markers',
                name='Bullish Divergence',
                marker=dict(size=12, color='lime', symbol='star', line=dict(color='darkgreen', width=1)),
                showlegend=True
            ), row=row_map["MACD"], col=1)

        if not bearish_divs.empty:
            fig.add_trace(go.Scatter(
                x=bearish_divs.index,
                y=bearish_divs['MACD'],
                mode='markers',
                name='Bearish Divergence',
                marker=dict(size=12, color='red', symbol='star', line=dict(color='darkred', width=1)),
                showlegend=True
            ), row=row_map["MACD"], col=1)

        fig.update_yaxes(title_text="MACD", row=row_map["MACD"], col=1)

    if "Stochastic" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Stoch_K'], name='%K', line=dict(color='blue', width=1)),
                      row=row_map["Stochastic"], col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Stoch_D'], name='%D', line=dict(color='red', width=1)),
                      row=row_map["Stochastic"], col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=0.5, row=row_map["Stochastic"], col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=0.5, row=row_map["Stochastic"], col=1)
        fig.update_yaxes(title_text="Stochastic", row=row_map["Stochastic"], col=1)

    if "Williams %R" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Williams_R'], name='Williams %R', line=dict(color='purple', width=1.5)),
                      row=row_map["Williams %R"], col=1)
        fig.add_hline(y=-20, line_dash="dash", line_color="red", line_width=0.5, row=row_map["Williams %R"], col=1)
        fig.add_hline(y=-80, line_dash="dash", line_color="green", line_width=0.5, row=row_map["Williams %R"], col=1)
        fig.update_yaxes(title_text="Williams %R", row=row_map["Williams %R"], col=1)

    if "ADX" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['ADX'], name='ADX', line=dict(color='black', width=1.5)),
                      row=row_map["ADX"], col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Plus_DI'], name='+DI', line=dict(color='green', width=1)),
                      row=row_map["ADX"], col=1)
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Minus_DI'], name='-DI', line=dict(color='red', width=1)),
                      row=row_map["ADX"], col=1)
        fig.update_yaxes(title_text="ADX", row=row_map["ADX"], col=1)

    if "CCI" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['CCI'], name='CCI', line=dict(color='teal', width=1.5)),
                      row=row_map["CCI"], col=1)
        fig.add_hline(y=100, line_dash="dash", line_color="red", line_width=0.5, row=row_map["CCI"], col=1)
        fig.add_hline(y=-100, line_dash="dash", line_color="green", line_width=0.5, row=row_map["CCI"], col=1)
        fig.update_yaxes(title_text="CCI", row=row_map["CCI"], col=1)

    if "OBV" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['OBV'], name='OBV', line=dict(color='navy', width=1.5)),
                      row=row_map["OBV"], col=1)
        fig.update_yaxes(title_text="OBV", row=row_map["OBV"], col=1)

    if "MFI" in oscillators_to_show:
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MFI'], name='MFI', line=dict(color='darkgreen', width=1.5)),
                      row=row_map["MFI"], col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=0.5, row=row_map["MFI"], col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=0.5, row=row_map["MFI"], col=1)
        fig.update_yaxes(title_text="MFI", row=row_map["MFI"], col=1)

    # Update layout
    chart_height = 400 + (num_rows - 1) * 150

    fig.update_layout(
        template="plotly_white",
        height=chart_height,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="left", x=0),
        margin=dict(l=50, r=50, t=30, b=50)
    )

    fig.update_yaxes(title_text=f"{ticker} Price", row=1, col=1)
    if "volume" in row_map:
        fig.update_yaxes(title_text="Volume", row=row_map["volume"], col=1)

    # Display chart
    plotly_full_width(fig, key="advanced_chart")

    # ===== PATTERN DETECTION SECTION (AFTER CHART) =====
    # Only show if pattern detection is enabled
    if show_pattern_detection:
        st.markdown("---")
        st.markdown("### 🔍 Chart Pattern Detection Report")
        st.markdown(f"**Analysis Period:** {st.session_state.chart_period} | **Total Candles:** {len(chart_data)}")

        # Detect patterns (with function-level caching + session state caching)
        pattern_cache_key = f"patterns_{cache_key}"
        if pattern_cache_key not in st.session_state:
            st.session_state[pattern_cache_key] = _detect_chart_patterns(chart_data)

        chart_patterns = st.session_state[pattern_cache_key]

        # Calculate pattern statistics
        total_patterns = sum(len(patterns) for patterns in chart_patterns.values())

        pattern_names = {
            'head_and_shoulders': 'Head & Shoulders (Bearish)',
            'inverse_head_and_shoulders': 'Inverse H&S (Bullish)',
            'double_top': 'Double Top (Bearish)',
            'double_bottom': 'Double Bottom (Bullish)',
            'triple_top': 'Triple Top (Bearish)',
            'triple_bottom': 'Triple Bottom (Bullish)',
            'ascending_triangle': 'Ascending Triangle (Bullish)',
            'descending_triangle': 'Descending Triangle (Bearish)',
            'symmetrical_triangle': 'Symmetrical Triangle',
            'bullish_flag': 'Bullish Flag (Continuation)',
            'bearish_flag': 'Bearish Flag (Continuation)',
            'bullish_pennant': 'Bullish Pennant',
            'bearish_pennant': 'Bearish Pennant',
            'cup_and_handle': 'Cup & Handle (Bullish)',
            'wedge_rising': 'Rising Wedge (Bearish)',
            'wedge_falling': 'Falling Wedge (Bullish)',
            'channel_up': 'Ascending Channel',
            'channel_down': 'Descending Channel'
        }

        # Pattern score calculation
        bullish_patterns = ['inverse_head_and_shoulders', 'double_bottom', 'triple_bottom',
                           'ascending_triangle', 'bullish_flag', 'bullish_pennant',
                           'cup_and_handle', 'wedge_falling']
        bearish_patterns = ['head_and_shoulders', 'double_top', 'triple_top',
                           'descending_triangle', 'bearish_flag', 'bearish_pennant', 'wedge_rising']

        bullish_count = sum(len(chart_patterns[p]) for p in bullish_patterns if p in chart_patterns)
        bearish_count = sum(len(chart_patterns[p]) for p in bearish_patterns if p in chart_patterns)

        pattern_score = (bullish_count - bearish_count) / max(total_patterns, 1) * 100

        # Display pattern summary
        sum_col1_pat, sum_col2_pat, sum_col3_pat, sum_col4_pat = st.columns(4)

        with sum_col1_pat:
            st.metric("Total Patterns Found", total_patterns)

        with sum_col2_pat:
            st.metric("Bullish Patterns", bullish_count, delta="🟢" if bullish_count > bearish_count else None)

        with sum_col3_pat:
            st.metric("Bearish Patterns", bearish_count, delta="🔴" if bearish_count > bullish_count else None)

        with sum_col4_pat:
            pattern_sentiment = "🟢 Bullish" if pattern_score > 20 else "🔴 Bearish" if pattern_score < -20 else "⚪ Neutral"
            st.metric("Pattern Score", f"{pattern_score:+.0f}", pattern_sentiment)

        # ===== PATTERN VISUALIZATION CHART =====
        if total_patterns > 0:
            st.markdown("---")
            st.markdown("### 📊 Pattern Detection Timeline")
            st.caption("Visual representation of detected patterns on the price chart with key levels marked")

            # Create a price chart with pattern annotations
            pattern_fig = go.Figure()

            # Add candlestick chart as base
            pattern_fig.add_trace(go.Candlestick(
                x=chart_data.index,
                open=chart_data['Open'],
                high=chart_data['High'],
                low=chart_data['Low'],
                close=chart_data['Close'],
                name='Price',
                showlegend=False
            ))

            # Collect all pattern occurrences for markers
            pattern_markers = []
            pattern_annotations = []

            # Color mapping for pattern types
            pattern_colors = {
                'bullish': '#00CC96',  # Green
                'bearish': '#EF553B',  # Red
                'neutral': '#636EFA'   # Blue
            }

            # Pattern symbols for markers
            pattern_symbols = {
                'bullish': 'triangle-up',
                'bearish': 'triangle-down',
                'neutral': 'diamond'
            }

            # Process all patterns and add markers
            for pattern_key, pattern_list in chart_patterns.items():
                if len(pattern_list) > 0:
                    pattern_display_name = pattern_names.get(pattern_key, pattern_key.replace('_', ' ').title())

                    # Determine pattern type
                    if pattern_key in bullish_patterns:
                        pattern_type = 'bullish'
                        pattern_emoji = '🟢'
                    elif pattern_key in bearish_patterns:
                        pattern_type = 'bearish'
                        pattern_emoji = '🔴'
                    else:
                        pattern_type = 'neutral'
                        pattern_emoji = '⚪'

                    # Add each occurrence
                    for occurrence in pattern_list:
                        pattern_markers.append({
                            'date': pd.to_datetime(occurrence['date']),
                            'price': occurrence['price'],
                            'name': pattern_display_name,
                            'type': pattern_type,
                            'confidence': occurrence['confidence'],
                            'emoji': pattern_emoji
                        })

            # Sort markers by date
            pattern_markers.sort(key=lambda x: x['date'])

            # Add markers to chart grouped by type
            for ptype in ['bullish', 'bearish', 'neutral']:
                type_markers = [m for m in pattern_markers if m['type'] == ptype]
                if type_markers:
                    pattern_fig.add_trace(go.Scatter(
                        x=[m['date'] for m in type_markers],
                        y=[m['price'] for m in type_markers],
                        mode='markers',
                        name=f"{ptype.title()} Patterns",
                        marker=dict(
                            size=15,
                            color=pattern_colors[ptype],
                            symbol=pattern_symbols[ptype],
                            line=dict(width=2, color='white')
                        ),
                        text=[f"{m['emoji']} {m['name']}<br>Price: ${m['price']:.2f}<br>Confidence: {m['confidence']}"
                              for m in type_markers],
                        hovertemplate='%{text}<extra></extra>',
                        showlegend=True
                    ))

            # Update layout for professional appearance
            pattern_fig.update_layout(
                title=f"{ticker} Price Chart with Detected Patterns",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                template="plotly_white",
                height=600,
                hovermode='closest',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                ),
                xaxis_rangeslider_visible=False
            )

            # Display the pattern visualization chart
            plotly_full_width(pattern_fig, key="pattern_detection_chart")

            st.markdown("---")

        # Detailed pattern breakdown
        if total_patterns > 0:
            with st.expander("📋 **DETAILED PATTERN BREAKDOWN** - Click to view all detected patterns", expanded=False):
                st.markdown("**All patterns detected in the selected time period with dates and confidence levels:**")
                st.markdown("*Click on any pattern name below to expand and view details*")
                st.markdown("")

                # Group patterns by type
                for pattern_key, pattern_list in chart_patterns.items():
                    if len(pattern_list) > 0:
                        pattern_display_name = pattern_names.get(pattern_key, pattern_key.replace('_', ' ').title())

                        # Determine pattern bias
                        if pattern_key in bullish_patterns:
                            bias_emoji = "🟢"
                            bias_text = "BULLISH"
                        elif pattern_key in bearish_patterns:
                            bias_emoji = "🔴"
                            bias_text = "BEARISH"
                        else:
                            bias_emoji = "⚪"
                            bias_text = "NEUTRAL"

                        # Make each pattern collapsible
                        with st.expander(f"{bias_emoji} {pattern_display_name} ({bias_text}) - {len(pattern_list)} occurrence(s)", expanded=False):
                            # Create table of occurrences
                            pattern_df = pd.DataFrame(pattern_list)
                            if not pattern_df.empty:
                                pattern_df['date'] = pd.to_datetime(pattern_df['date']).dt.strftime('%Y-%m-%d')
                                pattern_df['price'] = pattern_df['price'].apply(lambda x: f"${x:.2f}")

                                # Display as table
                                from app_utils import display_dataframe_full_width
                                display_dataframe_full_width(
                                    pattern_df.rename(columns={
                                        'date': 'Date Detected',
                                        'price': 'Price Level',
                                        'confidence': 'Confidence'
                                    }),
                                    hide_index=True
                                )

                # Pattern interpretation guide
                st.markdown("### 📚 Pattern Interpretation Guide")
                st.markdown("""
                **Reversal Patterns:** Indicate potential trend changes
                - Head & Shoulders / Double Top / Triple Top → **Bearish reversal**
                - Inverse H&S / Double Bottom / Triple Bottom → **Bullish reversal**

                **Continuation Patterns:** Suggest trend will continue
                - Bullish Flag / Pennant → **Uptrend continuation**
                - Bearish Flag / Pennant → **Downtrend continuation**

                **Breakout Patterns:** Price consolidation before breakout
                - Ascending Triangle → **Bullish breakout expected**
                - Descending Triangle → **Bearish breakdown expected**
                - Cup & Handle → **Bullish breakout**

                **Confidence Levels:**
                - **High:** Pattern meets strict criteria, stronger signal
                - **Medium:** Pattern partially formed, moderate signal
                """)
        else:
            st.info("ℹ️ No significant chart patterns detected in the selected time period. Try selecting a longer time range (6M, 1Y, or 5Y) for better pattern detection.")
