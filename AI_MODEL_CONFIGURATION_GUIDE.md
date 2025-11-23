# AI Model Configuration Guide

## Overview

Your Stock Analysis Dashboard now supports **multiple AI providers** with **dynamic model selection**. Users can choose which AI model to use for all AI-powered features including:

- News sentiment analysis
- Stock insights and recommendations
- Competitor analysis
- Market analysis
- Any other AI-powered features

## Supported AI Providers

### 1. **Google Gemini**
- ⚡ **Gemini 2.5 Flash** (Default) - Balanced speed and quality
- 💎 **Gemini 2.5 Pro** - Most capable, highest quality
- 💨 **Gemini 2.0 Flash-Lite** - Ultra-fast, cost-effective
- 🔄 **Gemini Flash Latest** - Always uses newest Flash model

### 2. **OpenAI**
- 💎 **GPT-4o** - Most advanced multimodal model
- 🚀 **GPT-4o Mini** - Fast, affordable, intelligent
- 💎 **GPT-4 Turbo** - High-intelligence for complex tasks
- 💨 **GPT-3.5 Turbo** - Fast and inexpensive

### 3. **Anthropic Claude**
- 💎 **Claude 4.5 Sonnet** - Latest Claude model
- ⚡ **Claude 3.5 Sonnet** - Balanced intelligence and speed
- 🚀 **Claude 3.5 Haiku** - Fast and affordable
- 💎 **Claude 3 Opus** - Most powerful Claude model

### 4. **X.AI Grok**
- ⚡ **Grok Beta** - Real-time X (Twitter) data access
- 💎 **Grok Vision Beta** - Grok with vision capabilities

---

## Setup: Adding API Keys

To use AI models, add your API keys to `.streamlit/secrets.toml`:

```toml
# Google Gemini
GOOGLE_API_KEY = "your-google-api-key-here"

# OpenAI
OPENAI_API_KEY = "your-openai-api-key-here"

# Anthropic Claude
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

# X.AI Grok
XAI_API_KEY = "your-xai-api-key-here"
```

### Where to Get API Keys:

1. **Google Gemini**: https://aistudio.google.com/app/apikey
2. **OpenAI**: https://platform.openai.com/api-keys
3. **Anthropic Claude**: https://console.anthropic.com/settings/keys
4. **X.AI Grok**: https://console.x.ai/

**Note**: You only need to configure the providers you want to use. The application will automatically detect which API keys are available.

---

## Using the Model Selector

### In the Sidebar:

1. **Enable AI Features** (checkbox in Settings)
2. The **AI Configuration** section will appear
3. Select your preferred model from the dropdown
4. Models are grouped by provider and tier:
   - `--- Google Gemini ---`
   - `--- OpenAI ---`
   - `--- Anthropic Claude ---`
   - `--- X.AI Grok ---`

### Model Information Display:

Click the **"ℹ️ Model Details"** expander to see:
- Full model name and description
- Tier (Premium/Standard/Fast/Lite)
- Input/output token limits
- Cost per 1,000 tokens
- Supported features (vision, function calling)

### Provider Status:

Click the **"🔑 API Configuration"** expander to check:
- ✅ Green checkmark = Provider configured
- ❌ Red X = Provider not configured (add API key)

---

## For Developers: Using AI Models in Code

### Quick Start

```python
from ai_model_config import (
    render_model_selector,
    get_selected_model,
    create_model_client,
    get_model_info,
    AIProvider
)

# 1. Render model selector in sidebar (typically in Home.py or page header)
selected_model = render_model_selector(
    session_key="selected_ai_model",  # Unique key for this feature
    label="AI Model:",
    help_text="Choose AI model for analysis",
    show_cost=True,
    show_details=True
)

# 2. Get the selected model anywhere in your code
model_id = get_selected_model("selected_ai_model")

# 3. Get model information
model_info = get_model_info(model_id)
print(f"Using: {model_info.display_name} ({model_info.provider.value})")

# 4. Create model client (automatically handles different providers)
model_client = create_model_client(model_id)
```

### Provider-Specific Usage

#### Google Gemini:
```python
if model_info.provider == AIProvider.GEMINI:
    model = create_model_client(model_id)
    response = model.generate_content("Your prompt here")
    print(response.text)
```

#### OpenAI:
```python
if model_info.provider == AIProvider.OPENAI:
    client = create_model_client(model_id)
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": "Your prompt"}]
    )
    print(response.choices[0].message.content)
```

