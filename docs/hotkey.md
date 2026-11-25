# Screen hotkey guide

Open a mail, press the hotkey, get a draft reply you can change. **draftbox never sends anything.**

## Install (once)
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
Mac extras: if Python says `No module named _tkinter`, run `brew install python-tk`. On first use macOS asks for permission: **System Settings > Privacy & Security > Accessibility** (for the hotkey) and **Screen Recording** (to read the mail), for the app you run `draftbox` from (Terminal, iTerm, VS Code). Then restart that app.

Leave the terminal open. Press **Ctrl+Alt+D** (Windows/Linux) or **Ctrl+Shift+D** (Mac; Option+letter types special characters on a Mac).

## What happens
1. Open the mail you want to answer, fully visible on screen (scroll so the whole mail shows; only what is on screen is read).
2. Press the hotkey. A notification says "Reading screen...".
3. A window opens with the draft. Nothing has been sent.

## The window
| Part | What it does |
|---|---|
| Draft box | Click and edit like any text. Scrolls if long. **Yellow** = `[CONFIRM: ...]`, a fact the AI did not know. Fill it in. |
| **Change request** + **Redo** | Don't like it? Type what to change (`shorter`, `more formal`, `say no politely`, `reply in Hindi`) and press Redo. It rewrites the draft currently in the box, including any edits you made by hand. Empty box = a fresh variation. Redo again as often as you like. |
| Engine dropdown | Which AI redoes it: `claude`, `ollama` (own model), `gemini`. |
| **Copy** | Copies the draft. Paste into your mail. |
| **Open in mail app (F8)** | Opens your default mail app (Outlook, Apple Mail, Gmail...) with To, Subject and body filled. You check the address and press Send there. Long mails: To and Subject are filled and the body is on your clipboard (Ctrl+V / Cmd+V). On a Mac laptop F8 may need the `fn` key. |
| **Close** | Closes the window. |

If the mail needs no reply (newsletter, notification) you only get a notification saying why.

## Engines
| `--engine` | What it is | Your screenshot goes to |
|---|---|---|
| `auto` (default) | Tries the logged-in `claude` CLI, then your own Ollama. Never Gemini. | Your Claude account, or nowhere (Ollama) |
| `claude` | The `claude` CLI, logged in on this PC | Claude |
| `ollama` | Your own model, free and offline. `ollama pull llama3.2-vision` once. `OLLAMA_MODEL` picks another. | Never leaves the PC |
| `gemini` | Extra quality. Key from `GEMINI_API_KEY` (env var or a `.env` file, see `.env.example`), or pasted once in the window (saved in `~/.draftbox/gemini.key`) | **Google. The whole screen, not just the mail.** Close other windows first |

Example: `draftbox hotkey --engine ollama`.

## Make the drafts sound like you
Files in `~/.draftbox` (run `draftbox init` to create them; lines starting with `#` are ignored):
- `instructions.md`: rules ("under 80 words", "sign off Regards, Sam").
- `style.md`: tone notes.
- `senders.md`: `boss@co.com: my manager, formal`.
- `examples.md`: paste 4 to 6 of your own real replies. Biggest quality jump.

## Works with Outlook, Gmail, anything
It reads pixels, so it works with Outlook (desktop, new Outlook, outlook.com), Gmail, Apple Mail, Thunderbird. To make F8 open **Outlook**, set it as your default mail app (Windows: Settings > Apps > Default apps > Mail; Mac: Mail app > Settings > Default email reader).

## Troubleshooting
| Problem | Fix |
|---|---|
| `hotkey Ctrl+Alt+D already taken` | Another app uses it. Close it, or run draftbox hotkey once only |
| Mac: nothing happens on the hotkey | Give your terminal Accessibility permission, restart it |
| Mac: draft is about a blank/desktop screen | Give Screen Recording permission, restart the terminal |
| `Failed: claude: claude CLI not found` | Install Claude Code and log in, or use `--engine ollama` |
| `no vision model in Ollama` | `ollama pull llama3.2-vision` |
| `no Gemini key` | Pick `gemini` in the window and press Redo; paste the key once |
| Draft misses details | The whole mail must be visible on screen; scroll and press again |
| Wrong To address | The AI read it off the screen. Always check before Send |
