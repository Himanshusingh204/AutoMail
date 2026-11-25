"""Local review page. 127.0.0.1 only; token + Host check; no JS framework."""
import html, os, re, time
from urllib.parse import parse_qs
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from .core import regenerate

CSS = """:root{--bg:#fafafa;--fg:#161616;--mut:#6b6b6b;--card:#fff;--bd:#e4e4e4;--ac:#2f5bea;--warn:#fff3cd;--ok:#e3f5e8;--bad:#fde4e4}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#eee;--mut:#9a9a9a;--card:#1a1a1a;--bd:#2c2c2c;--ac:#7b9bff;--warn:#4a3f12;--ok:#1d3a25;--bad:#4a1d1d}}
*{box-sizing:border-box}body{font:15px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg);margin:0}
main{max-width:820px;margin:0 auto;padding:20px 16px 60px}header{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}
h1{font-size:22px;margin:0}a{color:var(--ac);text-decoration:none}.mut{color:var(--mut);font-size:13px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0}.tabs a{padding:5px 12px;border:1px solid var(--bd);border-radius:99px;background:var(--card);color:var(--fg)}
.tabs a.on{background:var(--ac);color:#fff;border-color:var(--ac)}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px 16px;margin:12px 0}
.top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}.subj{font-weight:600}
.chip{font-size:12px;padding:2px 9px;border-radius:99px;background:var(--bd)}.chip.dry-run,.chip.drafted{background:var(--ok)}.chip.failed,.chip.gave_up{background:var(--bad)}
.draft{white-space:pre-wrap;background:var(--bg);border:1px solid var(--bd);border-radius:8px;padding:10px;margin:10px 0}
mark{background:var(--warn);color:inherit;padding:0 3px;border-radius:3px}.flag{background:var(--warn);padding:4px 8px;border-radius:6px;font-size:13px;margin-top:8px}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}input[type=text],textarea{font:inherit;color:var(--fg);background:var(--bg);border:1px solid var(--bd);border-radius:8px;padding:7px 10px}
input[type=text]{flex:1;min-width:180px}textarea{width:100%;min-height:110px}
button{font:inherit;cursor:pointer;border:1px solid var(--bd);background:var(--card);color:var(--fg);border-radius:8px;padding:6px 12px}button.p{background:var(--ac);color:#fff;border-color:var(--ac)}
.stat{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px}.stat b{font-size:18px}.empty{text-align:center;color:var(--mut);padding:40px 0}"""

TABS = [("all", "All"), ("drafts", "Drafts"), ("skipped", "Skipped"), ("problems", "Problems")]
GROUP = {"drafts": ("drafted", "dry-run", "edited_by_user"), "skipped": ("skipped", "dismissed"), "problems": ("failed", "gave_up")}


def _page(body, token, title="draftbox"):
    return (f"<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{CSS}</style><main>{body}</main>"
            "<script>document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=()=>{navigator.clipboard.writeText(document.getElementById(b.dataset.copy).innerText);b.textContent='Copied'})</script></html>")


def _mark(text):
    return re.sub(r"(\[CONFIRM:[^\]]*\])", r"<mark>\1</mark>", html.escape(text))


