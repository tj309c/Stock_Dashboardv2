"""
Pytest suite for news_fetcher.py AI sentiment analysis
Tests the multi-provider AI sentiment functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from news_fetcher import analyze_sentiment_ai, analyze_sentiment_simple


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def sample_article():
    """Sample article for testing"""
    return {
        'title': 'Apple Reports Record Quarterly Revenue',
        'text': 'Apple Inc. announced record-breaking quarterly revenue today, '
                'exceeding analyst expectations. The company reported strong iPhone sales '
                'and continued growth in its services division.'
    }


@pytest.fixture
def negative_article():
    """Sample negative article"""
    return {
        'title': 'Company Faces Major Lawsuit and Revenue Decline',
        'text': 'The company reported disappointing earnings and announced '
                'significant layoffs. Legal troubles continue to mount with '
                'multiple lawsuits pending.'
    }


@pytest.fixture
def neutral_article():
    """Sample neutral article"""
    return {
        'title': 'Company Announces Standard Quarterly Report',
        'text': 'The company released its quarterly report today, showing '
                'results in line with expectations.'
    }


@pytest.fixture
def mock_streamlit_with_gemini():
    """Mock Streamlit with Gemini API key"""
    with patch('news_fetcher.st') as mock_st:
        mock_st.session_state = {'selected_ai_model': 'gemini-2.5-flash'}
        mock_st.secrets = {'GOOGLE_API_KEY': 'test-key'}
        yield mock_st


@pytest.fixture
def mock_ai_model_config():
    """Mock ai_model_config module"""
    with patch('news_fetcher.get_model_info') as mock_get_info, \
         patch('news_fetcher.get_selected_model') as mock_get_selected, \
         patch('news_fetcher.create_model_client') as mock_create_client, \
         patch('news_fetcher.AIProvider') as mock_provider:

        # Setup default returns
        mock_get_selected.return_value = 'gemini-2.5-flash'

        yield {
            'get_model_info': mock_get_info,
            'get_selected_model': mock_get_selected,
            'create_model_client': mock_create_client,
            'AIProvider': mock_provider
        }


# ==========================================
# TEST SIMPLE SENTIMENT ANALYSIS
# ==========================================

class TestSimpleSentiment:
    """Test simple (NLTK-based) sentiment analysis"""

    def test_positive_sentiment(self, sample_article):
        """Test detection of positive sentiment"""
        result = analyze_sentiment_simple(
            sample_article['title'] + " " + sample_article['text']
        )

        assert result['sentiment'] in ['positive', 'neutral']  # Should be positive or neutral
        assert 'compound' in result
        assert result['compound'] >= 0  # Positive or neutral compound score

    def test_negative_sentiment(self, negative_article):
        """Test detection of negative sentiment"""
        result = analyze_sentiment_simple(
            negative_article['title'] + " " + negative_article['text']
        )

        assert result['sentiment'] in ['negative', 'neutral']
        assert 'compound' in result
        assert result['compound'] <= 0.05  # Should be negative or slightly positive

    def test_neutral_sentiment(self, neutral_article):
        """Test detection of neutral sentiment"""
        result = analyze_sentiment_simple(
            neutral_article['title'] + " " + neutral_article['text']
        )

        assert result['sentiment'] == 'neutral'
        assert abs(result['compound']) < 0.2  # Close to zero

    def test_result_structure(self, sample_article):
        """Test that result has correct structure"""
        result = analyze_sentiment_simple(sample_article['title'])

        assert 'sentiment' in result
        assert 'emoji' in result
        assert 'compound' in result
        assert 'positive' in result
        assert 'negative' in result
        assert 'neutral' in result

        assert result['sentiment'] in ['positive', 'negative', 'neutral']
        assert result['emoji'] in ['📈', '📉', '➖']
        assert -1.0 <= result['compound'] <= 1.0

    def test_empty_text(self):
        """Test handling of empty text"""
        result = analyze_sentiment_simple("")

        assert result['sentiment'] == 'neutral'
        assert result['compound'] == 0.0


# ==========================================
# TEST AI SENTIMENT WITH GEMINI
# ==========================================

class TestAISentimentGemini:
    """Test AI sentiment analysis with Gemini provider"""

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_gemini_positive_sentiment(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test Gemini AI sentiment analysis with positive article"""
        # Setup mocks
        mock_get_selected.return_value = 'gemini-2.5-flash'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.GEMINI
        mock_model_info.display_name = "Gemini 2.5 Flash"
        mock_get_model_info.return_value = mock_model_info

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "sentiment": "positive",
            "confidence": 0.85,
            "impact": "high",
            "reasoning": "Strong revenue growth and exceeded expectations"
        })
        mock_model.generate_content.return_value = mock_response
        mock_create_client.return_value = mock_model

        # Test
        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Assertions
        assert result['sentiment'] == 'positive'
        assert result['confidence'] == 0.85
        assert result['impact'] == 'high'
        assert 'reasoning' in result
        assert result['ai_powered'] is True
        assert result['model_used'] == "Gemini 2.5 Flash"

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_gemini_json_with_code_blocks(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test Gemini response with JSON in code blocks"""
        # Setup mocks
        mock_get_selected.return_value = 'gemini-2.5-flash'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.GEMINI
        mock_model_info.display_name = "Gemini 2.5 Flash"
        mock_get_model_info.return_value = mock_model_info

        mock_model = Mock()
        mock_response = Mock()
        # Response with code block
        mock_response.text = '''```json
{
    "sentiment": "positive",
    "confidence": 0.9,
    "impact": "medium",
    "reasoning": "Good news"
}
```'''
        mock_model.generate_content.return_value = mock_response
        mock_create_client.return_value = mock_model

        # Test
        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Assertions
        assert result['sentiment'] == 'positive'
        assert result['confidence'] == 0.9


# ==========================================
# TEST AI SENTIMENT WITH OPENAI
# ==========================================

class TestAISentimentOpenAI:
    """Test AI sentiment analysis with OpenAI provider"""

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_openai_sentiment(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test OpenAI sentiment analysis"""
        # Setup mocks
        mock_get_selected.return_value = 'gpt-4o'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.OPENAI
        mock_model_info.display_name = "GPT-4o"
        mock_get_model_info.return_value = mock_model_info

        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps({
            "sentiment": "positive",
            "confidence": 0.88,
            "impact": "high",
            "reasoning": "Excellent quarterly results"
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        # Test
        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Assertions
        assert result['sentiment'] == 'positive'
        assert result['confidence'] == 0.88
        assert result['model_used'] == "GPT-4o"


# ==========================================
# TEST AI SENTIMENT WITH CLAUDE
# ==========================================

class TestAISentimentClaude:
    """Test AI sentiment analysis with Claude provider"""

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_claude_sentiment(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test Claude sentiment analysis"""
        # Setup mocks
        mock_get_selected.return_value = 'claude-sonnet-4-5-20250929'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.CLAUDE
        mock_model_info.display_name = "Claude 4.5 Sonnet"
        mock_get_model_info.return_value = mock_model_info

        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps({
            "sentiment": "positive",
            "confidence": 0.92,
            "impact": "high",
            "reasoning": "Strong financial performance"
        })
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        # Test
        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Assertions
        assert result['sentiment'] == 'positive'
        assert result['confidence'] == 0.92
        assert result['model_used'] == "Claude 4.5 Sonnet"


# ==========================================
# TEST AI SENTIMENT WITH GROK
# ==========================================

class TestAISentimentGrok:
    """Test AI sentiment analysis with Grok provider"""

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_grok_sentiment(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test Grok sentiment analysis"""
        # Setup mocks
        mock_get_selected.return_value = 'grok-beta'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.GROK
        mock_model_info.display_name = "Grok Beta"
        mock_get_model_info.return_value = mock_model_info

        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps({
            "sentiment": "positive",
            "confidence": 0.87,
            "impact": "medium",
            "reasoning": "Revenue beat estimates"
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_create_client.return_value = mock_client

        # Test
        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Assertions
        assert result['sentiment'] == 'positive'
        assert result['confidence'] == 0.87
        assert result['model_used'] == "Grok Beta"


# ==========================================
# TEST ERROR HANDLING AND FALLBACKS
# ==========================================

class TestErrorHandling:
    """Test error handling and fallback mechanisms"""

    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    def test_fallback_to_simple_when_model_not_found(
        self,
        mock_get_selected,
        mock_get_model_info,
        sample_article
    ):
        """Test fallback to simple sentiment when model not found"""
        mock_get_selected.return_value = 'invalid-model'
        mock_get_model_info.return_value = None

        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Should fall back to simple sentiment
        assert 'sentiment' in result
        assert 'ai_powered' not in result  # Simple sentiment doesn't have this

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_fallback_on_api_error(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test fallback to simple sentiment on API error"""
        mock_get_selected.return_value = 'gemini-2.5-flash'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.GEMINI
        mock_get_model_info.return_value = mock_model_info

        # Make API call raise an exception
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_create_client.return_value = mock_model

        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Should fall back to simple sentiment
        assert 'sentiment' in result
        assert 'ai_powered' not in result

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_fallback_on_invalid_json(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test fallback when AI returns invalid JSON"""
        mock_get_selected.return_value = 'gemini-2.5-flash'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.GEMINI
        mock_get_model_info.return_value = mock_model_info

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"
        mock_model.generate_content.return_value = mock_response
        mock_create_client.return_value = mock_model

        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Should fall back to simple sentiment
        assert 'sentiment' in result


# ==========================================
# TEST RESULT STRUCTURE AND VALIDATION
# ==========================================

class TestResultValidation:
    """Test result structure and validation"""

    @patch('news_fetcher.create_model_client')
    @patch('news_fetcher.get_model_info')
    @patch('news_fetcher.get_selected_model')
    @patch('news_fetcher.AIProvider')
    def test_ai_result_structure(
        self,
        mock_provider,
        mock_get_selected,
        mock_get_model_info,
        mock_create_client,
        sample_article
    ):
        """Test that AI result has correct structure"""
        # Setup mocks for successful AI response
        mock_get_selected.return_value = 'gemini-2.5-flash'

        mock_model_info = Mock()
        mock_model_info.provider = mock_provider.GEMINI
        mock_model_info.display_name = "Gemini 2.5 Flash"
        mock_get_model_info.return_value = mock_model_info

        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "sentiment": "positive",
            "confidence": 0.85,
            "impact": "high",
            "reasoning": "Test reasoning"
        })
        mock_model.generate_content.return_value = mock_response
        mock_create_client.return_value = mock_model

        result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        # Check all required fields
        assert 'sentiment' in result
        assert 'emoji' in result
        assert 'compound' in result
        assert 'confidence' in result
        assert 'impact' in result
        assert 'reasoning' in result
        assert 'ai_powered' in result
        assert 'model_used' in result

        # Validate field types and values
        assert result['sentiment'] in ['positive', 'negative', 'neutral']
        assert 0.0 <= result['confidence'] <= 1.0
        assert result['impact'] in ['high', 'medium', 'low']
        assert result['ai_powered'] is True
        assert isinstance(result['model_used'], str)


# ==========================================
# INTEGRATION TESTS
# ==========================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_simple_to_ai_sentiment_comparison(self, sample_article):
        """Test that both simple and AI sentiment work independently"""
        # Simple sentiment should always work
        simple_result = analyze_sentiment_simple(
            sample_article['title'] + " " + sample_article['text']
        )

        assert 'sentiment' in simple_result
        assert simple_result['sentiment'] in ['positive', 'negative', 'neutral']

        # AI sentiment should fall back to simple if no API key
        ai_result = analyze_sentiment_ai(sample_article['text'], sample_article['title'])

        assert 'sentiment' in ai_result
        assert ai_result['sentiment'] in ['positive', 'negative', 'neutral']


# ==========================================
# PYTEST CONFIGURATION
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
