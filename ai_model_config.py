"""
Universal AI Model Configuration
Supports multiple AI providers: Google Gemini, OpenAI, Anthropic Claude, and X.AI Grok
"""
import streamlit as st
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from error_logger import log_error, log_warning

# Expose common provider SDK names at module-level so tests can patch them.
# Import failures are acceptable at runtime (missing SDKs) but exposing
# the names avoids AttributeError during tests.
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover - environment-dependent
    genai = None

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - environment-dependent
    OpenAI = None

try:
    import anthropic  # type: ignore
except Exception:  # pragma: no cover - environment-dependent
    anthropic = None


class AIProvider(Enum):
    """Supported AI providers"""
    GEMINI = "Google Gemini"
    OPENAI = "OpenAI"
    CLAUDE = "Anthropic Claude"
    GROK = "X.AI Grok"


@dataclass
class AIModelInfo:
    """Information about an AI model"""
    provider: AIProvider
    model_id: str
    display_name: str
    description: str
    tier: str  # 'premium', 'standard', 'fast', 'lite'
    input_token_limit: int
    output_token_limit: int
    supports_vision: bool = False
    supports_function_calling: bool = False
    cost_per_1k_input: float = 0.0  # USD
    cost_per_1k_output: float = 0.0  # USD

    @property
    def full_name(self) -> str:
        """Get provider + model name"""
        return f"{self.provider.value}: {self.display_name}"

    @property
    def tier_emoji(self) -> str:
        """Get emoji for tier"""
        tier_emojis = {
            'premium': '💎',
            'standard': '⚡',
            'fast': '🚀',
            'lite': '💨'
        }
        return tier_emojis.get(self.tier, '🤖')


# ==========================================
# MODEL CATALOG
# ==========================================

GEMINI_MODELS = [
    AIModelInfo(
        provider=AIProvider.GEMINI,
        model_id="gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        description="Latest balanced model - fast and capable",
        tier="standard",
        input_token_limit=1048576,
        output_token_limit=65536,
        supports_vision=True,
        cost_per_1k_input=0.075,
        cost_per_1k_output=0.30
    ),
    AIModelInfo(
        provider=AIProvider.GEMINI,
        model_id="gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        description="Most capable Gemini model",
        tier="premium",
        input_token_limit=1048576,
        output_token_limit=65536,
        supports_vision=True,
        cost_per_1k_input=1.25,
        cost_per_1k_output=5.00
    ),
    AIModelInfo(
        provider=AIProvider.GEMINI,
        model_id="gemini-2.0-flash-lite",
        display_name="Gemini 2.0 Flash-Lite",
        description="Ultra-fast, cost-effective",
        tier="lite",
        input_token_limit=1048576,
        output_token_limit=8192,
        supports_vision=False,
        cost_per_1k_input=0.0375,
        cost_per_1k_output=0.15
    ),
    AIModelInfo(
        provider=AIProvider.GEMINI,
        model_id="gemini-flash-latest",
        display_name="Gemini Flash (Latest)",
        description="Always uses newest Flash model",
        tier="standard",
        input_token_limit=1048576,
        output_token_limit=65536,
        supports_vision=True,
        cost_per_1k_input=0.075,
        cost_per_1k_output=0.30
    ),
]

