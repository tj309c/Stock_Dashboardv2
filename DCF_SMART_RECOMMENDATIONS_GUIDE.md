# DCF Smart Recommendations Guide

## Overview

The **AI-Powered Smart Recommendations** feature analyzes a company's historical performance, industry benchmarks, and fundamental characteristics to suggest optimal DCF input parameters. This helps users make informed valuation decisions based on data rather than guesswork.

---

## How It Works

### 1. **Historical Analysis**
- Calculates 5-year Revenue CAGR (Compound Annual Growth Rate)
- Analyzes recent revenue growth trends
- Evaluates earnings growth consistency
- Compares current vs. historical margins

### 2. **Industry Benchmarks**
The system uses sector-specific benchmarks for 11 major industries:

| Sector | Growth Rate | EBIT Margin | CapEx % | ROIC | Terminal Growth |
|--------|-------------|-------------|---------|------|-----------------|
| **Technology** | 15% | 25% | 5% | 20% | 3% |
| **Healthcare** | 12% | 20% | 6% | 18% | 3% |
| **Consumer Cyclical** | 8% | 12% | 8% | 12% | 2.5% |
| **Consumer Defensive** | 6% | 10% | 6% | 15% | 2.5% |
| **Financial Services** | 10% | 25% | 3% | 12% | 3% |
| **Industrials** | 8% | 12% | 10% | 14% | 2.5% |
| **Energy** | 5% | 15% | 15% | 10% | 2% |
| **Utilities** | 4% | 18% | 12% | 8% | 2% |
| **Real Estate** | 6% | 30% | 8% | 10% | 2.5% |
| **Communication Services** | 10% | 20% | 8% | 15% | 3% |
| **Basic Materials** | 6% | 12% | 12% | 12% | 2.5% |

### 3. **Company Size Adjustment**
Growth expectations are adjusted based on market capitalization:
- **Small Cap (<$2B)**: +20% growth multiplier (higher growth potential)
- **Mid Cap ($2B-$10B)**: +10% growth multiplier
- **Large Cap ($10B-$200B)**: Standard growth
- **Mega Cap (>$200B)**: -20% growth multiplier (limited runway)

### 4. **Growth Fade Logic**
Recommendations include intelligent growth fade over the 5-year projection:
- **Year 1**: Starts close to recent growth (adjusted for size)
- **Years 2-4**: Gradual linear fade toward industry average
- **Year 5**: Approaches industry benchmark growth rate

**Example for a mid-cap tech company:**
- Historical CAGR: 18%
- Recent growth: 22%
- Size-adjusted start: ~23% (22% × 1.1)
- Industry benchmark: 15%
- **Recommended forecast**: 23% → 20% → 18% → 16% → 15%

---

## Key Recommendations Explained

### **Revenue Growth Rates**
**How It's Calculated:**
```
Starting Growth = (Recent Growth × 70% + Historical CAGR × 30%) × Size Multiplier
Year N Growth = Starting Growth × (1 - Fade Factor) + Industry Growth × Fade Factor
```

**Confidence Indicators:**
- ✅ **Consistent**: Recent ≈ Historical CAGR (within 3%)
- ⚠️ **Accelerating**: Recent > 1.5× CAGR (may not sustain)
- ⚠️ **Slowing**: Recent < 0.5× CAGR (conservative forecast)

---

### **EBIT Margin**
**Uses:**
1. Company's actual operating margin (if available)
2. Industry average (if company data is missing or abnormal)

**Confidence Indicators:**
- ✅ **Premium**: Margin > 120% of industry average
- ⚠️ **Below Average**: Margin < 80% of industry average
- ✅ **In-Line**: Within ±20% of industry average

**Terminal Margin**: Set to 90% of industry average for conservatism

---

### **ROIC (Return on Invested Capital)**
**Calculation Priority:**
1. **From Balance Sheet**: NOPAT ÷ Invested Capital
2. **From ROE**: Adjusted for capital structure
3. **Industry Default**: 15% if data unavailable

**Formula:**
```
NOPAT = EBIT × (1 - Tax Rate)
Invested Capital = Total Debt + Total Equity - Cash
ROIC = NOPAT ÷ Invested Capital
```

**Used For**: Intelligent CapEx calculation when enabled
```
CapEx = (Revenue Growth × Revenue) ÷ ROIC
```

---

### **Cost of Debt**
**Calculation Methods:**
1. **Direct**: Interest Expense ÷ Total Debt
2. **Credit Rating Proxy**: Based on interest coverage ratio

