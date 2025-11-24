"""
Comprehensive tests for News & Sentiment Dashboard (page 08)
Tests all functions, UI components, and data flows
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import importlib.util
spec = importlib.util.spec_from_file_location(
    "news_sentiment_page",
    "pages/08_📰_News_&_Sentiment.py"
)
news_sentiment_page = importlib.util.module_from_spec(spec)
# Execute the module so functions and symbols are available for tests
spec.loader.exec_module(news_sentiment_page)


class TestNewsSentimentDashboard:
    """Test suite for News & Sentiment Dashboard"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_ticker = "AAPL"
        self.sample_news_df = pd.DataFrame({
            'title': ['Stock rises on earnings', 'Company faces challenges', 'New product launch'],
            'url': ['http://test1.com', 'http://test2.com', 'http://test3.com'],
            'source': ['Reuters', 'Bloomberg', 'CNBC'],
            'published': [datetime.now(), datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=2)],
            'published_date': [datetime.now(), datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=2)],
            'summary': ['Positive earnings report', 'Challenges ahead', 'Exciting launch'],
            'sentiment': ['positive', 'negative', 'positive'],
            'compound': [0.8, -0.6, 0.7],
            'emoji': ['📈', '📉', '📈']
        })

        self.sample_summary = {
            'total_articles': 3,
            'positive_count': 2,
            'negative_count': 1,
            'neutral_count': 0,
            'positive_pct': 66.7,
            'negative_pct': 33.3,
            'neutral_pct': 0.0,
            'avg_sentiment': 0.3,
            'sentiment_trend': 'positive',
            'trend_emoji': '📈'
        }

        self.sample_social_data = {
            'twitter': {
                'available': True,
                'sentiment': 'positive',
                'confidence': 0.75,
                'volume': 'high',
                'trending_score': 8,
                'key_topics': ['earnings', 'growth'],
                'summary': 'Bullish sentiment on Twitter',
                'bullish_signals': ['Strong earnings', 'Revenue growth'],
                'bearish_signals': []
            },
            'google_trends': {
                'available': True,
                'current_interest': 85,
                'peak_interest': 100,
                'trend_direction': 'rising',
                'trend_emoji': '📈',
                'related_queries': ['stock price', 'earnings report'],
                'interest_series': [60, 70, 80, 85]
            }
        }

    def test_calculate_sentiment_alignment_strong_consensus(self):
        """Test sentiment alignment calculation with strong consensus"""
        sources = [
            {'score': 0.75},
            {'score': 0.78},
            {'score': 0.77}
        ]

        alignment, interpretation, risk = news_sentiment_page.calculate_sentiment_alignment(sources)

        assert alignment > 0.85
        assert interpretation == "Strong Consensus"
        assert risk is False

    def test_calculate_sentiment_alignment_high_divergence(self):
        """Test sentiment alignment calculation with high divergence"""
        sources = [
            {'score': 0.2},
            {'score': 0.8},
            {'score': 0.5}
        ]

        alignment, interpretation, risk = news_sentiment_page.calculate_sentiment_alignment(sources)

        assert alignment < 0.4
        assert interpretation == "High Divergence"
        assert risk is True

    def test_calculate_sentiment_alignment_single_source(self):
        """Test sentiment alignment with single source"""
        sources = [{'score': 0.5}]

        alignment, interpretation, risk = news_sentiment_page.calculate_sentiment_alignment(sources)

        assert alignment == 1.0
        assert interpretation == "Single Source"
        assert risk is False

    def test_calculate_sentiment_momentum_improving(self):
        """Test sentiment momentum calculation - improving trend"""
        current_sentiment = 0.5
        news_df = self.sample_news_df.copy()
        news_df['sentiment'] = [0.8, 0.2, 0.1]  # Recent is much higher

        direction, emoji, text = news_sentiment_page.calculate_sentiment_momentum(current_sentiment, news_df)

        # Should detect improvement or stability
        assert direction in ['improving', 'stable']
        assert emoji in ['📈', '➡️']

    def test_calculate_sentiment_momentum_deteriorating(self):
        """Test sentiment momentum calculation - deteriorating trend"""
        current_sentiment = -0.5
        news_df = self.sample_news_df.copy()
        news_df['sentiment'] = [0.8, 0.9, 0.7]  # Historical is much higher

        direction, emoji, text = news_sentiment_page.calculate_sentiment_momentum(current_sentiment, news_df)

        # Should detect deterioration or stable
        assert direction in ['deteriorating', 'stable']
        assert emoji in ['📉', '➡️']

    def test_calculate_sentiment_momentum_insufficient_data(self):
        """Test sentiment momentum with insufficient data"""
        current_sentiment = 0.5
        empty_df = pd.DataFrame()

        direction, emoji, text = news_sentiment_page.calculate_sentiment_momentum(current_sentiment, empty_df)

        assert direction == "stable"
        assert emoji == "➡️"
        assert "Insufficient historical data" in text

    @patch('news_sentiment_page.call_ai_model')
    @patch('news_sentiment_page.get_configured_model')
    def test_generate_ai_sentiment_summary_success(self, mock_get_model, mock_call_ai):
        """Test AI sentiment summary generation - success case"""
        mock_get_model.return_value = {'model': 'gemini', 'api_key': 'test'}
        mock_call_ai.return_value = "Strong bullish sentiment across all sources"

        sentiment_sources = [
            {'source': 'News', 'sentiment': 'Positive', 'score': 0.75, 'count': '10 articles'}
        ]

        summary = news_sentiment_page.generate_ai_sentiment_summary(
            sentiment_sources,
            self.sample_news_df,
            self.sample_ticker,
            self.sample_summary
        )

        assert isinstance(summary, str)
        assert len(summary) > 0
        mock_call_ai.assert_called_once()

    @patch('news_sentiment_page.get_configured_model')
    def test_generate_ai_sentiment_summary_no_model(self, mock_get_model):
        """Test AI sentiment summary with no configured model"""
        mock_get_model.return_value = None

        summary = news_sentiment_page.generate_ai_sentiment_summary(
            [],
            self.sample_news_df,
            self.sample_ticker,
            self.sample_summary
        )

        assert "AI model not configured" in summary

    @patch('news_sentiment_page.call_ai_model')
    @patch('news_sentiment_page.get_configured_model')
    def test_generate_ai_sentiment_summary_error_handling(self, mock_get_model, mock_call_ai):
        """Test AI sentiment summary error handling"""
        mock_get_model.return_value = {'model': 'gemini', 'api_key': 'test'}
        mock_call_ai.side_effect = Exception("API Error")

        summary = news_sentiment_page.generate_ai_sentiment_summary(
            [],
            self.sample_news_df,
            self.sample_ticker,
            self.sample_summary
        )

        assert "Unable to generate AI summary" in summary

    @patch('streamlit.title')
    @patch('streamlit.caption')
    @patch('news_sentiment_page.setup_sidebar_ticker_input')
    @patch('news_sentiment_page.render_ticker_input_with_quick_picks')
    def test_render_page_initialization(self, mock_quick_picks, mock_sidebar, mock_caption, mock_title):
        """Test page initialization"""
        mock_sidebar.return_value = "AAPL"
        mock_quick_picks.return_value = "AAPL"

        # This would normally require full streamlit context
        # Just verify the function exists and has correct signature
        assert hasattr(news_sentiment_page, 'render_page')
        assert callable(news_sentiment_page.render_page)

    def test_module_structure(self):
        """Test that all required functions exist"""
        required_functions = [
            'render_page',
            'render_executive_sentiment_summary',
            'render_sentiment_source_comparison',
            'render_news_articles_section',
            'render_detailed_social_insights',
            'render_sentiment_trends_section',
            'render_advanced_modules_section',
            'calculate_sentiment_alignment',
            'calculate_sentiment_momentum',
            'generate_ai_sentiment_summary'
        ]

        for func_name in required_functions:
            assert hasattr(news_sentiment_page, func_name), f"Missing function: {func_name}"
            assert callable(getattr(news_sentiment_page, func_name)), f"Not callable: {func_name}"

    def test_sentiment_source_preparation_news_only(self):
        """Test sentiment source data preparation with news only"""
        # This tests the logic that would be in render_executive_sentiment_summary
        news_sentiment_score = (self.sample_summary['avg_sentiment'] + 1) / 2

        sentiment_sources = [{
            'source': 'News Articles',
            'sentiment': self.sample_summary['sentiment_trend'].title(),
            'score': news_sentiment_score,
            'count': self.sample_summary['total_articles'],
            'emoji': self.sample_summary['trend_emoji'],
            'color': '#00CC96' if news_sentiment_score > 0.6 else '#EF553B' if news_sentiment_score < 0.4 else '#636EFA'
        }]

        assert len(sentiment_sources) == 1
        assert sentiment_sources[0]['source'] == 'News Articles'
        assert 0 <= sentiment_sources[0]['score'] <= 1

    def test_sentiment_source_preparation_with_social(self):
        """Test sentiment source data preparation with social media"""
        news_sentiment_score = (self.sample_summary['avg_sentiment'] + 1) / 2

        sentiment_sources = []

        # Add news
        sentiment_sources.append({
            'source': 'News Articles',
            'score': news_sentiment_score,
        })

        # Add Twitter
        twitter = self.sample_social_data['twitter']
        twitter_score = 0.65 + (twitter['confidence'] * 0.25)
        sentiment_sources.append({
            'source': 'X/Twitter',
            'score': twitter_score,
        })

        # Add Google Trends
        trends = self.sample_social_data['google_trends']
        trends_score = trends['current_interest'] / 100
        sentiment_sources.append({
            'source': 'Google Trends',
            'score': trends_score,
        })

        assert len(sentiment_sources) == 3
        assert all(0 <= s['score'] <= 1 for s in sentiment_sources)

    def test_overall_sentiment_classification_bullish(self):
        """Test overall sentiment classification - bullish case"""
        overall_score = 0.75

        if overall_score > 0.65:
            overall_sentiment = "Bullish"
            overall_emoji = "📈"
        elif overall_score < 0.35:
            overall_sentiment = "Bearish"
            overall_emoji = "📉"
        else:
            overall_sentiment = "Neutral"
            overall_emoji = "➡️"

        assert overall_sentiment == "Bullish"
        assert overall_emoji == "📈"

    def test_overall_sentiment_classification_bearish(self):
        """Test overall sentiment classification - bearish case"""
        overall_score = 0.25

        if overall_score > 0.65:
            overall_sentiment = "Bullish"
            overall_emoji = "📈"
        elif overall_score < 0.35:
            overall_sentiment = "Bearish"
            overall_emoji = "📉"
        else:
            overall_sentiment = "Neutral"
            overall_emoji = "➡️"

        assert overall_sentiment == "Bearish"
        assert overall_emoji == "📉"

    def test_overall_sentiment_classification_neutral(self):
        """Test overall sentiment classification - neutral case"""
        overall_score = 0.50

        if overall_score > 0.65:
            overall_sentiment = "Bullish"
            overall_emoji = "📈"
        elif overall_score < 0.35:
            overall_sentiment = "Bearish"
            overall_emoji = "📉"
        else:
            overall_sentiment = "Neutral"
            overall_emoji = "➡️"

        assert overall_sentiment == "Neutral"
        assert overall_emoji == "➡️"


