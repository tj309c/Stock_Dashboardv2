# Copilot / AI agent instructions for Stock_Dashboardv2

Be practical and concise — focus on *this* codebase. When you edit or add files, prefer minimal, well-tested changes and keep the Streamlit UX intact.

Key concepts (big picture)
- Streamlit single-page app with multiple pages under `pages/` and `Home.py` as the main entrypoint. Use `st.session_state` and `st.query_params` for persistent UI state across user actions.
- Central shared state is the `AppContext` dataclass (`app_context.py`) populated by `initialize_data_and_context` (in `app_logic.py`). Changes to data flow usually route through these places.
- Data fetching and heavy work is done in `app_logic.py` (`Stock` class + `_fetch_stock_data`). Use `@st.cache_data` when adding expensive operations to avoid re-fetching.
- AI features are managed in `ai_model_config.py` and `ai_services.py`. Models are selected from a catalog and rely on API keys stored in `.streamlit/secrets.toml`.

Developer workflows & commands
- Install dependencies: `install.bat` (Windows) which runs `pip install -r requirements.txt` and creates a `.streamlit/secrets.toml` template.
- Quick environment check: `check-setup.bat`.
- Run the app (Windows): `start.bat` (normal) or `start-dev.bat` (hot-reload, debug). These run `streamlit run Home.py`.
- Tests: Run `pytest` from the repo root. `pytest.ini` sets environment flags used for test runs (e.g., `STREAMLIT_SERVER_HEADLESS=true`).

Project-specific patterns & conventions
- Tests live under `tests/` and follow `test_*.py` naming convention. Use `pytest -q` or `pytest -v` when needed.
- AppContext holds many derived fields; prefer modifying `initialize_data_and_context` when you need new fields derived from fetched data.
- Lightweight startup option `light_load=True` is supported in `initialize_data_and_context` for fast UI iteration.
- AI provider mapping uses environment secrets: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `XAI_API_KEY` in `.streamlit/secrets.toml`.

When working on AI integration (how-to)
- To select or inspect available models, inspect `ai_model_config.py` (model catalog and `get_model_info`, `create_model_client`).
- Use `create_model_client(model_id)` to get a provider-specific client; handle provider-specific API calls (examples in `AI_MODEL_CONFIGURATION_GUIDE.md`).
- Respect existing cost awareness in UI: `render_model_selector()` shows cost and token limits — avoid adding expensive defaults.

Testing / validation tips for agents
- Refer to `tests/test_ai_model_config.py` for examples testing model catalog / client creation logic.
- Keep tests small and deterministic; use mocks for external APIs (yfinance, OpenAI/Anthropic/Gemini).
- Run unit tests locally with `pytest` and only add integration tests when they don’t require private API keys.

Files you’ll touch most
- App entry / pages: `Home.py`, `pages/*.py`
- Core logic: `app_logic.py`, `app_context.py`, `data_fetcher.py`
- AI config: `ai_model_config.py`, `ai_services.py`, `AI_MODEL_CONFIGURATION_GUIDE.md`
- Dev scripts / docs: `start.bat`, `start-dev.bat`, `install.bat`, `check-setup.bat`, `docs/README-STARTUP.md`

Notes for PRs
- Include tests for behavior changes. If you change data shapes in `AppContext`, update existing tests and add new ones under `tests/`.
- Don't check in `.streamlit/secrets.toml` with real keys — tests should mock secret-based behavior.
	- `.streamlit/secrets.toml` is git-ignored and a template `.streamlit/secrets.toml.example` is provided. Use the example and never commit your real keys.
	- The repo includes `.pre-commit-config.yaml` and a CI job (`.github/workflows/scan-and-test.yml`) that runs `detect-secrets`. Install pre-commit locally (`pip install pre-commit`) and run `pre-commit install` to block accidental secrets before pushing.
- Keep UI changes backwards-compatible; Streamlit state management is sensitive to key names and session defaults.

If anything is unclear or you'd like more examples (prompts/typical edits), ask and I’ll expand a short sample edit + tests.  