| Interest Coverage | Rating | Cost of Debt |
|-------------------|--------|--------------|
| > 8× | AAA/AA | 4% |
| 6-8× | A | 5% |
| 4-6× | BBB | 6% |
| 2.5-4× | BB | 8% |
| 1.5-2.5× | B | 10% |
| < 1.5× | CCC | 15% |

**Default**: 6% (typical investment-grade corporate bond)

---

### **WACC (Weighted Average Cost of Capital)**
**Automatically Calculated When Advanced Mode Enabled:**

```
Cost of Equity = Risk-Free Rate + (Beta × Market Risk Premium)
After-Tax Cost of Debt = Cost of Debt × (1 - Tax Rate)
WACC = (E/V × Cost of Equity) + (D/V × After-Tax Cost of Debt)
```

**Smart Defaults:**
- **Risk-Free Rate**: 4.5% (current 10-year Treasury proxy)
- **Beta**: From company data (clamped 0.5-2.5)
- **Market Risk Premium**: 7% (historical average)
- **Cost of Debt**: Estimated from financials

---

### **CapEx & Net Working Capital**
**Industry-Specific Defaults:**
- **Asset-Heavy (Energy, Utilities)**: 12-15% CapEx
- **Asset-Light (Tech, Financial)**: 3-5% CapEx
- **Manufacturing (Industrials)**: 8-10% CapEx

**NWC Adjustments:**
- **High Inventory (Retail)**: 12-15% NWC
- **Low Inventory (Services)**: 5-8% NWC

---

### **Terminal Growth Rate**
**Based on Long-Term Economic Expectations:**
- **High-Growth Sectors** (Tech, Healthcare): 3%
- **Moderate Growth** (Industrials, Consumer): 2.5%
- **Mature/Cyclical** (Utilities, Energy): 2%

**Conservative Limit**: Never exceeds WACC × 0.9

---

## Confidence Notes Explained

### Growth Confidence
- ✅ **"Consistent growth"**: CAGR and recent growth align (reliable projection)
- ⚠️ **"Accelerating growth"**: Recent >> CAGR (may be temporary, use caution)
- ⚠️ **"Slowing growth"**: Recent << CAGR (conservative assumptions applied)

### Size Impact
- ✅ **"Small cap - higher growth potential"**: Can grow faster but riskier
- ⚠️ **"Mega cap - limited growth runway"**: Law of large numbers applies
- ✅ **"Mid/Large cap - balanced"**: Stable growth expectations

### Margin Confidence
- ✅ **"Premium margins"**: Sustainable competitive advantage
- ⚠️ **"Below-average margins"**: May face operational challenges
- ✅ **"In-line with industry"**: Typical for sector

---

## When to Override Recommendations

### **Override Growth Rates When:**
1. Company has announced major new product launches
2. Entering new markets not reflected in historical data
3. Undergoing significant restructuring
4. Industry disruption expected (up or down)

### **Override Margins When:**
1. Recent margin expansion from operational improvements
2. Known cost-cutting initiatives underway
3. Pricing power changes (e.g., monopoly position)
4. Temporary margin compression from investments

### **Override ROIC/CapEx When:**
1. Company shifting to asset-light model
2. Major factory/infrastructure buildout planned
3. R&D intensity changing significantly
4. Acquisition-heavy growth strategy

### **Override Terminal Growth When:**
1. Industry facing structural decline (e.g., legacy media)
2. Secular tailwinds (e.g., cloud computing, renewable energy)
3. Regulatory changes expected

---

## Example Walkthrough: Apple Inc. (AAPL)

**Company Profile:**
- Sector: Technology
- Market Cap: $3.0 Trillion (Mega Cap)
- Historical Revenue CAGR (5Y): 9%
- Recent Revenue Growth: 2%
- Operating Margin: 30%

**Smart Recommendations:**
```
Growth Rates:
  Year 1: 4.5%  (Recent 2% × 70% + CAGR 9% × 30%) × 0.8 mega cap adjustment
  Year 2: 5.2%
  Year 3: 6.8%
  Year 4: 9.5%
  Year 5: 12.0%  → Fading toward industry 15% (conservative due to size)

EBIT Margin: 30% (actual, well above 25% industry avg)
Terminal Margin: 22.5% (fade to 90% of industry avg)

ROIC: 45% (calculated from balance sheet - excellent capital efficiency)
CapEx: 3.5% (asset-light business model)
Terminal Growth: 2.5% (mega cap, mature market)
```

