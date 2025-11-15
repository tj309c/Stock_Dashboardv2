# Interactive DCF Calculator - User Guide

## Overview

The Interactive DCF (Discounted Cash Flow) Calculator is a powerful tool that allows you to:
- Adjust valuation assumptions in real-time
- See immediate impact on enterprise value
- Run Monte Carlo simulations for probability analysis
- Perform sensitivity analysis on key variables
- Compare Bear/Base/Bull scenarios side-by-side

## Getting Started

### Accessing the Calculator

1. Launch the app: `streamlit run main.py`
2. Navigate to the **Stocks Dashboard**
3. Enter a ticker symbol (e.g., "AAPL", "TSLA", "META")
4. Click "🔍 Analyze"
5. Click on the **"🎛️ Interactive DCF"** tab

## Tab 1: Interactive DCF

### What You'll See

The Interactive DCF tab shows:
- **7 Adjustable Sliders** for key valuation parameters
- **Real-time Fair Value** updates as you move sliders
- **Enterprise Value** and **Equity Value** calculations
- **Detailed Breakdown** of all intermediate steps
- **Visual Cash Flow Charts** showing projections

### The Sliders

#### 1. Growth Rate (Projection Period)
- **Range:** 0% to 50%
- **Default:** 10%
- **What it means:** Expected annual growth rate for free cash flow during the projection period
- **Rule of thumb:**
  - 0-5%: Mature, stable companies
  - 5-15%: Moderate growth companies
  - 15-30%: High-growth companies
  - 30%+: Hyper-growth (be conservative!)

#### 2. WACC (Discount Rate)
- **Range:** 5% to 20%
- **Default:** 10%
- **What it means:** Weighted Average Cost of Capital - the rate used to discount future cash flows
- **Rule of thumb:**
  - 5-8%: Large-cap, stable, low-risk companies
  - 8-12%: Mid-cap, moderate risk
  - 12-20%: Small-cap, high-risk, or speculative

#### 3. Terminal Growth Rate
- **Range:** 0% to 5%
- **Default:** 2.5%
- **What it means:** Perpetual growth rate after the projection period (forever)
- **Rule of thumb:**
  - Should be ≤ long-term GDP growth (typically 2-3%)
  - Conservative: 2-2.5%
  - Aggressive: 3-4% (rarely justified)
  - **MUST be less than WACC** or calculation will error

#### 4. Projection Years
- **Range:** 3 to 10 years
- **Default:** 5 years
- **What it means:** Number of years to explicitly project cash flows
- **Rule of thumb:**
  - 5 years: Standard for most companies
  - 3 years: Highly uncertain or cyclical industries
  - 7-10 years: Very stable, predictable businesses

### Understanding the Results

#### Fair Value per Share
- The calculated intrinsic value based on your assumptions
- Compare to **Current Price** to see if stock is undervalued or overvalued
- **Upside/Downside %** shows potential gain or loss

#### Enterprise Value (EV)
- Total value of the business (debt + equity)
- Represents what you'd pay to buy the entire company

#### Equity Value
- Value belonging to shareholders
- Formula: Enterprise Value + Cash - Debt

### Detailed Breakdown

Click **"📋 Detailed DCF Breakdown"** to see:

1. **Cash Flow Projections Table**
   - Year-by-year projected cash flows
   - Discount factors applied
   - Present value of each year's cash flow

2. **Terminal Value Calculation**
   - Terminal cash flow (Year 5 × terminal growth)
   - Terminal value (using perpetuity formula)
   - Present value of terminal value

3. **Value Bridge**
   - Step-by-step walkthrough from EV to fair value per share
   - Shows impact of cash and debt adjustments

## Tab 2: Monte Carlo Simulation

### What is Monte Carlo Simulation?

Instead of using single values for growth, WACC, and terminal growth, Monte Carlo simulation:
- Runs thousands of scenarios with random variations
- Assumes parameters follow a normal distribution (bell curve)
- Shows the range of possible outcomes
- Calculates probability of different fair values