OPENAI_MODELS = [
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o",
        display_name="GPT-4o",
        description="OpenAI's most advanced multimodal model",
        tier="premium",
        input_token_limit=128000,
        output_token_limit=16384,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=2.50,
        cost_per_1k_output=10.00
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        description="Fast, affordable, intelligent small model",
        tier="fast",
        input_token_limit=128000,
        output_token_limit=16384,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=0.15,
        cost_per_1k_output=0.60
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4-turbo",
        display_name="GPT-4 Turbo",
        description="High-intelligence model for complex tasks",
        tier="premium",
        input_token_limit=128000,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=10.00,
        cost_per_1k_output=30.00
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-3.5-turbo",
        display_name="GPT-3.5 Turbo",
        description="Fast, inexpensive for simple tasks",
        tier="lite",
        input_token_limit=16385,
        output_token_limit=4096,
        supports_function_calling=True,
        cost_per_1k_input=0.50,
        cost_per_1k_output=1.50
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o-extended",
        display_name="GPT-4o Extended",
        description="Higher-context GPT-4o variant for long-form analysis",
        tier="fast",
        input_token_limit=256000,
        output_token_limit=32768,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=0.35,
        cost_per_1k_output=1.25
    ),
]
"""
OPENAI_MODELS_DISABLED = [
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o",
        display_name="GPT-4o",
        description="OpenAI's most advanced multimodal model",
        tier="premium",
        input_token_limit=128000,
        output_token_limit=16384,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=2.50,
        cost_per_1k_output=10.00
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        description="Fast, affordable, intelligent small model",
        tier="fast",
        input_token_limit=128000,
        output_token_limit=16384,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=0.15,
        cost_per_1k_output=0.60
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4-turbo",
        display_name="GPT-4 Turbo",
        description="High-intelligence model for complex tasks",
        tier="premium",
        input_token_limit=128000,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=10.00,
        cost_per_1k_output=30.00
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-3.5-turbo",
        display_name="GPT-3.5 Turbo",
        description="Fast, inexpensive for simple tasks",
        tier="lite",
        input_token_limit=16385,
        output_token_limit=4096,
        supports_function_calling=True,
        cost_per_1k_input=0.50,
        cost_per_1k_output=1.50
    ),
    AIModelInfo(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o-extended",
        display_name="GPT-4o Extended",
        description="Higher-context GPT-4o variant for long-form analysis",
        tier="fast",
        input_token_limit=256000,
        output_token_limit=32768,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=0.35,
        cost_per_1k_output=1.25
    ),
]
"""

CLAUDE_MODELS = [
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-sonnet-4-5-20250929",
        display_name="Claude 4.5 Sonnet",
        description="Latest Claude - balanced intelligence and speed",
        tier="premium",
        input_token_limit=200000,
        output_token_limit=8192,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        description="Balance of intelligence and speed",
        tier="standard",
        input_token_limit=200000,
        output_token_limit=8192,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-3-5-haiku-20241022",
        display_name="Claude 3.5 Haiku",
        description="Fast and affordable",
        tier="fast",
        input_token_limit=200000,
        output_token_limit=8192,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=0.80,
        cost_per_1k_output=4.00
    ),
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-3-opus-20240229",
        display_name="Claude 3 Opus",
        description="Most powerful Claude model",
        tier="premium",
        input_token_limit=200000,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=15.00,
        cost_per_1k_output=75.00
    ),
]
"""
CLAUDE_MODELS_DISABLED = [
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-sonnet-4-5-20250929",
        display_name="Claude 4.5 Sonnet",
        description="Latest Claude - balanced intelligence and speed",
        tier="premium",
        input_token_limit=200000,
        output_token_limit=8192,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        description="Balance of intelligence and speed",
        tier="standard",
        input_token_limit=200000,
        output_token_limit=8192,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-3-5-haiku-20241022",
        display_name="Claude 3.5 Haiku",
        description="Fast and affordable",
        tier="fast",
        input_token_limit=200000,
        output_token_limit=8192,
        supports_vision=True,
        cost_per_1k_input=0.80,
        cost_per_1k_output=4.00
    ),
    AIModelInfo(
        provider=AIProvider.CLAUDE,
        model_id="claude-3-opus-20240229",
        display_name="Claude 3 Opus",
        description="Most powerful Claude model",
        tier="premium",
        input_token_limit=200000,
        output_token_limit=4096,
        supports_vision=True,
        cost_per_1k_input=15.00,
        cost_per_1k_output=75.00
    ),
]

GROK_MODELS = [
    AIModelInfo(
        provider=AIProvider.GROK,
        model_id="grok-beta",
        display_name="Grok Beta",
        description="X.AI's conversational AI with real-time X data access",
        tier="standard",
        input_token_limit=131072,
        output_token_limit=4096,
        supports_function_calling=True,
        cost_per_1k_input=5.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.GROK,
        model_id="grok-vision-beta",
        display_name="Grok Vision Beta",
        description="Grok with vision capabilities",
        tier="premium",
        input_token_limit=131072,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=5.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.GROK,
        model_id="grok-pro-2025",
        display_name="Grok Pro (2025)",
        description="Stable Grok Pro variant for testing and higher throughput",
        tier="standard",
        input_token_limit=131072,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=4.50,
        cost_per_1k_output=12.00
    ),
]
"""

