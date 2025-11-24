# PROJECT PLAN: RetailAnalyst Development
**Generated from Business Plan - November 23, 2025**
**Target Launch: 6 weeks from kickoff**
**Development Team Lead: [Your Name]**

---

## 1. Project Overview

### Mission Statement
Build and launch an MVP of RetailAnalyst - a Streamlit-based stock analysis dashboard that provides institutional-grade analytics at a retail price point ($0.25-$3/month).

### Success Criteria
- ✅ Stable data pipeline supporting 100+ tickers
- ✅ All 5 MVP modules operational (Dashboard, Data Engine, Valuation, Backtester, AI Summarizer)
- ✅ Closed beta with 10-20 users gathering feedback
- ✅ Response time < 3 seconds for most operations
- ✅ Data accuracy validated against known benchmarks

### Technical Constraints
- Python-based stack (Streamlit framework)
- Free-tier data APIs during MVP phase
- Zero-cost hosting initially (Streamlit Community Cloud or Cornell resources)
- Cornell SandboxAI for LLM integration (dev); OpenAI/Anthropic for production

---

## 2. Development Phases & Timeline

### Phase 1: Foundation (Week 1-2)
**Goal:** Build the skeleton app with basic data visualization

#### Epic 1.1: Project Setup & Infrastructure
- [ ] Initialize Git repository with proper .gitignore (secrets, API keys)
- [ ] Set up virtual environment with core dependencies (streamlit, pandas, numpy, yfinance)
- [ ] Configure project structure (modular architecture)
  ```
  /pages/           # Multi-page Streamlit app
  /utils/           # Data fetchers, calculators
  /config/          # API keys, settings
  /cache/           # SQLite database for caching
  /tests/           # Unit tests
  ```
- [ ] Set up SQLite database schema for caching ticker data
- [ ] Create requirements.txt with pinned versions
- [ ] Set up basic error logging and monitoring

#### Epic 1.2: Data Engine Foundation
**Owner:** Backend/Data Engineer
**Priority:** Critical Path

- [ ] Implement modular data connector interface (abstract class)
- [ ] Build yfinance connector with error handling
- [ ] Build Alpha Vantage connector as backup/fallback
- [ ] Implement aggressive caching strategy (SQLite)
  - Cache ticker price data (15-min refresh)
  - Cache fundamental data (24-hour refresh)
  - Cache news data (1-hour refresh)
- [ ] Add rate-limit handling with exponential backoff
- [ ] Create data validation functions (check for missing/stale data)
- [ ] Write unit tests for data fetchers

**Deliverables:**
- `data_fetcher.py` with swap-able data providers
- `cache_manager.py` for SQLite operations
- Test coverage > 80% for data layer

#### Epic 1.3: Basic Dashboard UI
**Owner:** Frontend/Streamlit Developer
**Priority:** Critical Path

- [ ] Create [Home.py](Home.py) landing page with ticker search
- [ ] Build stock overview page showing:
  - Current price, change (%), volume
  - Interactive price chart (line/candlestick)
  - Moving averages (20, 50, 200-day SMA)
- [ ] Implement ticker selection widget (sidebar)
- [ ] Add date range selector for charts
- [ ] Style with clean, professional theme (custom CSS if needed)
- [ ] Ensure mobile responsiveness basics

**Deliverables:**
- Working Streamlit app accessible at localhost:8501
- Screenshot/demo video for stakeholder review

---

### Phase 2: Core Analytics (Week 3-4)
**Goal:** Implement DCF calculator and backtesting engine

#### Epic 2.1: Valuation Module (DCF Calculator)
**Owner:** Financial Modeling Developer
**Priority:** High

**Background:** Automated Discounted Cash Flow analysis to estimate fair value

- [ ] Research and document DCF methodology
  - Free Cash Flow (FCF) calculation from financial statements
  - Terminal value calculation (Gordon Growth Model)
  - WACC (Weighted Average Cost of Capital) estimation
- [ ] Fetch required data:
  - Income statement (revenue, EBITDA, net income)
  - Balance sheet (debt, equity)
  - Cash flow statement (operating cash flow, capex)
- [ ] Implement DCF calculator class
  - Input: Ticker, growth rate, discount rate (user adjustable)
  - Output: Fair value estimate, margin of safety
- [ ] Build UI for DCF module
  - Display current price vs. fair value
  - Allow user to adjust assumptions (sliders)
  - Show sensitivity analysis table
- [ ] Add data quality warnings (if financials missing/stale)
- [ ] Write comprehensive tests with known valuations

