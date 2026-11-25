import pytest
from draftbox import hotkey


def boom(*a): raise RuntimeError("x")


def test_auto_prefers_claude_then_ollama_never_gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(hotkey, "via_gemini", lambda *a: 1 / 0)
    monkeypatch.setattr(hotkey, "via_claude", lambda p: "c")
    monkeypatch.setattr(hotkey, "via_ollama", lambda p: "o")
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
