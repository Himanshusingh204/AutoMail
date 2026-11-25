# Usage guide

## Daily flow
1. `draftbox run --accounts gmail,outlook --engine claude [--live]` polls every 2 minutes (`--interval`).
2. `draftbox serve` opens the review page. Check yellow highlights, copy or edit, send from your mail app.
3. In `--live` mode, drafts appear in your real Drafts folder. If you edit one, draftbox notices (`edited_by_user`) and never touches it again.

## Status meanings
| Status | Meaning |
|---|---|
| dry-run | Draft exists on the review page only |
| drafted | Draft written to your mailbox |
| edited_by_user | You changed it; hands off |
| skipped | No reply needed (reason shown). Use **Draft anyway** to override |
| dismissed | You or the mailbox removed it |
| failed / gave_up | Engine error; retried up to 3 times, then stops. Reason shown |

## Commands
| Command | Purpose |
|---|---|
| `init` | Create instructions/style/senders templates in `~/.draftbox` |
| `run` | Poll loop. `--once` for one pass, `--live` to write drafts |
| `serve` | Review page. `--engine fake` to try without the CLI |
| `hotkey` | Press a key on an open mail, get a draft in a window. `--engine auto/claude/ollama/gemini` |
| `try FILE` | Draft one pasted mail, no mailbox access |
| `learn-style` | Build style.md from your last Sent replies |
| `purge` | Delete drafts draftbox made that you have not touched |
| `pause` / `resume` | Kill switch (also a button on the page) |
| `stats` / `doctor` | Counts / last successful poll |
| `golden` | 20-mail quality check. Rerun after changing prompts or engine |

## Never-draft rules
OTP / security mails, no-reply senders, newsletters (`List-Unsubscribe`), auto-submitted mail, threads where you wrote last, and any thread labelled `no-ai`.

## Screen hotkey
See [hotkey.md](hotkey.md): Windows and Mac install, the window, engines, troubleshooting.

## Troubleshooting
- "RE-AUTH NEEDED": run `draftbox login-gmail` / `login-outlook` again (you also get a toast).
- Page says "No recent poll!": `run` is not running or failing; check `draftbox doctor`.
- Drafts contain extra commentary: make sure you use this repo's engine (`--setting-sources ""` keeps your personal hooks out).
- Everything lives in `~/.draftbox` (database + your 3 files). Delete the folder to wipe all data.
