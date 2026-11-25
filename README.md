# draftbox

**Open a mail, press one key, get a ready-to-edit professional reply.** Works on Windows and Mac, with Outlook, Gmail or any mail app. It never sends anything: you read, change and send it yourself.

## Quick start (2 minutes)

**Windows**
```
py -m venv .venv
.venv\Scripts\activate
pip install -e .
draftbox hotkey
```
**Mac**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
draftbox hotkey
```
Then open any mail and press **Ctrl+Alt+D** (Mac: **Ctrl+Shift+D**). A window shows your draft.
Mac first time: allow *Accessibility* and *Screen Recording* for your terminal. Details and fixes: [docs/hotkey.md](docs/hotkey.md).

You need one AI engine (pick any):
| Engine | Cost | Privacy |
|---|---|---|
| **claude** (default): the `claude` CLI, logged in on your PC | your Claude plan | screenshot goes to Claude |
| **ollama**: your own model on your PC (`ollama pull llama3.2-vision`) | free | never leaves your PC |
| **gemini**: only when *you* pick it in the window; paste a key once | free tier / paid | **whole screen goes to Google** |

`auto` (the default) uses claude, then ollama, and **never** gemini by itself.

## What you see

```
+------------------------------------------------------------+
| To: priya@x.com                                            |
| Subject: Re: Budget meeting                                |
|                                                            |
| Hi Priya,                                                  |
| Monday 3pm works. I will bring the Q3 numbers. [CONFIRM:   |
| room]  <- yellow: check this fact                          |
|                                                            |
+------------------------------------------------------------+
| Change request: [ shorter, more formal...  ] [claude v] [Redo]
| [Copy]  [Open in mail app (F8)]                     [Close]|
+------------------------------------------------------------+
```
- **Edit it** like normal text.
- **Don't like it?** Type "shorter", "more formal", "say no politely", "reply in Hindi" and press **Redo**. As many times as you want.
- **Copy** or **Open in mail app (F8)**: opens your default mail app (set Outlook as default to get Outlook) with To, Subject and body filled. You press Send there.

## Make it sound like you
Run `draftbox init`, then edit the files in `~/.draftbox`:
| File | What to put |
|---|---|
| `instructions.md` | Rules: "under 60 words", "sign off Thanks, Sam" |
| `style.md` | Tone. Or `draftbox learn-style --account gmail` fills it from your Sent folder |
| `examples.md` | 4-6 of your own real replies (best quality boost) |
| `senders.md` | `boss@co.com: my manager, formal` |

## Safety and privacy
- **No send code exists.** A test fails if any appears. The F8 button only opens your mail app.
- Your screenshot is read once and not stored. With `claude`/`ollama` it stays in your own account / PC. Only `gemini`, picked by you, sends it to Google, and the window says so.
- The AI is told everything in the mail is untrusted data, runs with no tools except reading the screenshot, and has 25 prompt-injection tests.
- Anything it is unsure about is marked `[CONFIRM: ...]` in yellow instead of being invented.
- Secrets: the Gemini key is saved only on your device (`~/.draftbox/gemini.key`, owner-only). Mailbox tokens live in the OS keyring. CI scans the full history for leaked secrets.
More: [docs/threat-model.md](docs/threat-model.md), [SECURITY.md](SECURITY.md).

## Optional: background mailbox mode (Gmail / Outlook)
Instead of pressing a key, draftbox can watch your inbox, decide which mails need a reply, and put drafts in your **Drafts folder** (or a review page).
```
draftbox init
draftbox run --once                  # demo mailbox, no accounts needed
draftbox serve --engine fake         # review page in your browser
```
Real accounts: set up [Gmail](docs/setup-gmail.md) or [Outlook](docs/setup-outlook.md), then `draftbox run --accounts gmail --engine claude` (starts in dry-run; add `--live` after a week of good drafts). Run at logon: `scripts\install-task.ps1`. Outlook uses `Mail.ReadWrite` only, never `Mail.Send`.

Try one mail without any mailbox: `draftbox try mail.txt --from "Priya <priya@x.com>" --subject "Budget meeting"`.

## All commands
`hotkey` · `run` · `serve` · `try` · `init` · `learn-style` · `purge` · `pause` / `resume` · `stats` · `doctor` · `golden` · `login-gmail` · `login-outlook`. See [docs/usage.md](docs/usage.md).

## Troubleshooting
| Problem | Fix |
|---|---|
| Nothing happens on the hotkey (Mac) | Allow Accessibility for your terminal, restart it |
| `claude CLI not found` | Install Claude Code and log in, or run `draftbox hotkey --engine ollama` |
| `no vision model in Ollama` | `ollama pull llama3.2-vision` |
| Draft misses details | The whole mail must be visible on screen. Scroll, press again |
| Wrong To address | It is read off the screen. Check it before Send |
More in [docs/hotkey.md](docs/hotkey.md).

## Not built yet
Gmail/Graph delta sync (polls latest mails), thread summaries, calendar and attachment reading, push notifications, one-click send from a real mailbox (the F8 button hands over to your mail app on purpose). The `claude -p` engine's subscription use: [docs/adr/0002-engine.md](docs/adr/0002-engine.md).

## Develop
`pip install -e ".[dev]"` then `pytest` (48 tests: 25 prompt-injection cases, every button of the draft window). CI runs on Windows, Mac and Linux. [CONTRIBUTING.md](CONTRIBUTING.md). MIT licence.
