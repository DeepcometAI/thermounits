# Development Guide

## Local Setup

```bash
git clone https://github.com/DeepcometAI/thermounits
cd thermounits
python -m venv .venv
```

Activate and install:

- PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

- Bash:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run Tests

```bash
pytest tests/ -v
```

## Linting and Type Checking

```bash
ruff check .
mypy thermounits
```

Current mypy mode is intentionally non-strict (`strict = false`) for early-stage ergonomics.

## Repository Conventions

- Keep public API unit-safe (`Quantity`-based inputs/outputs).
- Validate dimensions before thermodynamic arithmetic.
- Prefer SI internal values and convert only for presentation.
- Add tests for each new formula or conversion path.

## Adding New Units

1. Add unit registration in `thermounits/units/registry.py`.
2. Ensure correct `Dimension`.
3. Add aliases if needed.
4. Add conversion tests in `tests/test_thermounits.py`.

## Adding New Thermo Functions

1. Implement in `thermounits/thermo/functions.py`.
2. Validate argument dimensions with the internal `_require` helper.
3. Return `Quantity` where physical units apply.
4. Export through `thermounits/thermo/__init__.py` and package `thermounits/__init__.py` if public.
5. Add tests for both nominal and error paths.

## Adding New Fluid Models

For a new fluid:

1. Add static metadata in `thermounits/fluids/fluid.py` if registry-level only.
2. Add a dedicated module in `thermounits/fluids/` if dynamic property calculations are needed.
3. Add CLI command support when relevant.
4. Add documentation in `docs/`.

## Release Checklist (Suggested)

1. Update version in:
   - `pyproject.toml`
   - `thermounits/__init__.py`
2. Run:
   - tests
   - lint
   - type check
3. Update `CHANGELOG.md`.
4. Build package:

```bash
python -m build
```

5. Publish to PyPI with trusted workflow or twine process.
