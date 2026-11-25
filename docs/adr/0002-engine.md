# ADR 0002: Draft engine (fill in after Phase 0)

Run a handful of drafts via `draftbox run --engine claude` and record:
- Does `claude -p` use subscription quota or bill separately? ______
- Seconds per draft: ______ (rule: over 180s or metered billing => re-plan)
- Behaviour when quota is exhausted: ______
- `--tools ""` really disables tools: ______
Run `draftbox golden --engine claude` after any prompt/engine change.
