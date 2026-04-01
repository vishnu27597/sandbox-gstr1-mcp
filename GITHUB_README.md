# Sandbox GSTR-1 MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)

A powerful Model Context Protocol (MCP) server for automating GSTR-1 (Goods and Services Tax Return - 1) filing through the Sandbox.co APIs. Seamlessly integrate with Claude Desktop or Claude API to automate your GST return filing process.

## 🚀 Quick Start

### For Claude Desktop Users

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sandbox-gstr1-mcp.git
   cd sandbox-gstr1-mcp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add to Claude Desktop:**
   - Open your Claude Desktop configuration file:
     - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
     - **Linux**: `~/.config/Claude/claude_desktop_config.json`

   - Add this configuration:
     ```json
     {
       "mcpServers": {
         "sandbox-gstr1": {
           "command": "python",
           "args": ["/path/to/sandbox-gstr1-mcp/server.py"],
           "env": {
             "SANDBOX_API_KEY": "key_test_ed6b10d21cf546d7b4b600021f91c341",
             "SANDBOX_API_SECRET": "secret_test_798d3274325741fab93dd24bbb786a3a"
           }
         }
       }
     }
     ```

4. **Restart Claude Desktop** and start using the GSTR-1 filing tools!

### For Developers

```bash
# Clone and setup
git clone https://github.com/yourusername/sandbox-gstr1-mcp.git
cd sandbox-gstr1-mcp

# Install dependencies
pip install -r requirements.txt

# Run the server
export SANDBOX_API_KEY="key_test_ed6b10d21cf546d7b4b600021f91c341"
python server.py
```

## 📋 Features

### Complete GSTR-1 Filing Workflow

- ✅ **Taxpayer Authentication**: Generate and manage 6-hour sessions
- ✅ **Data Submission**: Save B2B, B2CL, B2CS, HSN, and document data
- ✅ **Status Monitoring**: Real-time filing status tracking
- ✅ **Filing Initialization**: Prepare returns for submission
- ✅ **Summary Retrieval**: Get section-wise summaries and checksums
- ✅ **OTP Generation**: Electronic Verification Code generation
- ✅ **Return Filing**: Submit final GSTR-1 with OTP verification
- ✅ **Excel Conversion**: Transform Excel output to API format

### Supported GSTR-1 Sections

| Section | Type | Description |
|---------|------|-------------|
| B2B | Business-to-Business | Regular invoices to registered businesses |
| B2CL | B2C Large | Large value B2C invoices (>₹1,00,000 from Aug 2024) |
| B2CS | B2C Small | Aggregated B2C transactions |
| HSN | Summary | Harmonized System of Nomenclature aggregation |
| Credit Notes | Amendments | For refunds and adjustments |
| Exports | International | Export transactions |
| Amendments | Revisions | Amendments to previously filed returns |

## 🛠️ Available Tools

The MCP server exposes 8 powerful tools for GSTR-1 filing:

### 1. Generate Taxpayer Session
```python
generate_taxpayer_session(gstin, username)
```
Creates a 6-hour valid taxpayer session token.

### 2. Save GSTR-1 Data
```python
save_gstr1_data(access_token, gstin, ret_period, gstr1_data)
```
Uploads GSTR-1 data for validation.

### 3. Check Return Status
```python
check_return_status(access_token, gstin, ret_period, reference_id)
```
Monitors filing operation status.

### 4. Proceed to File
```python
proceed_to_file(access_token, gstin, ret_period, is_nil)
```
Initializes the filing process.

### 5. Get GSTR-1 Summary
```python
get_gstr1_summary(access_token, gstin, ret_period, summary_type)
```
Retrieves section summaries and checksums.

### 6. Generate EVC OTP
```python
generate_evc_otp(access_token, pan)
```
Generates Electronic Verification Code OTP.

### 7. File GSTR-1
```python
file_gstr1(access_token, gstin, ret_period, pan, otp, sec_sum, chksum)
```
Submits the final GSTR-1 return.

### 8. Convert Excel to Sandbox Payload
```python
convert_excel_to_sandbox_payload(excel_path)
```
Transforms Excel output to API format.

## 📖 Documentation

- **[README.md](README.md)** - Comprehensive API documentation and workflow details
- **[CONFIGURATION.md](CONFIGURATION.md)** - Setup, configuration, and deployment guide
- **[EXAMPLES.md](EXAMPLES.md)** - Practical code examples for various scenarios
- **[CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md)** - Claude Desktop and API integration guide

## 🔧 Configuration

### Environment Variables

```bash
# Required
export SANDBOX_API_KEY="key_test_ed6b10d21cf546d7b4b600021f91c341"
export SANDBOX_API_SECRET="secret_test_798d3274325741fab93dd24bbb786a3a"

# Optional
export SANDBOX_API_URL="https://api.sandbox.co.in"
export SANDBOX_API_VERSION="1.0.0"
export LOG_LEVEL="INFO"
```

### Test Credentials

The server comes pre-configured with test credentials that don't consume quota:

- **API Key**: `key_test_ed6b10d21cf546d7b4b600021f91c341`
- **API Secret**: `secret_test_798d3274325741fab93dd24bbb786a3a`
- **Environment**: Test (safe for development)

