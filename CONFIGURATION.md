# Sandbox GSTR-1 MCP Server - Configuration Guide

This document provides detailed instructions for configuring and deploying the Sandbox GSTR-1 MCP Server.

## Quick Start

### 1. Install Dependencies

```bash
cd /home/ubuntu/sandbox-gstr1-mcp
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export SANDBOX_API_KEY="key_test_ed6b10d21cf546d7b4b600021f91c341"
export SANDBOX_API_SECRET="secret_test_798d3274325741fab93dd24bbb786a3a"
```

### 3. Run the Server

```bash
python3.11 server.py
```

## Detailed Configuration

### API Credentials

The MCP server requires Sandbox.co API credentials. These are obtained from your Sandbox console.

#### Test Environment Credentials

| Item | Value |
|------|-------|
| API Key | `key_test_ed6b10d21cf546d7b4b600021f91c341` |
| API Secret | `secret_test_798d3274325741fab93dd24bbb786a3a` |
| Base URL | `https://api.sandbox.co.in` |
| Environment | Test (no quota consumption) |

#### Obtaining Credentials

1. Log in to https://console.sandbox.co.in
2. Navigate to Settings → API Keys
3. Click "Generate Test Key"
4. Copy the Test API Key and Test API Secret
5. Set them as environment variables

### Environment Variables

Create a `.env` file in the server directory:

```bash
# Sandbox.co API Credentials
SANDBOX_API_KEY=key_test_ed6b10d21cf546d7b4b600021f91c341
SANDBOX_API_SECRET=secret_test_798d3274325741fab93dd24bbb786a3a

# Optional: Override default values
SANDBOX_API_URL=https://api.sandbox.co.in
SANDBOX_API_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO
```

### Using .env File

To automatically load environment variables from `.env`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("SANDBOX_API_KEY")
```

## GSTIN and PAN Configuration

### Test GSTIN

For testing purposes, use a test GSTIN. Common test GSTINs:

- `29AAACQ3770E000` - Standard test GSTIN
- `29AABCT5055K1Z5` - Alternative test GSTIN

### Test PAN

Common test PANs:

- `ABCCQ3123E` - Standard test PAN
- `AAACJ3770E` - Alternative test PAN

### Configuring for Your Business

Replace the placeholder values with your actual GSTIN and PAN:

1. **GSTIN**: 15-digit GST Identification Number from your GST registration
2. **PAN**: 10-character Permanent Account Number

## API Endpoints Configuration

### Base URL

The default base URL is `https://api.sandbox.co.in`. To use a different URL:

```python
SANDBOX_API_URL = "https://api.sandbox.co.in"  # Test environment
# or
SANDBOX_API_URL = "https://api.sandbox.co.in"  # Production (same URL, different API key)
```

### API Version

Current API version: `1.0.0`

To update the API version:

```python
API_VERSION = "1.0.0"
```

## Return Period Configuration

Return periods are specified in **MMYYYY** format:

| Period | Format | Example |
|--------|--------|---------|
| January 2026 | `012026` | January |
| February 2026 | `022026` | February |
| March 2026 | `032026` | March |
| Q1 2026 (Jan-Mar) | `032026` | Quarterly |

### Monthly vs Quarterly Filing

- **Monthly**: File for each month (01-12)
- **Quarterly**: File for the last month of the quarter (03, 06, 09, 12)

## Logging Configuration

### Log Levels

| Level | Description |
|-------|-------------|
| DEBUG | Detailed information for debugging |
| INFO | General informational messages |
| WARNING | Warning messages for potential issues |
| ERROR | Error messages for failures |
| CRITICAL | Critical errors requiring immediate attention |

### Configuring Log Level

```python
import logging

# Set log level
logging.basicConfig(level=logging.DEBUG)  # For verbose output
# or
logging.basicConfig(level=logging.INFO)   # For normal output
```

### Log Output

Logs are written to console by default. To write to a file:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gstr1_mcp.log'),
        logging.StreamHandler()
    ]
)
```

## Database Configuration (Optional)

For production deployments, you may want to store filing history:

```python
import sqlite3