GROK_MODELS = [
    AIModelInfo(
        provider=AIProvider.GROK,
        model_id="grok-beta",
        display_name="Grok Beta",
        description="X.AI's conversational AI with real-time X data access",
        tier="standard",
        input_token_limit=131072,
        output_token_limit=4096,
        supports_function_calling=True,
        cost_per_1k_input=5.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.GROK,
        model_id="grok-vision-beta",
        display_name="Grok Vision Beta",
        description="Grok with vision capabilities",
        tier="premium",
        input_token_limit=131072,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=5.00,
        cost_per_1k_output=15.00
    ),
    AIModelInfo(
        provider=AIProvider.GROK,
        model_id="grok-pro-2025",
        display_name="Grok Pro (2025)",
        description="Stable Grok Pro variant for testing and higher throughput",
        tier="standard",
        input_token_limit=131072,
        output_token_limit=4096,
        supports_vision=True,
        supports_function_calling=True,
        cost_per_1k_input=4.50,
        cost_per_1k_output=12.00
    ),
]

# Combine all models
ALL_MODELS = GEMINI_MODELS + OPENAI_MODELS + CLAUDE_MODELS + GROK_MODELS

# Default model
DEFAULT_MODEL = "gemini-2.5-flash"


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_all_models() -> List[AIModelInfo]:
    """Get all available models"""
    return ALL_MODELS


def get_models_by_provider(provider: AIProvider) -> List[AIModelInfo]:
    """Get models for a specific provider"""
    return [m for m in ALL_MODELS if m.provider == provider]


def get_model_info(model_id: str) -> Optional[AIModelInfo]:
    """Get information about a specific model"""
    for model in ALL_MODELS:
        if model.model_id == model_id:
            return model
    return None


def is_provider_configured(provider: AIProvider) -> bool:
    """Check if API key is configured for a provider"""
    key_mapping = {
        AIProvider.GEMINI: ['GOOGLE_API_KEY', 'GEMINI_API_KEY'],  # Support both key names
        AIProvider.OPENAI: ['OPENAI_API_KEY'],
        AIProvider.CLAUDE: ['ANTHROPIC_API_KEY'],
        AIProvider.GROK: ['XAI_API_KEY']
    }

    possible_keys = key_mapping.get(provider, [])
    # Return True if ANY of the possible keys exist
    return any(key in st.secrets for key in possible_keys)


def get_available_providers() -> List[AIProvider]:
    """Get list of providers that have API keys configured"""
    return [provider for provider in AIProvider if is_provider_configured(provider)]


def get_available_models() -> List[AIModelInfo]:
    """Get only models from configured providers"""
    available_providers = get_available_providers()
    return [m for m in ALL_MODELS if m.provider in available_providers]


# ==========================================
# UI COMPONENTS
# ==========================================

