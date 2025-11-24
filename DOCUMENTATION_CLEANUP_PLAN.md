# Documentation Cleanup Plan

**Date:** November 23, 2025
**Purpose:** Consolidate redundant markdown files into professional documentation

---

## Summary

**Current State:** 47 markdown files scattered across root directory and `/docs`
**Goal:** Organize into clean, professional structure with archived session notes

---

## Consolidated Documentation

### ✅ New Professional Docs (KEEP)

1. **`docs/BUSINESS_OVERVIEW.md`** ✨ NEW
   - Consolidates: `BUSINESS PLAN.md`, `PROJECT_PLAN.md`, `MVP_COMPLETION_ANALYSIS_REVISED.md`
   - Executive summary, market analysis, roadmap, financial projections
   - **Action:** Keep as primary business document

2. **`docs/DEVELOPER_GUIDE.md`** ✨ NEW
   - Consolidates: Architecture, data fetching, AI integration, testing, deployment
   - Comprehensive technical reference for developers
   - **Action:** Keep as primary developer document

3. **`CHANGELOG.md`** ✨ NEW
   - Consolidates: All session summaries, bugfix docs, completion reports
   - Professional version history
   - **Action:** Keep as primary changelog

4. **`README.md`**
   - Main project introduction
   - **Action:** Keep, update to reference new docs

---

## Existing Documentation to KEEP

### Core Business/Planning
- ✅ `PROJECT_PLAN.md` - Original 6-week MVP plan (historical reference)
- ✅ `BUSINESS PLAN.md` - Original business plan (historical reference)
- ⚠️ **Recommendation:** Move to `docs/archive/` folder for reference, update README to point to `BUSINESS_OVERVIEW.md`

### Technical Guides (Still Relevant)
- ✅ `docs/SETUP_GUIDE.md` - Installation instructions
- ✅ `docs/README-STARTUP.md` - Quick start guide
- ✅ `docs/ERROR_LOGGING_GUIDE.md` - Debugging guide
- ✅ `docs/PERFORMANCE_IMPROVEMENTS.md` - Performance tips
- ✅ `docs/YAHOOQUERY_MIGRATION.md` - Migration notes
- ✅ `DCF_SMART_RECOMMENDATIONS_GUIDE.md` - DCF usage guide
- ✅ `DATA_FETCHING_ARCHITECTURE.md` - Data architecture
- ✅ `AI_MODEL_CONFIGURATION_GUIDE.md` - AI setup
- ✅ `AI_SETUP_QUICKSTART.md` - AI quick start
- ✅ `HYBRID_MODE_IMPLEMENTATION_GUIDE.md` - Mode system guide
- ⚠️ **Recommendation:** Keep in root or move to `docs/guides/`

### Security/GitHub
- ✅ `.github/SECURITY_REMOVE_ENV.md` - Security guide
- ✅ `.github/ROTATE_COMPROMISED_KEYS.md` - Key rotation
- ✅ `.github/AGENT.md` - GitHub agent config
- ✅ `.github/copilot-instructions.md` - Copilot config
- **Action:** Keep, essential for security and GitHub workflows

---

## Files to ARCHIVE (Move to `docs/archive/`)

### Session Summaries (Redundant - Now in CHANGELOG.md)
- 📦 `BUGFIX_SESSION_SUMMARY.md` → Consolidated into CHANGELOG.md v0.7.5
- 📦 `SESSION_SUMMARY_FIXES_AND_PHASE2_START.md` → Consolidated into CHANGELOG.md
- 📦 `PHASE_1_COMPLETION_REPORT.md` → Consolidated into CHANGELOG.md v0.7.0
- 📦 `PHASE_2_COMPLETION_REPORT.md` → Consolidated into CHANGELOG.md v0.7.0
- 📦 `PHASE_3_COMPLETION_REPORT.md` → Consolidated into CHANGELOG.md v0.7.0
- 📦 `HYBRID_MODE_COMPLETE_SUMMARY.md` → Consolidated into CHANGELOG.md v0.7.0
- 📦 `GLOBAL_AI_UPDATE_SUMMARY.md` → Consolidated into CHANGELOG.md v0.6.0
- 📦 `SENTIMENT_ENHANCEMENTS_SUMMARY.md` → Consolidated into CHANGELOG.md v0.6.0

