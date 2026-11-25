# Threat model

| Threat | Control |
|---|---|
| Prompt injection via email | Body fenced as untrusted data, fence tags stripped from body, engine runs with all tools off in an empty temp dir, links/addresses not in the original are flagged, 25 hostile-mail tests |
| Accidental send | No send code; test greps source; Outlook has no `Mail.Send` |
| Token theft | OS keyring, least scopes |
| Review page abused by a website | 127.0.0.1 only, random per-run token, Host header check (DNS rebinding) |
| Secrets in git | `.gitignore`, gitleaks pre-commit + CI, audit history before going public |
| Personal mail in logs | Mail bodies are not stored; only ids, subject, sender and the draft |
| Silent failure | `draftbox doctor`, status badge, toast after 30 min without a poll |
| Screenshot leaves the PC (hotkey mode) | `auto` only uses claude CLI or local Ollama; Gemini runs only when you pick it, labelled in the window; key file is chmod 600 |
