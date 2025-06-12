import datetime
import base64
import os

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests


from app.radius.radius_utils import create_radius_user
from app.utils.credentials import get_metadata_from_store
from app.utils.credentials import get_access_token, generate_password
from app.utils.credentials import save_metadata_to_store 



# Assuming MPESA_CONFIG is correctly imported from app.config
MPESA_CONFIG = {
    "CALLBACK_URL": "https://6494-102-210-247-18.ngrok-free.app/darajaa/callback",
    "BUSINESS_SHORT_CODE": "174379",
    "STK_PUSH_URL": "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
    "QUERY_STATUS_URL": "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/queryid"
}

CALLBACK_URL = MPESA_CONFIG["CALLBACK_URL"]
BUSINESS_SHORT_CODE = MPESA_CONFIG["BUSINESS_SHORT_CODE"]


router = APIRouter()

# -------------------- Pydantic Model --------------------
class STKPushRequest(BaseModel):
    phone: str
    amount: int
    account_reference: Optional[str] = "zoomonet"
    transaction_desc: Optional[str] = "Internet"
    
    # Add your dynamic fields here for RADIUS user creation
    bandwidth: str
    session_time: str
    devices: int

class QueryPaymentStatusRequest(BaseModel):
    checkout_request_id: str

# -------------------- STK Push Endpoint --------------------
@router.post("/stkpush")
async def initiate_stk_push(payload: STKPushRequest):
    """
    Initiates an M-Pesa STK Push transaction.
    Stores initial payment metadata with a 'PENDING' status.
    Uses the actual generate_password and get_access_token from app.utils.credentials.
    """
    try:
        print(f"Received payment request: {payload.dict()}")

        access_token = get_access_token() # Uses your imported get_access_token
        password, timestamp = generate_password() # Uses your imported generate_password

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        mpesa_payload_data = {
            "BusinessShortCode": BUSINESS_SHORT_CODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": payload.amount,
            "PartyA": payload.phone,
            "PartyB": BUSINESS_SHORT_CODE,
            "PhoneNumber": payload.phone,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": payload.account_reference,
            "TransactionDesc": payload.transaction_desc
        }

        stk_url = MPESA_CONFIG["STK_PUSH_URL"]
        response = requests.post(stk_url, headers=headers, json=mpesa_payload_data)

        print(f"M-Pesa API Response [{response.status_code}]: {response.text}")

        if response.status_code == 200:
            mpesa_response = response.json()
            checkout_id = mpesa_response.get("CheckoutRequestID")
            response_code = mpesa_response.get("ResponseCode")

            if checkout_id and response_code == "0": # ResponseCode "0" means STK push was sent successfully to phone
                # Store the metadata in your database/cache with a PENDING status
                metadata = {
                    "status": "PENDING", # Initial status
                    "amount": payload.amount,
                    "phone": payload.phone,
                    "bandwidth": payload.bandwidth,
                    "session_time": payload.session_time,
                    "devices": payload.devices,
                    "mpesa_response": mpesa_response # Store full M-Pesa response for debugging
                }
                save_metadata_to_store(checkout_id, metadata) # Now using your imported save_metadata_to_store

                return {
                    "message": "STK Push initiated successfully.",
                    "checkout_request_id": checkout_id,
                    "customer_message": mpesa_response.get("CustomerMessage", "Awaiting payment confirmation on your phone.")
                }
            else:
                # Handle cases where M-Pesa didn't send STK push (e.g., invalid phone)
                error_detail = mpesa_response.get("ResponseDescription", "STK Push initiation failed.")
                raise HTTPException(status_code=400, detail=error_detail)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except requests.exceptions.RequestException as req_e:
        print(f"STK Push Request Error: {req_e}")
        raise HTTPException(status_code=503, detail=f"Failed to connect to M-Pesa: {req_e}")
    except Exception as e:
        print("STK Push General Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- M-Pesa Callback Endpoint --------------------
@router.post("/callback")
async def mpesa_callback(request: Request):
    """
    Handles the M-Pesa callback from Safaricom.
    Confirms payment, creates RADIUS user if successful, and updates metadata.
    Uses the actual create_radius_user from app.radius.radius_utils and
    get_metadata_from_store from app.utils.credentials.
    """
    try:
        payload = await request.json()
        print(f"Received M-Pesa callback: {payload}")

        # Extract relevant details from the callback payload
        stk_callback = payload.get("Body", {}).get("stkCallback", {})
        checkout_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        
        # Get actual M-Pesa transaction ID (e.g., LGFxxxxxxx)
        mpesa_receipt_number = None
        callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        for item in callback_metadata:
            if item.get("Name") == "MpesaReceiptNumber":
                mpesa_receipt_number = item.get("Value")
                break

        if not checkout_id:
            print("Callback Error: CheckoutRequestID not found in callback.")
            raise HTTPException(status_code=400, detail="CheckoutRequestID not found in callback")

        # Retrieve metadata from your store (e.g., Redis, database)
        metadata = get_metadata_from_store(checkout_id) # Now using your imported get_metadata_from_store

        if not metadata:
            print(f"Callback Error: Metadata not found for CheckoutRequestID: {checkout_id}")
            # It's crucial to acknowledge the callback to M-Pesa even if we can't find metadata
            return {"ResultCode": 0, "ResultDesc": "Callback received, but metadata not found."}

        # --- Process payment result ---
        if result_code == 0: # Payment was successful
            print(f"Payment successful for CheckoutRequestID: {checkout_id}")
            
            try:

                radius_creation_result = create_radius_user( # Uses your imported create_radius_user
                    metadata["phone"],
                    metadata["amount"],
                    metadata["bandwidth"],
                    metadata["session_time"],
                    metadata["devices"]
                )

                updated_metadata = metadata.copy()
                updated_metadata.update({
                    "status": "SUCCESS",
                    "radius_username": radius_creation_result.get("username"),
                    "radius_password": radius_creation_result.get("password"), 
                    "mpesa_receipt_number": mpesa_receipt_number,
                    "result_desc": result_desc
                })
                save_metadata_to_store(checkout_id, updated_metadata) 

                print(f"RADIUS user created and metadata updated for {checkout_id}")
                return {"ResultCode": 0, "ResultDesc": "Callback processed successfully and RADIUS user created."}

            except Exception as radius_e:
                # If RADIUS user creation fails, update status to indicate partial success/failure
                print(f"RADIUS user creation failed for {checkout_id}: {radius_e}")
                updated_metadata = metadata.copy()
                updated_metadata.update({
                    "status": "FAILED_RADIUS_CREATION",
                    "result_desc": f"Payment successful but RADIUS user creation failed: {radius_e}",
                    "mpesa_receipt_number": mpesa_receipt_number
                })
                save_metadata_to_store(checkout_id, updated_metadata) # Now using your imported save_metadata_to_store

                # Still return success to M-Pesa, as payment itself was successful
                return {"ResultCode": 0, "ResultDesc": "Payment successful but RADIUS user creation failed."}

        else: # Payment failed or was cancelled
            print(f"Payment failed for CheckoutRequestID: {checkout_id}. ResultCode: {result_code}, ResultDesc: {result_desc}")
            updated_metadata = metadata.copy()
            updated_metadata.update({
                "status": "FAILED",
                "result_code": result_code,
                "result_desc": result_desc
            })
            save_metadata_to_store(checkout_id, updated_metadata) # Now using your imported save_metadata_to_store
            return {"ResultCode": 0, "ResultDesc": "Payment failed, metadata updated."}

    except Exception as e:
        print("Callback General Error:", str(e))
        # Ensure M-Pesa receives a success response even on internal server errors
        # to prevent re-attempts, though logging is critical.
        return {"ResultCode": 1, "ResultDesc": f"Internal Server Error processing callback: {str(e)}"}


# -------------------- Query Payment Status Endpoint --------------------
@router.post("/query_payment_status")
async def query_payment_status(request_data: QueryPaymentStatusRequest):
    """
    Allows the frontend to query the payment status using CheckoutRequestID.
    Returns status and, if successful, RADIUS username and password.
    """
    checkout_id = request_data.checkout_request_id
    print(f"Received query for CheckoutRequestID: {checkout_id}")

    try:
        metadata = get_metadata_from_store(checkout_id) # Now using your imported get_metadata_from_store

        if not metadata:
            raise HTTPException(status_code=404, detail="Payment status not found for this request ID.")

        status = metadata.get("status", "UNKNOWN")
        response = {
            "checkout_request_id": checkout_id,
            "status": status,
            "amount": metadata.get("amount"),
            "phone": metadata.get("phone")
        }

        if status == "SUCCESS":
            response["radius_username"] = metadata.get("radius_username")
            response["radius_password"] = metadata.get("radius_password")
            response["message"] = "Payment successful and RADIUS user created!"
        elif status == "PENDING":
            response["message"] = "Payment is still pending. Awaiting confirmation from M-Pesa."
        elif status == "FAILED":
            response["message"] = metadata.get("result_desc", "Payment failed or was cancelled.")
        elif status == "FAILED_RADIUS_CREATION":
            response["message"] = metadata.get("result_desc", "Payment successful, but RADIUS user creation failed.")

        return response

    except Exception as e:
        print("Query Payment Status Error:", str(e))
        raise HTTPException(status_code=500, detail=f"Error querying payment status: {str(e)}")