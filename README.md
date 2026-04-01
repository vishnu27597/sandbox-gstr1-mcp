# Sandbox GSTR-1 MCP Server

A comprehensive Model Context Protocol (MCP) server for automating GSTR-1 (Goods and Services Tax Return - 1) filing through the Sandbox.co APIs. This server integrates with the official GST portal via Sandbox's comprehensive API suite to enable seamless filing of outward supplies, credit/debit notes, and amendments.

## Overview

The Sandbox GSTR-1 MCP Server provides a set of tools that implement the complete GSTR-1 filing workflow as defined by the Sandbox.co API documentation. It handles:

- **Taxpayer Authentication**: Generate and manage taxpayer sessions (valid for 6 hours)
- **Data Submission**: Save GSTR-1 data including B2B invoices, B2CL invoices, B2CS transactions, HSN summaries, and documents
- **Status Monitoring**: Check the status of save and filing operations
- **Filing Initialization**: Proceed to file after data validation
- **Summary Retrieval**: Get section-wise summaries and checksums required for filing
- **OTP Generation**: Generate Electronic Verification Code (EVC) OTP for final verification
- **Return Filing**: Submit the final GSTR-1 return with OTP verification
- **Excel Conversion**: Convert GSTR-1 Excel output from the unified skill to Sandbox API payload format

## Features

### Core Capabilities

1. **Full GSTR-1 Filing Workflow**: Implements all 7 steps of the official filing process
2. **Test Environment Support**: Uses Sandbox's test environment for safe integration testing
3. **Comprehensive Error Handling**: Detailed error messages and logging for debugging
4. **Flexible Configuration**: Environment variables for API credentials
5. **Excel to JSON Conversion**: Transforms GSTR-1 Excel output into Sandbox API format

### Supported GSTR-1 Sections

- **B2B (Business-to-Business)**: Regular invoices to registered businesses
- **B2CL (Business-to-Consumer Large)**: Large value B2C invoices (>₹1,00,000 from Aug 2024)
- **B2CS (Business-to-Consumer Small)**: Aggregated B2C transactions
- **HSN Summary**: Harmonized System of Nomenclature wise aggregation
- **Credit/Debit Notes**: For refunds and amendments
- **Exports**: Export transactions with or without payment
- **Amendments**: Amendments to previously filed returns

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Internet access to Sandbox.co APIs

### Setup

1. Clone or download the MCP server directory:
```bash
cd /home/ubuntu/sandbox-gstr1-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
export SANDBOX_API_KEY="key_test_ed6b10d21cf546d7b4b600021f91c341"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SANDBOX_API_KEY` | Test API Key from Sandbox console | `key_test_ed6b10d21cf546d7b4b600021f91c341` |
| `SANDBOX_API_SECRET` | Test API Secret (for future use) | `secret_test_798d3274325741fab93dd24bbb786a3a` |

### API Configuration

The server is configured to use:
- **Base URL**: `https://api.sandbox.co.in`
- **API Version**: `1.0.0`
- **Environment**: Test (does not consume quota or incur charges)

## Usage

### Starting the Server

```bash
python3.11 server.py
```

The server will start and listen for MCP client connections.

### Available Tools

#### 1. Generate Taxpayer Session
Creates a taxpayer session token valid for 6 hours.

**Parameters:**
- `gstin` (string): 15-digit GST Identification Number
- `username` (string): GST portal username

**Returns:**
- Access token and session details

**Example:**
```python
result = generate_taxpayer_session(
    gstin="29AAACQ3770E000",
    username="taxpayer_username"
)
```

#### 2. Save GSTR-1 Data
Uploads GSTR-1 data to the GST portal for validation.

**Parameters:**
- `access_token` (string): Taxpayer session token
- `gstin` (string): 15-digit GSTIN
- `ret_period` (string): Return period in MMYYYY format (e.g., "032026")
- `gstr1_data` (dict): Complete GSTR-1 payload

**Returns:**
- Reference ID for tracking status

**Example:**
```python
gstr1_payload = {
    "b2cl": [...],
    "b2cs": [...],
    "hsn": {...},
    "docs": {...}
}

result = save_gstr1_data(
    access_token="token_xyz",
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=gstr1_payload
)
```

#### 3. Check Return Status
Checks the status of a save or filing operation.

**Parameters:**
- `access_token` (string): Taxpayer session token
- `gstin` (string): 15-digit GSTIN
- `ret_period` (string): Return period in MMYYYY format
- `reference_id` (string): Reference ID from save/proceed operation

**Returns:**
- Current status of the operation

#### 4. Proceed to File
Initializes the filing process after data validation.

**Parameters:**
- `access_token` (string): Taxpayer session token
- `gstin` (string): 15-digit GSTIN
- `ret_period` (string): Return period in MMYYYY format
- `is_nil` (string): "Y" for nil return, "N" for regular return (default: "N")

**Returns:**
- Reference ID for tracking initialization

#### 5. Get GSTR-1 Summary
Retrieves section summaries and checksum required for filing.

**Parameters:**
- `access_token` (string): Taxpayer session token
- `gstin` (string): 15-digit GSTIN
- `ret_period` (string): Return period in MMYYYY format
- `summary_type` (string): "long" for detailed, "short" for basic (default: "long")

**Returns:**
- Complete GSTR-1 data with section summaries and checksum

#### 6. Generate EVC OTP
Generates an Electronic Verification Code OTP for filing verification.

**Parameters:**
- `access_token` (string): Taxpayer session token
- `pan` (string): Permanent Account Number

**Returns:**
- OTP generation status

#### 7. File GSTR-1
Submits the final GSTR-1 return with OTP verification.

