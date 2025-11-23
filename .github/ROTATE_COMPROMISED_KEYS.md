Rotate compromised API keys — immediate checklist
===============================================

If your repo had API keys committed to `.env`, treat those keys as compromised and rotate them immediately. Follow the steps below for each provider and then update your secrets storage.

1) Quick global steps (do these immediately)

   - Revoke / rotate each exposed key in the provider dashboard (AlphaVantage, Finnhub, FMP, Polygon, FRED, Visual Crossing, Coinbase, OpenAI, Anthropic, Gemini/Google, X.ai/Grok, etc.).
   - Replace the keys used by CI/CD and servers with the new keys (in GitHub Actions secrets, host environment variables, or `.streamlit/secrets.toml` for local dev where appropriate).
   - Update the local `README` or onboarding docs with guidance for developers to add their own keys to `.streamlit/secrets.toml` or use environment variables.

2) Provider-specific notes (summary)

   - AlphaVantage: Log into https://www.alphavantage.co and issue a new API key; revoke old key(s).
   - Finnhub: Revoke and re-issue keys in https://finnhub.io/dashboard and update any webhook/usage limits.
   - FMP (Financial Modeling Prep): Rotate keys in your FMP account and update the service endpoints.
   - Polygon: In the Polygon dashboard, revoke compromised keys and generate new ones; update rate-limit configs as needed.
   - FRED: Re-issue keys at https://fred.stlouisfed.org if used.
   - OpenAI: Revoke exposed keys and create new ones in the OpenAI dashboard (https://platform.openai.com/account/api-keys); consider switching to org-level keys and reducing permissions.
   - Anthropic Claude: Revoke and rotate at the Anthropic dev portal.
   - Google/Gemini: Rotate API keys via Google Cloud Console and reattach any required IAM permissions.
   - X.ai/Grok: Rotate keys in X.AI account settings.
   - Coinbase: For API credentials, revoke and create new API keys with scoped access.

3) Post-rotation steps

   - Grep or scan codebase and CI history for signs of additional secrets and ensure nothing else was leaked.
   - Create a `.secrets.baseline` file using detect-secrets to reduce false positives and keep CI helpful.
   - Notify teammates and third-party integrators about the incident and the change in keys.

4) Long term / best practices

   - Never commit secrets; use `.streamlit/secrets.toml` (ignored) or environment variables.
   - Use short-lived or scoped keys where possible.
   - Enable monitoring and usage alerts in provider consoles to detect abnormal activity quickly.

If you want, I can produce a customized checklist for a specific provider and help create the PR that updates CI/CD secrets placeholders for you (you would still need to update the real secrets in external dashboards).
