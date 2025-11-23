"""
Comprehensive pytest suite for ai_model_config.py
Tests all AI model configuration functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_model_config import (
    AIProvider,
    AIModelInfo,
    get_all_models,
    get_models_by_provider,
    get_model_info,
    is_provider_configured,
    get_available_providers,
    get_available_models,
    get_selected_model,
    GEMINI_MODELS,
    OPENAI_MODELS,
    CLAUDE_MODELS,
    GROK_MODELS,
    DEFAULT_MODEL
)


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit session_state and secrets"""
    with patch('ai_model_config.st') as mock_st:
        # Mock session_state
        mock_st.session_state = {}

        # Mock secrets
        mock_st.secrets = {
            'GOOGLE_API_KEY': 'test-google-key',
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': 'test-claude-key',
            'XAI_API_KEY': 'test-grok-key'
        }

        yield mock_st


@pytest.fixture
def mock_streamlit_no_keys():
    """Mock Streamlit with no API keys configured"""
    with patch('ai_model_config.st') as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {}
        yield mock_st


@pytest.fixture
def mock_streamlit_partial_keys():
    """Mock Streamlit with only some API keys"""
    with patch('ai_model_config.st') as mock_st:
        mock_st.session_state = {}
        mock_st.secrets = {
            'GOOGLE_API_KEY': 'test-google-key',
            'OPENAI_API_KEY': 'test-openai-key'
        }
        yield mock_st


# ==========================================
# TEST DATA CLASSES
# ==========================================

class TestAIProvider:
    """Test AIProvider enum"""

    def test_provider_enum_values(self):
        """Test that all providers have correct values"""
        assert AIProvider.GEMINI.value == "Google Gemini"
        assert AIProvider.OPENAI.value == "OpenAI"
        assert AIProvider.CLAUDE.value == "Anthropic Claude"
        assert AIProvider.GROK.value == "X.AI Grok"

    def test_provider_enum_count(self):
        """Test that we have exactly 4 providers"""
        assert len(AIProvider) == 4


class TestAIModelInfo:
    """Test AIModelInfo dataclass"""

    def test_model_info_creation(self):
        """Test creating a model info object"""
        model = AIModelInfo(
            provider=AIProvider.GEMINI,
            model_id="gemini-2.5-flash",
            display_name="Gemini 2.5 Flash",
            description="Test model",
            tier="standard",
            input_token_limit=1000000,
            output_token_limit=8192,
            supports_vision=True,
            supports_function_calling=False,
            cost_per_1k_input=0.075,
            cost_per_1k_output=0.30
        )

        assert model.provider == AIProvider.GEMINI
        assert model.model_id == "gemini-2.5-flash"
        assert model.tier == "standard"
        assert model.supports_vision is True
        assert model.cost_per_1k_input == 0.075

    def test_full_name_property(self):
        """Test full_name property"""
        model = AIModelInfo(
            provider=AIProvider.OPENAI,
            model_id="gpt-4o",
            display_name="GPT-4o",
            description="Test",
            tier="premium",
            input_token_limit=128000,
            output_token_limit=16384
        )

        assert model.full_name == "OpenAI: GPT-4o"

    def test_tier_emoji_property(self):
        """Test tier_emoji property"""
        premium_model = AIModelInfo(
            provider=AIProvider.CLAUDE,
            model_id="claude-opus",
            display_name="Claude Opus",
            description="Test",
            tier="premium",
            input_token_limit=200000,
            output_token_limit=4096
        )

        standard_model = AIModelInfo(
            provider=AIProvider.GEMINI,
            model_id="gemini-flash",
            display_name="Gemini Flash",
            description="Test",
            tier="standard",
            input_token_limit=1000000,
            output_token_limit=8192
        )

        assert premium_model.tier_emoji == '💎'
        assert standard_model.tier_emoji == '⚡'


# ==========================================
# TEST MODEL CATALOGS
# ==========================================

