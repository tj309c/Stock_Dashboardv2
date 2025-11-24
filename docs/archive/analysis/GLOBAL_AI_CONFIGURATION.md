# Global AI Configuration Guide

## Overview

The stock analysis dashboard now has a **centralized AI configuration system** that allows users to select their preferred AI model **once** in the sidebar, and that selection applies across **all pages** of the dashboard.

This eliminates the need for users to configure AI settings separately on each page and provides a consistent AI experience throughout the application.

---

## Architecture

### Key Components

1. **[global_sidebar.py](global_sidebar.py)** - Centralized sidebar component
   - Handles theme toggle (Dark/Light mode)
   - Manages global "Enable AI Features" toggle
   - Renders AI model selector with **global session key**
   - Can be imported and used by any page

2. **Session State Key: `global_ai_model`**
   - This is the **single source of truth** for AI model selection
   - All pages reference this key instead of page-specific keys
   - Stored in `st.session_state['global_ai_model']`

3. **[ai_model_config.py](ai_model_config.py)** - AI model configuration
   - Model catalog (Gemini, OpenAI, Claude, Grok)
   - `get_selected_model(session_key)` - retrieves selected model ID
   - `create_model_client(model_id, session_key)` - creates AI client
   - `render_model_selector(session_key)` - renders dropdown

---

## How It Works

### User Workflow

1. **User opens any page** in the dashboard
2. **Sidebar appears** with:
   - Theme toggle
   - "Enable AI Features" checkbox (global)
   - AI Model dropdown (if AI enabled)
3. **User selects a model** (e.g., "Gemini 2.5 Flash")
4. **Selection persists** across all pages in the session
5. **All AI features** use the selected model automatically

### Developer Workflow

When implementing a new page with AI features:

```python
# 1. Import global sidebar at the top of your page
from global_sidebar import render_global_sidebar, apply_theme_css

# 2. Render the global sidebar (after st.set_page_config)
sidebar_config = render_global_sidebar()
apply_theme_css(sidebar_config['theme'])

# 3. Check if AI features are enabled
if sidebar_config['enable_ai_features']:
    # AI features code here
    pass

# 4. Use global AI model key when calling AI functions
from ai_model_config import get_selected_model, create_model_client

model_id = get_selected_model("global_ai_model")  # ← GLOBAL KEY
client = create_model_client(model_id, "global_ai_model")  # ← GLOBAL KEY
```

---

## Implementation Examples

### Example 1: Market Overview & Economy Page

**File**: [`pages/01_📊_Market_Overview_&_Economy.py`](pages/01_📊_Market_Overview_&_Economy.py)

```python
# Top of file - imports
from global_sidebar import render_global_sidebar, apply_theme_css

# After st.set_page_config()
sidebar_config = render_global_sidebar()
apply_theme_css(sidebar_config['theme'])

# In generate_ai_market_summary() function
from ai_model_config import create_model_client, get_selected_model

# Use GLOBAL AI model selection
model_id = get_selected_model("global_ai_model")
client = create_model_client(model_id, "global_ai_model")
```

**AI Feature**: AI Market Intelligence tab generates market summaries

---

### Example 2: Home Page

**File**: [`Home.py`](Home.py)

```python
# Top of file
from global_sidebar import render_global_sidebar, apply_theme_css

# Render global sidebar
sidebar_config = render_global_sidebar()
apply_theme_css(sidebar_config['theme'])

# Show status
if sidebar_config['enable_ai_features'] and sidebar_config['selected_ai_model']:
    from ai_model_config import get_model_info
    model_info = get_model_info(sidebar_config['selected_ai_model'])
    st.success(f"AI Features Enabled - Using: {model_info.full_name}")
```

---

## Migration Guide

### Old Way (Page-Specific Keys)

**Before** - Each page had its own AI model selector:

```python
# Home.py - OLD WAY ❌
selected_model = render_model_selector(
    session_key="selected_ai_model",  # Page-specific
    ...
)

# Market Overview page - OLD WAY ❌
model_id = get_selected_model("market_overview_ai_model")  # Different key!
```

**Problem**: User had to configure AI separately on each page

### New Way (Global Key)

**After** - All pages use the same global key:

```python
# Home.py - NEW WAY ✅
sidebar_config = render_global_sidebar()  # Global sidebar

# Market Overview page - NEW WAY ✅
model_id = get_selected_model("global_ai_model")  # Same key everywhere!
```

**Benefit**: Configure once, works everywhere

---

## Benefits

### For Users

