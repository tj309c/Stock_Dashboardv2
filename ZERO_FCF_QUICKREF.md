# Zero-FCF Valuation Quick Reference

## 🚀 Quick Start

### Access in Dashboard
1. Go to **Advanced Analytics** dashboard
2. Click **🎯 Zero-FCF Valuation** tab
3. Enter ticker and click Analyze

### Programmatic Usage
```python
from zero_fcf_valuation import ZeroFCFValuationEngine

engine = ZeroFCFValuationEngine()
result = engine.calculate_comprehensive_valuation(info, financials)
```

---

## 📊 5 Valuation Methods

### 1️⃣ Revenue Multiple
- **Best For**: High-growth software, SaaS, e-commerce
- **Requires**: Revenue + growth rate
- **Multiple Range**: 1x - 10x+
- **Adjustment**: Growth-based (1.5x for 50%+ growth)

### 2️⃣ EBITDA Multiple
- **Best For**: Positive EBITDA, negative FCF companies
- **Requires**: EBITDA + margin
- **Multiple Range**: 8x - 30x
- **Adjustment**: Margin + growth based

### 3️⃣ Rule of 40 (SaaS)
- **Best For**: SaaS/subscription companies
- **Formula**: Revenue Growth % + FCF Margin % ≥ 40%
- **Scoring**: ≥60% excellent, ≥40% good, ≥20% fair
- **Premium**: Up to 1.5x multiplier

### 4️⃣ Unit Economics (SaaS)
- **Best For**: SaaS with customer metrics
- **Key Ratios**: LTV:CAC (target >3x)
- **Payback**: Target <12 months
- **Churn**: <5% good (SMB), <2% enterprise

### 5️⃣ Terminal Value
- **Best For**: Companies with revenue history
- **Approach**: 5-year CAGR projection
- **Growth**: Decelerates to 2.5% terminal
- **Discount**: WACC-based NPV

---

## 🎯 Auto-Selection Logic

```
Does company have positive FCF? 
├─ YES → Traditional DCF
└─ NO  → Zero-FCF Methods
         ├─ Detect company type (SaaS/Software/E-commerce/etc.)
         ├─ Run applicable methods (2-5 methods)
         ├─ Weight by company type + data quality
         └─ Return comprehensive valuation
```

---

## 📈 Company Type Matrix

| Type | Primary Method | Weight | Multiple |
|------|---------------|--------|----------|
| **SaaS** | Rule of 40 | 35% | 8-10x revenue |
| **Software** | Revenue | 30% | 6-8x revenue |
| **E-commerce** | Revenue | 40% | 2-3x revenue |
| **Biotech** | Revenue | 35% | 4-6x revenue |
| **Default** | EBITDA | 35% | 10-15x EBITDA |

---

## 🎨 Output Format

```python
{
    "fair_value": 40.33,           # Weighted average
    "current_price": 32.00,
    "upside": 26.0,                # Percentage
    "company_type": "SaaS",
    "confidence": "high",          # high/medium/low
    "primary_method": "rule_of_40",
    
    "scenarios": {
        "bear": 28.23,             # 70% of base
        "base": 40.33,             # Weighted avg
        "bull": 52.43,             # 130% of base
        "optimistic": 60.50        # 150% of base
    },
    
    "valuations": {
        "revenue": {
            "fair_value": 52.40,
            "revenue_multiple": 8.5,
            "data_quality": "high"
        },
        "ebitda": {...},
        "rule_of_40": {...},
        "unit_economics": {...},
        "terminal_value": {...}
    }
}
```

---

## 🔢 Industry Multiples Cheat Sheet

### Revenue Multiples
```
SaaS:              10.0x   (±3x based on growth)
Software:           8.0x
Technology:         6.0x
E-commerce:         2.5x
Biotech:            5.0x
Healthcare:         2.0x
Financial:          2.5x
```

### EBITDA Multiples
```
SaaS:              30.0x   (±10x based on margins)
Software:          25.0x
Technology:        18.0x
E-commerce:        12.0x
Biotech:           15.0x
Healthcare:        12.0x
Financial:          8.0x
```

---

## ⚡ Growth Adjustments

| Growth Rate | Multiplier |
|------------|-----------|
| >50% | 1.5x 🚀 |
| 30-50% | 1.3x 📈 |
| 15-30% | 1.1x 📊 |
| 0-15% | 1.0x ⚖️ |
| <0% | 0.7x 📉 |

---

## 🎯 Rule of 40 Scoring

| Score | Rating | Multiple | Example |
|-------|--------|----------|---------|
| ≥60% | 🌟 Excellent | 1.5x | 50% growth + 15% FCF margin |
| ≥40% | ✅ Good | 1.2x | 35% growth + 10% FCF margin |
| ≥20% | 👌 Fair | 1.0x | 25% growth + 0% FCF margin |
| <20% | ⚠️ Poor | 0.7x | 10% growth + 5% FCF margin |

---

## 💎 Unit Economics Benchmarks

### LTV:CAC Ratio
- **>5x**: 🌟 Excellent - Premium valuation
- **>3x**: ✅ Good - Sustainable growth
- **>2x**: ⚠️ Acceptable - Monitor closely
- **<2x**: 🔴 Poor - Efficiency issues

### Payback Period
- **<6 months**: 🌟 Exceptional
- **<12 months**: ✅ Good
- **<18 months**: ⚠️ Acceptable
- **>18 months**: 🔴 Too long