### Feature-Specific Fixes (Redundant - Now in CHANGELOG.md)
- 📦 `TREASURY_YIELD_CURVE_FIX.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `FED_FUNDS_RATE_CLARIFICATION.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `CORRELATION_FACTORS_BUGFIX.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `MARKET_PULSE_FIX_SUMMARY.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `SECTOR_HEATMAP_FIX.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `SECTOR_ROTATION_FIX.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `TAB_RESET_FIX.md` → Consolidated into CHANGELOG.md v0.7.0

### Test Results (Redundant - Now in CHANGELOG.md)
- 📦 `TEST_RESULTS_SUMMARY.md` → Consolidated into CHANGELOG.md
- 📦 `TIMEFRAME_TESTS_RESULTS.md` → Consolidated into CHANGELOG.md v0.7.0
- 📦 `ADVANCED_VISUALS_VALIDATION.md` → Consolidated into CHANGELOG.md v0.4.0
- 📦 `TEST_RESULTS_DASHBOARD_SPINOFF.md` → Consolidated into CHANGELOG.md

### Analysis Reports (Historical Reference)
- 📦 `MVP_COMPLETION_ANALYSIS.md` → Superseded by `MVP_COMPLETION_ANALYSIS_REVISED.md`
- 📦 `MVP_COMPLETION_ANALYSIS_REVISED.md` → Consolidated into BUSINESS_OVERVIEW.md
- 📦 `FEAR_GREED_PROFESSIONAL_ANALYSIS.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `MARKET_PULSE_AUDIT.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `CORRELATING_FACTORS_SUMMARY.md` → Consolidated into CHANGELOG.md v0.5.0
- 📦 `ADVANCED_VISUAL_ANALYSIS_REPORT.md` → Consolidated into CHANGELOG.md v0.4.0

### User Guides (May Keep or Archive)
- 📦 `SENTIMENT_VISUAL_GUIDE.md` → Consolidated into DEVELOPER_GUIDE.md
- 📦 `MODE_NOTIFICATIONS_GUIDE.md` → Consolidated into DEVELOPER_GUIDE.md
- 📦 `SECTOR_ROTATION_TIMEFRAME_SELECTOR.md` → Consolidated into DEVELOPER_GUIDE.md
- 📦 `GLOBAL_AI_CONFIGURATION.md` → Superseded by AI_MODEL_CONFIGURATION_GUIDE.md
- 📦 `PERFORMANCE_TRACKING.md` → Consolidated into DEVELOPER_GUIDE.md

---

## Proposed New Structure

