"""
Historical tracking and analysis for Fear & Greed Index
Provides persistence, trending, and professional-grade analytics
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np


class FearGreedHistory:
    """Manages historical Fear & Greed data with file-based persistence"""

    def __init__(self, data_file="data/fear_greed_history.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        self.history = self._load_history()

    def _load_history(self):
        """Load historical data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return []
        return []

    def _save_history(self):
        """Save historical data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_record(self, score, category, level, components):
        """
        Add a new Fear & Greed record

        Args:
            score: Overall F&G score (0-100)
            category: Category name (e.g., "Extreme Fear")
            level: Analysis level (1, 2, or 3)
            components: Dict of individual indicator scores
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'category': category,
            'level': level,
            'components': components
        }

        # Avoid duplicate entries within same hour
        if self.history:
            last_record = self.history[-1]
            last_time = datetime.fromisoformat(last_record['timestamp'])
            if datetime.now() - last_time < timedelta(hours=1):
                # Update existing record instead
                self.history[-1] = record
            else:
                self.history.append(record)
        else:
            self.history.append(record)

        # Keep only last 90 days
        cutoff_date = datetime.now() - timedelta(days=90)
        self.history = [
            r for r in self.history
            if datetime.fromisoformat(r['timestamp']) > cutoff_date
        ]

        self._save_history()

    def get_dataframe(self, days=30):
        """Get history as pandas DataFrame for analysis"""
        if not self.history:
            return pd.DataFrame()

        cutoff = datetime.now() - timedelta(days=days)
        recent_history = [
            r for r in self.history
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]

        if not recent_history:
            return pd.DataFrame()

        df = pd.DataFrame(recent_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        return df

    def get_trend(self, days=7):
        """
        Calculate trend over specified period

        Returns:
            dict with trend_direction, trend_strength, momentum
        """
        df = self.get_dataframe(days=days)

        if len(df) < 2:
            return {
                'trend_direction': 'neutral',
                'trend_strength': 0,
                'momentum': 0,
                'change': 0,
                'slope': 0
            }

        # Calculate linear regression slope
        x = np.arange(len(df))
        y = df['score'].values

        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]

        # Calculate momentum (recent rate of change)
        if len(df) >= 3:
            recent_change = df['score'].iloc[-1] - df['score'].iloc[-3]
        else:
            recent_change = df['score'].iloc[-1] - df['score'].iloc[0]

        # Overall change
        total_change = df['score'].iloc[-1] - df['score'].iloc[0]

        # Classify trend
        if slope > 0.5:
            direction = 'bullish'
        elif slope < -0.5:
            direction = 'bearish'
        else:
            direction = 'neutral'

        return {
            'trend_direction': direction,
            'trend_strength': abs(slope),
            'momentum': recent_change,
            'change': total_change,
            'slope': slope
        }

    def get_percentile(self, current_score, days=90):
        """Calculate percentile of current score vs historical data"""
        df = self.get_dataframe(days=days)

        if len(df) < 10:
            return None

        percentile = (df['score'] < current_score).sum() / len(df) * 100
        return percentile

    def detect_divergence(self, current_components):
        """
        Detect divergence between components

        Returns list of divergence warnings
        """
        warnings = []

        # Check for conflicting signals
        if 'vix' in current_components and 'put_call_ratio' in current_components:
            vix_score = current_components['vix']
            pc_score = current_components['put_call_ratio']

            # VIX low (greed) but put/call high (fear)
            if vix_score > 70 and pc_score < 30:
                warnings.append({
                    'type': 'VIX vs Put/Call Divergence',
                    'severity': 'medium',
                    'message': 'VIX shows complacency but heavy put buying suggests smart money hedging'
                })

        if 'market_breadth' in current_components and 'safe_haven_demand' in current_components:
            breadth = current_components['market_breadth']
            safe_haven = current_components['safe_haven_demand']

            # Strong breadth but high safe haven demand
            if breadth > 70 and safe_haven < 30:
                warnings.append({
                    'type': 'Breadth vs Safe Haven Divergence',
                    'severity': 'high',
                    'message': 'Market breadth strong but gold/treasuries outperforming - mixed signals'
                })

        if 'junk_bond_spread' in current_components:
            junk_score = current_components['junk_bond_spread']

            # Calculate overall equity sentiment (average of non-credit indicators)
            equity_indicators = ['vix', 'put_call_ratio', 'market_breadth', 'distance_52w_high']
            equity_scores = [current_components.get(k, 50) for k in equity_indicators if k in current_components]

            if equity_scores:
                avg_equity_sentiment = np.mean(equity_scores)

                # Credit market fear but equity greed
                if avg_equity_sentiment > 65 and junk_score < 35:
                    warnings.append({
                        'type': 'Credit vs Equity Divergence',
                        'severity': 'critical',
                        'message': 'Stocks showing greed but credit markets fearful - professional caution'
                    })

        return warnings

    def get_regime_context(self, current_score):
        """
        Analyze historical performance after similar F&G scores

        Returns dict with forward returns at various timeframes
        """
        df = self.get_dataframe(days=90)

        if len(df) < 30:
            return None

        # Find similar scores (±10 points)
        similar_periods = df[abs(df['score'] - current_score) < 10].copy()

        if len(similar_periods) < 5:
            return None

        # For simplicity, we can't calculate forward returns without price data
        # But we can show how often the score moved up/down
        results = {
            'similar_occurrences': len(similar_periods),
            'avg_score_in_similar_periods': similar_periods['score'].mean(),
            'score_range': (similar_periods['score'].min(), similar_periods['score'].max())
        }

        return results


def calculate_component_contributions(components, weights):
    """
    Calculate each component's contribution to overall score

    Args:
        components: Dict of component scores
        weights: Dict of component weights

    Returns:
        List of dicts with component, score, weight, contribution
    """
    contributions = []

    for key, weight in weights.items():
        if key in components:
            contribution = components[key] * weight
            contributions.append({
                'component': key,
                'score': components[key],
                'weight': weight,
                'contribution': contribution
            })

    # Sort by contribution (absolute value)
    contributions.sort(key=lambda x: abs(x['contribution'] - 50), reverse=True)

    return contributions
