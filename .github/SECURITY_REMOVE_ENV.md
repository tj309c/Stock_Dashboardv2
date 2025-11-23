SECURITY: Removing .env and rotating leaked keys
===============================================

This repository previously contained a tracked `.env` file with live API keys. This is a security risk — you should remove the file from the current working tree, purge it from Git history, and rotate any exposed keys immediately.

Immediate actions we took in this repository:

- Redacted the content of the tracked `.env` file and replaced the contents with placeholders (no real secrets remain in the working tree).
- Added `.env.example` to the repo with placeholders and usage instructions.
- Ensured `.env` is in `.gitignore` so it won't be re-added by accident.

Recommended next steps (must be executed locally by a repository maintainer):

1) Stop tracking `.env` in the current commit and commit that change

   git rm --cached .env
   git add .env.example
   git commit -m "chore(secrets): stop tracking .env and add .env.example"

2) Purge `.env` from Git history (pick one tool below)

   IMPORTANT: Purging history rewrites commits and requires a force-push. Coordinate with your team and prefer doing this on a non-main branch first.

   Option A — Using BFG (simpler):

     # Install BFG (https://rtyley.github.io/bfg-repo-cleaner/)
     java -jar bfg.jar --delete-files .env
     git reflog expire --expire=now --all && git gc --prune=now --aggressive
     git push --force

   Option B — Using git filter-repo (modern and recommended):

     # Install git-filter-repo (https://github.com/newren/git-filter-repo)
     git filter-repo --invert-paths --paths .env
     # verify, then force push
     git push origin --force --all
     git push origin --force --tags

   After rewriting history, collaborators must re-clone the repo or follow the migration instructions provided by git-filter-repo / BFG.

3) Rotate all secrets that may have been exposed

   - Immediately rotate keys for ALL services that were present in the old `.env` (AlphaVantage, Finnhub, FMP, Polygon, FRED, Visual Crossing, Coinbase, OpenAI, Anthropic, Google/Gemini, X.ai/grok, etc.).
   - Treat those keys as compromised — revoke and create new keys from each vendor portal.
   - Update the repo to point to secure storage: move provider keys to `.streamlit/secrets.toml` (ignored) or set them as environment variables in CI/CD and deployment environments.

4) Add a secrets baseline for detect-secrets and update CI

   - Run `detect-secrets scan > .secrets.baseline` and commit the baseline.
   - Update CI to scan for future leaks (CI workflow already configured in this repo to run detect-secrets + tests).

5) Notify stakeholders and rotate any downstream integrations (e.g., server credentials, third-party dashboards).

If you want, I can prepare the exact terminal commands you should run locally, and optionally generate a safe PR that:

- removes tracked .env (via content redaction or removal),
- adds `.env.example`,
- adds this security guidance file, and
- creates a detect-secrets baseline file (but cannot rotate keys for you).
