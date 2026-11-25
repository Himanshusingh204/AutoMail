# Contributing

`uv venv && uv pip install -e ".[dev]"`, then `pytest`. Test data must be synthetic (no real mail, names or addresses). Never add a send function. New providers/engines implement the small interfaces in `providers.py` / `engines.py`.
