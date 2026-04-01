# Sandbox GSTR-1 MCP Server - Claude Integration Guide

This guide explains how to integrate the Sandbox GSTR-1 MCP Server with Claude Desktop and Claude API.

## Table of Contents

1. [Claude Desktop Integration](#claude-desktop-integration)
2. [Claude API Integration](#claude-api-integration)
3. [Configuration](#configuration)
4. [Troubleshooting](#troubleshooting)

## Claude Desktop Integration

Claude Desktop supports MCP servers through configuration. This allows Claude to use the GSTR-1 filing tools directly within conversations.

### Prerequisites

- Claude Desktop installed (download from https://claude.ai/download)
- Python 3.11 or higher
- Git (for cloning the repository)

### Installation Steps

#### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/sandbox-gstr1-mcp.git

# Navigate to the directory
cd sandbox-gstr1-mcp

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Locate Claude Desktop Configuration

The configuration file location depends on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

#### Step 3: Add MCP Server Configuration

Open the `claude_desktop_config.json` file and add the MCP server configuration. If the file doesn't exist, create it.

**Example configuration:**

```json
{
  "mcpServers": {
    "sandbox-gstr1": {
      "command": "python",
      "args": [
        "/path/to/sandbox-gstr1-mcp/server.py"
      ],
      "env": {
        "SANDBOX_API_KEY": "key_test_ed6b10d21cf546d7b4b600021f91c341",
        "SANDBOX_API_SECRET": "secret_test_798d3274325741fab93dd24bbb786a3a"
      }
    }
  }
}
```

**Important:** Replace `/path/to/sandbox-gstr1-mcp/` with the actual path to your cloned repository.

#### Step 4: Restart Claude Desktop

Close Claude Desktop completely and reopen it. The MCP server should now be connected.

### Verifying the Connection

Once Claude Desktop is restarted:

1. Open a new conversation
2. Look for the **Tools** icon in the message input area
3. You should see "sandbox-gstr1" listed as an available MCP server
4. The GSTR-1 filing tools should be available for use

### Using the Tools in Claude

Once connected, you can ask Claude to use the GSTR-1 filing tools:

**Example prompts:**

```
"File a GSTR-1 return for GSTIN 29AAACQ3770E000 for March 2026"

"Generate a taxpayer session and save GSTR-1 data with B2B invoices"

"Check the status of my GSTR-1 filing with reference ID xyz123"

"Convert my GSTR-1 Excel file to the Sandbox API format"
```

Claude will automatically use the appropriate tools from the MCP server to accomplish these tasks.

## Claude API Integration

For programmatic integration with the Claude API, you can run the MCP server and connect to it via the API.

### Prerequisites

- Claude API key from https://console.anthropic.com
- Python 3.11 or higher
- The Sandbox GSTR-1 MCP server running

### Setup

#### Step 1: Start the MCP Server

```bash
cd /path/to/sandbox-gstr1-mcp
export SANDBOX_API_KEY="key_test_ed6b10d21cf546d7b4b600021f91c341"
export SANDBOX_API_SECRET="secret_test_798d3274325741fab93dd24bbb786a3a"
python server.py
```

The server will start listening for connections.

#### Step 2: Configure Claude API Client

Install the Claude SDK:

```bash
pip install anthropic
```

#### Step 3: Create a Python Script

```python
import anthropic
import json

# Initialize the Claude client
client = anthropic.Anthropic(api_key="your-api-key-here")

# Define the MCP tools
tools = [
    {
        "name": "generate_taxpayer_session",
        "description": "Generate a taxpayer session token valid for 6 hours",
        "input_schema": {
            "type": "object",
            "properties": {
                "gstin": {
                    "type": "string",
                    "description": "15-digit GST Identification Number"
                },
                "username": {
                    "type": "string",
                    "description": "GST portal username"
                }
            },
            "required": ["gstin", "username"]
        }
    },
    # Add other tools here...
]

# Send a message to Claude with tools
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {
            "role": "user",
            "content": "File a GSTR-1 return for GSTIN 29AAACQ3770E000 for March 2026"
        }
    ]
)

# Process the response
print(json.dumps(response, indent=2))
```

#### Step 4: Handle Tool Calls

Claude may request to use tools. Handle these requests:

```python
def handle_tool_use(tool_name, tool_input):
    """Handle tool calls from Claude"""
    
    if tool_name == "generate_taxpayer_session":
        # Call your MCP server endpoint
        result = generate_taxpayer_session(
            gstin=tool_input["gstin"],
            username=tool_input["username"]
        )
        return result
    
    elif tool_name == "save_gstr1_data":
        result = save_gstr1_data(
            access_token=tool_input["access_token"],
            gstin=tool_input["gstin"],
            ret_period=tool_input["ret_period"],
            gstr1_data=tool_input["gstr1_data"]
        )
        return result
    
    # Add handlers for other tools...
    
    return {"error": f"Unknown tool: {tool_name}"}
```

## Configuration

### Environment Variables

Set these environment variables before running the server:

```bash
# Required
export SANDBOX_API_KEY="your-test-api-key"
export SANDBOX_API_SECRET="your-test-api-secret"

# Optional
export SANDBOX_API_URL="https://api.sandbox.co.in"
export SANDBOX_API_VERSION="1.0.0"
export LOG_LEVEL="INFO"
```

### Configuration File

Create a `.env` file in the server directory:

```bash
SANDBOX_API_KEY=key_test_ed6b10d21cf546d7b4b600021f91c341
SANDBOX_API_SECRET=secret_test_798d3274325741fab93dd24bbb786a3a
SANDBOX_API_URL=https://api.sandbox.co.in
SANDBOX_API_VERSION=1.0.0
LOG_LEVEL=INFO
```

Load it in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("SANDBOX_API_KEY")
```

### Custom Configuration

For custom deployments, modify `server.py`:

```python
# Change the base URL
SANDBOX_API_URL = "https://your-custom-url.com"

# Change the API version
API_VERSION = "2.0.0"

# Change the default credentials
DEFAULT_API_KEY = "your-custom-key"
```

## Troubleshooting

### Issue: MCP Server Not Appearing in Claude Desktop

**Solution:**
1. Check the configuration file path is correct for your OS
2. Verify the Python path is correct in the configuration
3. Check that the server.py file exists at the specified path
4. Restart Claude Desktop completely
5. Check Claude Desktop logs for errors

**Log locations:**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`
- Linux: `~/.config/Claude/logs/`

### Issue: "Python not found" Error

**Solution:**
Use the full path to Python in the configuration:

```bash
# Find Python path
which python3.11
# Output: /usr/bin/python3.11

# Use in configuration
"command": "/usr/bin/python3.11"
```

### Issue: "Module not found" Error

**Solution:**
Ensure all dependencies are installed:

```bash
cd /path/to/sandbox-gstr1-mcp
pip install -r requirements.txt
```

If using a virtual environment, use the Python from the virtual environment:

```bash
# Activate virtual environment
source venv/bin/activate

# Find Python path
which python
# Use this path in the configuration
```

### Issue: API Connection Errors

**Solution:**
1. Verify your API key is correct
2. Check internet connectivity
3. Verify the API URL is correct
4. Check if the Sandbox API is operational
5. Review the server logs for detailed error messages

### Issue: Session Expired

**Solution:**
Taxpayer sessions expire after 6 hours. Generate a new session:

```
"Generate a new taxpayer session for GSTIN 29AAACQ3770E000"
```

### Issue: OTP Not Received

**Solution:**
1. Verify the PAN is correct and registered with GST portal
2. Check that your registered mobile number/email is correct
3. Wait a few minutes and try again
4. Check the Sandbox documentation for test OTP values

## Advanced Configuration

### Using a Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Find Python path
which python

# Use in Claude configuration
"command": "/full/path/to/venv/bin/python"
```

### Using Docker

If you prefer to run the server in Docker:

```bash
# Build the image
docker build -t sandbox-gstr1-mcp:1.0.0 .

# Run the container
docker run -d \
  -e SANDBOX_API_KEY="your-key" \
  -e SANDBOX_API_SECRET="your-secret" \
  -p 5000:5000 \
  sandbox-gstr1-mcp:1.0.0

# Use in Claude configuration
"command": "docker",
"args": ["run", "--rm", "-e", "SANDBOX_API_KEY=your-key", "sandbox-gstr1-mcp:1.0.0"]
```

### Running on a Remote Server

For remote deployments:

1. SSH into your server
2. Clone the repository
3. Install dependencies
4. Start the server
5. Configure Claude to connect to the remote server:

```json
{
  "mcpServers": {
    "sandbox-gstr1": {
      "command": "ssh",
      "args": [
        "user@remote-server",
        "cd /path/to/sandbox-gstr1-mcp && python server.py"
      ]
    }
  }
}
```

## Next Steps

1. Follow the installation steps above
2. Verify the connection in Claude Desktop
3. Try the example prompts
4. Refer to EXAMPLES.md for more detailed usage examples
5. Check README.md for API documentation

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Consult the main README.md documentation
4. Check the Sandbox.co API documentation
5. Open an issue on GitHub

## Resources

- **Claude Desktop**: https://claude.ai/download
- **Claude API**: https://console.anthropic.com
- **MCP Protocol**: https://modelcontextprotocol.io
- **Sandbox.co**: https://sandbox.co.in
- **Sandbox Developer Hub**: https://developer.sandbox.co.in

---

**Version**: 1.0.0  
**Last Updated**: April 1, 2026
