import argparse, os, secrets, subprocess, sys, time
from . import providers
from .core import Store, run_once, check_edits, learn_style, purge
from .engines import ClaudeCLI, FakeEngine


def _store():
    os.makedirs(providers.HOME, exist_ok=True)
    return Store(os.path.join(providers.HOME, "draftbox.db"))


def _read(name, default=""):
    p = os.path.join(providers.HOME, name)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else default


def _style(): return _read("style.md", "Short, polite, plain English.")


def notify(text, quiet=(22, 8)):
    """stderr always; Windows balloon toast outside quiet hours."""
    print("NOTICE:", text, file=sys.stderr)
    hr = time.localtime().tm_hour
    if hr >= quiet[0] or hr < quiet[1]: return
    msg = text.replace("'", "")
    ps = ("Add-Type -AssemblyName System.Windows.Forms;$n=New-Object Windows.Forms.NotifyIcon;"
          "$n.Icon=[Drawing.SystemIcons]::Information;$n.Visible=$true;"
          f"$n.ShowBalloonTip(5000,'draftbox','{msg}',0);Start-Sleep 6;$n.Dispose()")
    try: subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
    except OSError: pass


def main(argv=None):
    ap = argparse.ArgumentParser(prog="draftbox", description="Drafts replies. Never sends.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="poll loop")
    r.add_argument("--accounts", default="demo", help="comma list: demo, gmail, outlook")
    r.add_argument("--engine", default="fake", choices=["fake", "claude"])
    r.add_argument("--live", action="store_true", help="write drafts to mailbox (default: dry-run)")
    r.add_argument("--once", action="store_true")
    r.add_argument("--interval", type=int, default=120)
    s = sub.add_parser("serve"); s.add_argument("--port", type=int, default=8765)
    s.add_argument("--engine", default="claude", choices=["fake", "claude"]); s.add_argument("--no-open", action="store_true")
    for n in ("pause", "resume", "doctor", "stats", "login-outlook"): sub.add_parser(n)
    g = sub.add_parser("login-gmail"); g.add_argument("account"); g.add_argument("client_file")
    for n in ("learn-style", "purge", "golden"):
        x = sub.add_parser(n); x.add_argument("--account", default="demo"); x.add_argument("--engine", default="fake", choices=["fake", "claude"])
    t = sub.add_parser("try", help="draft for one pasted mail (no mailbox access)")
    t.add_argument("file"); t.add_argument("--from", dest="sender", default="Test <test@example.com>")
    t.add_argument("--subject", default="(no subject)"); t.add_argument("--engine", default="claude", choices=["fake", "claude"])
    sub.add_parser("hotkey", help="Ctrl+Alt+D: read screen, show a draft").add_argument("--engine", default="auto", choices=["auto", "claude", "ollama", "gemini"])
    sub.add_parser("init", help="create instructions.md / style.md / senders.md templates")
    a = ap.parse_args(argv)
    if a.cmd == "hotkey":
        from .hotkey import listen; return listen(a.engine)
    st = _store()
    if a.cmd == "init":
        NL = chr(10)
        tpl = {'instructions.md': NL.join(['# Rules here are optional; lines starting with # are ignored. Empty = the AI decides itself.', "# Sign off with 'Thanks, Himanshu'.", '# Never agree to meetings; say I will confirm.']) + NL,
               'style.md': '# Optional tone notes. Empty = professional, natural tone.' + NL,
               'senders.md': NL.join(['# email-or-domain: note', '# boss@company.com: my manager, formal']) + NL}
        for n, c in tpl.items():
            p = os.path.join(providers.HOME, n)
            if not os.path.exists(p): open(p, "w", encoding="utf-8").write(c)
        return print("templates in", providers.HOME)
    if a.cmd == "try":
        from .core import Msg, build_prompt, new_links, placeholders, sender_notes
        body = open(a.file, encoding="utf-8").read()
        m = Msg("try", "try", a.sender, a.subject, body)
        d = (ClaudeCLI() if a.engine == "claude" else FakeEngine()).draft(build_prompt(m, _style(), sender_notes(_read("senders.md"), a.sender), _read("instructions.md"))).strip()
        print(d, "\n\n--- checks:", new_links(d, body) or "no new links", "|", placeholders(d) or "no [CONFIRM]")
        return

    if a.cmd in ("pause", "resume"): st.setkv("paused", "1" if a.cmd == "pause" else "0"); print(a.cmd + "d")
    elif a.cmd == "login-gmail": providers.GmailProvider.login(a.account, a.client_file)
    elif a.cmd == "login-outlook": providers.OutlookProvider().login()
    elif a.cmd == "stats": print(st.metrics())
    elif a.cmd == "learn-style":
        t = learn_style(providers.get(a.account))
        open(os.path.join(providers.HOME, "style.md"), "w", encoding="utf-8").write(t); print("style.md written:", len(t), "chars")
    elif a.cmd == "purge": print("deleted", purge(providers.get(a.account), st), "untouched drafts")
    elif a.cmd == "golden":
        from .golden import run_golden
        run_golden(ClaudeCLI() if a.engine == "claude" else FakeEngine())
    elif a.cmd == "doctor":
        age = time.time() - float(st.get("last_ok", "0") or 0)
        print("last successful poll:", "never" if age > 1e9 else f"{int(age)}s ago", "| paused:", st.get("paused") == "1")
        print("failed items:", sum(1 for r in st.rows() if r[4] in ("failed", "gave_up")))
    elif a.cmd == "serve":
        import uvicorn
        from .web import make_app
        tok = secrets.token_urlsafe(16)
        url = f"http://127.0.0.1:{a.port}/?t={tok}"
        print("open", url)
        if not a.no_open:
            import webbrowser; webbrowser.open(url)
        uvicorn.run(make_app(st, tok, ClaudeCLI() if a.engine == "claude" else FakeEngine(), providers.HOME, _read), host="127.0.0.1", port=a.port, log_level="warning")
    elif a.cmd == "run":
        provs = [providers.get(n.strip()) for n in a.accounts.split(",")]
        eng = ClaudeCLI() if a.engine == "claude" else FakeEngine()
        while True:
            for p in provs:
                try:
                    n = run_once(p, eng, st, _style(), dry_run=not a.live, senders=_read("senders.md"), instructions=_read("instructions.md"))
                    if a.live: check_edits(p, st)
                    print(f"{p.account}: {n} drafted")
                except SystemExit as e: notify(str(e))
                except Exception as e: notify(f"{p.account}: poll failed: {e}")
            if a.once: break
            if time.time() - float(st.get("last_ok", "0") or 0) > 1800: notify("no successful poll for 30 minutes")
            time.sleep(a.interval)


if __name__ == "__main__": main()