```
Stocks/
├── README.md                                    # Main introduction
├── CHANGELOG.md                                 # ✨ NEW - Professional changelog
│
├── docs/
│   ├── BUSINESS_OVERVIEW.md                     # ✨ NEW - Business doc
│   ├── DEVELOPER_GUIDE.md                       # ✨ NEW - Technical doc
│   │
│   ├── guides/                                  # Technical guides (KEEP)
│   │   ├── SETUP_GUIDE.md
│   │   ├── README-STARTUP.md
│   │   ├── ERROR_LOGGING_GUIDE.md
│   │   ├── PERFORMANCE_IMPROVEMENTS.md
│   │   ├── YAHOOQUERY_MIGRATION.md
│   │   ├── DCF_SMART_RECOMMENDATIONS_GUIDE.md
│   │   ├── DATA_FETCHING_ARCHITECTURE.md
│   │   ├── AI_MODEL_CONFIGURATION_GUIDE.md
│   │   ├── AI_SETUP_QUICKSTART.md
│   │   └── HYBRID_MODE_IMPLEMENTATION_GUIDE.md
│   │
│   └── archive/                                 # Historical docs (ARCHIVE)
│       ├── business/
│       │   ├── PROJECT_PLAN.md
│       │   ├── BUSINESS_PLAN.md
│       │   ├── MVP_COMPLETION_ANALYSIS.md
│       │   └── MVP_COMPLETION_ANALYSIS_REVISED.md
│       │
│       ├── session-notes/                       # Session summaries
│       │   ├── BUGFIX_SESSION_SUMMARY.md
│       │   ├── SESSION_SUMMARY_FIXES_AND_PHASE2_START.md
│       │   ├── PHASE_1_COMPLETION_REPORT.md
│       │   ├── PHASE_2_COMPLETION_REPORT.md
│       │   ├── PHASE_3_COMPLETION_REPORT.md
│       │   ├── HYBRID_MODE_COMPLETE_SUMMARY.md
│       │   └── GLOBAL_AI_UPDATE_SUMMARY.md
│       │
│       ├── bugfixes/                            # Bug fix docs
│       │   ├── TREASURY_YIELD_CURVE_FIX.md
│       │   ├── FED_FUNDS_RATE_CLARIFICATION.md
│       │   ├── CORRELATION_FACTORS_BUGFIX.md
│       │   ├── MARKET_PULSE_FIX_SUMMARY.md
│       │   ├── SECTOR_HEATMAP_FIX.md
│       │   ├── SECTOR_ROTATION_FIX.md
│       │   └── TAB_RESET_FIX.md
│       │
│       ├── test-reports/                        # Test result docs
│       │   ├── TEST_RESULTS_SUMMARY.md
│       │   ├── TIMEFRAME_TESTS_RESULTS.md
│       │   ├── ADVANCED_VISUALS_VALIDATION.md
│       │   └── TEST_RESULTS_DASHBOARD_SPINOFF.md
│       │
│       └── analysis/                            # Analysis reports
│           ├── FEAR_GREED_PROFESSIONAL_ANALYSIS.md
│           ├── MARKET_PULSE_AUDIT.md
│           ├── CORRELATING_FACTORS_SUMMARY.md
│           ├── ADVANCED_VISUAL_ANALYSIS_REPORT.md
│           ├── SENTIMENT_ENHANCEMENTS_SUMMARY.md
│           ├── SENTIMENT_VISUAL_GUIDE.md
│           ├── MODE_NOTIFICATIONS_GUIDE.md
│           ├── SECTOR_ROTATION_TIMEFRAME_SELECTOR.md
│           ├── GLOBAL_AI_CONFIGURATION.md
│           └── PERFORMANCE_TRACKING.md
│
├── .github/
│   ├── SECURITY_REMOVE_ENV.md                   # KEEP - Security
│   ├── ROTATE_COMPROMISED_KEYS.md               # KEEP - Security
│   ├── AGENT.md                                 # KEEP - GitHub config
│   └── copilot-instructions.md                  # KEEP - GitHub config
│
├── .pytest_cache/
│   └── README.md                                # Auto-generated by pytest
│
└── [Other project files...]
```

---

## Recommended Actions

### Immediate
1. ✅ **Created:** `docs/BUSINESS_OVERVIEW.md`, `docs/DEVELOPER_GUIDE.md`, `CHANGELOG.md`
2. 📁 **Create:** Archive folder structure: `docs/archive/{business,session-notes,bugfixes,test-reports,analysis}`
3. 📦 **Move:** Redundant files to appropriate archive folders
4. 📝 **Update:** `README.md` to reference new consolidated docs

### Optional (User Decision)
- **Delete vs Archive:** Decide whether to keep archived files in Git or remove entirely
  - **Recommend:** Keep in `docs/archive/` for historical reference
  - **Alternative:** Create `ARCHIVE.md` with summary, then delete original files

### Post-Cleanup
- Update all internal doc links to point to new consolidated docs
- Update GitHub README badges/links
- Add note in archived files: "⚠️ This document is archived. See CHANGELOG.md or BUSINESS_OVERVIEW.md for latest information."

---

## Execution Script