def render_model_selector(
    session_key: str = "selected_ai_model",
    label: str = "🤖 AI Model:",
    help_text: str = "Choose the AI model for analysis",
    filter_provider: Optional[AIProvider] = None,
    show_cost: bool = True,
    show_details: bool = True
) -> str:
    """
    Render AI model selector in sidebar

    Args:
        session_key: Session state key for selection
        label: Label for selector
        help_text: Help text
        filter_provider: If set, only show models from this provider
        show_cost: Show cost information
        show_details: Show detailed model info

    Returns:
        Selected model ID
    """
    # Initialize with default if not set
    if session_key not in st.session_state:
        st.session_state[session_key] = DEFAULT_MODEL

    # Get available models
    if filter_provider:
        available = get_models_by_provider(filter_provider)
    else:
        available = get_available_models()

    if not available:
        st.sidebar.warning("⚠️ No AI providers configured. Add API keys to secrets.toml")
        st.sidebar.code("""
# Add to .streamlit/secrets.toml:
GOOGLE_API_KEY = "your-key-here"
OPENAI_API_KEY = "your-key-here"
ANTHROPIC_API_KEY = "your-key-here"
XAI_API_KEY = "your-key-here"
        """)
        return DEFAULT_MODEL

    # Group by provider
    providers = {}
    for model in available:
        if model.provider not in providers:
            providers[model.provider] = []
        providers[model.provider].append(model)

    # Build options
    options = []
    option_ids = []

    for provider in AIProvider:
        if provider in providers:
            # Add provider header
            options.append(f"--- {provider.value} ---")
            option_ids.append(None)

            # Add models for this provider
            for model in providers[provider]:
                label_parts = [f"  {model.tier_emoji} {model.display_name}"]

                if show_cost:
                    label_parts.append(f" (${model.cost_per_1k_input:.2f}/$"
                                     f"{model.cost_per_1k_output:.2f} per 1K)")

                options.append("".join(label_parts))
                option_ids.append(model.model_id)

    # Find current selection index
    current_model = st.session_state[session_key]
    try:
        current_index = option_ids.index(current_model)
    except ValueError:
        # Current model not available, use first non-separator
        current_index = next(i for i, id in enumerate(option_ids) if id is not None)

    # Render selector
    selected_display = st.sidebar.selectbox(
        label,
        options=options,
        index=current_index,
        help=help_text,
        key=f"{session_key}_selector"
    )

    # Map back to model ID
    selected_idx = options.index(selected_display)
    selected_id = option_ids[selected_idx]

    # Update session state if changed and valid
    if selected_id and selected_id != st.session_state[session_key]:
        st.session_state[session_key] = selected_id

    # Display model details
    if show_details:
        display_model_info_card(st.session_state[session_key])

    return st.session_state[session_key]


def display_model_info_card(model_id: str):
    """Display detailed information card for a model"""
    model = get_model_info(model_id)

    if model:
        with st.sidebar.expander("ℹ️ Model Details", expanded=False):
            st.markdown(f"**{model.full_name}**")
            st.caption(model.description)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tier", model.tier.title())
                st.metric("Input", f"{model.input_token_limit//1000}K")
            with col2:
                st.metric("Cost/1K In", f"${model.cost_per_1k_input:.2f}")
                st.metric("Output", f"{model.output_token_limit//1000}K")

            # Features
            features = []
            if model.supports_vision:
                features.append("🖼️ Vision")
            if model.supports_function_calling:
                features.append("🔧 Functions")

            if features:
                st.markdown("**Features**: " + " | ".join(features))

            # Tier explanation
            if model.tier == 'premium':
                st.info("💎 **Premium**: Highest capability, best for complex analysis")
            elif model.tier == 'standard':
                st.success("⚡ **Standard**: Great balance of speed and quality")
            elif model.tier == 'fast':
                st.success("🚀 **Fast**: Quick responses, good quality")
            elif model.tier == 'lite':
                st.success("💨 **Lite**: Fastest, most cost-effective")


def get_selected_model(session_key: str = "selected_ai_model") -> str:
    """Get currently selected model ID"""
    return st.session_state.get(session_key, DEFAULT_MODEL)