#### Anthropic Claude:
```python
if model_info.provider == AIProvider.CLAUDE:
    client = create_model_client(model_id)
    response = client.messages.create(
        model=model_id,
        max_tokens=1024,
        messages=[{"role": "user", "content": "Your prompt"}]
    )
    print(response.content[0].text)
```

#### X.AI Grok:
```python
if model_info.provider == AIProvider.GROK:
    client = create_model_client(model_id)
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": "Your prompt"}]
    )
    print(response.choices[0].message.content)
```

### Universal Example (handles all providers):

```python
from ai_model_config import get_selected_model, get_model_info, create_model_client, AIProvider
import json

def analyze_with_ai(prompt: str, model_id: str = None) -> dict:
    """
    Universal AI analysis function that works with any provider
    """
    if model_id is None:
        model_id = get_selected_model("selected_ai_model")

    model_info = get_model_info(model_id)

    if not model_info:
        return {"error": "Model not found"}

    try:
        # Generate response based on provider
        if model_info.provider == AIProvider.GEMINI:
            model = create_model_client(model_id)
            response = model.generate_content(prompt)
            text = response.text

        elif model_info.provider == AIProvider.OPENAI:
            client = create_model_client(model_id)
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content

        elif model_info.provider == AIProvider.CLAUDE:
            client = create_model_client(model_id)
            response = client.messages.create(
                model=model_id,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text

        elif model_info.provider == AIProvider.GROK:
            client = create_model_client(model_id)
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content

        # Parse JSON if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]

        return json.loads(text.strip())

    except Exception as e:
        return {"error": str(e)}
```

---

## Model Selection Best Practices

### For Sentiment Analysis (News):
- **Recommended**: Gemini 2.5 Flash, GPT-4o Mini
- **Why**: Fast enough for real-time processing, good quality
- **Cost**: Low to moderate

### For Complex Financial Analysis:
- **Recommended**: Claude 4.5 Sonnet, GPT-4o, Gemini 2.5 Pro
- **Why**: Better reasoning, understanding of complex financial concepts
- **Cost**: Higher, but worth it for accuracy

### For High-Volume Features:
- **Recommended**: Gemini 2.0 Flash-Lite, GPT-3.5 Turbo
- **Why**: Fastest, cheapest, good enough for simple tasks
- **Cost**: Very low

### For X/Twitter Sentiment:
- **Recommended**: Grok Beta
- **Why**: Has real-time access to X (Twitter) data
- **Cost**: Moderate

---

## Cost Optimization Tips

1. **Use Lite/Fast models for high-volume features**
   - Example: News sentiment analysis (hundreds of articles)

2. **Use Premium models for critical decisions**
   - Example: Final investment recommendations

3. **Cache AI responses aggressively**
   - Already implemented with `@st.cache_data(ttl=3600)`

4. **Let users choose**
   - Power users can select premium models
   - Cost-conscious users can select lite models

5. **Monitor usage**
   - Check model info card to see costs per 1K tokens
   - Estimate total cost: `(input_tokens + output_tokens) / 1000 * cost_per_1k`

---

## Default Model

**Current Default**: `gemini-2.5-flash`

To change the default model, edit `ai_model_config.py`:

```python
# Line 146
DEFAULT_MODEL = "gemini-2.5-flash"  # Change this
```

**Recommendation**: Keep `gemini-2.5-flash` as default because:
- ✅ Free tier available (60 requests/minute)
- ✅ Excellent balance of speed and quality
- ✅ Good for most use cases
- ✅ 1M+ token context window

---

## Troubleshooting

### "No AI providers configured"
- **Solution**: Add at least one API key to `.streamlit/secrets.toml`

### "Model not found"
- **Solution**: The model may have been deprecated. Run `python list_gemini_models.py` to see available models

### "Rate limit exceeded"
- **Solution**: Switch to a different provider or upgrade API plan

### Import errors
- **Solution**: Install required libraries:
  ```bash
  pip install google-generativeai openai anthropic
  ```

### Model costs too high
- **Solution**: Switch to lite/fast models or reduce usage frequency

---

## Future Enhancements

Planned improvements:
1. ✨ **Model performance tracking** - Log accuracy and user satisfaction per model
2. 📊 **Cost dashboard** - Real-time API cost tracking
3. 🎯 **Smart model routing** - Auto-select best model for each task
4. 🔄 **Fallback chains** - Automatically try backup models if primary fails
5. 📝 **Prompt templates** - Pre-built prompts optimized for each model

---

## Support

For questions or issues:
1. Check this guide first
2. Review error logs in the Debug Dashboard
3. Check provider status in sidebar
4. Verify API keys in `secrets.toml`
5. Test with different models to isolate issues

**Last Updated**: January 2025
**Version**: 1.0