**Confidence Notes:**
- ⚠️ **Slowing growth** (recent 2% vs 9% CAGR) - iPhone market saturation
- ⚠️ **Mega cap** - limited growth runway, law of large numbers
- ✅ **Premium margins** (30% vs 25% industry) - ecosystem moat

**Interpretation:**
The smart system recognizes Apple's growth deceleration but maintains conservative projections. Premium margins reflect durable competitive advantages. Users should consider:
- Services growth acceleration (not in revenue CAGR)
- India/emerging markets expansion
- New product categories (Vision Pro, Automotive?)

---

## Tips for Best Results

### 1. **Always Review the Rationale**
Don't blindly accept recommendations. Expand the "View Smart Recommendations Rationale" section to understand the logic.

### 2. **Cross-Check with Management Guidance**
Compare smart recommendations against company's forward guidance on earnings calls.

### 3. **Adjust for Non-Recurring Events**
Remove one-time charges, acquisitions, or divestitures from historical data mentally.

### 4. **Use Scenario Analysis**
Run bear/base/bull cases with different assumptions to understand valuation range.

### 5. **Sanity Check Terminal Value**
If Terminal Value > 80% of Enterprise Value, your terminal growth may be too high relative to WACC.

### 6. **Compare to Analyst Estimates**
Check if your growth assumptions align with Wall Street consensus (or understand why they differ).

---

## Advanced: How the Algorithm Adapts

### For High-Growth Companies (e.g., NVIDIA, Tesla)
- Recognizes recent acceleration
- Allows higher starting growth rates
- Fades more aggressively (higher risk of normalization)
- Uses higher ROIC assumptions

### For Mature Companies (e.g., Coca-Cola, P&G)
- Limits growth to GDP+ ranges
- Focuses on margin stability
- Lower terminal growth rates
- Dividend sustainability checks

### For Cyclical Companies (e.g., Airlines, Commodities)
- Smooths revenue volatility
- Uses mid-cycle margins
- Conservative terminal assumptions
- Higher cost of capital

### For Turnaround Stories (e.g., recovering companies)
- Weights recent trends more heavily if improving
- Allows margin expansion scenarios
- Flags high uncertainty in notes

---

## Limitations & Disclaimers

### **What Smart Recommendations CAN'T Predict:**
- ❌ Major M&A activity
- ❌ Regulatory changes or lawsuits
- ❌ Technological disruption
- ❌ Management changes
- ❌ Macroeconomic shocks
- ❌ Black swan events

### **Data Quality Dependencies:**
- Requires historical financial statements (min 2 years)
- Accuracy depends on Yahoo Finance data quality
- Industry classifications may be broad

### **User Responsibility:**
Smart recommendations are a **starting point**, not a final answer. Professional investors:
1. Build custom models for each company
2. Conduct proprietary research
3. Adjust for qualitative factors
4. Stress test assumptions
5. Update models quarterly

---

## Comparison to Professional Analysts

### **What You Get (Smart Recommendations):**
✅ Sector-specific benchmarks
✅ Historical trend analysis
✅ Size-adjusted growth expectations
✅ Intelligent fade logic
✅ Automated ROIC/WACC calculations

### **What Sell-Side Analysts Add:**
- Company-specific product cycle forecasts
- Customer channel checks
- Supplier/competitor intelligence
- Management access and guidance
- Proprietary surveys and data
- Industry expert networks

### **Your Edge as a Retail Investor:**
- No conflicts of interest (analysts may have banking relationships)
- Longer time horizon (no quarterly pressure)
- Ability to focus on select companies deeply
- Access to same financial data
- Can update models in real-time

---

## Next Steps

1. **Enable Smart Recommendations** for a stock you know well
2. **Review the rationale** and see if it matches your understanding
3. **Make adjustments** where you have better information
4. **Run scenario analysis** to understand valuation sensitivity
5. **Compare results** to current market price
6. **Document your thesis** (why you agree/disagree with assumptions)

---

## Feature Roadmap

**Coming Soon:**
- [ ] Peer comparison overlay (show where company ranks vs. competitors)
- [ ] Historical DCF accuracy tracking (how did past projections perform?)
- [ ] Earnings call integration (auto-update assumptions from guidance)
- [ ] Analyst consensus integration (compare to Wall Street)
- [ ] Custom industry benchmark creation
- [ ] ML-powered growth predictions
- [ ] Sentiment-adjusted forecasts

---

**Built with data-driven insights to empower informed investment decisions.**