class TestModelCatalogs:
    """Test model catalog constants"""

    def test_gemini_models_exist(self):
        """Test that Gemini models are defined"""
        assert len(GEMINI_MODELS) >= 4
        assert all(m.provider == AIProvider.GEMINI for m in GEMINI_MODELS)

    def test_openai_models_exist(self):
        """Test that OpenAI models are defined"""
        assert len(OPENAI_MODELS) >= 4
        assert all(m.provider == AIProvider.OPENAI for m in OPENAI_MODELS)

    def test_claude_models_exist(self):
        """Test that Claude models are defined"""
        assert len(CLAUDE_MODELS) >= 4
        assert all(m.provider == AIProvider.CLAUDE for m in CLAUDE_MODELS)

    def test_grok_models_exist(self):
        """Test that Grok models are defined"""
        assert len(GROK_MODELS) >= 1
        assert all(m.provider == AIProvider.GROK for m in GROK_MODELS)

    def test_default_model_is_gemini_flash(self):
        """Test that default model is gemini-2.5-flash"""
        assert DEFAULT_MODEL == "gemini-2.5-flash"

    def test_default_model_exists_in_catalog(self):
        """Test that default model exists in model list"""
        all_model_ids = [m.model_id for m in get_all_models()]
        assert DEFAULT_MODEL in all_model_ids

    def test_all_models_have_required_fields(self):
        """Test that all models have required fields populated"""
        for model in get_all_models():
            assert model.provider is not None
            assert model.model_id is not None
            assert model.display_name is not None
            assert model.description is not None
            assert model.tier in ['premium', 'standard', 'fast', 'lite']
            assert model.input_token_limit > 0
            assert model.output_token_limit > 0
            assert model.cost_per_1k_input >= 0
            assert model.cost_per_1k_output >= 0

    def test_model_ids_are_unique(self):
        """Test that all model IDs are unique"""
        model_ids = [m.model_id for m in get_all_models()]
        assert len(model_ids) == len(set(model_ids))


# ==========================================
# TEST HELPER FUNCTIONS
# ==========================================

class TestHelperFunctions:
    """Test helper functions"""

    def test_get_all_models(self):
        """Test get_all_models returns all models"""
        all_models = get_all_models()

        assert len(all_models) > 0
        expected_count = len(GEMINI_MODELS) + len(OPENAI_MODELS) + len(CLAUDE_MODELS) + len(GROK_MODELS)
        assert len(all_models) == expected_count

    def test_get_models_by_provider_gemini(self):
        """Test getting models by provider (Gemini)"""
        gemini_models = get_models_by_provider(AIProvider.GEMINI)

        assert len(gemini_models) == len(GEMINI_MODELS)
        assert all(m.provider == AIProvider.GEMINI for m in gemini_models)

    def test_get_models_by_provider_openai(self):
        """Test getting models by provider (OpenAI)"""
        openai_models = get_models_by_provider(AIProvider.OPENAI)

        assert len(openai_models) == len(OPENAI_MODELS)
        assert all(m.provider == AIProvider.OPENAI for m in openai_models)

    def test_get_models_by_provider_claude(self):
        """Test getting models by provider (Claude)"""
        claude_models = get_models_by_provider(AIProvider.CLAUDE)

        assert len(claude_models) == len(CLAUDE_MODELS)
        assert all(m.provider == AIProvider.CLAUDE for m in claude_models)

    def test_get_models_by_provider_grok(self):
        """Test getting models by provider (Grok)"""
        grok_models = get_models_by_provider(AIProvider.GROK)

        assert len(grok_models) == len(GROK_MODELS)
        assert all(m.provider == AIProvider.GROK for m in grok_models)

    def test_get_model_info_valid_id(self):
        """Test getting model info with valid ID"""
        model_info = get_model_info("gemini-2.5-flash")

        assert model_info is not None
        assert model_info.model_id == "gemini-2.5-flash"
        assert model_info.provider == AIProvider.GEMINI

    def test_get_model_info_invalid_id(self):
        """Test getting model info with invalid ID"""
        model_info = get_model_info("invalid-model-id")

        assert model_info is None

    def test_get_model_info_all_models(self):
        """Test that all models can be retrieved by ID"""
        for model in get_all_models():
            retrieved = get_model_info(model.model_id)
            assert retrieved is not None
            assert retrieved.model_id == model.model_id


# ==========================================
# TEST PROVIDER CONFIGURATION
# ==========================================

