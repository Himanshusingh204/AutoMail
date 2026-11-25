from fastapi.testclient import TestClient
from draftbox.core import Store, run_once
from draftbox.engines import FakeEngine
from draftbox.providers import DemoProvider
from draftbox.web import make_app


def client(tmp_path):
    st = Store(tmp_path / "t.db"); run_once(DemoProvider(), FakeEngine(), st)
    files = {}
    app = make_app(st, "tok", FakeEngine(), str(tmp_path), lambda n, d="": files.get(n, d))
    return st, TestClient(app, base_url="http://127.0.0.1", follow_redirects=False)


def test_index_filters_and_escaping(tmp_path):
    st, c = client(tmp_path)
    r = c.get("/?t=tok")
    assert r.status_code == 200 and "Meeting Thursday?" in r.text and "<mark>[CONFIRM" in r.text
    assert "Weekly digest" not in c.get("/?t=tok&view=drafts").text
    assert "Weekly digest" in c.get("/?t=tok&view=skipped").text


def test_dismiss_pause_and_regen(tmp_path):
    st, c = client(tmp_path)
    assert c.post("/dismiss?t=tok", content="a=demo&i=d1").status_code == 303
    assert st.item("demo", "d1")["status"] == "dismissed"
    c.post("/pause?t=tok"); assert st.get("paused") == "1"
    c.post("/resume?t=tok"); assert st.get("paused") == "0"
    # skipped mail can be drafted anyway, with a note
    assert c.post("/regen?t=tok", content="a=demo&i=d2&note=be+brief").status_code == 303
    assert st.item("demo", "d2")["status"] == "dry-run"


def test_settings_save_and_csrf(tmp_path):
    st, c = client(tmp_path)
    c.post("/settings?t=tok", content="instructions.md=Keep+it+short")
    assert (tmp_path / "instructions.md").read_text() == "Keep it short"
    assert c.post("/pause").status_code == 403                      # no token
    assert c.post("/pause?t=tok", headers={"origin": "http://evil.com"}).status_code == 403  # cross-site
