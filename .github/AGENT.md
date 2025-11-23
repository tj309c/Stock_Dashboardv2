# Agent handbook — Stock_Dashboardv2

Short, practical instructions so an AI coding agent starts productive work quickly.

Principles
- Be conservative: prefer small, well-tested edits over sweeping changes.
- Keep the Streamlit UX unchanged unless the task explicitly requires UI updates.
- Tests are the ultimate arbiter. Add or update tests for every behavior change.

Quick context (big picture)
- Single-page Streamlit app. Main entry: `Home.py`. Extra pages live in `pages/`.
- Shared state lives in the `AppContext` dataclass (`app_context.py`) and is created by `initialize_data_and_context` in `app_logic.py`.
- Data-fetch + heavy work: `app_logic.py`, `data_fetcher.py`, `fast_data_fetcher.py`. Use `@st.cache_data` for expensive functions.
- AI features: `ai_model_config.py` (catalog, provider selection) + `ai_services.py`. API keys live in `.streamlit/secrets.toml`.

Developer workflows you must follow
- Install and start (Windows):
  - `install.bat` (installs deps and templates `.streamlit/secrets.toml`)
  - `check-setup.bat` (quick environment check)
  - `start.bat` / `start-dev.bat` (run Streamlit)
- Tests: `pytest` (repo includes `pytest.ini` with `STREAMLIT_SERVER_HEADLESS=true`). Run tests locally before PRs.

Patterns & gotchas specific to this repo
- Use `st.session_state` and `st.query_params` for UI state (see `Home.py` patterns).
- `initialize_data_and_context(..., light_load=True)` is a fast-start path — prefer `light_load` when editing UI scaffolding.
- `AppContext` is the single source of truth for derived values — add derived fields there and initialize them in `initialize_data_and_context`.
- AI model catalog is a single source of truth in `ai_model_config.py`. Add models there and update tests in `tests/test_ai_model_config.py`.

Testing rules for agent code
- New feature or bugfix: include unit tests under `tests/`.
- Tests must be deterministic — mock external services (yfinance, AI SDKs).
- Keep tests focused and fast. Use `mock`/`patch` to avoid network calls.

Example small tasks (safe starters)
- Add a unit test verifying `create_model_client` raises a clear exception if an SDK isn't installed (use patching of `ai_model_config.genai/OpenAI/anthropic`).
- Add a `light_load` test that ensures `initialize_data_and_context(..., light_load=True)` returns an `AppContext` with default fields.

PR etiquette
- Keep changes small and self-contained.
- Update or add tests for every behavioral change.
- In PR description: explain why the change is safe, point to affected files, and list new tests.

If you ever need help
- Read `docs/AI_MODEL_CONFIGURATION_GUIDE.md` and `docs/README-STARTUP.md` for setup and AI model examples.
- Ask for clarification if a change affects cached or session state (Streamlit-specific concerns).

Secrets & API key safety
- The repository explicitly ignores `.streamlit/secrets.toml` (see `.gitignore`). Use `.streamlit/secrets.toml.example` as a template and never commit `secrets.toml`.
- Install pre-commit locally and run `pre-commit install` to automatically block common mistakes (this repo includes `.pre-commit-config.yaml` with `detect-secrets`).
- CI runs `detect-secrets` in `.github/workflows/scan-and-test.yml` so PRs will fail if real secrets are present.

Secrets baseline
- After installing `detect-secrets`, generate an initial baseline and commit it so future scans only flag new secrets:
  ```bash
  pip install detect-secrets
  detect-secrets scan --all-files > .secrets.baseline
  git add .secrets.baseline
  git commit -m "chore: add detect-secrets baseline"
  ```
  The baseline captures any existing false positives and makes future checks actionable.

That's it — be practical, test-driven, and conservative. Good luck.
