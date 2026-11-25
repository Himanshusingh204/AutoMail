# Gmail setup

1. console.cloud.google.com: new project, enable **Gmail API**.
2. OAuth consent screen: External, add yourself as test user, then publish to **In production** (unverified is fine for personal use) so refresh tokens do not expire after 7 days.
3. Credentials: OAuth client ID, type **Desktop app**, download JSON.
4. `draftbox login-gmail gmail path\to\client_secret.json` (click through the unverified-app warning).
5. `draftbox run --accounts gmail --engine claude` (dry-run), review at `draftbox serve`, then add `--live`.