def create_model_client(model_id: Optional[str] = None, session_key: str = "selected_ai_model") -> Any:
    """
    Create appropriate client for the selected model

    Args:
        model_id: Specific model to use (if None, uses selected)
        session_key: Session state key for selection

    Returns:
        Configured model client (varies by provider)
    """
    if model_id is None:
        model_id = get_selected_model(session_key)

    model_info = get_model_info(model_id)

    if not model_info:
        raise ValueError(f"Model not found: {model_id}")

    # Create provider-specific client
    if model_info.provider == AIProvider.GEMINI:
        # Use module-level genai (can be patched in tests). If SDK wasn't
        # importable at module import time genai will be None.
        if genai is None:
            raise ValueError("google.generativeai SDK is not available")
        # Support both GOOGLE_API_KEY and GEMINI_API_KEY
        api_key = None
        if 'GEMINI_API_KEY' in st.secrets:
            api_key = st.secrets['GEMINI_API_KEY']
        elif 'GOOGLE_API_KEY' in st.secrets:
            api_key = st.secrets['GOOGLE_API_KEY']

        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not configured")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(model_id)

    elif model_info.provider == AIProvider.OPENAI:
        # Use the module-level OpenAI class (patched in tests) if available.
        if OpenAI is None:
            raise ValueError("openai SDK is not available")
        if 'OPENAI_API_KEY' not in st.secrets:
            raise ValueError("OPENAI_API_KEY not configured")
        return OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

    elif model_info.provider == AIProvider.CLAUDE:
        # Use module-level anthropic (patched in tests) if available.
        if anthropic is None:
            raise ValueError("anthropic SDK is not available")
        if 'ANTHROPIC_API_KEY' not in st.secrets:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        return anthropic.Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])

    elif model_info.provider == AIProvider.GROK:
        # Grok is OpenAI-compatible; use module-level OpenAI class if available
        if OpenAI is None:
            raise ValueError("openai SDK is not available for GROK")
        if 'XAI_API_KEY' not in st.secrets:
            raise ValueError("XAI_API_KEY not configured")
        return OpenAI(api_key=st.secrets['XAI_API_KEY'], base_url="https://api.x.ai/v1")

    else:
        raise ValueError(f"Unsupported provider: {model_info.provider}. Only Gemini is currently enabled.")


def get_provider_status() -> Dict[str, bool]:
    """Get configuration status for all providers"""
    return {
        provider.value: is_provider_configured(provider)
        for provider in AIProvider
    }


def display_provider_status():
    """Display provider configuration status in sidebar"""
    with st.sidebar.expander("🔑 API Configuration", expanded=False):
        status = get_provider_status()

        for provider_name, is_configured in status.items():
            if is_configured:
                st.success(f"✅ {provider_name}")
            else:
                st.error(f"❌ {provider_name}")

        if not any(status.values()):
            st.warning("No AI providers configured. Add API keys to `.streamlit/secrets.toml`")


# ==========================================
# HELPER FUNCTIONS FOR COMMON USE CASES
# ==========================================

def get_configured_model(session_key: str = "global_ai_model") -> Optional[AIModelInfo]:
    """
    Get the currently configured AI model info

    Args:
        session_key: Session state key for model selection (default: global_ai_model)

    Returns:
        AIModelInfo if model is selected and configured, None otherwise
    """
    model_id = get_selected_model(session_key)
    if not model_id:
        return None

    model_info = get_model_info(model_id)
    if not model_info:
        return None

    # Check if provider is configured
    if not is_provider_configured(model_info.provider):
        return None

    return model_info


def call_ai_model(
    model_info: AIModelInfo,
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    session_key: str = "global_ai_model"
) -> str:
    """
    Universal function to call any AI model with a prompt

    Args:
        model_info: AIModelInfo object
        prompt: The prompt to send to the model
        max_tokens: Maximum tokens in response
        temperature: Temperature for response randomness (0.0-1.0)
        session_key: Session state key (default: global_ai_model)

    Returns:
        AI model response as string

    Raises:
        Exception: If AI call fails
    """
    try:
        client = create_model_client(model_info.model_id, session_key)

        if model_info.provider == AIProvider.GEMINI:
            response = client.generate_content(prompt)
            return response.text

        elif model_info.provider == AIProvider.OPENAI or model_info.provider == AIProvider.GROK:
            response = client.chat.completions.create(
                model=model_info.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content

        elif model_info.provider == AIProvider.CLAUDE:
            response = client.messages.create(
                model=model_info.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        else:
            raise ValueError(f"Unsupported provider: {model_info.provider}. Only Gemini is currently enabled.")

    except Exception as e:
        # Return a friendly failure string instead of raising so callers (and UI)
        # can show useful messages without causing noisy stack traces in the app
        return f"failed: {str(e)}"