### How to Use

#### Step 1: Set Mean Parameters
- **Growth Rate (Mean):** Your base case growth assumption
- **WACC (Mean):** Your base case discount rate
- **Terminal Growth (Mean):** Your base case terminal growth

#### Step 2: Set Standard Deviations
- **Growth Rate (Std Dev):** How much growth could vary (e.g., 3% = ±3%)
- **WACC (Std Dev):** Uncertainty in discount rate
- **Terminal Growth (Std Dev):** Uncertainty in long-term growth

**Example:**
- If you expect 10% growth but it could range from 7% to 13%:
  - Mean: 10%
  - Std Dev: ~3% (68% of values will be within 7-13%)

#### Step 3: Choose Number of Simulations
- **100:** Quick test (5 seconds)
- **1,000:** Standard analysis (10 seconds)
- **5,000:** More precise (30 seconds)
- **10,000:** Very precise (1 minute)

#### Step 4: Click "🚀 Run Monte Carlo Simulation"

### Interpreting Results

#### Summary Statistics
- **Mean Fair Value:** Average across all simulations
- **Median Fair Value:** Middle value (less affected by outliers)
- **Std Deviation:** How spread out the results are

#### Confidence Intervals
- **50% CI:** There's a 50% chance fair value is in this range (narrow)
- **80% CI:** There's an 80% chance (moderate)
- **90% CI:** There's a 90% chance (wide)

#### Distribution Chart
- Shows histogram of all fair value outcomes
- **Current Price Line (Red):** Where the stock trades now
- **Mean Line (Green):** Average fair value from simulations

**What to look for:**
- If current price is far left of distribution → Likely undervalued
- If current price is far right → Likely overvalued
- If current price is in the middle → Fairly valued

#### Percentiles
- **5th percentile:** Worst-case scenario (95% of outcomes are better)
- **50th percentile:** Median outcome
- **95th percentile:** Best-case scenario (95% of outcomes are worse)

## Tab 3: Sensitivity Analysis

### What is Sensitivity Analysis?

Shows how fair value changes when you vary ONE parameter while keeping others constant. Helps you understand which assumptions matter most.

### One-Way Sensitivity

#### Step 1: Set Base Parameters
- Growth Rate
- WACC
- Terminal Growth
- Projection Years

#### Step 2: Choose Variable to Analyze
- **Growth Rate:** See impact of different growth assumptions
- **WACC:** See impact of different discount rates
- **Terminal Growth:** See impact of different terminal assumptions

#### Step 3: Click "📊 Run Sensitivity Analysis"

#### Interpreting the Chart
- **X-axis:** The parameter you're varying
- **Y-axis:** Resulting fair value
- **Red Dashed Line:** Current stock price

**What to look for:**
- **Steep slope:** Fair value is very sensitive to this parameter
- **Flat slope:** Fair value is less sensitive
- **Where line crosses current price:** Implied assumption in market

**Example:**
If fair value line crosses current price at 15% growth:
- Market is pricing in 15% growth
- If you believe growth will be higher → Undervalued
- If you believe growth will be lower → Overvalued

### Two-Way Sensitivity Matrix

Shows fair value for combinations of two parameters (Growth Rate vs WACC).

#### Interpreting the Heatmap
- **Green:** High fair values (bullish)
- **Yellow:** Moderate fair values
- **Red:** Low fair values (bearish)
- **Each cell:** Fair value for that combination

**How to use:**
1. Find your base case assumptions
2. Look at adjacent cells to see margin of safety
3. If most cells are green → More confident in valuation
4. If mix of colors → High uncertainty

## Tab 4: Scenario Comparison

### Pre-Built Scenarios

The tool provides three pre-built scenarios:

#### 🐻 Bear Case (Pessimistic)
- **Growth:** 5% (slow growth)
- **WACC:** 12% (higher risk premium)
- **Terminal Growth:** 1.5% (below long-term average)

#### 📊 Base Case (Realistic)
- **Growth:** 10% (moderate growth)
- **WACC:** 10% (market average)
- **Terminal Growth:** 2.5% (in line with GDP)

