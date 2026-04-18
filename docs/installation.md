# Installation

## Requirements

- Python `>=3.9`
- No runtime dependencies (stdlib-only package)

## Install from PyPI

```bash
pip install thermounits
```

## Verify Installation

```bash
thermounits version
```

Expected output:

```text
thermounits 0.1.0
```

## Install for Development

Clone repository and install editable mode with developer tools:

```bash
git clone https://github.com/DeepcometAI/thermounits
cd thermounits
pip install -e ".[dev]"
```

Developer extras include:

- `pytest` (tests)
- `pytest-cov` (coverage)
- `ruff` (linting)
- `mypy` (type checks)

## Recommended Virtual Environment

Use a virtual environment to isolate tools:

```bash
python -m venv .venv
```

Activate:

- Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

- Bash:

```bash
source .venv/bin/activate
```

Then install:

```bash
pip install -e ".[dev]"
```
