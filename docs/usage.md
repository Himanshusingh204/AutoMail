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
| `try FILE` | Draft one pasted mail, no mailbox access |
| `learn-style` | Build style.md from your last Sent replies |
| `purge` | Delete drafts draftbox made that you have not touched |
| `pause` / `resume` | Kill switch (also a button on the page) |
| `stats` / `doctor` | Counts / last successful poll |
| `golden` | 20-mail quality check. Rerun after changing prompts or engine |

## Never-draft rules
OTP / security mails, no-reply senders, newsletters (`List-Unsubscribe`), auto-submitted mail, threads where you wrote last, and any thread labelled `no-ai`.

## Screen hotkey (`draftbox hotkey`)
Open any mail on screen, press **Ctrl+Alt+D**. A window shows a draft you can edit. No mailbox login needed. Works on Windows, Mac and Linux (Mac: allow Accessibility for your terminal).

| Engine | What it is | Where your screenshot goes |
|---|---|---|
| `auto` (default) | Uses an AI already logged in on this PC (`claude` CLI), else your own local Ollama model. Never Gemini. | Stays on this PC / your Claude account |
| `claude` | The logged-in `claude` CLI | Claude |
| `ollama` | Your own model, free and offline. Needs a vision model: `ollama pull llama3.2-vision` (override with `OLLAMA_MODEL`) | Never leaves the PC |
| `gemini` | Better quality, only when you pick it. Key from `GEMINI_API_KEY` or pasted once in the window (saved in `~/.draftbox/gemini.key`) | **Sent to Google, the whole screen** |

Start with `draftbox hotkey --engine ollama` to pin one. In the window: edit the draft, **Copy**, **Open in mail app (F8)** (fills To/Subject/body; you press Send yourself, draftbox never sends), or pick another engine in the dropdown and **Redo**. Put 4-6 of your own old replies in `~/.draftbox/examples.md` to teach it your tone. Close other windows before using `gemini`: the whole screen is sent. Works with Outlook (desktop, new Outlook, outlook.com in a browser) because it reads the screen. F8 opens your *default* mail app: to get Outlook, set it in Windows Settings > Apps > Default apps > Mail.

## Troubleshooting
- "RE-AUTH NEEDED": run `draftbox login-gmail` / `login-outlook` again (you also get a toast).
- Page says "No recent poll!": `run` is not running or failing; check `draftbox doctor`.
- Drafts contain extra commentary: make sure you use this repo's engine (`--setting-sources ""` keeps your personal hooks out).
- Everything lives in `~/.draftbox` (database + your 3 files). Delete the folder to wipe all data.
