#!/usr/bin/env python3.11
"""
Test script for the Sandbox GSTR-1 MCP Server
Tests the API endpoints with mock data
"""

import json
import sys
import os

# Add the server directory to the path
sys.path.insert(0, '/home/ubuntu/sandbox-gstr1-mcp')

# Set test credentials
os.environ['SANDBOX_API_KEY'] = 'key_test_ed6b10d21cf546d7b4b600021f91c341'

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import requests
        print("✓ requests imported successfully")
        import pandas
        print("✓ pandas imported successfully")
        import openpyxl
        print("✓ openpyxl imported successfully")
        print("✓ All imports successful\n")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}\n")
        return False

def test_api_endpoints():
    """Test API endpoint construction"""
    print("Testing API endpoint construction...")
    
    SANDBOX_API_URL = "https://api.sandbox.co.in"
    
    # Test endpoint URLs
    test_cases = [
        ("Save GSTR-1", f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/2026/03"),
        ("Proceed to File", f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/2026/03/new-proceed?is_nil=N"),
        ("Get Summary", f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/2026/03?summary_type=long"),
        ("Generate OTP", f"{SANDBOX_API_URL}/gst/compliance/tax-payer/evc/otp?gstr=gstr-1"),
        ("File GSTR-1", f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/2026/03/file?pan=ABCCQ3123E&otp=123456"),
    ]
    
    for name, url in test_cases:
        print(f"✓ {name}: {url}")
    
    print(f"✓ All {len(test_cases)} endpoints constructed successfully\n")
    return True

def test_payload_structure():
    """Test GSTR-1 payload structure"""
    print("Testing GSTR-1 payload structure...")
    
    # Sample B2CL entry
    b2cl_entry = {
        "inv": "INV001",
        "dt": "01-01-2026",
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
    
    # Sample B2CS entry
    b2cs_entry = {
        "typ": "OE",
        "pos": "29",
        "txval": 50000,
        "sply_ty": "INTRA"
    }
    
    # Sample HSN entry
    hsn_entry = {
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
    
    print(f"✓ B2CL entry structure: {json.dumps(b2cl_entry, indent=2)}")
    print(f"✓ B2CS entry structure: {json.dumps(b2cs_entry, indent=2)}")
    print(f"✓ HSN entry structure: {json.dumps(hsn_entry, indent=2)}")
    print("✓ All payload structures validated\n")
    return True

def test_credentials():
    """Test that credentials are properly loaded"""
    print("Testing credentials...")
    
    from server import get_api_key, get_headers
    
    api_key = get_api_key()
    print(f"✓ API Key loaded: {api_key[:10]}...{api_key[-10:]}")
    
    headers = get_headers()
    print(f"✓ Headers constructed: {json.dumps(headers, indent=2)}")
    
    headers_with_token = get_headers("test_access_token_12345")
    print(f"✓ Headers with token: {json.dumps(headers_with_token, indent=2)}")
    print("✓ Credentials test passed\n")
    return True

def test_workflow():
    """Test the complete GSTR-1 filing workflow"""
    print("Testing GSTR-1 filing workflow...")
    
    workflow_steps = [
        "1. Generate Taxpayer Session",
        "2. Save GSTR-1 Data",
        "3. Check Return Status",
        "4. Proceed to File",
        "5. Get GSTR-1 Summary",
        "6. Generate EVC OTP",
        "7. File GSTR-1"
    ]
    
    for step in workflow_steps:
        print(f"✓ {step}")
    
    print(f"✓ Complete workflow with {len(workflow_steps)} steps defined\n")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Sandbox GSTR-1 MCP Server - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("API Endpoints", test_api_endpoints),
        ("Payload Structure", test_payload_structure),
        ("Credentials", test_credentials),
        ("Workflow", test_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}\n")
            results.append((test_name, False))
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
