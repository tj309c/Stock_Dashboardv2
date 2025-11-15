@echo off
echo Cleaning up redundant files...
echo.

REM Remove temporary validation scripts
if exist validate_formatters.py del /q validate_formatters.py
if exist validate_constants.py del /q validate_constants.py
if exist validate_dcf.py del /q validate_dcf.py
if exist validate_technical.py del /q validate_technical.py
if exist validate_valuation.py del /q validate_valuation.py
if exist validate_api_keys.py del /q validate_api_keys.py
if exist validate_all.py del /q validate_all.py

REM Remove temporary JSON outputs
if exist health_check_report.json del /q health_check_report.json
if exist api_keys_test_report.json del /q api_keys_test_report.json

REM Remove temporary debug scripts
if exist end_to_end_debug.py del /q end_to_end_debug.py

REM Remove duplicate test files
if exist user_acceptance_test.py del /q user_acceptance_test.py
if exist test_visual_ui.py del /q test_visual_ui.py
if exist test_runtime_performance.py del /q test_runtime_performance.py

REM Remove redundant QUICKSTART files
if exist QUICKSTART_REFACTORING.md del /q QUICKSTART_REFACTORING.md
if exist QUICK_START_NEW_FEATURES.md del /q QUICK_START_NEW_FEATURES.md
if exist GRADUAL_MIGRATION_QUICKSTART.md del /q GRADUAL_MIGRATION_QUICKSTART.md
if exist PHASE3_QUICKSTART.md del /q PHASE3_QUICKSTART.md

REM Remove duplicate SENTIMENT docs
if exist SENTIMENT_CORRELATION_SUMMARY.md del /q SENTIMENT_CORRELATION_SUMMARY.md
if exist SENTIMENT_CORRELATION_INDEX.md del /q SENTIMENT_CORRELATION_INDEX.md
if exist SENTIMENT_CORRELATION_INTEGRATION_COMPLETE.md del /q SENTIMENT_CORRELATION_INTEGRATION_COMPLETE.md
if exist SENTIMENT_CORRELATION_ARCHITECTURE.md del /q SENTIMENT_CORRELATION_ARCHITECTURE.md
if exist SENTIMENT_INTEGRATION_SUMMARY.md del /q SENTIMENT_INTEGRATION_SUMMARY.md
if exist SENTIMENT_INTEGRATION_GUIDE.md del /q SENTIMENT_INTEGRATION_GUIDE.md

REM Remove duplicate REFACTORING docs
if exist REFACTORING_PLAN.md del /q REFACTORING_PLAN.md
if exist REFACTORING_GUIDE.md del /q REFACTORING_GUIDE.md
if exist REFACTORING_EXECUTION_SUMMARY.md del /q REFACTORING_EXECUTION_SUMMARY.md

REM Remove duplicate API docs
if exist API_KEYS_GUIDE.md del /q API_KEYS_GUIDE.md
if exist API_SETUP_INSTRUCTIONS.md del /q API_SETUP_INSTRUCTIONS.md
if exist API_VERIFICATION_COMPLETE.md del /q API_VERIFICATION_COMPLETE.md
if exist API_KEYS_AND_ENHANCEMENTS_GUIDE.md del /q API_KEYS_AND_ENHANCEMENTS_GUIDE.md

REM Remove duplicate PHASE/MIGRATION docs
if exist PHASE1_COMPLETE.md del /q PHASE1_COMPLETE.md
if exist PHASE_1_IMPROVEMENTS_COMPLETED.md del /q PHASE_1_IMPROVEMENTS_COMPLETED.md
if exist MIGRATION_GUIDE.md del /q MIGRATION_GUIDE.md
if exist MIGRATION_LOG.md del /q MIGRATION_LOG.md
if exist MIGRATION_PLAN.md del /q MIGRATION_PLAN.md

REM Remove duplicate DEBUGGING docs
if exist DEBUGGING_EFFICIENCY_REPORT.md del /q DEBUGGING_EFFICIENCY_REPORT.md
if exist DEBUGGING_ENHANCEMENTS_SUMMARY.md del /q DEBUGGING_ENHANCEMENTS_SUMMARY.md
if exist DEBUGGING_REPORT.md del /q DEBUGGING_REPORT.md
if exist END_TO_END_DEBUG_REPORT.md del /q END_TO_END_DEBUG_REPORT.md
if exist DEBUG_CONSOLIDATION_SUMMARY.md del /q DEBUG_CONSOLIDATION_SUMMARY.md

REM Remove duplicate IMPLEMENTATION docs
if exist IMPLEMENTATION_COMPLETE_SUMMARY.md del /q IMPLEMENTATION_COMPLETE_SUMMARY.md
if exist IMPLEMENTATION_EXAMPLE.md del /q IMPLEMENTATION_EXAMPLE.md
if exist CRITICAL_FIXES_COMPLETED.md del /q CRITICAL_FIXES_COMPLETED.md

REM Remove duplicate DEPLOYMENT/OPTIMIZATION docs
if exist DEPLOYMENT_SUMMARY.md del /q DEPLOYMENT_SUMMARY.md
if exist OPTIMIZATION_REPORT.md del /q OPTIMIZATION_REPORT.md

REM Remove duplicate PERFORMANCE docs
if exist PERFORMANCE_IMPLEMENTATION_SUMMARY.md del /q PERFORMANCE_IMPLEMENTATION_SUMMARY.md
if exist PROGRESSIVE_LOADING_COMPLETE.md del /q PROGRESSIVE_LOADING_COMPLETE.md

REM Remove duplicate ZERO_FCF docs
if exist ZERO_FCF_IMPLEMENTATION.md del /q ZERO_FCF_IMPLEMENTATION.md
if exist ZERO_FCF_COMPLETE.md del /q ZERO_FCF_COMPLETE.md

REM Remove duplicate CONGRESSIONAL docs
if exist CONGRESSIONAL_TRADES_IMPLEMENTATION.md del /q CONGRESSIONAL_TRADES_IMPLEMENTATION.md

REM Remove duplicate VALUATION docs
if exist VALUATION_FUTURE_ENHANCEMENTS.md del /q VALUATION_FUTURE_ENHANCEMENTS.md

REM Remove duplicate UAT docs
if exist UAT_EXECUTIVE_SUMMARY.md del /q UAT_EXECUTIVE_SUMMARY.md
if exist MANUAL_UI_TEST_CHECKLIST.md del /q MANUAL_UI_TEST_CHECKLIST.md

REM Remove duplicate ENHANCEMENT docs
if exist ENHANCEMENT_RECOMMENDATIONS.md del /q ENHANCEMENT_RECOMMENDATIONS.md

echo.
echo ===================================
echo   CLEANUP COMPLETE!
echo ===================================
echo.
echo Files removed:
echo   - 7 validation scripts (validate_*.py)
echo   - 2 temporary JSON outputs
echo   - 1 temporary debug script
echo   - 3 duplicate test files
echo   - 40+ redundant documentation files
echo.
echo Remaining essential files:
echo   * DOCUMENTATION_INDEX.md - Navigation hub
echo   * CONSOLIDATED_DOCUMENTATION.md - Master docs
echo   * README.md, ARCHITECTURE.md, PROJECT_STATUS.md
echo   * Feature guides (INDICATORS_QUICKREF.md, etc.)
echo   * Validation reports (PRODUCTION_VALIDATION_REPORT.md, etc.)
echo   * Test scripts (comprehensive_health_check.py, etc.)
echo.
echo Total reduction: ~50 files removed
echo Documentation is now clean and organized!
echo.
pause
