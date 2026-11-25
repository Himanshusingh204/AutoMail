# Security

- draftbox never sends mail: there is no send code, a test fails if one appears, and the Outlook scope is `Mail.ReadWrite` only. (Gmail's `gmail.compose` scope can technically send; protection there is code + tests.)
- Tokens live in the OS keyring. Real config/data live in `~/.draftbox`, never in the repo.
- Report vulnerabilities privately via GitHub Security Advisories on this repo.
- Revoke access any time: Google https://myaccount.google.com/permissions , Microsoft https://account.live.com/consent/Manage

See `docs/threat-model.md`.