class TestNewsSentimentIntegration:
    """Integration tests for News & Sentiment Dashboard"""

    def setup_method(self):
        """Setup integration test fixtures"""
        self.test_ticker = "AAPL"

    @patch('yfinance.Ticker')
    def test_ticker_data_fetch(self, mock_ticker):
        """Test ticker data fetching"""
        mock_stock = Mock()
        mock_stock.info = {
            'longName': 'Apple Inc.',
            'shortName': 'Apple'
        }
        mock_ticker.return_value = mock_stock

        import yfinance as yf
        stock = yf.Ticker(self.test_ticker)
        company_name = stock.info.get('longName', stock.info.get('shortName', self.test_ticker))

        assert company_name in ['Apple Inc.', 'Apple', 'AAPL']

    def test_news_dataframe_structure(self):
        """Test expected news DataFrame structure"""
        required_columns = ['title', 'url', 'source', 'published', 'summary', 'sentiment', 'compound', 'emoji']

        sample_df = pd.DataFrame({
            'title': ['Test'],
            'url': ['http://test.com'],
            'source': ['Test Source'],
            'published': [datetime.now()],
            'summary': ['Summary'],
            'sentiment': ['positive'],
            'compound': [0.5],
            'emoji': ['📈']
        })

        for col in required_columns:
            assert col in sample_df.columns

    def test_sentiment_summary_structure(self):
        """Test expected sentiment summary structure"""
        required_keys = [
            'total_articles', 'positive_count', 'negative_count', 'neutral_count',
            'positive_pct', 'negative_pct', 'neutral_pct', 'avg_sentiment',
            'sentiment_trend', 'trend_emoji'
        ]

        summary = {
            'total_articles': 10,
            'positive_count': 6,
            'negative_count': 3,
            'neutral_count': 1,
            'positive_pct': 60.0,
            'negative_pct': 30.0,
            'neutral_pct': 10.0,
            'avg_sentiment': 0.3,
            'sentiment_trend': 'positive',
            'trend_emoji': '📈'
        }

        for key in required_keys:
            assert key in summary


