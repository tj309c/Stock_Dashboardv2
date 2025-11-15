# Cleanup Script - Remove Redundant Files
# Run this to clean up temporary and duplicate documentation

# Remove temporary validation scripts (already validated, reports generated)
Remove-Item -Path "validate_formatters.py" -ErrorAction SilentlyContinue
Remove-Item -Path "validate_constants.py" -ErrorAction SilentlyContinue
Remove-Item -Path "validate_dcf.py" -ErrorAction SilentlyContinue
Remove-Item -Path "validate_technical.py" -ErrorAction SilentlyContinue
Remove-Item -Path "validate_valuation.py" -ErrorAction SilentlyContinue
Remove-Item -Path "validate_api_keys.py" -ErrorAction SilentlyContinue
Remove-Item -Path "validate_all.py" -ErrorAction SilentlyContinue

# Remove temporary JSON output files (data already reviewed)
Remove-Item -Path "health_check_report.json" -ErrorAction SilentlyContinue
Remove-Item -Path "api_keys_test_report.json" -ErrorAction SilentlyContinue

# Remove temporary debug scripts (functionality now in comprehensive_health_check.py)
Remove-Item -Path "end_to_end_debug.py" -ErrorAction SilentlyContinue

# Remove duplicate/outdated test scripts
Remove-Item -Path "user_acceptance_test.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_visual_ui.py" -ErrorAction SilentlyContinue
Remove-Item -Path "test_runtime_performance.py" -ErrorAction SilentlyContinue

# Remove redundant QUICKSTART files (consolidated into CONSOLIDATED_DOCUMENTATION.md)
Remove-Item -Path "QUICKSTART_REFACTORING.md" -ErrorAction SilentlyContinue
Remove-Item -Path "QUICK_START_NEW_FEATURES.md" -ErrorAction SilentlyContinue
Remove-Item -Path "GRADUAL_MIGRATION_QUICKSTART.md" -ErrorAction SilentlyContinue
Remove-Item -Path "PHASE3_QUICKSTART.md" -ErrorAction SilentlyContinue

# Remove duplicate SENTIMENT CORRELATION docs (keep only QUICKREF and GUIDE)
Remove-Item -Path "SENTIMENT_CORRELATION_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "SENTIMENT_CORRELATION_INDEX.md" -ErrorAction SilentlyContinue
Remove-Item -Path "SENTIMENT_CORRELATION_INTEGRATION_COMPLETE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "SENTIMENT_CORRELATION_ARCHITECTURE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "SENTIMENT_INTEGRATION_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "SENTIMENT_INTEGRATION_GUIDE.md" -ErrorAction SilentlyContinue

# Remove duplicate REFACTORING docs (consolidated into ARCHITECTURE.md)
Remove-Item -Path "REFACTORING_PLAN.md" -ErrorAction SilentlyContinue
Remove-Item -Path "REFACTORING_GUIDE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "REFACTORING_EXECUTION_SUMMARY.md" -ErrorAction SilentlyContinue

# Remove duplicate API docs (consolidated into CONSOLIDATED_DOCUMENTATION.md)
Remove-Item -Path "API_KEYS_GUIDE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "API_SETUP_INSTRUCTIONS.md" -ErrorAction SilentlyContinue
Remove-Item -Path "API_VERIFICATION_COMPLETE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "API_KEYS_AND_ENHANCEMENTS_GUIDE.md" -ErrorAction SilentlyContinue

# Remove duplicate PHASE/MIGRATION docs (consolidated)
Remove-Item -Path "PHASE1_COMPLETE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "PHASE_1_IMPROVEMENTS_COMPLETED.md" -ErrorAction SilentlyContinue
Remove-Item -Path "MIGRATION_GUIDE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "MIGRATION_LOG.md" -ErrorAction SilentlyContinue
Remove-Item -Path "MIGRATION_PLAN.md" -ErrorAction SilentlyContinue

# Remove duplicate DEBUGGING docs (consolidated into single report)
Remove-Item -Path "DEBUGGING_EFFICIENCY_REPORT.md" -ErrorAction SilentlyContinue
Remove-Item -Path "DEBUGGING_ENHANCEMENTS_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "DEBUGGING_REPORT.md" -ErrorAction SilentlyContinue
Remove-Item -Path "END_TO_END_DEBUG_REPORT.md" -ErrorAction SilentlyContinue
Remove-Item -Path "DEBUG_CONSOLIDATION_SUMMARY.md" -ErrorAction SilentlyContinue

