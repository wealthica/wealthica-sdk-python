# Wealthica Investment API Python SDK

Official Python SDK for the [Wealthica](https://wealthica.com) Investment API.

## What is Wealthica?

Wealthica is an API for connecting with Canadian financial institutions and brokerages platforms. Instead of manually integrating with multiple institution APIs - you can simply use Wealthica for them all.

For our updated list of integrations, check out our list of [Wealthica Integrations](https://wealthica.com/status/).

## Features

- Secure JWT-based token authentication with automatic refresh
- Investment positions with security details
- Transaction history across all connected institutions
- Balance history tracking over time
- Support for 150+ Canadian financial institutions
- Context manager support for automatic cleanup
- Typed exception classes for granular error handling

## Installation

```bash
pip install wealthica
```

## Configuration

Set your credentials as environment variables:

```bash
export WEALTHICA_CLIENT_ID="your_client_id"
export WEALTHICA_CLIENT_SECRET="your_secret"
```

To obtain API keys, reach out to the team at [sales@wealthica.com](mailto:sales@wealthica.com).

## Quick Start

```python
from wealthica import Wealthica

# Initialize the client with your API credentials
wealthica = Wealthica(
    client_id="your_client_id",
    secret="your_secret"
)

# Get list of supported providers (no user login required)
providers = wealthica.providers.get_list()
print(f"Wealthica supports {len(providers)} providers")

# Get team information
team = wealthica.get_team()
print(f"Team: {team['name']}")
```

## User Authentication

To access user-specific data like institutions, positions, and transactions, you need to login as a user:

```python
from wealthica import Wealthica

wealthica = Wealthica(
    client_id="your_client_id",
    secret="your_secret"
)

# Login as a specific user (use your internal user ID)
user = wealthica.login("user_123")

# Now you can access user-specific resources
institutions = user.institutions.get_list()
for inst in institutions:
    print(f"Institution: {inst['provider']['display_name']}")
    for balance in inst.get('balances', []):
        print(f"  {balance['ticker']}: {balance['amount']}")
```

## API Reference

### Provider APIs

These APIs don't require user authentication:

#### Get All Providers

```python
providers = wealthica.providers.get_list()

# Each provider includes:
# - name: unique identifier
# - display_name: human-friendly name
# - auth_type: authentication type
# - credentials: required credential types
```

#### Get a Specific Provider

```python
provider = wealthica.providers.get_one("questrade")
print(f"Auth type: {provider['auth_type']}")
```

### Institution APIs

These APIs require user authentication:

#### List All Institutions

```python
user = wealthica.login("user_123")
institutions = user.institutions.get_list()

for inst in institutions:
    print(f"ID: {inst['id']}")
    print(f"Provider: {inst['provider']['display_name']}")
```

#### Get a Specific Institution

```python
institution = user.institutions.get_one("603522490d2b02001233a5d6")
```

#### Sync an Institution

Trigger a refresh to fetch the latest data from the provider:

```python
institution = user.institutions.sync("603522490d2b02001233a5d6")
```

#### Remove an Institution

```python
user.institutions.remove("603522490d2b02001233a5d6")
```

### Position APIs

#### Get Positions

```python
user = wealthica.login("user_123")

# Get all positions
positions = user.positions.get_list()

# Get positions for specific institutions
positions = user.positions.get_list(
    institutions=["603522490d2b02001233a5d6"]
)

for pos in positions:
    security = pos.get('security', {})
    print(f"{security['name']} ({security['symbol']})")
    print(f"  Quantity: {pos['quantity']}")
    print(f"  Market Value: {pos['market_value']}")
    print(f"  Gain: {pos['gain_percent']}%")
```

### Transaction APIs

#### List Transactions

```python
user = wealthica.login("user_123")

# Get all transactions
transactions = user.transactions.get_list(
    institutions=["603522490d2b02001233a5d6"]
)

# With filters
transactions = user.transactions.get_list(
    institutions=["603522490d2b02001233a5d6"],
    from_date="2024-01-01",
    to_date="2024-06-30",
    limit=100
)
```

#### Get a Specific Transaction

```python
tx = user.transactions.get_one(tx_id="603522490d2b02001233a5d7")
```

### Balance History APIs

#### Get Balance History

```python
user = wealthica.login("user_123")

history = user.history.get_list(
    institutions=["603522490d2b02001233a5d6"],
    from_date="2024-01-01",
    to_date="2024-06-30"
)

for entry in history:
    print(f"Date: {entry['date']}, Investment: {entry['investment']}")
```

## Error Handling

The SDK provides specific exception classes for different error types:

```python
from wealthica import (
    Wealthica,
    WealthicaError,
    WealthicaAuthenticationError,
    WealthicaAPIError,
    WealthicaValidationError,
    WealthicaNotFoundError,
    WealthicaRateLimitError,
)

try:
    user = wealthica.login("user_123")
    institution = user.institutions.get_one("invalid_id")
except WealthicaNotFoundError as e:
    print(f"Institution not found: {e.message}")
except WealthicaAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except WealthicaRateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
except WealthicaAPIError as e:
    print(f"API error [{e.status_code}]: {e.message}")
except WealthicaError as e:
    print(f"Wealthica error: {e.message}")
```

## Context Manager Support

The SDK supports context managers for automatic cleanup:

```python
with Wealthica(client_id="...", secret="...") as wealthica:
    providers = wealthica.providers.get_list()
    # Connection is automatically closed when exiting the block
```

## Configuration Options

```python
wealthica = Wealthica(
    client_id="your_client_id",              # Required
    secret="your_secret",                    # Required
    base_url="https://api.wealthica.com/v1", # Optional, default API URL
    connect_url="https://connect.wealthica.com",  # Optional, Connect widget URL
    timeout=30.0,                            # Optional, request timeout in seconds
)
```

## Connecting Users (Frontend Integration)

To connect user institutions, you'll need to use Wealthica Connect in your frontend. Here's how the flow works:

1. **Backend**: Generate a user token

```python
user = wealthica.login("user_123")
token = user.get_token()
# Send this token to your frontend
```

2. **Frontend**: Use the token with Wealthica Connect (JavaScript)

```javascript
import Wealthica from 'wealthica-sdk-js';

const wealthica = Wealthica.init({
    clientId: 'YOUR_CLIENT_ID',
    authEndpoint: '/wealthica/auth',
});

const user = wealthica.login();
user.connect()
    .onConnection((institution) => {
        console.log('Connected:', institution);
    })
    .onError((error) => {
        console.error('Error:', error);
    });
```

3. **Backend**: Handle the callback to receive the connected institution

For full frontend integration, see the [JavaScript SDK](https://github.com/wealthica/wealthica-sdk-js).

## Publishing to PyPI

To release a new version of the SDK:

### 1. Update Version

Update the version number in `pyproject.toml`:

```toml
version = "X.Y.Z"
```

And in `src/wealthica/__init__.py`:

```python
__version__ = "X.Y.Z"
```

### 2. Update Changelog

Add release notes to `CHANGELOG.md`.

### 3. Commit and Tag

```bash
git add -A
git commit -m "vX.Y.Z: Description of changes"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main --tags
```

### 4. Build the Package

```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Build
python3 -m build
```

### 5. Upload to PyPI

```bash
# Upload using twine (requires PyPI API token)
python3 -m twine upload dist/* -u __token__ -p YOUR_PYPI_TOKEN
```

To get a PyPI API token:
1. Go to https://pypi.org/manage/account/
2. Create an API token with "Upload packages" scope
3. Use `__token__` as username and the token as password

## Documentation

- [Wealthica API Documentation](https://wealthica.com/docs)
- [JavaScript SDK](https://github.com/wealthica/wealthica-sdk-js)

## Support

- Email: [hello@wealthica.com](mailto:hello@wealthica.com)
- Documentation: [https://wealthica.com/docs](https://wealthica.com/docs)

## License

MIT License - see [LICENSE](LICENSE) for details.