def make_app(store, token, engine=None, home=None, load=lambda n, d="": d):
    app = FastAPI()
    q = f"?t={token}"

    @app.middleware("http")
    async def guard(req: Request, call_next):
        if req.headers.get("host", "").split(":")[0] not in ("127.0.0.1", "localhost"):
            return HTMLResponse("forbidden", 403)
        if req.query_params.get("t") != token:
            return HTMLResponse("open the URL printed by `draftbox serve`", 403)
        o = req.headers.get("origin")
        if o and o.split("//")[-1].split(":")[0] not in ("127.0.0.1", "localhost"):
            return HTMLResponse("forbidden", 403)
        return await call_next(req)

    async def form(req): return {k: v[0] for k, v in parse_qs((await req.body()).decode()).items()}

    @app.get("/", response_class=HTMLResponse)
    def index(view: str = "all"):
        age = time.time() - float(store.get("last_ok", "0") or 0)
        paused = store.get("paused") == "1"
        pill = "Paused" if paused else ("Running" if age < 1800 else "No recent poll!")
        m = store.metrics()
        stat = "".join(f"<span><b>{m.get(k, 0)}</b> <span class=mut>{lbl}</span></span>" for k, lbl in
                       (("dry-run", "in review"), ("drafted", "in mailbox"), ("skipped", "skipped"), ("failed", "failed"))) + f"<span><b>{m['edited_pct']}%</b> <span class=mut>edited by you</span></span>"
        tabs = "".join(f"<a class='{'on' if view == k else ''}' href='/{q}&view={k}'>{lbl}</a>" for k, lbl in TABS)
        cards = ""
        for n, (a, i, sender, subj, st, why, draft, flags, did, bh) in enumerate(store.rows()):
            if view in GROUP and st not in GROUP[view]: continue
            fl = f"<div class=flag>Check before sending: {html.escape(flags)}</div>" if flags else ""
            dr = f"<div class=draft id=d{n}>{_mark(draft)}</div>" if draft else ""
            act = ""
            if draft: act += f"<button data-copy=d{n}>Copy draft</button>"
            can_regen = engine and st not in ("drafted", "edited_by_user")
            if st not in ("dismissed", "drafted", "edited_by_user"):
                act += (f"<form method=post action='/dismiss{q}' style='display:inline'><input type=hidden name=a value='{html.escape(a)}'>"
                        f"<input type=hidden name=i value='{html.escape(i)}'><button>Dismiss</button></form>")
            rg = ""
            if can_regen:
                rg = (f"<form method=post action='/regen{q}' class=row style='margin-top:10px'><input type=hidden name=a value='{html.escape(a)}'>"
                      f"<input type=hidden name=i value='{html.escape(i)}'><input type=text name=note placeholder='Optional note, e.g. shorter, say no politely'>"
                      f"<button class=p>{'Draft anyway' if st == 'skipped' else 'Regenerate'}</button></form>")
            cards += (f"<div class=card><div class=top><span class=subj>{html.escape(subj)}</span><span class='chip {st}'>{st}</span></div>"
                      f"<div class=mut>{html.escape(sender)} · {html.escape(a)} · {html.escape(why)}</div>{dr}{fl}<div class=row>{act}</div>{rg}</div>")
        body = (f"<header><h1>draftbox</h1><div class=row><span class=chip>{pill}</span>"
                f"<form method=post action='/{'resume' if paused else 'pause'}{q}'><button>{'Resume' if paused else 'Pause'}</button></form>"
                f"<a href='/settings{q}'>Settings</a></div></header><div class=stat>{stat}</div><div class=tabs>{tabs}</div>"
                f"{cards or '<div class=empty>Nothing here yet. Run <code>draftbox run</code> to process mail.</div>'}"
                "<p class=mut>draftbox only creates drafts. You edit and send from your mail app.</p>")
        return _page(body, token)

    @app.post("/dismiss")
    async def dismiss(req: Request):
        f = await form(req); store.set(f["a"], f["i"], "dismissed")
        return RedirectResponse(f"/{q}", 303)

    @app.post("/pause")
    async def pause(): store.setkv("paused", "1"); return RedirectResponse(f"/{q}", 303)

    @app.post("/resume")
    async def resume(): store.setkv("paused", "0"); return RedirectResponse(f"/{q}", 303)

    @app.post("/regen")
    async def regen(req: Request):
        f = await form(req)
        try:
            regenerate(store, engine, f["a"], f["i"], f.get("note", ""), load("style.md"), load("senders.md"), load("instructions.md"))
        except Exception as e:
            return HTMLResponse(_page(f"<p>Could not regenerate: {html.escape(str(e))}</p><a href='/{q}'>Back</a>", token), 400)
        return RedirectResponse(f"/{q}", 303)

    FILES = [("instructions.md", "Standing instructions", "Rules every draft must follow. One per line."),
             ("style.md", "Writing style", "Tone, length, sign-off. Run `draftbox learn-style` to fill from your Sent folder."),
             ("senders.md", "People", "One per line: email-or-domain: note (e.g. boss@co.com: my manager, formal).")]

    @app.get("/settings", response_class=HTMLResponse)
    def settings(saved: str = ""):
        fs = "".join(f"<h3>{t}</h3><p class=mut>{d}</p><textarea name='{n}'>{html.escape(load(n))}</textarea>" for n, t, d in FILES)
        ok = "<p class=chip style='background:var(--ok)'>Saved</p>" if saved else ""
        return _page(f"<header><h1>Settings</h1><a href='/{q}'>Back</a></header>{ok}<form method=post action='/settings{q}'>{fs}<p><button class=p>Save</button></p></form>", token, "draftbox settings")

    @app.post("/settings")
    async def save(req: Request):
        f = await form(req)
        if home:
            os.makedirs(home, exist_ok=True)
            for n, *_ in FILES:
                if n in f: open(os.path.join(home, n), "w", encoding="utf-8").write(f[n].replace("\r\n", "\n"))
        return RedirectResponse(f"/settings{q}&saved=1", 303)

    return app
