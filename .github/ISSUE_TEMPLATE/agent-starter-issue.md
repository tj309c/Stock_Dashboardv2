---
name: AI Agent starter task
about: Small, safe, test-backed task for an AI agent to practice repository workflow
title: "Agent: Add unit tests for ai_model_config SDK fallbacks"
labels: help wanted, good first issue, tests
assignees: ''
---

## Goal

Add unit tests that verify `ai_model_config.create_model_client` raises clear, documented errors when provider SDKs are not available at runtime.

Why this is a good starter task:
- Small, well-scoped change
- Test-backed and safe (no UI changes)
- Exercises mocking, test discovery, and repo PR rules

## Suggested steps for the agent
1. Add tests under `tests/test_ai_model_config.py` that patch module-level values:
   - Patch `ai_model_config.genai` to None and assert creating a Gemini client raises a ValueError indicating SDK unavailable.
   - Patch `ai_model_config.OpenAI` to None and assert creating an OpenAI/Grok client raises a ValueError indicating SDK unavailable.
   - Patch `ai_model_config.anthropic` to None and assert creating a Claude client raises a ValueError indicating SDK unavailable.
2. Run `pytest` locally to ensure tests pass (or fail where appropriate), make fixes, and re-run tests.
3. Open a PR with a concise description, reference this issue, and include test results in the PR body.

## Files to inspect
- `ai_model_config.py` (create_model_client and module-level fallbacks)
- `tests/test_ai_model_config.py` (existing tests and patterns to follow)

---
If you want the tests authored for you, reply to this issue and I'll draft an initial failing test + patch.