#### 🚀 Bull Case (Optimistic)
- **Growth:** 20% (high growth)
- **WACC:** 8% (lower risk premium)
- **Terminal Growth:** 3.5% (above average)

### Customizing Scenarios

Click **"🎛️ Customize Scenarios"** to adjust assumptions for each scenario.

### Side-by-Side Comparison

The comparison shows:
- **Fair Value** for each scenario
- **Upside/Downside %** vs current price
- **Enterprise Value** for each scenario
- **Visual Charts** for easy comparison

### How to Use Scenarios

1. **Bear Case < Current Price < Bull Case:**
   - Stock is fairly valued in base case
   - Consider buy if closer to bear case
   - Consider sell if closer to bull case

2. **All Scenarios > Current Price:**
   - Stock may be undervalued
   - Even in pessimistic scenario, fair value is higher
   - Higher confidence in upside

3. **All Scenarios < Current Price:**
   - Stock may be overvalued
   - Even in optimistic scenario, fair value is lower
   - Consider reducing position

## Best Practices

### 1. Start Conservative
- Use conservative assumptions first
- Gradually increase if you have conviction
- If even conservative scenario shows upside → Stronger buy signal

### 2. Focus on Range, Not Point Estimate
- Fair value is a range, not a single number
- Use Monte Carlo to understand probability distribution
- Consider margin of safety (buy at 20-30% discount to fair value)

### 3. Sensitivity Analysis Shows Key Drivers
- Identify which assumptions matter most
- Focus research on those key drivers
- If fair value is very sensitive to growth, spend time on growth forecasts

### 4. Compare to Market Multiples
- If your DCF fair value is very different from P/E-based valuation:
  - Either you found mispricing OR
  - Your assumptions are too aggressive/conservative
- Cross-check with other valuation methods

### 5. Document Your Assumptions
- Write down WHY you chose each assumption
- Review quarterly as company reports earnings
- Adjust model as fundamentals change

## Common Mistakes to Avoid

### ❌ Mistake 1: Terminal Growth > Long-term GDP
**Why it's wrong:** No company can grow faster than the economy forever.
**Fix:** Keep terminal growth at 2-3% maximum.

### ❌ Mistake 2: Using Same Growth Rate for 10 Years
**Why it's wrong:** Growth rates naturally decline as companies mature.
**Fix:** Use higher growth early, then declining growth, or shorter projection period.

### ❌ Mistake 3: Ignoring Capital Structure
**Why it's wrong:** High debt reduces equity value.
**Fix:** Check debt levels on balance sheet. High debt = higher risk = higher WACC.

### ❌ Mistake 4: Extrapolating Recent Growth Forever
**Why it's wrong:** High growth is hard to sustain. Mean reversion happens.
**Fix:** Use industry average or slightly above, not recent peak growth.

### ❌ Mistake 5: Not Comparing to Current Price
**Why it's wrong:** Valuation is relative, not absolute.
**Fix:** Always compare fair value to current price and consider margin of safety.

## Real-World Example

Let's value Apple (AAPL) as an example:

### Step 1: Base Case Assumptions
- **Growth Rate:** 8% (mature tech company, stable)
- **WACC:** 9% (low risk, strong balance sheet)
- **Terminal Growth:** 2.5% (GDP growth)
- **Projection Years:** 5

### Step 2: Run Interactive DCF
Suppose we get:
- **Fair Value:** $185/share
- **Current Price:** $170/share
- **Upside:** 8.8%

### Step 3: Monte Carlo (1,000 simulations)
- **Mean Fair Value:** $188/share
- **50% CI:** [$175, $195]
- **90% CI:** [$160, $210]

**Interpretation:** Even in 95th percentile worst case ($160), downside is limited. Upside to mean is $18/share (10.6%).

### Step 4: Sensitivity Analysis (WACC)
- At 7% WACC: Fair value = $210 (optimistic)
- At 9% WACC: Fair value = $185 (base)
- At 11% WACC: Fair value = $165 (pessimistic)