### Monthly Churn
- **<2%**: 🌟 Excellent (Enterprise)
- **<3%**: ✅ Good (Mid-market)
- **<5%**: ⚠️ Acceptable (SMB)
- **>5%**: 🔴 High risk

---

## 🎨 Confidence Levels

| Level | Criteria | Interpretation |
|-------|----------|----------------|
| **🟢 High** | 3+ methods, 2+ high quality | Reliable valuation |
| **🟡 Medium** | 2+ methods, 1+ high quality | Good estimate |
| **🔴 Low** | 1 method or limited data | Use with caution |

---

## 🔧 Data Requirements

### Minimum (All Methods)
```python
{
    "totalRevenue": <number>,
    "sharesOutstanding": <number>,
    "currentPrice": <number>
}
```

### Revenue Method
```python
{
    "totalRevenue": <number>,
    "revenueGrowth": <number>,  # Optional but recommended
    "sector": <string>,
    "industry": <string>
}
```

### EBITDA Method
```python
{
    "ebitda": <number>,
    "ebitdaMargins": <number>,  # Optional
    "revenueGrowth": <number>   # Optional
}
```

### Rule of 40
```python
{
    "totalRevenue": <number>,
    "revenueGrowth": <number>
}
# Plus cash flow data in financials dict
```

### Unit Economics
```python
{
    "totalRevenue": <number>,
    "revenueGrowth": <number>,
    "grossMargins": <number>
}
```

### Terminal Value
```python
{
    "totalRevenue": <number>,
    "beta": <number>  # Optional, defaults to 1.0
}
# Plus revenue history in financials dict
```

---

## 🚨 Common Issues & Fixes

### "No cash flow data available"
✅ **Normal** - Engine uses Zero-FCF methods automatically

### "Insufficient data for valuation"
❌ **Problem** - Missing required data (usually revenue)
🔧 **Fix**: Ensure `totalRevenue` and `sharesOutstanding` present

### Low confidence rating
⚠️ **Warning** - Limited data or methods disagree
🔧 **Review**: Check individual method results

### Method missing from results
ℹ️ **Info** - Method not applicable for company type
🔧 **Expected**: E.g., Rule of 40 only for SaaS

---

## 💡 Best Practices

### ✅ DO
- Use comprehensive valuation (all methods)
- Check confidence level
- Review primary method reasoning
- Consider scenario analysis
- Compare multiple tickers

### ❌ DON'T
- Rely on single method alone
- Ignore low confidence warnings
- Apply SaaS methods to non-SaaS
- Use without understanding methodology
- Ignore current market conditions

---

## 📖 Example Use Cases

### Case 1: High-Growth SaaS
```
Company: 45% revenue growth, $200M revenue
Methods Used: Rule of 40, Unit Economics, Revenue
Primary: Rule of 40 (excellent score)
Confidence: High
Result: $45/share (35% upside)
```

### Case 2: E-commerce Startup
```
Company: 30% growth, negative EBITDA, $100M revenue
Methods Used: Revenue, Terminal Value
Primary: Revenue (high growth adjustment)
Confidence: Medium
Result: $12/share (50% upside)
```

### Case 3: Mature Software
```
Company: 10% growth, positive EBITDA, $500M revenue
Methods Used: EBITDA, Revenue, Terminal Value
Primary: EBITDA (profitability focus)
Confidence: High
Result: $65/share (15% upside)
```

---

## 🧪 Testing

### Run All Tests
```bash
python test_zero_fcf.py
```

### Expected Output
```
7 passed, 0 failed
🎉 All tests passed!
```

### Test Coverage
- ✅ Revenue valuation
- ✅ EBITDA valuation
- ✅ Rule of 40
- ✅ Unit economics
- ✅ Terminal value
- ✅ Company type detection
- ✅ Comprehensive valuation

---

## 📚 Additional Resources

### Documentation
- Full guide: `ZERO_FCF_IMPLEMENTATION.md`
- Test file: `test_zero_fcf.py`
- Source code: `zero_fcf_valuation.py`
- UI module: `src/utils/zero_fcf_display.py`

### Dashboard Integration
- Tab: Advanced Analytics → Zero-FCF Valuation
- Auto-selection: Built into ValuationEngine
- Fallback chain: DCF → Zero-FCF → Multiples

---

## 🎯 Key Takeaways

1. **5 Methods**: Revenue, EBITDA, Rule of 40, Unit Economics, Terminal Value
2. **Auto-Selection**: Engine picks best methods for company type
3. **Weighted Average**: Methods weighted by reliability + company type
4. **Confidence Levels**: High/Medium/Low based on data quality
5. **Scenario Analysis**: Bear/Base/Bull/Optimistic cases
6. **100% Tested**: All 7 test cases passing

---

## 🔗 Quick Links

| Link | Description |
|------|-------------|
| 📖 [Full Documentation](ZERO_FCF_IMPLEMENTATION.md) | Complete implementation guide |
| 🧪 [Test Suite](test_zero_fcf.py) | Comprehensive test cases |
| 💻 [Engine Code](zero_fcf_valuation.py) | Core valuation logic |
| 🎨 [UI Module](src/utils/zero_fcf_display.py) | Dashboard components |
| 📊 [Dashboard](dashboard_advanced.py) | Integration point |