**Deliverables:**
- `valuation.py` module
- New Streamlit page: "Fundamental Analysis"
- Documentation of DCF assumptions and limitations

#### Epic 2.2: Backtesting Engine
**Owner:** Quant/Algorithm Developer
**Priority:** High

**Background:** Vectorized backtesting for technical strategies

- [ ] Design backtest framework architecture
  - Strategy definition interface
  - Entry/exit signal generation
  - Position sizing logic
- [ ] Implement vectorized backtester using Pandas
  - No loops - all operations on DataFrame columns
  - Support for multiple timeframes (daily, weekly)
- [ ] Build 3-5 pre-built strategies:
  - RSI mean reversion (buy RSI < 30, sell RSI > 70)
  - Moving average crossover (50/200 SMA)
  - Bollinger Band breakouts
- [ ] Calculate performance metrics:
  - Total return, CAGR, Sharpe ratio
  - Max drawdown, win rate
  - Number of trades, average holding period
- [ ] Build backtesting UI
  - Strategy selector dropdown
  - Parameter inputs (RSI thresholds, MA periods)
  - Date range for backtest
  - Results visualization (equity curve, trade markers)
- [ ] Add disclaimer about backtesting limitations

**Deliverables:**
- `backtester.py` with strategy classes
- New Streamlit page: "Risk & Forecasting"
- Validation against known backtest results (SPY buy-and-hold baseline)

---

### Phase 3: AI Integration (Week 5)
**Goal:** Add LLM-powered news summarization

#### Epic 3.1: AI Summarizer
**Owner:** AI/NLP Engineer
**Priority:** Medium-High

**Background:** Generate concise 3-bullet summaries of recent news for tickers

- [ ] Set up Cornell SandboxAI API integration (dev environment)
- [ ] Fetch recent news for ticker
  - Use yfinance news feed or NewsAPI
  - Filter for relevance (ticker mentioned in title/body)
  - Sort by recency (last 7 days)
- [ ] Design prompt template for LLM
  ```
  You are a financial analyst. Summarize these news articles about {TICKER} in 3 concise bullet points.
  Focus on: earnings, product launches, regulatory issues, major partnerships.

  Articles: {news_text}
  ```
- [ ] Implement API call with error handling
  - Timeout handling (5-second max)
  - Fallback to "No recent news" if API fails
  - Token limit management (truncate long articles)
- [ ] Cache AI summaries (24-hour TTL) to reduce API costs
- [ ] Add UI component to display summaries
  - Expandable section on stock overview page
  - Timestamp of last update
- [ ] Set up OpenAI/Anthropic API for production (conditional)
- [ ] Add cost tracking (log token usage per request)

**Deliverables:**
- `ai_summarizer.py` module
- Integration into existing stock overview page
- Cost projection report (tokens per user per month)

---

### Phase 4: Testing & Launch Prep (Week 6)
**Goal:** Bug fixes, performance optimization, beta launch

#### Epic 4.1: Quality Assurance
**Owner:** QA Lead / All Developers
**Priority:** Critical

- [ ] Write integration tests
  - End-to-end test: Search ticker → View DCF → Run backtest
  - Test with 10 diverse tickers (large cap, small cap, international)
- [ ] Performance testing
  - Load test with 50 concurrent users (locust or similar)
  - Identify slow queries and optimize
  - Target: 95th percentile response time < 3 seconds
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile responsiveness testing (iOS, Android)
- [ ] Data accuracy validation
  - Compare DCF outputs to manual calculations
  - Verify backtest results against TradingView/QuantConnect
- [ ] Security audit
  - Ensure no API keys in code (use environment variables)
  - Input validation (prevent SQL injection, XSS)
  - Rate limiting on user actions

**Deliverables:**
- Test report with pass/fail status
- List of known issues and workarounds
- Performance benchmark report

#### Epic 4.2: Deployment & Infrastructure
**Owner:** DevOps / Lead Developer
**Priority:** Critical Path

- [ ] Choose hosting platform
  - Option A: Streamlit Community Cloud (free, 1 app)
  - Option B: AWS t2.micro ($9/mo) with custom domain
- [ ] Set up production environment
  - Environment variables for API keys (Streamlit secrets or AWS Secrets Manager)
  - Production database (SQLite → PostgreSQL if scaling)
  - Logging and monitoring (Sentry for error tracking)
- [ ] Configure domain and SSL (if custom hosting)
- [ ] Set up CI/CD pipeline (GitHub Actions)
  - Auto-run tests on pull requests
  - Deploy to production on merge to main
