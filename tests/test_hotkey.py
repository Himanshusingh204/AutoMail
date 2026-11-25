import pytest
from draftbox import hotkey


def boom(*a, **k): raise RuntimeError("x")


def test_auto_prefers_claude_then_ollama_never_gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(hotkey, "via_gemini", lambda *a: 1 / 0)
    monkeypatch.setattr(hotkey, "via_claude", lambda p, note="": "c")
    monkeypatch.setattr(hotkey, "via_ollama", lambda p, note="": "o")
    assert hotkey.draft("auto", b"") == "c"
    monkeypatch.setattr(hotkey, "via_claude", boom)
    assert hotkey.draft("auto", b"") == "o"
    monkeypatch.setattr(hotkey, "via_ollama", boom)
    with pytest.raises(RuntimeError, match="claude: x | ollama: x"): hotkey.draft("auto", b"")


def test_explicit_gemini_and_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(hotkey.providers, "HOME", "/nonexistent")
    with pytest.raises(RuntimeError, match="no Gemini key"): hotkey.draft("gemini", b"")


def test_ollama_picks_vision_model(monkeypatch):
    class R:
        def __init__(s, j): s.j = j
        def json(s): return s.j
        def raise_for_status(s): pass
    sent = {}
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.setattr(hotkey.requests, "get", lambda *a, **k: R({"models": [{"name": "llama3:8b"}, {"name": "llama3.2-vision:11b"}]}))
    monkeypatch.setattr(hotkey.requests, "post", lambda u, json, **k: sent.update(json) or R({"message": {"content": " hi "}}))
    assert hotkey.via_ollama(b"png") == "hi" and sent["model"] == "llama3.2-vision:11b"
    monkeypatch.setattr(hotkey.requests, "get", lambda *a, **k: R({"models": [{"name": "llama3:8b"}]}))
    with pytest.raises(RuntimeError, match="ollama pull"): hotkey.via_ollama(b"png")


def test_mailto_prefills_and_flags_long_body(monkeypatch):
    urls = []
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", urls.append)
    assert hotkey.mailto("To: a@b.com\nSubject: Re: Hi\n\nHello Sam,\nOK.") is True
    assert urls[0].startswith("mailto:a@b.com?subject=Re%3A%20Hi&body=Hello")
    assert hotkey.mailto("Subject: x\n\n" + "word " * 600) is False
    assert "&body=" not in urls[1]


# ---- review window: every button, driven for real (skipped when there is no display) ----
def _walk(w):
    for c in w.winfo_children():
        yield c
        yield from _walk(c)


def _run(monkeypatch, script, text="To: a@b.com\nSubject: Re: x\n\nHi [CONFIRM: date]", png=b"p"):
    tk = pytest.importorskip("tkinter")

    def loop(self):
        script(self)
        try: self.destroy()
        except tk.TclError: pass
    monkeypatch.setattr(tk.Tk, "mainloop", loop)
    init = tk.Tk.__init__  # hide the window the moment it exists so the test never flashes on screen
    monkeypatch.setattr(tk.Tk, "__init__", lambda self, *a, **k: (init(self, *a, **k), self.withdraw())[0])
    try: hotkey.review(text, png)
    except tk.TclError as e: pytest.skip(f"no display: {e}")


def _btn(r, text):
    return next(w for w in _walk(r) if w.winfo_class() == "Button" and text in w.cget("text"))


def _text(r): return next(w for w in _walk(r) if w.winfo_class() == "Text")
def _status(r): return next(w for w in _walk(r) if w.winfo_class() == "Label" and w.cget("fg") == "#555").cget("text")


def test_window_copy_mail_close_and_highlight(monkeypatch):
    import webbrowser
    urls, seen = [], {}
    monkeypatch.setattr(webbrowser, "open", urls.append)

    def s(r):
        t = _text(r)
        assert t.tag_ranges("c")  # [CONFIRM] is highlighted
        assert r.bind("<F8>")
        t.insert("end", " edited")  # user edits by hand
        _btn(r, "Copy").invoke(); seen["clip"] = r.clipboard_get(); seen["copy"] = _status(r)
        _btn(r, "Open in mail app").invoke(); seen["mail"] = _status(r)
        _btn(r, "Close").invoke(); seen["closed"] = True
    _run(monkeypatch, s)
    assert seen["clip"].endswith("edited") and seen["copy"].startswith("Copied")
    assert urls[0].startswith("mailto:a@b.com?subject=Re%3A%20x") and "edited" in urls[0] and seen["mail"].startswith("Opened")


def test_window_redo_applies_change_request_and_survives_failure(monkeypatch):
    calls, seen = [], {}
    def fake(e, png, note=""): calls.append((e, note)); return "Subject: Re: x\n\nShort."
    monkeypatch.setattr(hotkey, "draft", fake)

    def s(r):
        e = next(w for w in _walk(r) if w.winfo_class() == "Entry"); e.insert(0, "shorter")
        _btn(r, "Redo").invoke(); seen["text"] = _text(r).get("1.0", "end").strip()
        monkeypatch.setattr(hotkey, "draft", boom)
        _btn(r, "Redo").invoke(); seen["fail"] = _status(r); seen["kept"] = _text(r).get("1.0", "end").strip()
    _run(monkeypatch, s)
    assert calls[0][0] == "claude" and "Previous draft:" in calls[0][1] and "Change wanted: shorter" in calls[0][1]
    assert seen["text"].endswith("Short.") and seen["fail"].startswith("Failed") and seen["kept"] == seen["text"]


def test_window_gemini_asks_key_once_and_saves_it(monkeypatch, tmp_path):
    sd = pytest.importorskip("tkinter.simpledialog")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(hotkey.providers, "HOME", str(tmp_path))
    monkeypatch.setattr(sd, "askstring", lambda *a, **k: "KEY123")
    monkeypatch.setattr(hotkey, "via_gemini", lambda png, key="", note="": f"g:{key}")

    def s(r):
        r.setvar(next(w for w in _walk(r) if w.winfo_class() == "Menubutton").cget("textvariable"), "gemini")
        _btn(r, "Redo").invoke()
        assert _text(r).get("1.0", "end").strip() == "g:KEY123"
    _run(monkeypatch, s)
    assert (tmp_path / "gemini.key").read_text() == "KEY123"


def test_rewrite_note_reaches_every_engine_prompt():
    assert "REWRITE" in hotkey._prompt(note="Previous draft: x") and "REWRITE" not in hotkey._prompt()
