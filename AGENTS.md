# Repository Guidelines

## Project Structure & Module Organization
- `mara.py` is the main CLI entry point and orchestrates data fetch, module execution, and plotting.
- `modules/` contains analysis modules (e.g., `generic.py`, `peg.py`) that implement the `ModuleProtocol` interface (`init`, `get`, optional `plot`).
- `utils/` holds integration helpers, currently the Tushare wrapper in `utils/tushare.py`.
- `doc/` stores API reference notes for financial endpoints.
- Top-level `requirements.txt` pins runtime dependencies; `version.py` centralizes version metadata.

## Build, Test, and Development Commands
- `python3 -m venv .venv` creates a local virtual environment.
- `pip install -r requirements.txt` installs runtime dependencies.
- `python3 mara.py --help` shows available CLI flags.
- `python3 mara.py [OPTIONS] [KEYWORD ...]` runs analyses and generates plots; add `--list` or `-c <COLUMN>` for listing/filtering.

## Coding Style & Naming Conventions
- Python code uses 4-space indentation and PEP 8 style.
- Module and function names follow `snake_case`; classes use `PascalCase`.
- Keep module APIs consistent with `ModuleProtocol` in `mara.py` to ensure discovery and execution.

## Testing Guidelines
- No automated test suite is currently configured.
- If you add tests, create a `tests/` directory and document the runner command here.

## Commit & Pull Request Guidelines
- Recent history uses short, imperative messages with optional prefixes (e.g., `fix: ...`, `Add ...`).
- Keep commits focused and scoped to a single change.
- PRs should describe the problem, the approach, and include CLI examples or screenshots for plot changes when applicable.

## Security & Configuration Tips
- Tushare credentials live in `~/.mararc` (YAML) under `token`.
- Do not commit tokens or generated `.xlsx` outputs; keep local artifacts untracked.
