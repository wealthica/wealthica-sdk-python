# Wealthica Python SDK Examples

This directory contains example scripts demonstrating how to use the Wealthica Python SDK.

## Prerequisites

1. Install the Wealthica SDK:

```bash
pip install wealthica
```

2. Get your API credentials from [Wealthica](https://wealthica.com)

3. Set up environment variables:

```bash
export WEALTHICA_CLIENT_ID="your_client_id"
export WEALTHICA_CLIENT_SECRET="your_secret"
```

## Examples

### Basic Example (`basic.py`)

A command-line script demonstrating core SDK functionality:

- Fetching provider information
- Getting team details
- User authentication
- Listing institutions and balances
- Fetching positions, transactions, and history

```bash
python basic.py
```

### Flask Server Example (`flask_server.py`)

A web server demonstrating how to integrate Wealthica into a backend application:

- REST API endpoints for all Wealthica operations
- Token generation for frontend authentication
- Interactive web interface for testing

```bash
# Install Flask
pip install flask python-dotenv

# Run the server
python flask_server.py
```

Then open http://localhost:3001 in your browser.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WEALTHICA_CLIENT_ID` | Your Wealthica client ID | Yes |
| `WEALTHICA_CLIENT_SECRET` | Your Wealthica client secret | Yes |
| `WEALTHICA_TEST_USER_ID` | User ID for testing (default: "test_user_123") | No |

## Connecting User Institutions

To connect user institutions to your application, you need to use **Wealthica Connect** in your frontend. The flow is:

1. **Backend**: Generate an auth token for your user:

```python
user = wealthica.login("user_id_from_your_database")
token = user.get_token()
# Return this token to your frontend
```

2. **Frontend**: Use the token with Wealthica Connect (JavaScript):

```javascript
import Wealthica from 'wealthica-sdk-js';

const wealthica = Wealthica.init({
    clientId: 'YOUR_CLIENT_ID',
    authEndpoint: '/api/auth/token',  // Your backend endpoint
});

const user = wealthica.login();
user.connect()
    .onConnection((institution) => {
        console.log('Institution connected:', institution);
    })
    .onError((error) => {
        console.error('Connection error:', error);
    });
```

3. **Backend**: Once connected, fetch the institution data:

```python
user = wealthica.login("user_id")
institutions = user.institutions.get_list()
```

For full frontend integration, see the [JavaScript SDK](https://github.com/wealthica/wealthica-sdk-js).

## More Information

- [Wealthica Documentation](https://wealthica.com/docs)
- [API Reference](https://wealthica.com/docs/api/)
- [JavaScript SDK](https://github.com/wealthica/wealthica-sdk-js)
