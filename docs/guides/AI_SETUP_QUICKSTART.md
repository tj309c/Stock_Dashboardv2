# 🚀 AI Model Configuration - Quick Start

## What's New?

Your Stock Analysis Dashboard now supports **4 AI providers** with **user-selectable models**!

### Supported Providers:
- 🟦 **Google Gemini** (Default: `gemini-2.5-flash`)
- 🟩 **OpenAI** (GPT-4o, GPT-4o Mini, GPT-3.5)
- 🟪 **Anthropic Claude** (Claude 4.5, 3.5, 3)
- ⬛ **X.AI Grok** (With real-time X/Twitter data)

---

## ⚡ Quick Setup (3 Steps)

### 1. Add API Keys

Edit `.streamlit/secrets.toml`:

```toml
# Add any or all of these:
GOOGLE_API_KEY = "AIzaSy..."          # Get from: https://aistudio.google.com/app/apikey
OPENAI_API_KEY = "sk-proj-..."        # Get from: https://platform.openai.com/api-keys
ANTHROPIC_API_KEY = "sk-ant-..."      # Get from: https://console.anthropic.com/settings/keys
XAI_API_KEY = "xai-..."                # Get from: https://console.x.ai/
```

### 2. Enable AI Features

In the sidebar:
1. Check "Enable AI Features"
2. The **AI Configuration** section will appear

### 3. Select Your Model

Choose from the dropdown in **AI Configuration**:
- Models grouped by provider (Gemini, OpenAI, Claude, Grok)
- Shows cost per 1K tokens
- Click "Model Details" to see full specs

**Done!** The selected model will be used for all AI features.

---

## 🎯 Recommended Models by Use Case

### For Sentiment Analysis (News):
```
⚡ Gemini 2.5 Flash          ($0.075/$0.30 per 1K)  ← Default
🚀 GPT-4o Mini               ($0.15/$0.60 per 1K)
🚀 Claude 3.5 Haiku          ($0.80/$4.00 per 1K)
```

### For Deep Financial Analysis:
```
💎 Claude 4.5 Sonnet         ($3.00/$15.00 per 1K)
💎 GPT-4o                    ($2.50/$10.00 per 1K)
💎 Gemini 2.5 Pro            ($1.25/$5.00 per 1K)
```

### For High-Volume/Cost-Conscious:
```
💨 Gemini 2.0 Flash-Lite     ($0.0375/$0.15 per 1K)
💨 GPT-3.5 Turbo             ($0.50/$1.50 per 1K)
```

### For X/Twitter Sentiment:
```
⚡ Grok Beta                 ($5.00/$15.00 per 1K)  ← Has real-time X data
```

---

## 💰 Cost Comparison

| Provider | Model | Input (per 1M) | Output (per 1M) | Best For |
|----------|-------|----------------|-----------------|----------|
| Gemini | 2.5 Flash | $75 | $300 | **General use** |
| Gemini | 2.0 Flash-Lite | $37.50 | $150 | **High volume** |
| Gemini | 2.5 Pro | $1,250 | $5,000 | **Complex analysis** |
| OpenAI | GPT-4o Mini | $150 | $600 | **Balanced** |
| OpenAI | GPT-4o | $2,500 | $10,000 | **Premium quality** |
| OpenAI | GPT-3.5 Turbo | $500 | $1,500 | **Budget** |
| Claude | 3.5 Haiku | $800 | $4,000 | **Fast & affordable** |
| Claude | 4.5 Sonnet | $3,000 | $15,000 | **Best reasoning** |
| Grok | Beta | $5,000 | $15,000 | **X/Twitter data** |

---

## 🔧 For Developers

### Using in Your Code:

```python
from ai_model_config import get_selected_model, create_model_client

# Get selected model
model_id = get_selected_model("selected_ai_model")

# Create client (automatically handles all providers)
client = create_model_client(model_id)

# Use it (provider-specific, see full guide for details)
response = client.generate_content("Your prompt")  # Gemini
# or
response = client.chat.completions.create(...)     # OpenAI/Grok
# or
response = client.messages.create(...)             # Claude
```

See [AI_MODEL_CONFIGURATION_GUIDE.md](AI_MODEL_CONFIGURATION_GUIDE.md) for complete examples.

---

## 📁 Files Created/Modified

### New Files:
1. **`ai_model_config.py`** - Universal AI model configuration
2. **`gemini_config.py`** - Original Gemini-only config (deprecated, use ai_model_config.py)
3. **`list_gemini_models.py`** - Script to list all available Gemini models
4. **`AI_MODEL_CONFIGURATION_GUIDE.md`** - Comprehensive guide
5. **`AI_SETUP_QUICKSTART.md`** - This file

### Modified Files:
1. **`Home.py`** - Added model selector to sidebar
2. **`news_fetcher.py`** - Updated to support all AI providers

### Next Steps (Optional):
- Update other files that use AI (e.g., ai_services.py, Debug Dashboard)
- All new AI features should use `ai_model_config.py`

---

## ✅ Benefits

1. **Flexibility**: Users choose their preferred AI provider
2. **Cost Control**: Select cheaper models for high-volume features
3. **Reliability**: Fall back to different provider if one fails
4. **Future-Proof**: Automatically supports new models from each provider
5. **Performance**: Use faster models when speed matters
6. **Quality**: Use premium models for critical analysis

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No AI providers configured" | Add at least one API key to `secrets.toml` |
| Can't see certain models | That provider's API key isn't configured |
| Model errors | Check API key is valid and has credits |
| Costs too high | Switch to lite/fast models |

---

## 📖 Full Documentation

For complete details, examples, and advanced usage:
👉 See [AI_MODEL_CONFIGURATION_GUIDE.md](AI_MODEL_CONFIGURATION_GUIDE.md)

---

**Status**: ✅ Fully Implemented
**Default Model**: `gemini-2.5-flash`
**Last Updated**: January 2025