```bash
# Create archive structure
mkdir -p docs/archive/business
mkdir -p docs/archive/session-notes
mkdir -p docs/archive/bugfixes
mkdir -p docs/archive/test-reports
mkdir -p docs/archive/analysis
mkdir -p docs/guides

# Move business docs
mv "BUSINESS PLAN.md" docs/archive/business/
mv PROJECT_PLAN.md docs/archive/business/
mv MVP_COMPLETION_ANALYSIS.md docs/archive/business/
mv MVP_COMPLETION_ANALYSIS_REVISED.md docs/archive/business/

# Move session notes
mv BUGFIX_SESSION_SUMMARY.md docs/archive/session-notes/
mv SESSION_SUMMARY_FIXES_AND_PHASE2_START.md docs/archive/session-notes/
mv PHASE_1_COMPLETION_REPORT.md docs/archive/session-notes/
mv PHASE_2_COMPLETION_REPORT.md docs/archive/session-notes/
mv PHASE_3_COMPLETION_REPORT.md docs/archive/session-notes/
mv HYBRID_MODE_COMPLETE_SUMMARY.md docs/archive/session-notes/
mv GLOBAL_AI_UPDATE_SUMMARY.md docs/archive/session-notes/
mv SENTIMENT_ENHANCEMENTS_SUMMARY.md docs/archive/session-notes/

# Move bugfix docs
mv TREASURY_YIELD_CURVE_FIX.md docs/archive/bugfixes/
mv FED_FUNDS_RATE_CLARIFICATION.md docs/archive/bugfixes/
mv CORRELATION_FACTORS_BUGFIX.md docs/archive/bugfixes/
mv MARKET_PULSE_FIX_SUMMARY.md docs/archive/bugfixes/
mv SECTOR_HEATMAP_FIX.md docs/archive/bugfixes/
mv SECTOR_ROTATION_FIX.md docs/archive/bugfixes/
mv TAB_RESET_FIX.md docs/archive/bugfixes/

# Move test reports
mv TEST_RESULTS_SUMMARY.md docs/archive/test-reports/
mv TIMEFRAME_TESTS_RESULTS.md docs/archive/test-reports/
mv ADVANCED_VISUALS_VALIDATION.md docs/archive/test-reports/
mv TEST_RESULTS_DASHBOARD_SPINOFF.md docs/archive/test-reports/

# Move analysis reports
mv FEAR_GREED_PROFESSIONAL_ANALYSIS.md docs/archive/analysis/
mv MARKET_PULSE_AUDIT.md docs/archive/analysis/
mv CORRELATING_FACTORS_SUMMARY.md docs/archive/analysis/
mv ADVANCED_VISUAL_ANALYSIS_REPORT.md docs/archive/analysis/
mv SENTIMENT_VISUAL_GUIDE.md docs/archive/analysis/
mv MODE_NOTIFICATIONS_GUIDE.md docs/archive/analysis/
mv SECTOR_ROTATION_TIMEFRAME_SELECTOR.md docs/archive/analysis/
mv GLOBAL_AI_CONFIGURATION.md docs/archive/analysis/
mv PERFORMANCE_TRACKING.md docs/archive/analysis/

# Move technical guides to docs/guides/
mv DCF_SMART_RECOMMENDATIONS_GUIDE.md docs/guides/
mv DATA_FETCHING_ARCHITECTURE.md docs/guides/
mv AI_MODEL_CONFIGURATION_GUIDE.md docs/guides/
mv AI_SETUP_QUICKSTART.md docs/guides/
mv HYBRID_MODE_IMPLEMENTATION_GUIDE.md docs/guides/

# Note: docs/SETUP_GUIDE.md etc. are already in docs/

echo "✅ Documentation cleanup complete!"
echo "📁 Archived files are in docs/archive/"
echo "📚 Technical guides are in docs/guides/"
echo "📝 Professional docs: docs/BUSINESS_OVERVIEW.md, docs/DEVELOPER_GUIDE.md, CHANGELOG.md"
```

---

## Benefits of This Structure

1. **Professional** - Clean, organized documentation structure
2. **Discoverable** - Clear hierarchy, easy to navigate
3. **Maintainable** - One source of truth (CHANGELOG.md, BUSINESS_OVERVIEW.md, DEVELOPER_GUIDE.md)
4. **Historical** - Preserved session notes and bug reports in archive
5. **Git-Friendly** - Reduced clutter in root directory

---

## Next Steps

**Would you like me to:**
1. Execute the cleanup script to reorganize files?
2. Update README.md with new documentation structure?
3. Add deprecation notices to archived files?

---

**Created:** November 23, 2025
**Status:** Ready for execution pending user approval
