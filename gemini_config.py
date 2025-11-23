"""
Centralized Gemini Model Configuration
Provides dynamic model selection and configuration for all AI features
"""
import streamlit as st
import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from error_logger import log_error, log_warning

@dataclass
class GeminiModelInfo:
    """Information about a Gemini model"""
    name: str
    display_name: str
    description: str
    is_flash: bool
    is_pro: bool
    supports_generation: bool
    input_token_limit: int
    output_token_limit: int

    @property
    def tier(self) -> str:
        """Get the model tier for categorization"""
        if 'pro' in self.name.lower():
            return 'pro'
        elif 'flash-lite' in self.name.lower() or 'lite' in self.name.lower():
            return 'lite'
        elif 'flash' in self.name.lower():
            return 'flash'
        else:
            return 'other'

    @property
    def short_label(self) -> str:
        """Get a short, user-friendly label"""
        # Extract version and type
        parts = self.name.split('/')[-1]  # Remove 'models/' prefix

        if 'flash-lite' in parts:
            version = parts.split('flash-lite')[0].replace('gemini-', '').replace('-', ' ')
            return f"Flash-Lite {version.strip()}"
        elif 'flash' in parts:
            version = parts.split('flash')[0].replace('gemini-', '').replace('-', ' ')
            return f"Flash {version.strip()}"
        elif 'pro' in parts:
            version = parts.split('pro')[0].replace('gemini-', '').replace('-', ' ')
            return f"Pro {version.strip()}"

        return parts


# Default model to use across the application
DEFAULT_MODEL = "gemini-2.5-flash"


def get_available_gemini_models(force_refresh: bool = False) -> List[GeminiModelInfo]:
    """
    Get list of available Gemini models that support content generation

    Args:
        force_refresh: If True, bypass cache and fetch fresh model list

    Returns:
        List of GeminiModelInfo objects
    """
    cache_key = '_gemini_models_cache'

    # Use cached models if available and not forcing refresh
    if not force_refresh and cache_key in st.session_state:
        return st.session_state[cache_key]

    try:
        if 'GOOGLE_API_KEY' not in st.secrets:
            log_warning("GOOGLE_API_KEY not configured", "gemini_config.get_available_gemini_models")
            return []

        genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

        models = []
        for model in genai.list_models():
            # Only include models that support generateContent
            if 'generateContent' in model.supported_generation_methods:
                # Filter for Gemini models only (no embedding, live, etc.)
                if 'gemini' in model.name.lower() and 'embedding' not in model.name.lower():
                    # Skip live/audio/vision-specific models for text generation
                    if any(skip in model.name.lower() for skip in ['live', 'native-audio', 'robotics', 'computer-use']):
                        continue

                    models.append(GeminiModelInfo(
                        name=model.name.split('/')[-1],  # Remove 'models/' prefix
                        display_name=model.display_name,
                        description=model.description,
                        is_flash='flash' in model.name.lower(),
                        is_pro='pro' in model.name.lower(),
                        supports_generation=True,
                        input_token_limit=getattr(model, 'input_token_limit', 0),
                        output_token_limit=getattr(model, 'output_token_limit', 0)
                    ))

        # Cache the results
        st.session_state[cache_key] = models

        return models

    except Exception as e:
        log_error(e, "gemini_config.get_available_gemini_models", {})
        return []


def get_categorized_models() -> Dict[str, List[GeminiModelInfo]]:
    """
    Get models organized by tier (Pro, Flash, Lite)

    Returns:
        Dictionary with keys: 'pro', 'flash', 'lite'
    """
    all_models = get_available_gemini_models()

    categorized = {
        'pro': [],
        'flash': [],
        'lite': [],
        'other': []
    }

    for model in all_models:
        categorized[model.tier].append(model)

    # Sort each category (newest/most capable first)
    for tier in categorized:
        # Prioritize stable releases over previews/experimental
        categorized[tier].sort(key=lambda m: (
            'preview' not in m.name.lower() and 'exp' not in m.name.lower(),  # Stable first
            m.name.lower()  # Then alphabetically
        ), reverse=True)

    return categorized