- [ ] Create backup strategy for user data/cache
- [ ] Write deployment runbook (steps to deploy updates)

**Deliverables:**
- Live URL for beta testers
- Monitoring dashboard (uptime, error rates)

#### Epic 4.3: Documentation & User Onboarding
**Owner:** Technical Writer / Product Manager
**Priority:** Medium

- [ ] Write user documentation
  - Getting started guide
  - Feature explanations (DCF, backtesting, AI summaries)
  - FAQ (data sources, accuracy, limitations)
- [ ] Create in-app tooltips and help text
- [ ] Record demo video (2-3 minutes)
- [ ] Prepare beta tester feedback form (Google Forms / Typeform)
- [ ] Draft email template for beta invitations

**Deliverables:**
- README.md with user-facing documentation
- Demo video uploaded to YouTube/Vimeo
- Beta feedback form link

#### Epic 4.4: Beta Launch
**Owner:** Product Manager
**Priority:** Critical Path

- [ ] Recruit 10-20 beta testers
  - Reddit posts (r/algotrading, r/investing)
  - Cornell University community (students, professors)
  - Personal network
- [ ] Send beta invitations with clear instructions
- [ ] Set up communication channel (Discord server or Slack)
- [ ] Monitor usage and gather feedback
  - Weekly check-ins with testers
  - Track feature usage metrics (which pages visited most)
- [ ] Prioritize bug fixes based on severity/frequency
- [ ] Iterate on UI/UX based on feedback

**Deliverables:**
- 10+ active beta users
- Feedback summary document
- Prioritized backlog for post-MVP improvements

---

## 3. Post-MVP Roadmap (Future Enhancements)

### Phase 5: Monetization Prep (Month 2-3)
**Not part of MVP - plan for future sprints**

- [ ] Integrate Stripe payment processing
- [ ] Build user authentication system (accounts, login)
- [ ] Implement subscription management (free tier vs. paid tier)
- [ ] Add usage limits for free tier (10 tickers/day, 5 backtests/week)
- [ ] Create billing page (Stripe customer portal)
- [ ] Legal compliance: Terms of Service, Privacy Policy, Disclaimer

### Phase 6: Advanced Features (Month 4-6)
**Revenue-dependent enhancements**

- [ ] **Social Sentiment Engine**
  - Scrape Reddit (r/wallstreetbets) and X/Twitter for ticker mentions
  - Calculate sentiment score using NLP (VADER, FinBERT)
  - Display sentiment trend chart
- [ ] **Satellite Imagery Verification**
  - Integrate with satellite API (Planet Labs, Sentinel Hub)
  - Show before/after images of microcap company HQs
  - Flag unusual activity (construction, parking lot changes)
- [ ] **Advanced Forecasting Models**
  - ARIMA for time-series prediction
  - GARCH for volatility modeling
  - Monte Carlo simulations for risk assessment
- [ ] **Portfolio Tracker**
  - Allow users to input holdings
  - Calculate portfolio-level metrics (beta, correlation matrix)
  - Rebalancing suggestions
- [ ] **Alerts & Notifications**
  - Email/SMS alerts when price crosses threshold
  - Earnings announcement reminders
  - Backtest signal notifications

---

## 4. Team Roles & Responsibilities

### Core Team (MVP Phase)
| Role | Responsibilities | Time Commitment |
|------|------------------|-----------------|
| **Lead Developer / Product Manager** | Architecture, project coordination, code review | Full-time (40h/week) |
| **Backend/Data Engineer** | Data connectors, caching, API integrations | Part-time (20h/week) |
| **Frontend/Streamlit Developer** | UI/UX, Streamlit pages, visualization | Part-time (20h/week) |
| **Quant/Financial Modeler** | DCF, backtesting, financial calculations | Part-time (15h/week) |
| **AI/NLP Engineer** | LLM integration, prompt engineering | Part-time (10h/week) |

### Extended Team (Post-MVP)
- QA Tester (contract)
- Technical Writer (contract)
- Marketing/Community Manager

---

## 5. Technical Stack Reference

