# Copilot / AI agent instructions — Stock_Dashboardv2

Short, practical guidance tailored to this repo. Edit minimally, add tests, and preserve the Streamlit UX.

Core architecture (big picture)
- Single-page Streamlit app: `Home.py` is the entrypoint; extra pages live under `pages/`.
- Global state = `AppContext` dataclass (`app_context.py`). Most derived fields are set by `initialize_data_and_context()` in `app_logic.py` — modify there when adding fields.
- Heavy data work happens in `app_logic.py` (look for the `Stock` class and `_fetch_stock_data`). Use `@st.cache_data` for expensive operations.
- AI layer: `ai_model_config.py` (model catalog + factory) and `ai_services.py` (provider adapters). API keys come from `.streamlit/secrets.toml`.

Developer workflows & common commands
- Install (Windows): run `install.bat` (creates `.streamlit/secrets.toml` template and installs deps).
- Quick check: `check-setup.bat`.
- Run app: `start.bat` (normal) or `start-dev.bat` (hot-reload debug). These call `streamlit run Home.py`.
- Tests: run `pytest` from repo root. `pytest.ini` sets env flags (e.g., `STREAMLIT_SERVER_HEADLESS=true`) used in CI.

Project-specific patterns & tips
- UI state: prefer `st.session_state` and `st.query_params` for persistent UI values; renaming keys is a breaking change — keep backwards compatibility when possible.
- To add derived data to the app, update `initialize_data_and_context()` (not many other places derive AppContext).
- Use `light_load=True` for quick dev cycles when instantiating `AppContext` in tests or the UI.
- For AI model work, use `create_model_client(model_id)` from `ai_model_config.py` and follow examples in `AI_MODEL_CONFIGURATION_GUIDE.md`.

Tests & external integration
- Keep tests deterministic; mock external APIs (yfinance, OpenAI/Anthropic/Gemini). See `tests/test_ai_model_config.py` and other tests for patterns.
- Don’t commit real API keys — use `.streamlit/secrets.toml.example` or CI secrets. CI runs `detect-secrets` and blocks secrets in PRs.

Files to inspect first when contributing
- UI: `Home.py`, `pages/*` — preserve UX flow.
- Core: `app_logic.py`, `app_context.py`, `data_fetcher.py`, `fast_data_fetcher.py`.
- AI: `ai_model_config.py`, `ai_services.py`, `AI_MODEL_CONFIGURATION_GUIDE.md`.

PR checklist for agents
- Add targeted unit tests; update `tests/` when AppContext shapes change.
- Mock external APIs and secrets in tests.
- Keep Streamlit state keys and query params backwards-compatible.

If any of this is unclear or you want examples applied to a specific change, ask and I’ll expand the instructions or add exemplar edits/tests.