def render_model_selector(
    session_key: str = "selected_gemini_model",
    label: str = "AI Model:",
    help_text: str = "Choose the Gemini model for AI-powered features",
    show_tiers: bool = True,
    show_details: bool = False
) -> str:
    """
    Render a model selector in the UI (typically in sidebar)

    Args:
        session_key: Session state key to store selection
        label: Label for the selector
        help_text: Help text to display
        show_tiers: If True, show models grouped by tier
        show_details: If True, show detailed model info

    Returns:
        Selected model name
    """
    # Initialize with default if not set
    if session_key not in st.session_state:
        st.session_state[session_key] = DEFAULT_MODEL

    models = get_available_gemini_models()

    if not models:
        st.sidebar.warning("⚠️ No Gemini models available. Check API key.")
        return DEFAULT_MODEL

    if show_tiers:
        # Categorized display
        categorized = get_categorized_models()

        # Build options with tier labels
        options = []
        option_names = []

        # Pro models
        if categorized['pro']:
            options.append("--- Pro Models (Best Quality) ---")
            option_names.append(None)  # Separator
            for model in categorized['pro'][:5]:  # Top 5 pro models
                options.append(f"  💎 {model.display_name}")
                option_names.append(model.name)

        # Flash models
        if categorized['flash']:
            options.append("--- Flash Models (Balanced) ---")
            option_names.append(None)  # Separator
            for model in categorized['flash'][:5]:  # Top 5 flash models
                options.append(f"  ⚡ {model.display_name}")
                option_names.append(model.name)

        # Lite models
        if categorized['lite']:
            options.append("--- Lite Models (Fastest) ---")
            option_names.append(None)  # Separator
            for model in categorized['lite'][:5]:  # Top 5 lite models
                options.append(f"  🚀 {model.display_name}")
                option_names.append(model.name)

        # Find current selection index
        current_model = st.session_state[session_key]
        try:
            current_index = option_names.index(current_model)
        except ValueError:
            # Default not in list, use first non-separator
            current_index = next(i for i, name in enumerate(option_names) if name is not None)

        # Render selectbox
        selected_display = st.sidebar.selectbox(
            label,
            options=options,
            index=current_index,
            help=help_text,
            key=f"{session_key}_selector"
        )

        # Map back to model name
        selected_idx = options.index(selected_display)
        selected_model = option_names[selected_idx]

        # Update session state if changed
        if selected_model and selected_model != st.session_state[session_key]:
            st.session_state[session_key] = selected_model

        return st.session_state[session_key]

    else:
        # Simple display (all models in one list)
        model_names = [m.name for m in models]
        model_displays = [f"{m.display_name}" for m in models]

        # Find current selection
        current_model = st.session_state[session_key]
        try:
            current_index = model_names.index(current_model)
        except ValueError:
            current_index = 0

        selected_display = st.sidebar.selectbox(
            label,
            options=model_displays,
            index=current_index,
            help=help_text,
            key=f"{session_key}_selector"
        )

        # Map back to model name
        selected_idx = model_displays.index(selected_display)
        selected_model = model_names[selected_idx]

        st.session_state[session_key] = selected_model
        return selected_model


def get_selected_model(session_key: str = "selected_gemini_model") -> str:
    """
    Get the currently selected model (or default if not set)

    Args:
        session_key: Session state key for model selection

    Returns:
        Model name string
    """
    return st.session_state.get(session_key, DEFAULT_MODEL)


def create_model_instance(
    model_name: Optional[str] = None,
    session_key: str = "selected_gemini_model",
    **generation_config
) -> genai.GenerativeModel:
    """
    Create a Gemini model instance with the selected or specified model

    Args:
        model_name: Specific model to use (if None, uses selected model)
        session_key: Session state key for model selection
        **generation_config: Additional generation config parameters

    Returns:
        Configured GenerativeModel instance
    """
    if model_name is None:
        model_name = get_selected_model(session_key)

    # Ensure we have the API key
    if 'GOOGLE_API_KEY' not in st.secrets:
        raise ValueError("GOOGLE_API_KEY not configured in secrets.toml")

    genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

    # Create model with optional generation config
    if generation_config:
        return genai.GenerativeModel(model_name, generation_config=generation_config)
    else:
        return genai.GenerativeModel(model_name)


def get_model_info(model_name: str) -> Optional[GeminiModelInfo]:
    """
    Get detailed information about a specific model

    Args:
        model_name: Name of the model

    Returns:
        GeminiModelInfo or None if not found
    """
    models = get_available_gemini_models()

    for model in models:
        if model.name == model_name:
            return model

    return None


def display_model_info_card(model_name: Optional[str] = None, session_key: str = "selected_gemini_model"):
    """
    Display a card with information about the currently selected model

    Args:
        model_name: Specific model to show info for (if None, uses selected)
        session_key: Session state key for model selection
    """
    if model_name is None:
        model_name = get_selected_model(session_key)

    model_info = get_model_info(model_name)

    if model_info:
        with st.sidebar.expander("ℹ️ Model Details", expanded=False):
            st.markdown(f"**{model_info.display_name}**")
            st.caption(model_info.description)
            st.markdown(f"- **Tier**: {model_info.tier.title()}")
            st.markdown(f"- **Input Tokens**: {model_info.input_token_limit:,}")
            st.markdown(f"- **Output Tokens**: {model_info.output_token_limit:,}")

            # Recommendations
            if model_info.tier == 'pro':
                st.info("💎 **Pro**: Best quality, highest cost")
            elif model_info.tier == 'flash':
                st.success("⚡ **Flash**: Great balance of speed and quality")
            elif model_info.tier == 'lite':
                st.success("🚀 **Lite**: Fastest, lowest cost")


# Convenience function for backward compatibility
def get_default_model() -> str:
    """Get the default model name"""
    return DEFAULT_MODEL