**Interpretation:** Fair value is sensitive to WACC. Need to be confident in risk assessment.

### Step 5: Scenario Comparison
- **Bear:** $155/share (still near current price)
- **Base:** $185/share (8.8% upside)
- **Bull:** $220/share (29% upside)

**Interpretation:** Asymmetric risk/reward. Downside to bear case is 9%, upside to bull case is 29%. Favorable odds.

### Decision: BUY ✅
- Base case shows 8.8% upside
- Even bear case doesn't have significant downside
- Bull case has strong upside potential
- Monte Carlo confirms base case is reasonable
- Sensitivity analysis shows assumptions are achievable

## Frequently Asked Questions

### Q: Where does base cash flow come from?
**A:** The calculator automatically extracts free cash flow from the company's financial statements. If not available, it estimates from operating cash flow or net income.

### Q: Can I input my own cash flow?
**A:** Currently, base cash flow is auto-calculated. Future versions may allow manual input.

### Q: Why is my fair value very different from analyst targets?
**A:** Different assumptions lead to different valuations. Analysts may use different growth rates, discount rates, or valuation methods. Use this as one input, not the only input.

### Q: Should I use DCF for all companies?
**A:** DCF works best for:
- ✅ Mature companies with stable cash flows
- ✅ Companies with predictable business models
- ❌ Startups or pre-profit companies (use comparable multiples)
- ❌ Financial companies (use P/B or dividend discount model)
- ❌ Highly cyclical industries (average cycle cash flows)

### Q: What if I don't know what WACC to use?
**A:** Start with 10% for most companies. Adjust based on:
- Lower WACC (8-9%): Large-cap, low debt, stable
- Higher WACC (11-15%): Small-cap, high debt, volatile

### Q: How often should I update my valuation?
**A:** 
- **Quarterly:** After earnings reports
- **As needed:** If major company or industry news
- **Annually:** Full model refresh

### Q: What's a good margin of safety?
**A:**
- Conservative: 30-40% discount to fair value
- Moderate: 20-30% discount
- Aggressive: 10-20% discount

### Q: Can I export my analysis?
**A:** Currently, you can screenshot results. Export to PDF is planned for future release.

## Tips for Advanced Users

### 1. Adjust Terminal Value Calculation
Terminal value typically represents 70-80% of enterprise value. If it's >90%, your terminal growth is too high or projection period is too short.

### 2. Use Historical Cash Flow Growth
Look at past 5 years of cash flow growth. If company grew at 12% historically, projecting 25% growth needs strong justification.

### 3. Cross-Check with Other Metrics
- **P/E Ratio:** Implied P/E = Fair Value ÷ EPS
- **EV/EBITDA:** Compare to industry average
- **P/FCF:** Compare to historical average

### 4. Stress Test Your Assumptions
- What if growth is 50% lower than expected?
- What if WACC is 2% higher due to rates?
- Monte Carlo helps with this automatically

### 5. Consider Qualitative Factors
DCF is quantitative, but also consider:
- Management quality
- Competitive moat
- Industry tailwinds/headwinds
- Regulatory risks

## Keyboard Shortcuts

- **Tab:** Navigate between sliders
- **Arrow Keys:** Fine-tune slider values
- **Ctrl+R:** Refresh data (browser)
- **Ctrl+Click:** Open expandable sections

## Getting Help

If you encounter issues:
1. Check that ticker symbol is valid
2. Verify company has cash flow data available
3. Ensure WACC > Terminal Growth
4. Check error messages in UI
5. Review DEBUGGING_REPORT.md for known issues

## Related Documentation

- **README.md** - Project overview and setup
- **DEBUGGING_REPORT.md** - Technical health check and testing
- **PROJECT_STATUS.md** - Feature completion status

---

**Happy Valuing! 📊💰🚀**

*Remember: This is a tool to inform your decisions, not replace them. Always do your own research and never invest more than you can afford to lose.*
