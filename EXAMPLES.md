# Sandbox GSTR-1 MCP Server - Usage Examples

This document provides practical examples of how to use the Sandbox GSTR-1 MCP Server for various GSTR-1 filing scenarios.

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Simple GSTR-1 Filing](#simple-gstr1-filing)
3. [Filing with B2B Invoices](#filing-with-b2b-invoices)
4. [Filing with B2CL Invoices](#filing-with-b2cl-invoices)
5. [Filing with B2CS Transactions](#filing-with-b2cs-transactions)
6. [Filing with HSN Summary](#filing-with-hsn-summary)
7. [Filing with Credit Notes](#filing-with-credit-notes)
8. [Error Handling](#error-handling)
9. [Complete End-to-End Example](#complete-end-to-end-example)

## Basic Setup

### Import and Initialize

```python
import os
import sys
import time
import json

# Add server to path
sys.path.insert(0, '/home/ubuntu/sandbox-gstr1-mcp')

# Set credentials
os.environ['SANDBOX_API_KEY'] = 'key_test_ed6b10d21cf546d7b4b600021f91c341'

# Import server functions
from server import (
    generate_taxpayer_session,
    save_gstr1_data,
    check_return_status,
    proceed_to_file,
    get_gstr1_summary,
    generate_evc_otp,
    file_gstr1
)
```

## Simple GSTR-1 Filing

### Example 1: File a Nil Return

```python
# Step 1: Generate taxpayer session
session = generate_taxpayer_session(
    gstin="29AAACQ3770E000",
    username="taxpayer_username"
)

if "error" in session:
    print(f"Error: {session['error']}")
    exit(1)

access_token = session.get("access_token")
print(f"Session created: {access_token[:20]}...")

# Step 2: For nil return, save empty data
nil_payload = {
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

save_response = save_gstr1_data(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=nil_payload
)

reference_id = save_response.get("reference_id")
print(f"Data saved with reference: {reference_id}")

# Step 3: Poll status
for i in range(10):
    status = check_return_status(
        access_token=access_token,
        gstin="29AAACQ3770E000",
        ret_period="032026",
        reference_id=reference_id
    )
    
    if status.get("status") == "COMPLETED":
        print("Data validation completed")
        break
    
    print(f"Status: {status.get('status')} - Waiting...")
    time.sleep(5)

# Step 4: Proceed to file
proceed_response = proceed_to_file(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    is_nil="Y"  # Nil return
)

print(f"Proceeding to file: {proceed_response}")
```

## Filing with B2B Invoices

### Example 2: File B2B Invoices (Business-to-Business)

```python
# B2B invoice data
b2b_invoices = [
    {
        "inv": "INV-001",
        "dt": "01-Mar-2026",
        "val": 150000,
        "pos": "29",  # Place of supply (state code)
        "rchrg": "N",  # Reverse charge
        "inv_typ": "REG",
        "itms": [
            {
                "num": 1,
                "itm_det": {
                    "txval": 100000,
                    "sgst_amt": 9000,
                    "cgst_amt": 9000,
                    "cess_amt": 0
                }
            }
        ]
    },
    {
        "inv": "INV-002",
        "dt": "05-Mar-2026",
        "val": 200000,
        "pos": "27",  # Different state
        "rchrg": "N",
        "inv_typ": "REG",
        "itms": [
            {
                "num": 1,
                "itm_det": {
                    "txval": 200000,
                    "igst_amt": 36000,
                    "cess_amt": 0
                }
            }
        ]
    }
]

# Create payload
payload = {
    "fp": "032026",
    "gstin": "29AAACQ3770E000",
    "gt": 350000,
    "cur_gt": 350000,
    "b2b": b2b_invoices,
    "b2cl": [],
    "b2cs": [],
    "hsn": {"data": []},
    "docs": {"doc_det": []}
}

# Save data
save_response = save_gstr1_data(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=payload
)

print(f"B2B data saved: {save_response}")
```

## Filing with B2CL Invoices

### Example 3: File Large Value B2C Invoices

```python
# B2CL invoices (>₹1,00,000 from Aug 2024)
b2cl_invoices = [
    {
        "inv": "B2CL-001",
        "dt": "10-Mar-2026",
        "val": 150000,  # Greater than ₹1,00,000
        "pos": "29",
        "rchrg": "N",
        "inv_typ": "REG",
        "itms": [
            {
                "num": 1,
                "itm_det": {
                    "txval": 127119,
                    "igst_amt": 22881,
                    "cess_amt": 0
                }
            }
        ]
    },
    {
        "inv": "B2CL-002",
        "dt": "15-Mar-2026",
        "val": 200000,
        "pos": "27",
        "rchrg": "N",
        "inv_typ": "REG",
        "itms": [
            {
                "num": 1,
                "itm_det": {
                    "txval": 169492,
                    "igst_amt": 30508,
                    "cess_amt": 0
                }
            }
        ]
    }
]

# Create payload
payload = {
    "fp": "032026",
    "gstin": "29AAACQ3770E000",
    "gt": 350000,
    "cur_gt": 350000,
    "b2b": [],
    "b2cl": b2cl_invoices,
    "b2cs": [],
    "hsn": {"data": []},
    "docs": {"doc_det": []}
}

# Save data
save_response = save_gstr1_data(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=payload
)

print(f"B2CL data saved: {save_response}")
```

## Filing with B2CS Transactions

### Example 4: File Small Value B2C Transactions (Aggregated)

```python
# B2CS transactions (aggregated by state and rate)
b2cs_transactions = [
    {
        "typ": "OE",  # OE = Own E-commerce, E = Marketplace
        "pos": "29",
        "txval": 50000,
        "sply_ty": "INTRA"  # INTRA = Intra-state, INTER = Inter-state
    },
    {
        "typ": "E",  # E-commerce through marketplace
        "pos": "27",
        "txval": 75000,
        "sply_ty": "INTER"
    },
    {
        "typ": "OE",
        "pos": "29",
        "txval": 100000,
        "sply_ty": "INTRA"
    }
]

# Create payload
payload = {
    "fp": "032026",
    "gstin": "29AAACQ3770E000",
    "gt": 225000,
    "cur_gt": 225000,
    "b2b": [],
    "b2cl": [],
    "b2cs": b2cs_transactions,
    "hsn": {"data": []},
    "docs": {"doc_det": []}
}

# Save data
save_response = save_gstr1_data(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=payload
)

print(f"B2CS data saved: {save_response}")
```

## Filing with HSN Summary

### Example 5: Include HSN (Harmonized System of Nomenclature) Summary

```python
# HSN summary (aggregated by HSN and tax rate)
hsn_summary = {
    "data": [
        {
            "hsn_sc": "85183011",  # HSN code
            "desc": "Electronic components",
            "uqc": "NOS",  # Unit of Quantity Code
            "qty": 100,
            "val": 50000,
            "txval": 42373,
            "iamt": 6350,  # IGST amount
            "camt": 0,     # CGST amount
            "samt": 0,     # SGST amount
            "csamt": 0     # Cess amount
        },
        {
            "hsn_sc": "85176000",
            "desc": "Electrical machinery",
            "uqc": "NOS",
            "qty": 50,
            "val": 100000,
            "txval": 84746,
            "iamt": 12700,
            "camt": 0,
            "samt": 0,
            "csamt": 0
        }
    ]
}

# Create payload
payload = {
    "fp": "032026",
    "gstin": "29AAACQ3770E000",
    "gt": 150000,
    "cur_gt": 150000,
    "b2b": [],
    "b2cl": [],
    "b2cs": [],
    "hsn": hsn_summary,
    "docs": {"doc_det": []}
}

# Save data
save_response = save_gstr1_data(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=payload
)

print(f"HSN data saved: {save_response}")
```

## Filing with Credit Notes

### Example 6: File Credit Notes for Refunds

```python
# Credit notes (for refunds/returns)
credit_notes = [
    {
        "nt_num": "CN-001",
        "nt_dt": "20-Mar-2026",
        "p_gst_amt": 18000,  # Original GST amount
        "nt_val": 100000,
        "pos": "29",
        "itms": [
            {
                "num": 1,
                "itm_det": {
                    "txval": 84746,
                    "sgst_amt": 7627,
                    "cgst_amt": 7627,
                    "cess_amt": 0
                }
            }
        ]
    }
]

# Create payload
payload = {
    "fp": "032026",
    "gstin": "29AAACQ3770E000",
    "gt": -100000,  # Negative for credit notes
    "cur_gt": -100000,
    "b2b": [],
    "b2cl": [],
    "b2cs": [],
    "hsn": {"data": []},
    "cdnr": credit_notes,  # Credit/Debit Notes for Registered
    "docs": {"doc_det": []}
}

# Save data
save_response = save_gstr1_data(
    access_token=access_token,
    gstin="29AAACQ3770E000",
    ret_period="032026",
    gstr1_data=payload
)

print(f"Credit notes saved: {save_response}")
```

## Error Handling

### Example 7: Comprehensive Error Handling

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_file_gstr1(gstin, ret_period, username, pan, otp):
    """File GSTR-1 with comprehensive error handling"""
    
    try:
        # Step 1: Generate session
        logger.info(f"Generating session for {gstin}")
        session = generate_taxpayer_session(gstin=gstin, username=username)
        
        if "error" in session:
            logger.error(f"Session generation failed: {session['error']}")
            return {"success": False, "error": session['error']}
        
        access_token = session.get("access_token")
        
        # Step 2: Prepare and save data
        logger.info("Preparing GSTR-1 data")
        payload = {
            "fp": ret_period,
            "gstin": gstin,
            "gt": 500000,
            "cur_gt": 500000,
            "b2b": [],
            "b2cl": [],
            "b2cs": [],
            "hsn": {"data": []},
            "docs": {"doc_det": []}
        }
        
        logger.info("Saving GSTR-1 data")
        save_response = save_gstr1_data(
            access_token=access_token,
            gstin=gstin,
            ret_period=ret_period,
            gstr1_data=payload
        )
        
        if "error" in save_response:
            logger.error(f"Save failed: {save_response['error']}")
            return {"success": False, "error": save_response['error']}
        
        reference_id = save_response.get("reference_id")
        
        # Step 3: Poll status
        logger.info(f"Polling status with reference {reference_id}")
        for attempt in range(12):  # 12 attempts * 5 seconds = 60 seconds
            status = check_return_status(
                access_token=access_token,
                gstin=gstin,
                ret_period=ret_period,
                reference_id=reference_id
            )
            
            if "error" in status:
                logger.warning(f"Status check error: {status['error']}")
            elif status.get("status") == "COMPLETED":
                logger.info("Data validation completed")
                break
            
            if attempt < 11:
                logger.info(f"Attempt {attempt + 1}/12 - Status: {status.get('status')}")
                time.sleep(5)
        
        # Step 4: Proceed to file
        logger.info("Proceeding to file")
        proceed_response = proceed_to_file(
            access_token=access_token,
            gstin=gstin,
            ret_period=ret_period,
            is_nil="N"
        )
        
        if "error" in proceed_response:
            logger.error(f"Proceed failed: {proceed_response['error']}")
            return {"success": False, "error": proceed_response['error']}
        
        # Step 5: Get summary
        logger.info("Getting GSTR-1 summary")
        summary = get_gstr1_summary(
            access_token=access_token,
            gstin=gstin,
            ret_period=ret_period
        )
        
        if "error" in summary:
            logger.error(f"Summary retrieval failed: {summary['error']}")
            return {"success": False, "error": summary['error']}
        
        sec_sum = summary.get("sec_sum", [])
        chksum = summary.get("chksum", "")
        
        # Step 6: Generate OTP
        logger.info("Generating EVC OTP")
        otp_response = generate_evc_otp(
            access_token=access_token,
            pan=pan
        )
        
        if "error" in otp_response:
            logger.error(f"OTP generation failed: {otp_response['error']}")
            return {"success": False, "error": otp_response['error']}
        
        # Step 7: File GSTR-1
        logger.info("Filing GSTR-1")
        file_response = file_gstr1(
            access_token=access_token,
            gstin=gstin,
            ret_period=ret_period,
            pan=pan,
            otp=otp,
            sec_sum=sec_sum,
            chksum=chksum
        )
        
        if "error" in file_response:
            logger.error(f"Filing failed: {file_response['error']}")
            return {"success": False, "error": file_response['error']}
        
        logger.info("GSTR-1 filed successfully")
        return {"success": True, "response": file_response}
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return {"success": False, "error": str(e)}

# Usage
result = safe_file_gstr1(
    gstin="29AAACQ3770E000",
    ret_period="032026",
    username="taxpayer_username",
    pan="ABCCQ3123E",
    otp="123456"
)

print(json.dumps(result, indent=2))
```

## Complete End-to-End Example

### Example 8: Complete GSTR-1 Filing Workflow

```python
#!/usr/bin/env python3.11
"""
Complete GSTR-1 filing example
"""

import os
import sys
import time
import json

sys.path.insert(0, '/home/ubuntu/sandbox-gstr1-mcp')
os.environ['SANDBOX_API_KEY'] = 'key_test_ed6b10d21cf546d7b4b600021f91c341'

from server import (
    generate_taxpayer_session,
    save_gstr1_data,
    check_return_status,
    proceed_to_file,
    get_gstr1_summary,
    generate_evc_otp,
    file_gstr1
)

def main():
    # Configuration
    GSTIN = "29AAACQ3770E000"
    USERNAME = "taxpayer_username"
    PAN = "ABCCQ3123E"
    OTP = "123456"
    RET_PERIOD = "032026"
    
    print("=" * 60)
    print("GSTR-1 Filing Workflow")
    print("=" * 60)
    
    # Step 1: Generate session
    print("\n[1/7] Generating taxpayer session...")
    session = generate_taxpayer_session(gstin=GSTIN, username=USERNAME)
    if "error" in session:
        print(f"ERROR: {session['error']}")
        return
    
    access_token = session.get("access_token")
    print(f"✓ Session created")
    
    # Step 2: Prepare and save data
    print("\n[2/7] Preparing and saving GSTR-1 data...")
    payload = {
        "fp": RET_PERIOD,
        "gstin": GSTIN,
        "gt": 500000,
        "cur_gt": 500000,
        "b2b": [
            {
                "inv": "INV-001",
                "dt": "01-Mar-2026",
                "val": 150000,
                "pos": "29",
                "rchrg": "N",
                "inv_typ": "REG",
                "itms": [{"num": 1, "itm_det": {"txval": 127119, "sgst_amt": 11441, "cgst_amt": 11441, "cess_amt": 0}}]
            }
        ],
        "b2cl": [],
        "b2cs": [],
        "hsn": {"data": []},
        "docs": {"doc_det": []}
    }
    
    save_response = save_gstr1_data(
        access_token=access_token,
        gstin=GSTIN,
        ret_period=RET_PERIOD,
        gstr1_data=payload
    )
    
    if "error" in save_response:
        print(f"ERROR: {save_response['error']}")
        return
    
    reference_id = save_response.get("reference_id")
    print(f"✓ Data saved (Reference: {reference_id})")
    
    # Step 3: Poll status
    print("\n[3/7] Checking data validation status...")
    for i in range(10):
        status = check_return_status(
            access_token=access_token,
            gstin=GSTIN,
            ret_period=RET_PERIOD,
            reference_id=reference_id
        )
        
        if status.get("status") == "COMPLETED":
            print(f"✓ Data validation completed")
            break
        
        print(f"  Status: {status.get('status')} - Waiting...")
        time.sleep(3)
    
    # Step 4: Proceed to file
    print("\n[4/7] Proceeding to file...")
    proceed_response = proceed_to_file(
        access_token=access_token,
        gstin=GSTIN,
        ret_period=RET_PERIOD,
        is_nil="N"
    )
    
    if "error" in proceed_response:
        print(f"ERROR: {proceed_response['error']}")
        return
    
    print(f"✓ Filing initialized")
    
    # Step 5: Get summary
    print("\n[5/7] Retrieving GSTR-1 summary...")
    summary = get_gstr1_summary(
        access_token=access_token,
        gstin=GSTIN,
        ret_period=RET_PERIOD
    )
    
    if "error" in summary:
        print(f"ERROR: {summary['error']}")
        return
    
    sec_sum = summary.get("sec_sum", [])
    chksum = summary.get("chksum", "")
    print(f"✓ Summary retrieved (Checksum: {chksum[:16]}...)")
    
    # Step 6: Generate OTP
    print("\n[6/7] Generating EVC OTP...")
    otp_response = generate_evc_otp(
        access_token=access_token,
        pan=PAN
    )
    
    if "error" in otp_response:
        print(f"ERROR: {otp_response['error']}")
        return
    
    print(f"✓ OTP generated")
    
    # Step 7: File GSTR-1
    print("\n[7/7] Filing GSTR-1...")
    file_response = file_gstr1(
        access_token=access_token,
        gstin=GSTIN,
        ret_period=RET_PERIOD,
        pan=PAN,
        otp=OTP,
        sec_sum=sec_sum,
        chksum=chksum
    )
    
    if "error" in file_response:
        print(f"ERROR: {file_response['error']}")
        return
    
    print(f"✓ GSTR-1 filed successfully")
    
    print("\n" + "=" * 60)
    print("GSTR-1 Filing Completed Successfully!")
    print("=" * 60)
    print(f"\nResponse: {json.dumps(file_response, indent=2)}")

if __name__ == "__main__":
    main()
```

## Running the Examples

### Run the complete example:

```bash
cd /home/ubuntu/sandbox-gstr1-mcp
python3.11 EXAMPLES.md  # Won't work directly, copy code to a file
```

### Or create a file and run:

```bash
cat > example_complete.py << 'EOF'
# Paste the complete example code here
EOF

python3.11 example_complete.py
```

## Expected Output

```
============================================================
GSTR-1 Filing Workflow
============================================================

[1/7] Generating taxpayer session...
✓ Session created

[2/7] Preparing and saving GSTR-1 data...
✓ Data saved (Reference: ref_12345)

[3/7] Checking data validation status...
  Status: PROCESSING - Waiting...
  Status: PROCESSING - Waiting...
✓ Data validation completed

[4/7] Proceeding to file...
✓ Filing initialized

[5/7] Retrieving GSTR-1 summary...
✓ Summary retrieved (Checksum: dacc6e65dd43...)

[6/7] Generating EVC OTP...
✓ OTP generated

[7/7] Filing GSTR-1...
✓ GSTR-1 filed successfully

============================================================
GSTR-1 Filing Completed Successfully!
============================================================
```

## Next Steps

1. Modify the examples with your actual GSTIN and PAN
2. Prepare your GSTR-1 data in the required format
3. Test with the test environment first
4. Deploy to production when ready
5. Monitor the logs for any issues

For more information, see the README.md and CONFIGURATION.md files.
