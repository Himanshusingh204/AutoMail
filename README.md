# draftbox

Reads your Gmail / Outlook inbox, decides which mails need a reply, and writes a **draft** reply in your own style. You review it, edit it and press send yourself in your mail app.

**It never sends.** There is no send code (a test fails if one appears) and the Outlook scope is `Mail.ReadWrite` only.

## 5-minute demo (no accounts needed)
```
uv venv
uv pip install -e ".[dev]"
.venv\Scripts\draftbox init                      # creates your instruction files
.venv\Scripts\draftbox run --once                # demo mailbox, fake engine
.venv\Scripts\draftbox serve --engine fake       # opens the review page in your browser
```

## Try it on a real mail (safe, no mailbox access)
Paste the mail text into `mail.txt`, then:
```
draftbox try mail.txt --from "Priya <priya@x.com>" --subject "Budget meeting"
```
Needs the `claude` CLI logged in. Prints the draft plus safety checks (new links, `[CONFIRM]` placeholders).

## Screen hotkey: read the open mail, get a draft
Open any mail on screen, press **Ctrl+Alt+D**. A window shows a draft you can edit. No mailbox login needed. Works on Windows, Mac and Linux (Mac: allow Accessibility for your terminal).

| Engine | What it is | Where your screenshot goes |
|---|---|---|
| `auto` (default) | Uses an AI already logged in on this PC (`claude` CLI), else your own local Ollama model. Never Gemini. | Stays on this PC / your Claude account |
| `claude` | The logged-in `claude` CLI | Claude |
| `ollama` | Your own model, free and offline. Needs a vision model: `ollama pull llama3.2-vision` (override with `OLLAMA_MODEL`) | Never leaves the PC |
| `gemini` | Better quality, only when you pick it. Key from `GEMINI_API_KEY` or pasted once in the window (saved in `~/.draftbox/gemini.key`) | **Sent to Google, the whole screen** |

Start with `draftbox hotkey --engine ollama` to pin one. In the window: edit the draft, **Copy**, **Open in mail app (F8)** (fills To/Subject/body; you press Send yourself, draftbox never sends), or pick another engine in the dropdown and **Redo**. Put 4-6 of your own old replies in `~/.draftbox/examples.md` to teach it your tone. Close other windows before using `gemini`: the whole screen is sent. Works with Outlook (desktop, new Outlook, outlook.com in a browser) because it reads the screen. F8 opens your *default* mail app: to get Outlook, set it in Windows Settings > Apps > Default apps > Mail.

## Your instructions
`draftbox init` creates instruction files in `~/.draftbox` (or edit them in the page: **Settings**):
| File | What it is |
|---|---|
| `instructions.md` | Rules every draft must follow: "under 60 words", "sign off Thanks, Sam", "reply in Hinglish if they do" |
| `style.md` | Tone. `draftbox learn-style --account gmail` fills it from your Sent folder |
| `examples.md` | 4-6 of your real old replies (hotkey mode copies their tone) |
| `senders.md` | `boss@co.com: my manager, formal` , per person/domain notes |

## Review page (`draftbox serve`)
- Tabs: All / Drafts / Skipped / Problems, with a reason shown for every skip.
- **Copy draft**, **Dismiss**, **Regenerate** with a one-off note ("shorter", "say no politely"), **Draft anyway** for a skipped mail.
- Yellow highlights = `[CONFIRM: ...]` facts the AI was unsure about, and any new link/address it added. Check these.
- Pause/Resume, Settings editor. Runs on `127.0.0.1` only, with a per-run secret token in the URL.

## Real accounts
1. Set up access: [Gmail](docs/setup-gmail.md) / [Outlook](docs/setup-outlook.md).
2. `draftbox run --accounts gmail --engine claude` starts in **dry-run** (drafts appear only on the review page).
3. After a week of good drafts add `--live` to write them into your mailbox Drafts folder.
4. Run at logon: `scripts\install-task.ps1`.

## Commands
`run` · `serve` · `hotkey` · `try` · `init` · `learn-style` · `purge` (delete untouched drafts it made) · `pause` / `resume` · `stats` · `doctor` · `golden` · `login-gmail` · `login-outlook`. See [docs/usage.md](docs/usage.md).

## Privacy and safety
Tokens live in the OS keyring. Original mail text is kept 30 days (for Regenerate), then erased; drafts and metadata stay. Mail text is fenced as untrusted data, the AI runs with all tools off. Details: [docs/threat-model.md](docs/threat-model.md), [SECURITY.md](SECURITY.md).

## Not built yet
Gmail history / Graph delta sync (polls latest mails instead), thread summaries, calendar and attachment reading, push notifications, edit-distance metric. Verify that `claude -p` runs on your subscription before relying on it: [docs/adr/0002-engine.md](docs/adr/0002-engine.md).

## Develop
`pytest` (44 tests incl. 25 prompt-injection cases). Contributing: [CONTRIBUTING.md](CONTRIBUTING.md). MIT licence.