# Create database
conn = sqlite3.connect('gstr1_filings.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS filings (
        id INTEGER PRIMARY KEY,
        gstin TEXT,
        ret_period TEXT,
        reference_id TEXT,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
```

## Proxy Configuration (If Behind Corporate Proxy)

```python
import os

proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080',
}

# Use in requests
response = requests.post(url, headers=headers, json=payload, proxies=proxies)
```

## SSL/TLS Configuration

### Disable SSL Verification (Not Recommended for Production)

```python
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Make request without SSL verification
response = requests.post(url, headers=headers, json=payload, verify=False)
```

### Use Custom CA Certificate

```python
response = requests.post(
    url,
    headers=headers,
    json=payload,
    verify='/path/to/ca-bundle.crt'
)
```

## Rate Limiting

Sandbox.co APIs have rate limits. Implement rate limiting in your client:

```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def api_call():
    # Your API call here
    pass
```

## Timeout Configuration

Set appropriate timeouts for API calls:

```python
# Timeout in seconds
TIMEOUT = 30

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=TIMEOUT
)
```

## Retry Configuration

Implement retry logic for transient failures:

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Use in requests
session = requests_retry_session()
response = session.post(url, headers=headers, json=payload)
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server.py .

ENV SANDBOX_API_KEY=key_test_ed6b10d21cf546d7b4b600021f91c341
ENV SANDBOX_API_SECRET=secret_test_798d3274325741fab93dd24bbb786a3a

CMD ["python", "server.py"]
```

### Build and Run

```bash
# Build image
docker build -t sandbox-gstr1-mcp:1.0.0 .

# Run container
docker run -e SANDBOX_API_KEY=your_key -e SANDBOX_API_SECRET=your_secret sandbox-gstr1-mcp:1.0.0
```

## Systemd Service (Linux)

### Create Service File

Create `/etc/systemd/system/sandbox-gstr1-mcp.service`:

```ini
[Unit]
Description=Sandbox GSTR-1 MCP Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sandbox-gstr1-mcp
Environment="SANDBOX_API_KEY=key_test_ed6b10d21cf546d7b4b600021f91c341"
Environment="SANDBOX_API_SECRET=secret_test_798d3274325741fab93dd24bbb786a3a"
ExecStart=/usr/bin/python3.11 /home/ubuntu/sandbox-gstr1-mcp/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable sandbox-gstr1-mcp
sudo systemctl start sandbox-gstr1-mcp
sudo systemctl status sandbox-gstr1-mcp
```

## Monitoring and Health Checks

### Health Check Endpoint

Add a health check tool to the MCP server:

```python
@mcp.tool()
def health_check() -> Dict[str, Any]:
    """Check the health of the MCP server"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_url": SANDBOX_API_URL,
        "api_version": API_VERSION
    }
```

### Monitoring Logs

Monitor the server logs in real-time:

```bash
tail -f gstr1_mcp.log
```

## Troubleshooting Configuration

### Verify Credentials

```bash
python3.11 -c "
import os
from server import get_api_key, get_headers

print('API Key:', get_api_key()[:10] + '...')
print('Headers:', get_headers())
"
```

### Test API Connection

```bash
python3.11 -c "
import requests
from server import SANDBOX_API_URL, get_headers

response = requests.get(
    SANDBOX_API_URL + '/health',
    headers=get_headers(),
    timeout=10
)
print('Status:', response.status_code)
print('Response:', response.json())
"
```

### Check Environment Variables

```bash
env | grep SANDBOX
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Use HTTPS** for all API calls
5. **Implement rate limiting** to prevent abuse
6. **Monitor logs** for suspicious activity
7. **Use strong PAN/GSTIN** validation
8. **Implement access controls** for the MCP server

## Performance Tuning

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
session.mount('https://', adapter)
```

### Batch Processing

For multiple filings, implement batch processing:

```python
def batch_file_gstr1(filings):
    """File multiple GSTR-1 returns"""
    results = []
    for filing in filings:
        result = file_gstr1(**filing)
        results.append(result)
        time.sleep(1)  # Rate limiting
    return results
```

## Next Steps

1. Review the README.md for usage examples
2. Run the test suite to validate setup
3. Configure your GSTIN and PAN
4. Test with sample data
5. Deploy to production environment

For more information, see the main README.md file.
