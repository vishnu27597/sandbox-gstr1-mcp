import os
import sys
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

# IMPORTANT: Log to stderr ONLY — stdout must remain clean for MCP JSON-RPC protocol.
# Claude Desktop communicates with MCP servers over stdout/stdin. Any text written
# to stdout that is not valid JSON-RPC will break the connection.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("sandbox-gstr1-mcp")

# Initialize FastMCP server
mcp = FastMCP("Sandbox GSTR-1 MCP Server")

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
SANDBOX_API_URL = "https://api.sandbox.co.in"
API_VERSION = "1.0.0"

# Default test credentials — override via environment variables in production
DEFAULT_API_KEY = os.environ.get("SANDBOX_API_KEY", "key_test_ed6b10d21cf546d7b4b600021f91c341")
DEFAULT_API_SECRET = os.environ.get("SANDBOX_API_SECRET", "secret_test_798d3274325741fab93dd24bbb786a3a")


def get_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    """Build the standard request headers for Sandbox.co API calls."""
    headers = {
        "x-api-key": DEFAULT_API_KEY,
        "x-api-version": API_VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if access_token:
        headers["authorization"] = access_token
    return headers


# ─────────────────────────────────────────────
# MCP Tools
# ─────────────────────────────────────────────

@mcp.tool()
def generate_taxpayer_session(gstin: str, username: str) -> Dict[str, Any]:
    """
    Generate a taxpayer session (access token) valid for 6 hours.

    This is Step 1 of the GSTR-1 filing workflow. The returned access_token
    must be passed to all subsequent tool calls.

    Args:
        gstin: 15-digit GST Identification Number (e.g. "29AAACQ3770E000")
        username: GST portal username of the taxpayer

    Returns:
        Dict with access_token and session metadata, or an error dict.
    """
    logger.info("Generating taxpayer session for GSTIN: %s", gstin)

    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/authenticate"
    payload = {
        "gstin": gstin,
        "username": username,
        "action": "AUTHTAXPAYER",
    }

    try:
        response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error generating session: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def save_gstr1_data(
    access_token: str,
    gstin: str,
    ret_period: str,
    gstr1_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Upload GSTR-1 data to the GST portal for validation (Step 2).

    After calling this tool, use check_return_status() with the returned
    reference_id to poll until the status is COMPLETED before proceeding.

    Args:
        access_token: Taxpayer session token from generate_taxpayer_session()
        gstin: 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format (e.g. "032026" for March 2026)
        gstr1_data: Complete GSTR-1 payload dict containing b2b, b2cl, b2cs,
                    hsn, docs sections etc.

    Returns:
        Dict with reference_id for status polling, or an error dict.
    """
    month = ret_period[:2]
    year = ret_period[2:]
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1/{year}/{month}"

    payload = gstr1_data.copy()
    payload["gstin"] = gstin
    payload["fp"] = ret_period

    logger.info("Saving GSTR-1 data for GSTIN: %s, Period: %s", gstin, ret_period)

    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error saving GSTR-1 data: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def check_return_status(
    access_token: str,
    gstin: str,
    ret_period: str,
    reference_id: str,
) -> Dict[str, Any]:
    """
    Poll the status of a save or proceed operation (Step 3).

    Call this repeatedly (every 5 seconds) until status == "COMPLETED".

    Args:
        access_token: Taxpayer session token
        gstin: 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        reference_id: The reference_id returned by save_gstr1_data() or
                      proceed_to_file()

    Returns:
        Dict with status field ("PENDING", "PROCESSING", "COMPLETED", "ERROR").
    """
    month = ret_period[:2]
    year = ret_period[2:]
    url = (
        f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1"
        f"/{year}/{month}/status?reference_id={reference_id}"
    )

    logger.info("Checking status for Reference ID: %s", reference_id)

    try:
        response = requests.get(url, headers=get_headers(access_token), timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error checking status: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def proceed_to_file(
    access_token: str,
    gstin: str,
    ret_period: str,
    is_nil: str = "N",
) -> Dict[str, Any]:
    """
    Initialise the filing process after data validation is complete (Step 4).

    Poll check_return_status() with the returned reference_id until COMPLETED
    before calling get_gstr1_summary().

    Args:
        access_token: Taxpayer session token
        gstin: 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        is_nil: "Y" for a nil return, "N" for a regular return (default "N")

    Returns:
        Dict with reference_id for status polling, or an error dict.
    """
    month = ret_period[:2]
    year = ret_period[2:]
    url = (
        f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1"
        f"/{year}/{month}/new-proceed?is_nil={is_nil}"
    )
    payload = {"gstin": gstin, "ret_period": ret_period}

    logger.info("Proceeding to file for GSTIN: %s, Period: %s", gstin, ret_period)

    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error proceeding to file: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def get_gstr1_summary(
    access_token: str,
    gstin: str,
    ret_period: str,
    summary_type: str = "long",
) -> Dict[str, Any]:
    """
    Retrieve the GSTR-1 summary including sec_sum and chksum needed for filing (Step 5).

    The sec_sum and chksum values returned here must be passed directly to
    file_gstr1().

    Args:
        access_token: Taxpayer session token
        gstin: 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        summary_type: "long" for full section detail (default), "short" for totals only

    Returns:
        Dict with sec_sum array and chksum string, or an error dict.
    """
    month = ret_period[:2]
    year = ret_period[2:]
    url = (
        f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1"
        f"/{year}/{month}?summary_type={summary_type}"
    )

    logger.info("Getting GSTR-1 summary for GSTIN: %s, Period: %s", gstin, ret_period)

    try:
        response = requests.get(url, headers=get_headers(access_token), timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error getting summary: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def generate_evc_otp(access_token: str, pan: str) -> Dict[str, Any]:
    """
    Generate an Electronic Verification Code (EVC) OTP for filing (Step 6).

    The OTP is sent to the mobile number and email registered with the GST portal.
    Pass the received OTP to file_gstr1().

    Args:
        access_token: Taxpayer session token
        pan: Permanent Account Number associated with the GSTIN (e.g. "ABCCQ3123E")

    Returns:
        Dict with OTP generation status, or an error dict.
    """
    url = f"{SANDBOX_API_URL}/gst/compliance/tax-payer/evc/otp?gstr=gstr-1"
    payload = {"pan": pan}

    logger.info("Generating EVC OTP for PAN: %s", pan)

    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error generating OTP: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def file_gstr1(
    access_token: str,
    gstin: str,
    ret_period: str,
    pan: str,
    otp: str,
    sec_sum: List[Dict[str, Any]],
    chksum: str,
) -> Dict[str, Any]:
    """
    Submit the final GSTR-1 return with EVC OTP verification (Step 7 — final step).

    Args:
        access_token: Taxpayer session token
        gstin: 15-digit GST Identification Number
        ret_period: Return period in MMYYYY format
        pan: Permanent Account Number
        otp: EVC OTP received after calling generate_evc_otp()
        sec_sum: Section summaries array from get_gstr1_summary()
        chksum: Checksum string from get_gstr1_summary()

    Returns:
        Dict with filing acknowledgement number (ARN) and status, or an error dict.
    """
    month = ret_period[:2]
    year = ret_period[2:]
    url = (
        f"{SANDBOX_API_URL}/gst/compliance/tax-payer/gstrs/gstr-1"
        f"/{year}/{month}/file?pan={pan}&otp={otp}"
    )
    payload = {
        "ret_period": ret_period,
        "newSumFlag": True,
        "sec_sum": sec_sum,
        "gstin": gstin,
        "chksum": chksum,
    }

    logger.info("Filing GSTR-1 for GSTIN: %s, Period: %s", gstin, ret_period)

    try:
        response = requests.post(url, headers=get_headers(access_token), json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error filing GSTR-1: %s", e)
        detail = e.response.text if hasattr(e, "response") and e.response is not None else ""
        return {"error": str(e), "details": detail}


@mcp.tool()
def convert_excel_to_sandbox_payload(excel_path: str) -> Dict[str, Any]:
    """
    Convert a GSTR-1 Excel file (output of the unified-gstr1 skill) into the
    JSON payload format required by the Sandbox.co save_gstr1_data() API.

    Reads the b2b, b2cl, b2cs, and hsn sheets from the Excel file and maps
    each row to the corresponding Sandbox.co API structure.

    Args:
        excel_path: Absolute path to the GSTR-1 Excel file

    Returns:
        Dict with the formatted payload ready to pass to save_gstr1_data(),
        or an error dict.
    """
    try:
        import pandas as pd

        logger.info("Converting Excel file: %s", excel_path)

        payload: Dict[str, Any] = {
            "b2b": [],
            "b2cl": [],
            "b2cs": [],
            "hsn": {"data": []},
            "docs": {"doc_det": []},
        }

        xl = pd.ExcelFile(excel_path)
        available_sheets = xl.sheet_names
        logger.info("Available sheets: %s", available_sheets)

        # ── b2b ──────────────────────────────────────────────
        if "b2b" in available_sheets:
            df = pd.read_excel(excel_path, sheet_name="b2b", skiprows=3)
            df.dropna(how="all", inplace=True)
            for _, row in df.iterrows():
                try:
                    invoice = {
                        "inv": str(row.get("Invoice Number", "")),
                        "dt": str(row.get("Invoice Date", "")),
                        "val": float(row.get("Invoice Value", 0) or 0),
                        "pos": str(row.get("Place Of Supply", "")).split("-")[0].strip(),
                        "rchrg": str(row.get("Reverse Charge", "N")),
                        "inv_typ": str(row.get("Invoice Type", "REG")),
                        "itms": [
                            {
                                "num": 1,
                                "itm_det": {
                                    "txval": float(row.get("Taxable Value", 0) or 0),
                                    "igst_amt": float(row.get("Integrated Tax Amount", 0) or 0),
                                    "cgst_amt": float(row.get("Central Tax Amount", 0) or 0),
                                    "sgst_amt": float(row.get("State/UT Tax Amount", 0) or 0),
                                    "cess_amt": float(row.get("Cess Amount", 0) or 0),
                                },
                            }
                        ],
                    }
                    payload["b2b"].append(invoice)
                except Exception as row_err:
                    logger.warning("Skipping b2b row due to error: %s", row_err)

        # ── b2cl ─────────────────────────────────────────────
        if "b2cl" in available_sheets:
            df = pd.read_excel(excel_path, sheet_name="b2cl", skiprows=3)
            df.dropna(how="all", inplace=True)
            for _, row in df.iterrows():
                try:
                    invoice = {
                        "inv": str(row.get("Invoice Number", "")),
                        "dt": str(row.get("Invoice Date", "")),
                        "val": float(row.get("Invoice Value", 0) or 0),
                        "pos": str(row.get("Place Of Supply", "")).split("-")[0].strip(),
                        "rchrg": "N",
                        "inv_typ": "REG",
                        "itms": [
                            {
                                "num": 1,
                                "itm_det": {
                                    "txval": float(row.get("Taxable Value", 0) or 0),
                                    "igst_amt": float(row.get("Integrated Tax Amount", 0) or 0),
                                    "cess_amt": float(row.get("Cess Amount", 0) or 0),
                                },
                            }
                        ],
                    }
                    payload["b2cl"].append(invoice)
                except Exception as row_err:
                    logger.warning("Skipping b2cl row due to error: %s", row_err)

        # ── b2cs ─────────────────────────────────────────────
        if "b2cs" in available_sheets:
            df = pd.read_excel(excel_path, sheet_name="b2cs", skiprows=3)
            df.dropna(how="all", inplace=True)
            for _, row in df.iterrows():
                try:
                    txn = {
                        "typ": str(row.get("Type", "OE")),
                        "pos": str(row.get("Place Of Supply", "")).split("-")[0].strip(),
                        "txval": float(row.get("Taxable Value", 0) or 0),
                        "sply_ty": "INTRA" if str(row.get("Supply Type", "INTRA")).upper() == "INTRA" else "INTER",
                    }
                    payload["b2cs"].append(txn)
                except Exception as row_err:
                    logger.warning("Skipping b2cs row due to error: %s", row_err)

        # ── hsn ──────────────────────────────────────────────
        hsn_sheet = next((s for s in available_sheets if "hsn" in s.lower()), None)
        if hsn_sheet:
            df = pd.read_excel(excel_path, sheet_name=hsn_sheet, skiprows=3)
            df.dropna(how="all", inplace=True)
            for _, row in df.iterrows():
                try:
                    entry = {
                        "hsn_sc": str(row.get("HSN", row.get("HSN/SAC", ""))),
                        "desc": str(row.get("Description", "")),
                        "uqc": str(row.get("UQC", "NOS")),
                        "qty": float(row.get("Total Quantity", 0) or 0),
                        "val": float(row.get("Total Value", 0) or 0),
                        "txval": float(row.get("Taxable Value", 0) or 0),
                        "iamt": float(row.get("Integrated Tax Amount", 0) or 0),
                        "camt": float(row.get("Central Tax Amount", 0) or 0),
                        "samt": float(row.get("State/UT Tax Amount", 0) or 0),
                        "csamt": float(row.get("Cess Amount", 0) or 0),
                    }
                    payload["hsn"]["data"].append(entry)
                except Exception as row_err:
                    logger.warning("Skipping hsn row due to error: %s", row_err)

        summary = {
            "b2b_count": len(payload["b2b"]),
            "b2cl_count": len(payload["b2cl"]),
            "b2cs_count": len(payload["b2cs"]),
            "hsn_count": len(payload["hsn"]["data"]),
        }
        logger.info("Conversion complete: %s", summary)

        return {"status": "success", "summary": summary, "payload": payload}

    except Exception as e:
        logger.error("Error converting Excel: %s", e)
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting Sandbox GSTR-1 MCP Server (stdio transport)...")
    # mcp.run() uses stdio transport by default — required for Claude Desktop
    mcp.run()