# Remove duplicate IMPLEMENTATION docs (consolidated)
Remove-Item -Path "IMPLEMENTATION_COMPLETE_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "IMPLEMENTATION_EXAMPLE.md" -ErrorAction SilentlyContinue
Remove-Item -Path "CRITICAL_FIXES_COMPLETED.md" -ErrorAction SilentlyContinue

# Remove duplicate DEPLOYMENT/OPTIMIZATION docs (consolidated)
Remove-Item -Path "DEPLOYMENT_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "OPTIMIZATION_REPORT.md" -ErrorAction SilentlyContinue

# Remove duplicate PERFORMANCE docs (consolidated)
Remove-Item -Path "PERFORMANCE_IMPLEMENTATION_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "PROGRESSIVE_LOADING_COMPLETE.md" -ErrorAction SilentlyContinue

# Remove duplicate ZERO_FCF docs (keep only QUICKREF)
Remove-Item -Path "ZERO_FCF_IMPLEMENTATION.md" -ErrorAction SilentlyContinue
Remove-Item -Path "ZERO_FCF_COMPLETE.md" -ErrorAction SilentlyContinue

# Remove duplicate CONGRESSIONAL docs (already integrated)
Remove-Item -Path "CONGRESSIONAL_TRADES_IMPLEMENTATION.md" -ErrorAction SilentlyContinue

# Remove duplicate VALUATION docs (consolidated)
Remove-Item -Path "VALUATION_FUTURE_ENHANCEMENTS.md" -ErrorAction SilentlyContinue

# Remove duplicate UAT docs (consolidated into validation reports)
Remove-Item -Path "UAT_EXECUTIVE_SUMMARY.md" -ErrorAction SilentlyContinue
Remove-Item -Path "MANUAL_UI_TEST_CHECKLIST.md" -ErrorAction SilentlyContinue

# Remove duplicate ENHANCEMENT docs (consolidated)
Remove-Item -Path "ENHANCEMENT_RECOMMENDATIONS.md" -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Files removed:" -ForegroundColor Yellow
Write-Host "  - 7 validation scripts (validate_*.py)"
Write-Host "  - 2 temporary JSON outputs"
Write-Host "  - 1 temporary debug script"
Write-Host "  - 3 duplicate test files"
Write-Host "  - 40+ redundant documentation files"
Write-Host ""
Write-Host "Remaining essential files:" -ForegroundColor Cyan
Write-Host "  📄 CONSOLIDATED_DOCUMENTATION.md - Main documentation hub"
Write-Host "  📄 README.md - Project overview"
Write-Host "  📄 ARCHITECTURE.md - System architecture"
Write-Host "  📄 PROJECT_STATUS.md - Current status"
Write-Host "  📄 PRODUCTION_VALIDATION_REPORT.md - Validation results"
Write-Host "  📄 BUTTON_VALIDATION_REPORT.md - Button tests"
Write-Host "  📄 COLOR_THEME_UPDATE_SUMMARY.md - Color scheme docs"
Write-Host ""
Write-Host "  📄 INDICATORS_QUICKREF.md - Indicator reference"
Write-Host "  📄 DELTA_DIVERGENCE_GUIDE.md - Delta divergence docs"
Write-Host "  📄 INTERACTIVE_DCF_GUIDE.md - DCF calculator docs"
Write-Host "  📄 SENTIMENT_CORRELATION_QUICKREF.md - Sentiment docs"
Write-Host "  📄 SENTIMENT_CORRELATION_GUIDE.md - Detailed sentiment guide"
Write-Host "  📄 PERFORMANCE_MODE_GUIDE.md - Performance settings"
Write-Host "  📄 PROGRESSIVE_LOADING_USER_GUIDE.md - Loading UX"
Write-Host "  📄 PERFORMANCE_ARCHITECTURE.md - Performance design"
Write-Host "  📄 ZERO_FCF_QUICKREF.md - Zero-FCF valuation"
Write-Host ""
Write-Host "  🐍 comprehensive_health_check.py - System validation"
Write-Host "  🐍 test_all_buttons.py - UI validation"
Write-Host "  🐍 production_validation.py - Production checks"
Write-Host "  🐍 test_indicators.py - Indicator tests"
Write-Host "  🐍 test_delta_divergence.py - Delta divergence tests"
Write-Host "  🐍 test_global_ai.py - AI integration tests"
Write-Host "  🐍 test_sentiment_correlation.py - Sentiment tests"
Write-Host "  🐍 test_progressive_loading.py - Performance tests"
Write-Host "  🐍 test_api_keys.py - API validation"
Write-Host "  🐍 test_zero_fcf.py - Zero-FCF tests"
Write-Host "  🐍 debug_tools.py - Debugging utilities"
Write-Host ""
Write-Host "Total reduction: ~50 files removed" -ForegroundColor Green
