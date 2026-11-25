from draftbox.core import Msg, build_prompt
from draftbox.cli import main


def test_instructions_in_prompt_outside_fence():
    p = build_prompt(Msg("1", "a", "x@y.z", "s", "hi"), "", "", "Keep under 80 words")
    assert p.index("Keep under 80 words") < p.index("<email>\n")


def test_init_and_try(tmp_path, monkeypatch, capsys):
    from draftbox import providers
    monkeypatch.setattr(providers, "HOME", str(tmp_path))
    main(["init"])
    assert (tmp_path / "instructions.md").exists()
    f = tmp_path / "m.txt"; f.write_text("Can we meet Thursday?", encoding="utf-8")
    main(["try", str(f), "--engine", "fake"])
    assert "[CONFIRM" in capsys.readouterr().out