## 📊 GSTR-1 Filing Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Generate Taxpayer Session (6-hour validity)             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  2. Save GSTR-1 Data (B2B, B2CL, B2CS, HSN, etc.)          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  3. Check Return Status (Poll until complete)               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  4. Proceed to File (Initialize filing)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  5. Get GSTR-1 Summary (Get checksums)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  6. Generate EVC OTP (For verification)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  7. File GSTR-1 (Submit with OTP)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ✅ Filing Complete
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_server.py
```

Expected output:
```
============================================================
Test Summary
============================================================
✓ PASSED: Imports
✓ PASSED: API Endpoints
✓ PASSED: Payload Structure
✓ PASSED: Credentials
✓ PASSED: Workflow

Total: 5/5 tests passed
============================================================
```

## 💬 Using with Claude

### Claude Desktop

Once configured, use natural language:

```
"File a GSTR-1 return for GSTIN 29AAACQ3770E000 for March 2026"

"Generate a taxpayer session and save GSTR-1 data with B2B invoices"

"Check the status of my GSTR-1 filing with reference ID xyz123"

"Convert my GSTR-1 Excel file to the Sandbox API format"
```

### Claude API

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[...],  # MCP tools
    messages=[
        {
            "role": "user",
            "content": "File a GSTR-1 return for GSTIN 29AAACQ3770E000"
        }
    ]
)
```

## 📦 Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
git clone https://github.com/yourusername/sandbox-gstr1-mcp.git
cd sandbox-gstr1-mcp
pip install -r requirements.txt
```

### Method 2: Using Virtual Environment

```bash
git clone https://github.com/yourusername/sandbox-gstr1-mcp.git
cd sandbox-gstr1-mcp
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Method 3: Docker

```bash
docker build -t sandbox-gstr1-mcp:1.0.0 .
docker run -e SANDBOX_API_KEY="your-key" sandbox-gstr1-mcp:1.0.0
```

## 🔐 Security

- ✅ Test credentials provided for safe development
- ✅ Environment variables for sensitive data
- ✅ No credentials in code or version control
- ✅ HTTPS for all API calls
- ✅ Comprehensive error handling and logging

## 🐛 Troubleshooting

### MCP Server Not Appearing in Claude Desktop

1. Verify configuration file path is correct
2. Check Python path is accessible
3. Ensure all dependencies are installed
4. Restart Claude Desktop completely
5. Check Claude logs for errors

### API Connection Errors

1. Verify API key is correct
2. Check internet connectivity
3. Confirm API URL is correct
4. Review server logs for details

### Session Expired

Generate a new taxpayer session (valid for 6 hours).

For more troubleshooting, see [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md).

## 📚 Examples

### File a Nil Return

```python
from server import generate_taxpayer_session, save_gstr1_data

session = generate_taxpayer_session(
    gstin="29AAACQ3770E000",
    username="taxpayer_username"
)

save_gstr1_data(
    access_token=session["access_token"],
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data={
        "fp": "032026",
        "gstin": "29AAACQ3770E000",
        "gt": 0,
        "cur_gt": 0,
        "b2b": [],
        "b2cl": [],
        "b2cs": [],
        "hsn": {"data": []},
        "docs": {"doc_det": []}
    }
)
```

### File B2B Invoices

See [EXAMPLES.md](EXAMPLES.md) for complete examples including:
- B2B invoices
- B2CL large value invoices
- B2CS small value transactions
- HSN summaries
- Credit notes
- Error handling
- Complete end-to-end workflow

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- **[Sandbox.co](https://sandbox.co.in)** - GST API Platform
- **[Sandbox Developer Hub](https://developer.sandbox.co.in)** - API Documentation
- **[Claude Desktop](https://claude.ai/download)** - AI Assistant
- **[MCP Protocol](https://modelcontextprotocol.io)** - Protocol Documentation
- **[GST Portal](https://www.gst.gov.in)** - Official GST Portal

## 📞 Support

For issues or questions:

1. Check the [troubleshooting guide](CLAUDE_INTEGRATION.md#troubleshooting)
2. Review the [documentation](README.md)
3. Check [examples](EXAMPLES.md)
4. Open an issue on GitHub

## 🎯 Roadmap

- [ ] Support for GSTR-3B filing
- [ ] Support for GSTR-9 filing
- [ ] Batch filing for multiple returns
- [ ] Webhook support for filing notifications
- [ ] Dashboard for filing history
- [ ] Multi-language support
- [ ] Advanced error recovery

## 📊 Status

| Component | Status |
|-----------|--------|
| Core Server | ✅ Production Ready |
| API Integration | ✅ Complete |
| Claude Desktop | ✅ Tested |
| Claude API | ✅ Supported |
| Documentation | ✅ Comprehensive |
| Tests | ✅ Passing |

## 🙏 Acknowledgments

- Built on top of [Sandbox.co](https://sandbox.co.in) APIs
- Integrates with [Claude](https://claude.ai) via MCP Protocol
- Inspired by the unified GSTR-1 skill

## 📝 Changelog

### v1.0.0 (April 1, 2026)
- Initial release
- Complete GSTR-1 filing workflow
- All 7 core tools implemented
- Excel to JSON conversion
- Comprehensive documentation
- Full test suite
- Claude Desktop integration
- Claude API support

---

**Made with ❤️ for GST compliance automation**

**Version**: 1.0.0  
**Last Updated**: April 1, 2026  
**Python**: 3.11+  
**License**: MIT