✅ **Configure once** - Set AI model preference in sidebar once
✅ **Consistent experience** - Same AI model used across all features
✅ **Easy to change** - Switch models globally with one dropdown
✅ **Clear status** - See which model is active at a glance

### For Developers

✅ **Simple integration** - Just use `global_ai_model` key
✅ **No duplication** - No need to render model selector on each page
✅ **Maintainable** - Centralized logic in `global_sidebar.py`
✅ **Flexible** - Easy to add new AI features to any page

---

## Available AI Providers

The system supports 4 AI providers (configured in `.streamlit/secrets.toml`):

### Google Gemini
- **API Key**: `GOOGLE_API_KEY`
- **Models**: Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 1.5 Flash
- **Best for**: Fast, cost-effective analysis

### OpenAI
- **API Key**: `OPENAI_API_KEY`
- **Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Best for**: Premium quality analysis

### Anthropic Claude
- **API Key**: `ANTHROPIC_API_KEY`
- **Models**: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- **Best for**: Detailed, nuanced analysis

### X.AI Grok
- **API Key**: `XAI_API_KEY`
- **Models**: Grok Beta
- **Best for**: Experimental features

---

## Adding AI Features to a New Page

### Step-by-Step Template

```python
"""
Your New Page
"""
import streamlit as st
from global_sidebar import render_global_sidebar, apply_theme_css

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Your Page",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# GLOBAL SIDEBAR (Theme, AI Settings)
# ============================
sidebar_config = render_global_sidebar()
apply_theme_css(sidebar_config['theme'])

# ============================
# YOUR PAGE CONTENT
# ============================
st.title("Your Page Title")

# Check if AI features enabled
if sidebar_config['enable_ai_features']:
    # Option 1: Use AI directly in your code
    from ai_model_config import get_selected_model, create_model_client, get_model_info, AIProvider

    model_id = get_selected_model("global_ai_model")
    model_info = get_model_info(model_id)

    if model_info:
        client = create_model_client(model_id, "global_ai_model")

        # Call AI model based on provider
        if model_info.provider == AIProvider.GEMINI:
            response = client.generate_content("Your prompt here")
            st.write(response.text)

        elif model_info.provider == AIProvider.OPENAI or model_info.provider == AIProvider.GROK:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "Your prompt"}],
                max_tokens=500
            )
            st.write(response.choices[0].message.content)

        elif model_info.provider == AIProvider.CLAUDE:
            response = client.messages.create(
                model=model_id,
                max_tokens=500,
                messages=[{"role": "user", "content": "Your prompt"}]
            )
            st.write(response.content[0].text)
    else:
        st.warning("Please select an AI model in the sidebar")
else:
    st.info("Enable AI features in the sidebar to use this feature")
```

---

## Troubleshooting

### Issue: "No AI providers configured"

**Cause**: No API keys found in `.streamlit/secrets.toml`

**Solution**: Add at least one API key:
```toml
# Add to .streamlit/secrets.toml
GOOGLE_API_KEY = "your-google-api-key"
# OR
OPENAI_API_KEY = "your-openai-api-key"
# OR
ANTHROPIC_API_KEY = "your-anthropic-api-key"
# OR
XAI_API_KEY = "your-xai-api-key"
```

### Issue: Model selection not persisting

**Cause**: Using page-specific key instead of global key

**Solution**: Always use `"global_ai_model"` as the session key:
```python
# ❌ Wrong
model_id = get_selected_model("my_custom_key")

# ✅ Correct
model_id = get_selected_model("global_ai_model")
```

### Issue: Different models on different pages

**Cause**: Old page-specific keys still in use

**Solution**: Search for all instances of session keys and replace with `"global_ai_model"`:
```bash
# Find all AI model references
grep -r "selected_ai_model\|_ai_model" pages/
```

---

## Future Enhancements

### Planned Features

1. **Model Comparison Mode**
   - Run same prompt through multiple models
   - Compare responses side-by-side

2. **Cost Tracking**
   - Track AI API usage per session
   - Show estimated costs in sidebar

3. **Model Performance Metrics**
   - Track response times
   - Show quality ratings from users

4. **Custom Model Presets**
   - Save favorite models per feature type
   - "Fast mode" vs "Quality mode" presets

---

## Summary

The **Global AI Configuration** system provides:

✅ **Single model selection** across all pages
✅ **Centralized sidebar** component (`global_sidebar.py`)
✅ **Session key**: `global_ai_model`
✅ **Easy integration** for new AI features
✅ **Better UX** for users (configure once)
✅ **Better DX** for developers (less code duplication)

**Key Takeaway**: Always use `"global_ai_model"` as your session key when building AI features!
