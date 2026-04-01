import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("sandbox-gstr1-mcp")

# Initialize FastMCP server
mcp = FastMCP("Sandbox GSTR-1 MCP Server")

# Configuration
SANDBOX_API_URL = "https://api.sandbox.co.in"
API_VERSION = "1.0.0"

# Default credentials (can be overridden by environment variables)
DEFAULT_API_KEY = "key_test_ed6b10d21cf546d7b4b600021f91c341"
DEFAULT_API_SECRET = "secret_test_798d3274325741fab93dd24bbb786a3a"

def get_api_key() -> str:
    return os.environ.get("SANDBOX_API_KEY", DEFAULT_API_KEY)

def get_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "x-api-key": get_api_key(),
        "x-api-version": API_VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if access_token:
        headers["authorization"] = access_token
    return headers

@mcp.tool()
def generate_taxpayer_session(gstin: str, username: str) -> Dict[str, Any]:
    """
    Generate a taxpayer session (access token) valid for 6 hours.
    
    Args:
        gstin: The 15-digit GST Identification Number
        username: The GST portal username
        
    Returns:
        Dict containing the access token and session details
    """
    logger.info(f"Generating taxpayer session for GSTIN: {gstin}")
    
    # This is a placeholder for the actual authentication endpoint
    # According to Sandbox docs, this is typically a multi-step process (OTP based)
    # For the test environment, we'll simulate a successful response or use the actual endpoint if known
    
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/authenticate"
    
    payload = {
        "gstin": gstin,
        "username": username,
        "action": "AUTHTAXPAYER"
    }
    
    try:
        response = requests.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating session: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def save_gstr1_data(access_token: str, gstin: str, ret_period: str, gstr1_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save GSTR-1 data to the GST portal for validation.
    
    Args:
        access_token: The taxpayer session token
        gstin: The 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format (e.g., "122023")
        gstr1_data: The complete GSTR-1 payload (b2b, b2cl, b2cs, hsn, etc.)
        
    Returns:
        Dict containing the reference_id for tracking status
    """
    # Extract year and month from ret_period (MMYYYY)
    month = ret_period[:2]
    year = ret_period[2:]
    
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/{year}/{month}"
    
    # Ensure required fields are present
    payload = gstr1_data.copy()
    payload["gstin"] = gstin
    payload["fp"] = ret_period
    
    logger.info(f"Saving GSTR-1 data for GSTIN: {gstin}, Period: {ret_period}")
    
    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error saving GSTR-1 data: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def check_return_status(access_token: str, gstin: str, ret_period: str, reference_id: str) -> Dict[str, Any]:
    """
    Check the status of a saved GSTR-1 or filing initialization.
    
    Args:
        access_token: The taxpayer session token
        gstin: The 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        reference_id: The reference ID returned from save or proceed operations
        
    Returns:
        Dict containing the status details
    """
    month = ret_period[:2]
    year = ret_period[2:]
    
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/{year}/{month}/status?reference_id={reference_id}"
    
    logger.info(f"Checking status for Reference ID: {reference_id}")
    
    try:
        response = requests.get(url, headers=get_headers(access_token))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking status: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def proceed_to_file(access_token: str, gstin: str, ret_period: str, is_nil: str = "N") -> Dict[str, Any]:
    """
    Initialize the filing process after saving data.
    
    Args:
        access_token: The taxpayer session token
        gstin: The 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        is_nil: "Y" for nil return, "N" for regular return
        
    Returns:
        Dict containing the reference_id for tracking initialization status
    """
    month = ret_period[:2]
    year = ret_period[2:]
    
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/{year}/{month}/new-proceed?is_nil={is_nil}"
    
    payload = {
        "gstin": gstin,
        "ret_period": ret_period
    }
    
    logger.info(f"Proceeding to file for GSTIN: {gstin}, Period: {ret_period}")
    
    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proceeding to file: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def get_gstr1_summary(access_token: str, gstin: str, ret_period: str, summary_type: str = "long") -> Dict[str, Any]:
    """
    Retrieve the GSTR-1 summary including section summaries and checksum required for filing.
    
    Args:
        access_token: The taxpayer session token
        gstin: The 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        summary_type: "long" for detailed summary, "short" for basic
        
    Returns:
        Dict containing the summary, sec_sum array, and chksum
    """
    month = ret_period[:2]
    year = ret_period[2:]
    
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/{year}/{month}?summary_type={summary_type}"
    
    logger.info(f"Getting GSTR-1 summary for GSTIN: {gstin}, Period: {ret_period}")
    
    try:
        response = requests.get(url, headers=get_headers(access_token))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting summary: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def generate_evc_otp(access_token: str, pan: str) -> Dict[str, Any]:
    """
    Generate an EVC OTP for filing verification.
    
    Args:
        access_token: The taxpayer session token
        pan: The Permanent Account Number associated with the GSTIN
        
    Returns:
        Dict containing the OTP generation status
    """
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/evc/otp?gstr=gstr-1"
    
    payload = {
        "pan": pan
    }
    
    logger.info(f"Generating EVC OTP for PAN: {pan}")
    
    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating OTP: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def file_gstr1(access_token: str, gstin: str, ret_period: str, pan: str, otp: str, sec_sum: List[Dict[str, Any]], chksum: str) -> Dict[str, Any]:
    """
    Submit the final GSTR-1 return with OTP verification.
    
    Args:
        access_token: The taxpayer session token
        gstin: The 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        pan: The Permanent Account Number
        otp: The EVC OTP received
        sec_sum: The section summaries array from get_gstr1_summary
        chksum: The checksum from get_gstr1_summary
        
    Returns:
        Dict containing the filing confirmation
    """
    month = ret_period[:2]
    year = ret_period[2:]
    
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/{year}/{month}/file?pan={pan}&otp={otp}"
    
    payload = {
        "ret_period": ret_period,
        "newSumFlag": True,
        "sec_sum": sec_sum,
        "gstin": gstin,
        "chksum": chksum
    }
    
    logger.info(f"Filing GSTR-1 for GSTIN: {gstin}, Period: {ret_period}")
    
    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error filing GSTR-1: {e}")
        if hasattr(e, 'response') and e.response is not None:
            return {"error": str(e), "details": e.response.text}
        return {"error": str(e)}

@mcp.tool()
def convert_excel_to_sandbox_payload(excel_path: str) -> Dict[str, Any]:
    """
    Convert the GSTR-1 Excel output from the skill into the JSON payload format required by Sandbox.co.
    
    Args:
        excel_path: Path to the GSTR-1 Excel file
        
    Returns:
        Dict containing the formatted JSON payload
    """
    import pandas as pd
    import numpy as np
    
    logger.info(f"Converting Excel file {excel_path} to Sandbox payload")
    
    try:
        # This is a simplified conversion logic based on the skill documentation
        # In a real implementation, this would parse each sheet and map to the exact JSON structure
        
        payload = {
            "b2b": [],
            "b2cl": [],
            "b2cs": [],
            "hsn": {"data": []},
            "docs": {"doc_det": []}
        }
        
        # Read b2cl sheet
        try:
            df_b2cl = pd.read_excel(excel_path, sheet_name='b2cl', skiprows=3)
            # Process b2cl data...
            logger.info(f"Found {len(df_b2cl)} rows in b2cl sheet")
        except Exception as e:
            logger.warning(f"Could not read b2cl sheet: {e}")
            
        # Read b2cs sheet
        try:
            df_b2cs = pd.read_excel(excel_path, sheet_name='b2cs', skiprows=3)
            # Process b2cs data...
            logger.info(f"Found {len(df_b2cs)} rows in b2cs sheet")
        except Exception as e:
            logger.warning(f"Could not read b2cs sheet: {e}")
            
        # Read hsn sheet
        try:
            df_hsn = pd.read_excel(excel_path, sheet_name='hsn(b2c)', skiprows=3)
            # Process hsn data...
            logger.info(f"Found {len(df_hsn)} rows in hsn sheet")
        except Exception as e:
            logger.warning(f"Could not read hsn sheet: {e}")
            
        return {"status": "success", "message": "Excel parsed successfully (mock implementation)", "payload": payload}
        
    except Exception as e:
        logger.error(f"Error converting Excel: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("Starting Sandbox GSTR-1 MCP Server...")
    mcp.run()
