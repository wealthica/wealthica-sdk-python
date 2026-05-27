# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Official Wealthica Python SDK — a client library for the Wealthica Investment Data API, supporting Python 3.8+. Published as `wealthica` on PyPI.

The SDK wraps the Wealthica REST API (`https://api.wealthica.com/v1`) and handles authentication (JWT token generation via `client_id` + `secret`), resource access, and error handling. It is the Python counterpart to `wealthica-sdk-js`.

## Commands

- **Install (dev):** `pip install -e ".[dev]"`
- **Test:** `pytest`
- **Test with coverage:** `pytest --cov=wealthica`
- **Lint:** `ruff check src/`
- **Format:** `black src/ tests/` and `isort src/ tests/`
- **Type check:** `mypy src/`
- **Build:** `python -m build` (outputs `dist/`)

## Architecture

**Package root:** `src/wealthica/` — the `src/` layout keeps the package directory clean from project-level files.

**Entry point:** `src/wealthica/__init__.py` — re-exports the `Wealthica` client class and `__version__`.

**Core client:** `src/wealthica/client.py` — the `Wealthica` class handles:
- Authentication via `client_id` + `secret` (JWT signed with the secret, cached and auto-refreshed)
- HTTP transport using `httpx` (synchronous; persistent client stored as `_client`)
- Context manager support (`__enter__` / `__exit__` call `close()` on the underlying httpx client)
- `login(login_name)` — sets the current user context and initialises user-scoped resources
- `get_token()` — returns a valid bearer token, fetching a new one if near expiry
- `get_team()` — returns the authenticated team's metadata

**Resources:** `src/wealthica/resources/`
- `base.py` — `BaseResource` with `_get`, `_post`, `_delete` helpers that delegate to `client._request`
- Data resources (attached at init): `providers`, `teams`
- User resources (attached on `login()`): `institutions`, `history`, `transactions`, `positions`
- Each resource class wraps the corresponding Wealthica API endpoint collection

**Constants:** `src/wealthica/constants.py` — `BASE_API_URL`, `CONNECT_URL`, `API_VERSION`, token lifetime defaults.

**Exceptions:** `src/wealthica/exceptions.py` — hierarchy rooted at `WealthicaError`; subclasses: `WealthicaAuthenticationError`, `WealthicaAPIError`, `WealthicaValidationError`, `WealthicaNotFoundError`, `WealthicaRateLimitError`.

**Tests:** `tests/` — `test_client.py` and `test_resources.py` using pytest. No `.github/workflows/` — CI is run locally before publishing.

## Code Style

- Line length: 100 characters (`black`, `ruff`, `mypy` all configured for 100)
- Formatter: `black` with `isort` (profile `black`)
- Linter: `ruff`
- Type annotations: required on all functions (`disallow_untyped_defs = true` in mypy)
- Python target: 3.8 (use only features available in 3.8+)
- Private attributes/methods use `_` prefix convention

## Release Process

Published to PyPI as `wealthica` (see `name` in `pyproject.toml`).

```bash
# 1. Bump version in pyproject.toml (and src/wealthica/__init__.py if it has __version__)
# 2. Build the distribution
python -m build

# 3. Upload to PyPI (requires twine + PyPI credentials)
twine upload dist/*
```

Verify the new version is live on https://pypi.org/project/wealthica/.

There is no separate staging environment for this package — every published version is available to all consumers. Test changes locally with `pip install -e .` before publishing.

There are no GitHub Actions workflows for automated publishing — all releases are manual.