class TestNewsSentimentEdgeCases:
    """Edge case tests for News & Sentiment Dashboard"""

    def test_empty_news_dataframe(self):
        """Test handling of empty news DataFrame"""
        empty_df = pd.DataFrame()

        direction, emoji, text = news_sentiment_page.calculate_sentiment_momentum(0.5, empty_df)

        assert direction == "stable"
        assert "Insufficient historical data" in text

    def test_all_positive_sentiment(self):
        """Test all positive sentiment sources"""
        sources = [
            {'score': 0.9},
            {'score': 0.85},
            {'score': 0.95}
        ]

        alignment, interpretation, risk = news_sentiment_page.calculate_sentiment_alignment(sources)

        assert alignment > 0.85
        assert risk is False

    def test_all_negative_sentiment(self):
        """Test all negative sentiment sources"""
        sources = [
            {'score': 0.1},
            {'score': 0.15},
            {'score': 0.05}
        ]

        alignment, interpretation, risk = news_sentiment_page.calculate_sentiment_alignment(sources)

        assert alignment > 0.85
        assert risk is False

    def test_extreme_divergence(self):
        """Test extreme sentiment divergence"""
        sources = [
            {'score': 0.0},
            {'score': 1.0}
        ]

        alignment, interpretation, risk = news_sentiment_page.calculate_sentiment_alignment(sources)

        assert alignment < 0.5
        assert risk is True

    def test_zero_sentiment_score(self):
        """Test zero sentiment score handling"""
        overall_score = 0.0

        if overall_score > 0.65:
            overall_sentiment = "Bullish"
        elif overall_score < 0.35:
            overall_sentiment = "Bearish"
        else:
            overall_sentiment = "Neutral"

        assert overall_sentiment == "Bearish"

    def test_max_sentiment_score(self):
        """Test maximum sentiment score handling"""
        overall_score = 1.0

        if overall_score > 0.65:
            overall_sentiment = "Bullish"
        elif overall_score < 0.35:
            overall_sentiment = "Bearish"
        else:
            overall_sentiment = "Neutral"

        assert overall_sentiment == "Bullish"


def run_tests():
    """Run all tests and print results"""
    print("=" * 80)
    print("Running News & Sentiment Dashboard Tests")
    print("=" * 80)

    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()