class TestProviderConfiguration:
    """Test provider configuration detection"""

    def test_is_provider_configured_all_providers(self, mock_streamlit):
        """Test detecting all configured providers"""
        assert is_provider_configured(AIProvider.GEMINI) is True
        assert is_provider_configured(AIProvider.OPENAI) is True
        assert is_provider_configured(AIProvider.CLAUDE) is True
        assert is_provider_configured(AIProvider.GROK) is True

    def test_is_provider_configured_no_providers(self, mock_streamlit_no_keys):
        """Test detecting no configured providers"""
        assert is_provider_configured(AIProvider.GEMINI) is False
        assert is_provider_configured(AIProvider.OPENAI) is False
        assert is_provider_configured(AIProvider.CLAUDE) is False
        assert is_provider_configured(AIProvider.GROK) is False

    def test_is_provider_configured_partial(self, mock_streamlit_partial_keys):
        """Test detecting partially configured providers"""
        assert is_provider_configured(AIProvider.GEMINI) is True
        assert is_provider_configured(AIProvider.OPENAI) is True
        assert is_provider_configured(AIProvider.CLAUDE) is False
        assert is_provider_configured(AIProvider.GROK) is False

    def test_get_available_providers_all(self, mock_streamlit):
        """Test getting all available providers"""
        providers = get_available_providers()

        assert len(providers) == 4
        assert AIProvider.GEMINI in providers
        assert AIProvider.OPENAI in providers
        assert AIProvider.CLAUDE in providers
        assert AIProvider.GROK in providers

    def test_get_available_providers_none(self, mock_streamlit_no_keys):
        """Test getting available providers with none configured"""
        providers = get_available_providers()

        assert len(providers) == 0

    def test_get_available_providers_partial(self, mock_streamlit_partial_keys):
        """Test getting available providers with partial config"""
        providers = get_available_providers()

        assert len(providers) == 2
        assert AIProvider.GEMINI in providers
        assert AIProvider.OPENAI in providers
        assert AIProvider.CLAUDE not in providers
        assert AIProvider.GROK not in providers

    def test_get_available_models_all_providers(self, mock_streamlit):
        """Test getting available models with all providers configured"""
        models = get_available_models()

        assert len(models) == len(get_all_models())

    def test_get_available_models_no_providers(self, mock_streamlit_no_keys):
        """Test getting available models with no providers configured"""
        models = get_available_models()

        assert len(models) == 0

    def test_get_available_models_partial_providers(self, mock_streamlit_partial_keys):
        """Test getting available models with partial providers"""
        models = get_available_models()

        expected_count = len(GEMINI_MODELS) + len(OPENAI_MODELS)
        assert len(models) == expected_count

        # Check that only Gemini and OpenAI models are returned
        providers = {m.provider for m in models}
        assert providers == {AIProvider.GEMINI, AIProvider.OPENAI}


# ==========================================
# TEST MODEL SELECTION
# ==========================================

class TestModelSelection:
    """Test model selection functionality"""

    def test_get_selected_model_default(self, mock_streamlit):
        """Test getting selected model with default"""
        selected = get_selected_model("test_key")

        assert selected == DEFAULT_MODEL

    def test_get_selected_model_custom(self, mock_streamlit):
        """Test getting selected model with custom selection"""
        mock_streamlit.session_state['test_key'] = 'gpt-4o'
        selected = get_selected_model("test_key")

        assert selected == 'gpt-4o'

    def test_get_selected_model_different_keys(self, mock_streamlit):
        """Test that different session keys are independent"""
        mock_streamlit.session_state['key1'] = 'gemini-2.5-flash'
        mock_streamlit.session_state['key2'] = 'gpt-4o'

        assert get_selected_model('key1') == 'gemini-2.5-flash'
        assert get_selected_model('key2') == 'gpt-4o'


# ==========================================
# TEST MODEL CLIENT CREATION
# ==========================================

class TestModelClientCreation:
    """Test model client creation (mocked)"""

    @patch('ai_model_config.genai')
    def test_create_gemini_client(self, mock_genai, mock_streamlit):
        """Test creating Gemini model client"""
        from ai_model_config import create_model_client

        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model

        client = create_model_client("gemini-2.5-flash")

        mock_genai.configure.assert_called_once_with(api_key='test-google-key')
        mock_genai.GenerativeModel.assert_called_once_with("gemini-2.5-flash")
        assert client == mock_model

    @patch('ai_model_config.OpenAI')
    def test_create_openai_client(self, mock_openai_class, mock_streamlit):
        """Test creating OpenAI model client"""
        from ai_model_config import create_model_client

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        client = create_model_client("gpt-4o")

        mock_openai_class.assert_called_once_with(api_key='test-openai-key')
        assert client == mock_client

    @patch('ai_model_config.anthropic')
    def test_create_claude_client(self, mock_anthropic, mock_streamlit):
        """Test creating Claude model client"""
        from ai_model_config import create_model_client

        mock_client = Mock()
        mock_anthropic.Anthropic.return_value = mock_client

        client = create_model_client("claude-sonnet-4-5-20250929")

        mock_anthropic.Anthropic.assert_called_once_with(api_key='test-claude-key')
        assert client == mock_client

    @patch('ai_model_config.OpenAI')
    def test_create_grok_client(self, mock_openai_class, mock_streamlit):
        """Test creating Grok model client"""
        from ai_model_config import create_model_client

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        client = create_model_client("grok-beta")

        mock_openai_class.assert_called_once_with(
            api_key='test-grok-key',
            base_url="https://api.x.ai/v1"
        )
        assert client == mock_client

    def test_create_client_no_api_key(self, mock_streamlit_no_keys):
        """Test creating client without API key raises error"""
        from ai_model_config import create_model_client

        with pytest.raises(ValueError, match="not configured"):
            create_model_client("gemini-2.5-flash")

    def test_create_client_invalid_model(self, mock_streamlit):
        """Test creating client with invalid model ID"""
        from ai_model_config import create_model_client

        with pytest.raises(ValueError, match="Model not found"):
            create_model_client("invalid-model-id")