### Core Dependencies
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.28
alpha-vantage>=2.3.1
scikit-learn>=1.3.0
plotly>=5.17.0
requests>=2.31.0
beautifulsoup4>=4.12.0
openai>=1.0.0  # or anthropic
```

### Development Tools
- **Version Control:** Git + GitHub
- **Testing:** pytest, pytest-cov
- **Linting:** ruff, black (code formatting)
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry (error tracking), Streamlit Analytics

### Data Sources
- **Market Data:** yfinance (primary), Alpha Vantage (backup)
- **News:** yfinance news feed, NewsAPI
- **Fundamentals:** yfinance, Financial Modeling Prep API (if needed)

### Database
- **MVP:** SQLite (file-based, simple)
- **Production Scale:** PostgreSQL (if > 1,000 users)

---

## 6. Risk Mitigation Strategies

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Data API rate limits** | High - App unusable if rate-limited | Aggressive caching (15-min for prices, 24h for fundamentals). Swap-able data connectors. |
| **LLM API costs spike** | Medium - Could exceed budget | Cache summaries (24h TTL). Set hard limit on API calls per user. |
| **Poor performance with 100+ users** | High - User churn | Load testing during Week 6. Optimize slow queries. Consider Redis for caching. |
| **Streamlit limitations** | Medium - May need custom solution | Start with Streamlit Cloud. Plan migration to FastAPI + React if needed. |

### Business Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Low user adoption** | High - No revenue | Focus on niche (microcap stocks). Viral marketing via Reddit case studies. |
| **Trust issues with financial data** | Medium - Users hesitant to use | "White box" transparency - show all calculations. Open-source non-proprietary code. |
| **Regulatory compliance (FinCEN, SEC)** | Low-Medium - Not providing trading advice | Clear disclaimers. Consult lawyer before monetization. |

---

## 7. Success Metrics & KPIs

### MVP Launch Success (Week 6)
- ✅ 10+ active beta users
- ✅ Average session time > 5 minutes
- ✅ < 5 critical bugs reported
- ✅ 95% uptime during beta period

### 3-Month Goals (Post-Launch)
- 📈 100 registered users
- 📈 50% weekly active user rate
- 📈 Net Promoter Score (NPS) > 30
- 💰 $100-$300 revenue (if monetization starts)

### 6-Month Goals (Growth Phase)
- 📈 1,000 registered users
- 💰 $3,000/year revenue (self-sustaining)
- 📈 Average 3+ features used per session
- 🌟 Featured in 1-2 finance/tech blogs or subreddits

---

## 8. Communication & Project Management

### Daily Standups (Async)
- Post in team channel: What did you complete? What are you working on? Any blockers?
- 5 minutes per team member

### Weekly Sprint Review (Fridays)
- Demo completed features
- Review sprint goals vs. actuals
- Plan next week's priorities

### Tools
- **Task Tracking:** GitHub Projects or Trello
- **Documentation:** Notion or Google Docs
- **Code Repository:** GitHub (private repo)
- **Communication:** Discord or Slack

### Definition of Done
A task is "done" when:
- Code is committed and pushed to Git
- Unit tests written and passing
- Code reviewed by at least one other developer
- Feature tested manually in dev environment
- Documentation updated (if user-facing feature)

---

## 9. Launch Checklist

### Pre-Launch (Before Week 6)
- [ ] All 5 MVP modules functional
- [ ] Data pipeline tested with 100+ tickers
- [ ] Performance benchmarks met (< 3 sec response time)
- [ ] Security audit completed
- [ ] User documentation written
- [ ] Demo video recorded

### Launch Day
- [ ] Deploy to production hosting
- [ ] Send beta invitations to 20 testers
- [ ] Monitor error logs (Sentry dashboard)
- [ ] Post announcement on Reddit (r/algotrading)
- [ ] Set up feedback collection form

### First Week Post-Launch
- [ ] Daily bug triage and hotfixes
- [ ] Respond to all user feedback within 24 hours
- [ ] Track usage metrics (page views, feature adoption)
- [ ] Schedule first retrospective meeting

---

## 10. Appendix: Key Technical Decisions

### Why Streamlit?
- ✅ Rapid prototyping (MVP in weeks, not months)
- ✅ Python-native (no JS required)
- ✅ Built-in caching and state management
- ❌ Limited customization compared to React
- **Decision:** Use for MVP. Re-evaluate if scaling beyond 10,000 users.

### Why SQLite for Caching?
- ✅ Zero-config, file-based database
- ✅ Fast for read-heavy workloads
- ❌ Not suitable for write-heavy or concurrent writes
- **Decision:** Sufficient for MVP (single instance). Migrate to PostgreSQL if multi-instance deployment needed.

### Why Vectorized Backtesting?
- ✅ 100-1000x faster than loop-based backtesting
- ✅ Leverages Pandas' optimized C backend
- ❌ More complex to implement (requires matrix thinking)
- **Decision:** Worth the upfront investment. Critical for user experience.

---

## Contact & Questions
For questions about this project plan, contact [Your Name] at [email].

**Last Updated:** November 23, 2025
**Version:** 1.0
