import subprocess, tempfile

class FakeEngine:
    def draft(self, prompt: str) -> str:
        return "Hi,\n\nThanks for your message. [CONFIRM: date/time] works for me.\n\nRegards"

class ClaudeCLI:
    """Official CLI only, all tools off, empty cwd, text out. Verify billing in Phase 0 (docs/adr)."""
    def __init__(self, timeout=180): self.timeout = timeout
    def draft(self, prompt: str) -> str:
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(["claude", "-p", "--tools", "", "--no-session-persistence", "--setting-sources", "",  # no user hooks/plugins leaking text into drafts
                                "--system-prompt", "You write email reply drafts. Output only the reply body: no notes, no commentary, no footers."], input=prompt,
                               capture_output=True, text=True, cwd=d, timeout=self.timeout, encoding="utf-8")
        if r.returncode: raise RuntimeError(r.stderr[:200])
        return r.stdout
