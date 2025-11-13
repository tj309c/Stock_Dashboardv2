import json
import time
import streamlit as st
import google.generativeai as genai

@st.cache_resource(show_spinner="Initializing AI Model...")
def get_generative_model():
    """Finds and returns the best available generative model."""
    gemini_1_5_pro_latest = None
    gemini_pro_models = []
    gemini_flash_models = []
    other_generative_models = [] # For any other model supporting generateContent

    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "gemini-1.5-pro-latest" in m.name:
                gemini_1_5_pro_latest = m.name
            elif "gemini-1.0-pro" in m.name or "gemini-pro" in m.name:
                gemini_pro_models.append(m.name)
            elif "gemini-1.0-flash" in m.name or "gemini-flash" in m.name:
                gemini_flash_models.append(m.name)
            else:
                other_generative_models.append(m.name)

    model_to_use = None
    if gemini_1_5_pro_latest:
        model_to_use = gemini_1_5_pro_latest
    elif gemini_pro_models:
        # Take the first 'pro' model found.
        model_to_use = gemini_pro_models[0]
    elif gemini_flash_models:
        # Take the first 'flash' model found.
        model_to_use = gemini_flash_models[0]
    elif other_generative_models:
        # Take the first of any other generative model.
        model_to_use = other_generative_models[0]

    if not model_to_use:
        raise ValueError("No suitable generative models found for your API key.")
    
    return genai.GenerativeModel(model_to_use)

def _call_generative_model_with_retry(model, prompt, response_parser, default_on_fail, max_retries=3):
    """
    Calls the generative model, handles retries, and parses the response.

    Args:
        model: The generative model instance.
        prompt (str): The prompt to send to the model.
        response_parser (function): A function that takes the raw text response and parses it (e.g., json.loads).
        default_on_fail: The value to return if all attempts and parsing fail.
        max_retries (int): The maximum number of retries.

    Returns:
        The parsed response or the default value on failure.
    """
    json_str = "" # Initialize json_str for scope in exception block

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            json_str = response.text
            parsed_result = response_parser(json_str)
            return parsed_result
        except json.JSONDecodeError as e:
            st.warning(f"AI response parsing failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                st.error(f"Failed to parse AI response after {max_retries} attempts. Response was: {json_str[:200]}")
                return default_on_fail
            time.sleep(1)
        except Exception as e:
            st.warning(f"AI call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                st.error(f"AI call failed after {max_retries} attempts.")
                return default_on_fail
            time.sleep(1)

    return default_on_fail


@st.cache_data(ttl=3600, show_spinner="Fetching comparable companies...")
def get_ai_comparables(ticker: str, sector: str):
    """
    Fetches comparable companies using AI analysis.
    Returns a dictionary with sector comparison metrics.
    """
    try:
        model = get_generative_model()

        prompt = f"""You are a financial analyst. For the company ticker {ticker} in the {sector} sector,
provide comparable companies analysis with the following metrics:

Return a JSON object with this structure:
{{
    "pe": <median P/E ratio for sector>,
    "priceToBook": <median Price to Book for sector>,
    "enterpriseValueRevenue": <median EV/Revenue for sector>,
    "enterpriseValueEBITDA": <median EV/EBITDA for sector>,
    "comparable_tickers": ["TICKER1", "TICKER2", "TICKER3"]
}}

Provide realistic estimates based on the {sector} sector.
"""

        result = _call_generative_model_with_retry(
            model,
            prompt,
            json.loads,
            {
                "pe": 20.0,
                "priceToBook": 3.0,
                "enterpriseValueRevenue": 5.0,
                "enterpriseValueEBITDA": 15.0,
                "comparable_tickers": []
            }
        )

        return result

    except Exception as e:
        st.warning(f"Could not fetch AI comparables: {e}")
        return {
            "pe": 20.0,
            "priceToBook": 3.0,
            "enterpriseValueRevenue": 5.0,
            "enterpriseValueEBITDA": 15.0,
            "comparable_tickers": []
        }


@st.cache_data(ttl=3600, show_spinner="Analyzing chart patterns...")
def get_ai_chart_analysis(ticker: str, price_data):
    """
    Analyzes chart patterns using AI.
    Returns a markdown-formatted analysis.
    """
    try:
        import pandas as pd

        model = get_generative_model()

        # Get recent price data summary
        recent_data = price_data.tail(20)
        price_summary = f"""
Recent price data for {ticker}:
- Latest Close: ${recent_data['Close'].iloc[-1]:.2f}
- 20-day High: ${recent_data['Close'].max():.2f}
- 20-day Low: ${recent_data['Close'].min():.2f}
- 20-day Average: ${recent_data['Close'].mean():.2f}
- Price change (20 days): {((recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0] - 1) * 100):.2f}%
"""

        # Include technical indicators if available
        if 'RSI_14' in recent_data.columns:
            price_summary += f"- Latest RSI: {recent_data['RSI_14'].iloc[-1]:.2f}\n"
        if 'MACD_12_26_9' in recent_data.columns:
            price_summary += f"- Latest MACD: {recent_data['MACD_12_26_9'].iloc[-1]:.2f}\n"

        prompt = f"""You are a technical analyst. Analyze the following price data and identify chart patterns:

{price_summary}

Identify any notable patterns such as:
- Support/Resistance levels
- Trend channels
- Head and shoulders, double tops/bottoms
- Triangle patterns
- Breakout potential

Provide a concise analysis in markdown format (2-3 paragraphs max).
"""

        def text_parser(response_text):
            # Remove markdown code fences if present
            cleaned = response_text.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned
            return cleaned

        analysis = _call_generative_model_with_retry(
            model,
            prompt,
            text_parser,
            f"**Chart Analysis for {ticker}**\n\nUnable to generate AI analysis at this time. Please review the technical indicators manually."
        )

        return analysis

    except Exception as e:
        st.warning(f"Could not generate AI chart analysis: {e}")
        return f"**Chart Analysis for {ticker}**\n\nUnable to generate AI analysis at this time. Error: {str(e)}"