**Parameters:**
- `access_token` (string): Taxpayer session token
- `gstin` (string): 15-digit GSTIN
- `ret_period` (string): Return period in MMYYYY format
- `pan` (string): Permanent Account Number
- `otp` (string): EVC OTP received
- `sec_sum` (list): Section summaries from get_gstr1_summary
- `chksum` (string): Checksum from get_gstr1_summary

**Returns:**
- Filing confirmation

#### 8. Convert Excel to Sandbox Payload
Converts GSTR-1 Excel output from the unified skill to Sandbox API format.

**Parameters:**
- `excel_path` (string): Path to the GSTR-1 Excel file

**Returns:**
- Formatted JSON payload ready for submission

## GSTR-1 Filing Workflow

The complete GSTR-1 filing process follows these steps:

```
1. Generate Taxpayer Session
   ↓
2. Save GSTR-1 Data
   ↓
3. Check Return Status (Poll until complete)
   ↓
4. Proceed to File
   ↓
5. Check Return Status (Poll until complete)
   ↓
6. Get GSTR-1 Summary
   ↓
7. Generate EVC OTP
   ↓
8. File GSTR-1 (with OTP)
   ↓
Filing Complete
```

### Important Notes

- **Session Validity**: Taxpayer access tokens are valid for 6 hours. Plan your filing workflow accordingly.
- **Status Polling**: Check status every 10-15 seconds after save or proceed operations. Processing typically completes within 1-2 minutes.
- **Previous Returns**: Ensure all previous period returns have been filed before filing the current period.
- **Test Environment**: The test API key does not consume quota or incur wallet charges, making it ideal for development and testing.

## GSTR-1 Payload Structure

### B2CL (Business-to-Consumer Large) Format

```json
{
  "inv": "Invoice Number",
  "dt": "DD-MMM-YYYY",
  "val": 150000,
  "pos": "29",
  "rchrg": "N",
  "inv_typ": "REG",
  "itms": [
    {
      "num": 1,
      "itm_det": {
        "txval": 100000,
        "sgst_amt": 0,
        "cess_amt": 0,
        "igst_amt": 18000
      }
    }
  ]
}
```

### B2CS (Business-to-Consumer Small) Format

```json
{
  "typ": "OE",
  "pos": "29",
  "txval": 50000,
  "sply_ty": "INTRA"
}
```

### HSN Summary Format

```json
{
  "hsn_sc": "85183011",
  "desc": "Electronic components",
  "uqc": "NOS",
  "qty": 100,
  "val": 50000,
  "txval": 42373,
  "iamt": 6350,
  "camt": 0,
  "samt": 0,
  "csamt": 0
}
```

## Testing

Run the included test suite to validate the MCP server setup:

```bash
python3.11 test_server.py
```

The test suite validates:
- All required module imports
- API endpoint construction
- GSTR-1 payload structures
- Credential loading
- Complete filing workflow

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

## Error Handling

The server includes comprehensive error handling:

- **Request Errors**: Network and connection issues are caught and logged
- **API Errors**: HTTP error responses include detailed error messages
- **Data Validation**: Payload validation before submission
- **Logging**: All operations are logged for debugging and audit trails

## Logging

The server uses Python's standard logging module with INFO level by default. Logs include:

- Timestamp
- Logger name
- Log level
- Message

Example log output:
```
2026-04-01 13:00:52,406 - sandbox-gstr1-mcp - INFO - Generating taxpayer session for GSTIN: 29AAACQ3770E000
2026-04-01 13:00:53,123 - sandbox-gstr1-mcp - INFO - Saving GSTR-1 data for GSTIN: 29AAACQ3770E000, Period: 032026
```

## Integration with Unified GSTR-1 Skill

This MCP server is designed to work seamlessly with the unified GSTR-1 skill. The workflow is:

1. **Skill generates GSTR-1 Excel** from multiple sources (Amazon MTR, Flipkart, SmartBiz, etc.)
2. **MCP server converts Excel to JSON** using the `convert_excel_to_sandbox_payload` tool
3. **MCP server submits to Sandbox.co** using the complete filing workflow
4. **GST portal receives and processes** the GSTR-1 return

## API Reference

For detailed API documentation, refer to:
- **Sandbox Developer Hub**: https://developer.sandbox.co.in/
- **GSTR-1 Filing Recipe**: https://developer.sandbox.co.in/recipes/gst/gstr-1/file_gstr_1
- **Authentication Guide**: https://developer.sandbox.co.in/guides/authentication

## Troubleshooting

### Common Issues

**Issue**: "API Key not found"
- **Solution**: Ensure the `SANDBOX_API_KEY` environment variable is set or use the default test key

**Issue**: "Session expired"
- **Solution**: Regenerate a new taxpayer session. Sessions are valid for 6 hours.

**Issue**: "Validation errors in saved data"
- **Solution**: Check the error details in the status response and correct the data before proceeding

**Issue**: "OTP not received"
- **Solution**: Verify the PAN is correct and registered with the GST portal

## Support

For issues or questions:

1. Check the logs for detailed error messages
2. Verify API credentials are correct
3. Ensure the return period is in MMYYYY format
4. Confirm all previous period returns are filed
5. Review the Sandbox API documentation

## License

This MCP server is provided as-is for integration with Sandbox.co APIs.

## Version

- **Version**: 1.0.0
- **Release Date**: April 1, 2026
- **API Version**: 1.0.0
- **Sandbox Environment**: Test

## Changelog

### v1.0.0 (April 1, 2026)
- Initial release
- Complete GSTR-1 filing workflow implementation
- All 7 core tools implemented
- Excel to JSON conversion support
- Comprehensive error handling and logging
- Full test suite included