# ==========================================
# TEST PROVIDER STATUS
# ==========================================

class TestProviderStatus:
    """Test provider status functions"""

    def test_get_provider_status_all_configured(self, mock_streamlit):
        """Test getting provider status with all configured"""
        from ai_model_config import get_provider_status

        status = get_provider_status()

        assert len(status) == 4
        assert status["Google Gemini"] is True
        assert status["OpenAI"] is True
        assert status["Anthropic Claude"] is True
        assert status["X.AI Grok"] is True

    def test_get_provider_status_none_configured(self, mock_streamlit_no_keys):
        """Test getting provider status with none configured"""
        from ai_model_config import get_provider_status

        status = get_provider_status()

        assert len(status) == 4
        assert all(v is False for v in status.values())

    def test_get_provider_status_partial(self, mock_streamlit_partial_keys):
        """Test getting provider status with partial configuration"""
        from ai_model_config import get_provider_status

        status = get_provider_status()

        assert status["Google Gemini"] is True
        assert status["OpenAI"] is True
        assert status["Anthropic Claude"] is False
        assert status["X.AI Grok"] is False


# ==========================================
# INTEGRATION TESTS
# ==========================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_workflow_with_all_providers(self, mock_streamlit):
        """Test complete workflow with all providers configured"""
        # 1. Check all providers are available
        providers = get_available_providers()
        assert len(providers) == 4

        # 2. Get all available models
        models = get_available_models()
        assert len(models) > 15  # Should have many models

        # 3. Select a model
        mock_streamlit.session_state['selected_ai_model'] = 'gemini-2.5-flash'
        selected = get_selected_model('selected_ai_model')
        assert selected == 'gemini-2.5-flash'

        # 4. Get model info
        model_info = get_model_info(selected)
        assert model_info is not None
        assert model_info.provider == AIProvider.GEMINI

    def test_complete_workflow_with_limited_providers(self, mock_streamlit_partial_keys):
        """Test complete workflow with limited providers"""
        # 1. Check only some providers available
        providers = get_available_providers()
        assert len(providers) == 2
        assert AIProvider.GEMINI in providers
        assert AIProvider.OPENAI in providers

        # 2. Get available models (only Gemini and OpenAI)
        models = get_available_models()
        model_providers = {m.provider for m in models}
        assert model_providers == {AIProvider.GEMINI, AIProvider.OPENAI}

        # 3. Cannot use Claude model
        claude_models = [m for m in get_all_models() if m.provider == AIProvider.CLAUDE]
        available_models = get_available_models()
        for claude_model in claude_models:
            assert claude_model not in available_models


# ==========================================
# EDGE CASES AND ERROR HANDLING
# ==========================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_model_id(self):
        """Test behavior with empty model ID"""
        model_info = get_model_info("")
        assert model_info is None

    def test_none_model_id(self):
        """Test behavior with None model ID"""
        model_info = get_model_info(None)
        assert model_info is None

    def test_whitespace_model_id(self):
        """Test behavior with whitespace model ID"""
        model_info = get_model_info("   ")
        assert model_info is None

    def test_case_sensitive_model_id(self):
        """Test that model ID lookup is case-sensitive"""
        # This should not match
        model_info = get_model_info("GEMINI-2.5-FLASH")
        assert model_info is None

        # This should match
        model_info = get_model_info("gemini-2.5-flash")
        assert model_info is not None


# ==========================================
# PYTEST CONFIGURATION
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
