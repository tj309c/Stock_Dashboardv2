"""
Global AI Analysis UI Component
Floating "Analyze Everything" button and comprehensive results display
"""
import streamlit as st
import asyncio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, List
import pandas as pd
from datetime import datetime
import json

from src.analysis.global_ai_analyzer import get_global_ai_analyzer, AI_MODELS


def render_floating_ai_button():
    """
    Render floating "Analyze Everything" button that persists across all tabs.
    Uses Streamlit's custom HTML/CSS for positioning.
    """
    st.markdown("""
    <style>
    .floating-ai-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .ai-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 50px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .ai-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)


def render_ai_analysis_panel(data: Dict):
    """
    Comprehensive AI Analysis Panel - The main "Analyze Everything" interface
    """
    st.markdown("## 🤖 Global AI Analysis Engine")
    st.markdown("""
    **Multi-Model AI Consensus System** - Leverages Claude, GPT-4, Gemini Pro, and Grok to provide 
    comprehensive stock analysis with weighted consensus from the world's most advanced AI models.
    """)
    
    # Initialize analyzer
    analyzer = get_global_ai_analyzer()
    available_models = analyzer.get_available_models()
    
    # API Key Status
    with st.expander("🔑 AI Model Status & Configuration", expanded=False):
        cols = st.columns(4)
        
        for idx, (model_id, config) in enumerate(AI_MODELS.items()):
            with cols[idx]:
                is_available = model_id in available_models
                if is_available:
                    st.success(f"✅ **{config.name}**")
                    st.caption(f"Weight: {config.weight*100:.0f}%")
                    st.caption(f"Max Tokens: {config.max_tokens}")
                else:
                    st.error(f"❌ **{config.name}**")
                    st.caption("API key not configured")
        
        if not available_models:
            st.error("⚠️ **No AI models configured!** Please add API keys to `.streamlit/secrets.toml`")
            st.code("""
# Add to .streamlit/secrets.toml:
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY = "sk-..."
GOOGLE_API_KEY = "AIza..."
XAI_API_KEY = "xai-..."
            """)
            st.info("""
**Model Requirements:**
- **Claude**: Anthropic API key (Pay-as-you-go)
- **GPT-4**: OpenAI API key (Requires GPT-4 access)
- **Gemini**: Google AI API key (Free tier available)
- **Grok**: xAI API key (Requires credits purchase)
            """)
            return
        
        st.info(f"**{len(available_models)}/{len(AI_MODELS)}** AI models configured")
        
        if len(available_models) < len(AI_MODELS):
            missing = [AI_MODELS[m].name for m in AI_MODELS.keys() if m not in available_models]
            st.caption(f"💡 Missing: {', '.join(missing)} - Add API keys to improve consensus")
    
    # Model Selection
    st.markdown("### 🎯 Select Analysis Mode")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_mode = st.radio(
            "Choose how to analyze:",
            options=['consensus', 'single'],
            format_func=lambda x: {
                'consensus': '🌟 Consensus Mode (All Models) - Recommended',
                'single': '🎯 Single Model Mode'
            }[x],
            horizontal=False
        )
    
    selected_models = []
    
    if analysis_mode == 'single':
        with col2:
            single_model = st.selectbox(
                "Select AI Model:",
                options=available_models,
                format_func=lambda x: f"{AI_MODELS[x].name} ({AI_MODELS[x].weight*100:.0f}% weight)"
            )
            selected_models = [single_model]
    else:
        selected_models = available_models
        st.info(f"💡 Using **weighted consensus** from {len(available_models)} models: " + 
                ", ".join([AI_MODELS[m].name for m in available_models]))
    
    # Analysis Configuration
    with st.expander("⚙️ Advanced Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            use_cache = st.checkbox("Use cached results (faster)", value=True)
            include_alternatives = st.checkbox("Include alternative scenarios", value=True)
        
        with col2:
            detail_level = st.select_slider(
                "Analysis depth:",
                options=['concise', 'standard', 'comprehensive'],
                value='comprehensive'
            )
            include_charts = st.checkbox("Generate visualization charts", value=True)
    
    st.markdown("---")
    
    # Initialize session state for analysis trigger
    if 'run_ai_analysis' not in st.session_state:
        st.session_state.run_ai_analysis = False
    if 'ai_analysis_result' not in st.session_state:
        st.session_state.ai_analysis_result = None
    
    # Big Analysis Button - Set flag instead of running immediately
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "🚀 ANALYZE EVERYTHING",
            use_container_width=True,
            type="primary",
            key="analyze_everything_btn"
        ):
            st.session_state.run_ai_analysis = True
            st.session_state.ai_analysis_result = None
    
    # Process analysis if flag is set (happens on next render, preserving tab state)
    if st.session_state.run_ai_analysis:
        st.session_state.run_ai_analysis = False  # Reset flag
        
        ticker = data.get('ticker', 'Unknown')
        
        # Show what's being analyzed
        st.markdown(f"### 🔍 Analyzing {ticker}...")
        
        with st.spinner("🧠 AI models are analyzing... This may take 30-60 seconds..."):
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📊 Aggregating dashboard data...")
            progress_bar.progress(10)
            
            # Aggregate all data
            aggregated_data = analyzer.aggregate_dashboard_data(data)
            
            status_text.text("🤖 Calling AI models in parallel...")
            progress_bar.progress(30)
            
            # Use selected models
            models_to_use = selected_models
            
            # Run async analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    analyzer.analyze_with_all_models(aggregated_data, models_to_use)
                )
            finally:
                loop.close()
            
            status_text.text("📊 Building consensus...")
            progress_bar.progress(80)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store in session state
            st.session_state.ai_analysis_result = result
            st.session_state['ai_analysis_time'] = datetime.now()
            
            # Clear progress indicators to prevent floating
            progress_bar.empty()
            status_text.empty()
    
    # Display Results
    if st.session_state.ai_analysis_result is not None:
        result = st.session_state.ai_analysis_result
        
        st.markdown("---")
        st.markdown("## 📊 AI Analysis Results")
        
        if 'error' in result:
            st.error(f"❌ Analysis failed: {result['error']}")
            if 'details' in result:
                with st.expander("Error Details"):
                    st.json(result['details'])
            return
        
        # Timestamp and model info
        analysis_time = st.session_state.get('ai_analysis_time', datetime.now())
        metadata = result.get('consensus', {}).get('_metadata', {})
        responding = metadata.get('responding_models', [])
        valid_count = metadata.get('valid_models', 0)
        total_count = metadata.get('total_models', 0)
        
        if responding:
            st.caption(f"Generated: {analysis_time.strftime('%Y-%m-%d %H:%M:%S')} | " + 
                      f"✅ Responding: {', '.join(responding)} ({valid_count}/{total_count} models)")
        else:
            st.caption(f"Generated: {analysis_time.strftime('%Y-%m-%d %H:%M:%S')} | " + 
                      f"Models queried: {', '.join([AI_MODELS[m].name for m in result['successful_models']])}")
        
        # Debug: Show raw responses
        with st.expander("🔍 Debug: View Raw Model Responses", expanded=False):
            st.json(result['individual_responses'])
        
        # Display Consensus Summary
        render_consensus_summary(result['consensus'], data)
        
        st.markdown("---")
        
        # Individual Model Responses
        render_individual_model_responses(result['individual_responses'], result['successful_models'])
        
        # Detailed Breakdown
        render_detailed_breakdown(result)
        
        # Export Options
        render_export_options(result, data.get('ticker', 'Unknown'))


def render_consensus_summary(consensus: Dict, data: Dict):
    """Render the weighted consensus summary from all AI models"""
    st.markdown("### 🎯 Consensus Analysis")
    
    # Check if we have valid data
    metadata = consensus.get('_metadata', {})
    if metadata.get('models_with_valuation', 0) == 0:
        responding = metadata.get('responding_models', [])
        if responding:
            st.warning(f"⚠️ Models responded but didn't return structured valuation data. Responding: {', '.join(responding)}")
            st.info("💡 The AI models may need more specific prompting. Check the raw responses below to see what data they provided.")
        else:
            st.warning("⚠️ No AI models returned valid structured data. Check raw responses and API keys below.")
    
    # Consolidated AI Summary (expandable)
    with st.expander("📋 Consolidated AI Summary - What All Models Said", expanded=True):
        st.markdown("### 🤖 Multi-Model Consensus")
        
        responding_models = metadata.get('responding_models', [])
        if responding_models:
            st.success(f"✅ **{len(responding_models)} Model(s) Responded:** {', '.join(responding_models)}")
        
        # Executive summaries from all models
        st.markdown("#### 📝 Executive Summaries")
        for model_id in data.get('successful_models', []):
            model_name = AI_MODELS.get(model_id, type('', (), {'name': model_id})).name
            response = data.get('individual_responses', {}).get(model_id, {})
            
            if isinstance(response, dict) and 'executive_summary' in response:
                st.markdown(f"**{model_name}:**")
                st.markdown(f"> {response['executive_summary']}")
                st.markdown("")
        
        # Assumptions validation consolidated
        st.markdown("#### 🎯 Dashboard Assumptions Validation")
        st.markdown("*AI models' assessment of the dashboard's valuation assumptions:*")
        
        assumptions_feedback = []
        for model_id in data.get('successful_models', []):
            response = data.get('individual_responses', {}).get(model_id, {})
            if isinstance(response, dict) and 'dashboard_assumptions_validation' in response:
                model_name = AI_MODELS.get(model_id, type('', (), {'name': model_id})).name
                validation = response['dashboard_assumptions_validation']
                assumptions_feedback.append((model_name, validation))
        
        if assumptions_feedback:
            for model_name, validation in assumptions_feedback:
                st.markdown(f"**{model_name}'s Assessment:**")
                if 'overall_assessment' in validation:
                    st.info(validation['overall_assessment'])
                
                # DCF assumptions
                if 'dcf_assumptions' in validation:
                    dcf = validation['dcf_assumptions']
                    with st.expander(f"{model_name} - DCF Assumptions Review"):
                        for key, value in dcf.items():
                            st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
        else:
            st.info("Models did not provide assumptions validation. Check individual responses below.")
        
        # Key insights across all models
        st.markdown("#### 💡 Key Insights Across All Models")
        all_insights = []
        for model_id in data.get('successful_models', []):
            response = data.get('individual_responses', {}).get(model_id, {})
            if isinstance(response, dict) and 'action_recommendation' in response:
                rec = response['action_recommendation']
                if 'reasoning' in rec:
                    model_name = AI_MODELS.get(model_id, type('', (), {'name': model_id})).name
                    all_insights.append(f"**{model_name}:** {rec['reasoning']}")
        
        if all_insights:
            for insight in all_insights:
                st.markdown(f"- {insight}")
        else:
            st.info("No consolidated insights available. Models may not have returned structured data.")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fair_value = consensus.get('fair_value', 0)
        current_price = data.get('current_price', 0)
        if fair_value > 0:
            st.metric(
                "Fair Value (Consensus)",
                f"${fair_value:.2f}",
                delta=f"{((fair_value/current_price - 1) * 100):.1f}%" if current_price > 0 else None
            )
        else:
            st.metric("Fair Value", "N/A")
    
    with col2:
        upside = consensus.get('upside_pct', 0)
        st.metric("Upside/Downside", f"{upside:+.1f}%")
    
    with col3:
        conviction = consensus.get('conviction', 0)
        st.metric("Conviction Level", f"{conviction:.0f}/100")
    
    with col4:
        confidence = consensus.get('confidence', 0)
        st.metric("Confidence Score", f"{confidence:.0f}/100")
    
    # Recommendation
    recommendation = consensus.get('recommendation', 'HOLD')
    rec_colors = {
        'Strong Buy': '🟢',
        'Buy': '🟢',
        'Hold': '🟡',
        'Sell': '🔴',
        'Strong Sell': '🔴'
    }
    
    rec_color = rec_colors.get(recommendation, '⚪')
    st.markdown(f"### {rec_color} Recommendation: **{recommendation}**")
    
    # Executive Summary
    st.markdown("#### 📝 Executive Summary")
    st.markdown(consensus.get('executive_summary', 'No summary available'))
    
    # Bull vs Bear Balance
    st.markdown("#### ⚖️ Bull vs Bear Case")
    
    bull_strength = consensus.get('bull_case_strength', 50)
    bear_strength = consensus.get('bear_case_strength', 50)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[bull_strength],
        y=['Probability'],
        name='Bull Case',
        orientation='h',
        marker=dict(color='#00cc00'),
        text=[f'{bull_strength:.0f}%'],
        textposition='inside'
    ))
    
    fig.add_trace(go.Bar(
        x=[bear_strength],
        y=['Probability'],
        name='Bear Case',
        orientation='h',
        marker=dict(color='#ff3333'),
        text=[f'{bear_strength:.0f}%'],
        textposition='inside'
    ))
    
    fig.update_layout(
        barmode='group',
        height=150,
        showlegend=True,
        xaxis_title="Probability (%)",
        yaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Model Agreement
    if 'model_agreement' in consensus and consensus['model_agreement']:
        with st.expander("📊 Model Agreement Metrics"):
            agreement = consensus['model_agreement']
            
            if 'fair_value_std_dev' in agreement:
                st.metric("Fair Value Std Dev", f"${agreement['fair_value_std_dev']:.2f}")
            
            if 'fair_value_range' in agreement:
                low, high = agreement['fair_value_range']
                st.metric("Fair Value Range", f"${low:.2f} - ${high:.2f}")


def render_individual_model_responses(responses: Dict, successful_models: List[str]):
    """Display individual AI model responses in expandable sections"""
    st.markdown("### 🤖 Individual AI Model Insights")
    
    for model_id in successful_models:
        config = AI_MODELS[model_id]
        response = responses[model_id]
        
        with st.expander(f"{config.name} Analysis (Weight: {config.weight*100:.0f}%)", expanded=False):
            if 'error' in response:
                st.error(f"Error: {response['error']}")
                continue
            
            # Valuation
            if 'valuation_analysis' in response:
                st.markdown("#### 💰 Valuation")
                val = response['valuation_analysis']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fair Value", f"${val.get('fair_value_estimate', 0):.2f}")
                with col2:
                    st.metric("Upside", f"{val.get('upside_downside_pct', 0):+.1f}%")
                with col3:
                    st.write(f"**Method:** {val.get('valuation_method_used', 'N/A')}")
                
                st.write(val.get('reasoning', ''))
            
            # Action Recommendation
            if 'action_recommendation' in response:
                st.markdown("#### 🎯 Recommendation")
                action = response['action_recommendation']
                
                st.success(f"**{action.get('decision', 'N/A')}** (Conviction: {action.get('conviction_level', 0)}/100)")
                st.write(action.get('reasoning', ''))
            
            # Bull/Bear Cases
            cols = st.columns(2)
            
            with cols[0]:
                if 'bull_case' in response:
                    st.markdown("#### 📈 Bull Case")
                    bull = response['bull_case']
                    st.success(f"Probability: {bull.get('probability', 0)}%")
                    for arg in bull.get('arguments', []):
                        st.write(f"✅ {arg}")
            
            with cols[1]:
                if 'bear_case' in response:
                    st.markdown("#### 📉 Bear Case")
                    bear = response['bear_case']
                    st.error(f"Probability: {bear.get('probability', 0)}%")
                    for arg in bear.get('arguments', []):
                        st.write(f"❌ {arg}")
            
            # Devil's Advocate
            if 'devils_advocate' in response:
                st.markdown("#### 😈 Devil's Advocate")
                devil = response['devils_advocate']
                
                st.markdown("**Critical Analysis**")
                st.write("**Critique of Bull Case:**")
                st.write(devil.get('critique_of_bull_case', ''))
                
                st.write("**Critique of Bear Case:**")
                st.write(devil.get('critique_of_bear_case', ''))
                
                if 'overlooked_factors' in devil:
                    st.write("**Overlooked Factors:**")
                    for factor in devil['overlooked_factors']:
                        st.write(f"• {factor}")


def render_detailed_breakdown(result: Dict):
    """Render detailed breakdown of all analysis components"""
    st.markdown("### 📊 Detailed Analysis Breakdown")
    
    # Get first successful response for detailed data
    successful_models = result.get('successful_models', [])
    if not successful_models:
        return
    
    first_model = successful_models[0]
    response = result['individual_responses'][first_model]
    
    tabs = st.tabs([
        "📈 Technical",
        "📊 Options",
        "💬 Sentiment",
        "⚠️ Risks",
        "🎯 Catalysts",
        "💡 Suggestions"
    ])
    
    # Technical Analysis Tab
    with tabs[0]:
        if 'technical_analysis' in response:
            tech = response['technical_analysis']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Trend & Momentum")
                st.write(f"**Trend:** {tech.get('trend', 'N/A')}")
                st.write(f"**Momentum Score:** {tech.get('momentum_score', 0)}/100")
                st.write(f"**Pattern:** {tech.get('pattern_recognition', 'N/A')}")
            
            with col2:
                st.markdown("#### Outlook")
                st.write(f"**Short-term:** {tech.get('short_term_outlook', 'N/A')}")
                st.write(f"**Medium-term:** {tech.get('medium_term_outlook', 'N/A')}")
            
            if 'key_levels' in tech:
                levels = tech['key_levels']
                st.write("**Support Levels:**", levels.get('support', []))
                st.write("**Resistance Levels:**", levels.get('resistance', []))
    
    # Options Tab
    with tabs[1]:
        if 'options_insights' in response:
            opts = response['options_insights']
            
            st.write(f"**Market Expectation:** {opts.get('market_expectation', 'N/A')}")
            st.write(f"**Delta Bias:** {opts.get('delta_bias', 'N/A')}")
            st.write(f"**Implied vs Realized Vol:** {opts.get('implied_vs_realized_vol', 'N/A')}")
            st.write(f"**Gamma Risk:** {opts.get('gamma_risk', 'N/A')}")
            
            if 'key_strikes' in opts:
                st.write("**Key Strike Levels:**", opts['key_strikes'])
    
    # Sentiment Tab
    with tabs[2]:
        if 'sentiment_score' in response:
            sent = response['sentiment_score']
            
            overall = sent.get('overall_sentiment', 0)
            st.metric("Overall Sentiment", f"{overall:+.0f}", 
                     help="Scale: -100 (Very Bearish) to +100 (Very Bullish)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Retail:** {sent.get('retail_sentiment', 'N/A')}")
                st.write(f"**Insider Signal:** {sent.get('insider_signal', 'N/A')}")
            
            with col2:
                st.write(f"**Institutional:** {sent.get('institutional_positioning', 'N/A')}")
                st.write(f"**Contrarian View:** {sent.get('contrarian_view', 'N/A')}")
    
    # Risks Tab
    with tabs[3]:
        if 'risk_assessment' in response:
            risk = response['risk_assessment']
            
            st.error(f"**Risk Level:** {risk.get('risk_level', 'N/A')}")
            
            st.write("**Key Risks:**")
            for r in risk.get('key_risks', []):
                st.write(f"⚠️ {r}")
            
            st.write("**Black Swan Scenarios:**")
            for scenario in risk.get('black_swan_scenarios', []):
                st.write(f"🦢 {scenario}")
            
            st.write("**Hedging Suggestions:**")
            st.info(risk.get('hedging_suggestions', 'N/A'))
    
    # Catalysts Tab
    with tabs[4]:
        if 'catalysts' in response:
            cat = response['catalysts']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("**Positive Catalysts:**")
                for c in cat.get('positive_catalysts', []):
                    st.write(f"✅ {c}")
            
            with col2:
                st.error("**Negative Catalysts:**")
                for c in cat.get('negative_catalysts', []):
                    st.write(f"❌ {c}")
            
            st.write(f"**Timeline:** {cat.get('timeline', 'N/A')}")
            st.write(f"**Probability-Weighted Impact:** {cat.get('probability_weighted_impact', 'N/A')}")
    
    # Suggestions Tab
    with tabs[5]:
        if 'suggested_adjustments' in response:
            sugg = response['suggested_adjustments']
            
            st.markdown("**Model Refinements:**")
            for ref in sugg.get('model_refinements', []):
                st.write(f"• {ref}")
            
            st.markdown("**Additional Data to Collect:**")
            for data in sugg.get('data_to_collect', []):
                st.write(f"• {data}")
            
            st.markdown("**Assumptions to Revisit:**")
            for assume in sugg.get('assumptions_to_revisit', []):
                st.write(f"• {assume}")


def render_export_options(result: Dict, ticker: str):
    """Render export options for AI analysis"""
    st.markdown("---")
    st.markdown("### 💾 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export to JSON", use_container_width=True):
            json_str = json.dumps(result, indent=2, default=str)
            st.download_button(
                "Download JSON",
                data=json_str,
                file_name=f"{ticker}_ai_analysis_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Export Summary (TXT)", use_container_width=True):
            summary = generate_text_summary(result, ticker)
            st.download_button(
                "Download TXT",
                data=summary,
                file_name=f"{ticker}_ai_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.info("Summary copied! (Simulated - use browser extension for real clipboard access)")


def generate_text_summary(result: Dict, ticker: str) -> str:
    """Generate a text summary of AI analysis for export"""
    consensus = result.get('consensus', {})
    
    summary = f"""
AI ANALYSIS REPORT - {ticker}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Models: {', '.join([AI_MODELS[m].name for m in result.get('successful_models', [])])}

{'='*80}
CONSENSUS SUMMARY
{'='*80}

Fair Value: ${consensus.get('fair_value', 0):.2f}
Upside/Downside: {consensus.get('upside_pct', 0):+.1f}%
Recommendation: {consensus.get('recommendation', 'N/A')}
Conviction: {consensus.get('conviction', 0):.0f}/100
Confidence: {consensus.get('confidence', 0):.0f}/100

{'='*80}
EXECUTIVE SUMMARY
{'='*80}

{consensus.get('executive_summary', 'N/A')}

{'='*80}
BULL VS BEAR
{'='*80}

Bull Case Strength: {consensus.get('bull_case_strength', 0):.0f}%
Bear Case Strength: {consensus.get('bear_case_strength', 0):.0f}%

{'='*80}
END OF REPORT
{'='*80}
"""
    
    return summary


def check_and_run_global_ai():
    """
    Check if analysis button was clicked and display results.
    Called from dashboard tabs to show analysis panel.
    """
    # The button is rendered in render_floating_ai_button()
    # Results are displayed via render_ai_analysis_panel() when data is available
    
    # Get current ticker data from session state
    data = st.session_state.get('data', {})
    
    if data and not data.get('error'):
        # Render the analysis panel
        render_ai_analysis_panel(data)
    else:
        st.info("""
        **No data available for AI analysis**
        
        Load a stock ticker first to enable global AI analysis.
        """)
