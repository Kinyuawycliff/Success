# #! RECOVERY IF THE CODE BELOW WILL NOT WORK

# from fastapi import APIRouter, Request
# from pydantic import BaseModel
# from fastapi import HTTPException
# from typing import Optional
# import requests


# # from app.config import MPESA_CONFIG
# # from app.config import (CALLBACK_URL,BUSINESS_SHORT_CODE)
# from app.config import (MPESA_CONFIG)
# from app.utils.credentials import (get_access_token, generate_password)


# # # Load M-Pesa configuration
# CALLBACK_URL = MPESA_CONFIG["CALLBACK_URL"]
# BUSINESS_SHORT_CODE = MPESA_CONFIG["BUSINESS_SHORT_CODE"]


# router = APIRouter()


# # -------------------- Pydantic Model --------------------
# class STKPushRequest(BaseModel):
#     phone: str
#     amount: int
#     account_reference: Optional[str] = "zoomonet"
#     transaction_desc: Optional[str] = "Internet"




# # -------------------- STK Push Endpoint --------------------
# @router.post("/stkpush")
# def initiate_stk_push(payload: STKPushRequest):
#     try:
#         print(f"Received payment request: {payload.dict()}")

#         access_token = get_access_token()
#         password, timestamp = generate_password()

#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }

#         payload_data = {
#             "BusinessShortCode": BUSINESS_SHORT_CODE,
#             "Password": password,
#             "Timestamp": timestamp,
#             "TransactionType": "CustomerPayBillOnline",
#             "Amount": payload.amount,
#             "PartyA": payload.phone,
#             "PartyB": BUSINESS_SHORT_CODE,
#             "PhoneNumber": payload.phone,
#             "CallBackURL": CALLBACK_URL,
#             "AccountReference": payload.account_reference,
#             "TransactionDesc": payload.transaction_desc
#         }

#         stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#         response = requests.post(stk_url, headers=headers, json=payload_data)

#         print(f"M-Pesa API Response [{response.status_code}]: {response.text}")

#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)

#     except Exception as e:
#         print("STK Push Error:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

















from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi import HTTPException
from typing import Optional
import requests


from app.radius.radius_utils import create_radius_user
from app.utils.credentials import get_metadata_from_store


# from app.config import MPESA_CONFIG
# from app.config import (CALLBACK_URL,BUSINESS_SHORT_CODE)
from app.config import (MPESA_CONFIG)
from app.utils.credentials import (get_access_token, generate_password)
from app.utils.credentials import save_metadata_to_store


# # Load M-Pesa configuration
CALLBACK_URL = MPESA_CONFIG["CALLBACK_URL"]
BUSINESS_SHORT_CODE = MPESA_CONFIG["BUSINESS_SHORT_CODE"]


router = APIRouter()


# -------------------- Pydantic Model --------------------
class STKPushRequest(BaseModel):
    phone: str
    amount: int
    account_reference: Optional[str] = "zoomonet"
    transaction_desc: Optional[str] = "Internet"
    
    # Add your dynamic fields here
    bandwidth: str
    session_time: str
    devices: int



# -------------------- STK Push Endpoint --------------------
@router.post("/stkpush")
def initiate_stk_push(payload: STKPushRequest):
    try:
        print(f"Received payment request: {payload.dict()}")

        access_token = get_access_token()
        password, timestamp = generate_password()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload_data = {
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

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_url, headers=headers, json=payload_data)

        print(f"M-Pesa API Response [{response.status_code}]: {response.text}")

        # if response.status_code == 200:
        #     return response.json()
        





        if response.status_code == 200:
            mpesa_response = response.json()
            checkout_id = mpesa_response.get("CheckoutRequestID")


            # Store the metadata in your database or cache
            metadata = {
                "amount": payload.amount,
                "phone": payload.phone,
                "bandwidth": payload.bandwidth,
                "session_time": payload.session_time,
                "devices": payload.devices
            }

            # TODO: Store metadata in Redis, database, or even a Python dict (if for quick test)
            save_metadata_to_store(checkout_id, metadata)

            return {
        "mpesa_response": mpesa_response, **metadata}
        









        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        print("STK Push Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))





#! NOTE: This callback endpoint below is not complete its for testing purposes only it fails and creates a user
# -------------------- Callback Endpoint --------------------
@router.post("/callback")
async def mpesa_callback(request: Request):  # <-- make this async
    try:
        payload = await request.json()  # <-- await here
        print(f"Received M-Pesa callback: {payload}")

        # Extract CheckoutRequestID from the callback
        checkout_id = payload.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")

        if not checkout_id:
            raise HTTPException(status_code=400, detail="CheckoutRequestID not found in callback")

        # Retrieve metadata from your store (e.g., Redis, database)
        metadata = get_metadata_from_store(checkout_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found for CheckoutRequestID")

        # Create a radius user with the metadata
        result = create_radius_user(
                        metadata["phone"],
                        metadata["amount"],
                        metadata["bandwidth"],
                        metadata["session_time"],
                        metadata["devices"]
        )

        print(f"RADIUS user created successfully: {result}")
        return {"status": "success", "message": "Callback processed successfully"}

    except Exception as e:
        print("Callback Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))






#! NOTE: This callback endpoint quite works a bit well but its also for testing purposes it fails. it does not well.
# -------------------- Callback Endpoint --------------------
# @router.post("/callback")
# async def mpesa_callback(request: Request):
#     try:
#         payload = await request.json()
#         print(f"Received M-Pesa callback: {payload}")

#         callback_data = payload.get("Body", {}).get("stkCallback", {})
#         checkout_id = callback_data.get("CheckoutRequestID")
#         result_code = callback_data.get("ResultCode")
#         result_desc = callback_data.get("ResultDesc")

#         if not checkout_id:
#             raise HTTPException(status_code=400, detail="CheckoutRequestID not found in callback")

#         if result_code != 0:
#             # Transaction failed or cancelled
#             print(f"Transaction failed: {result_desc}")
#             return {
#                 "status": "failed",
#                 "message": f"Transaction not successful: {result_desc}",
#                 "code": result_code
#             }

#         # Transaction successful – proceed
#         metadata = get_metadata_from_store(checkout_id)

#         if not metadata:
#             raise HTTPException(status_code=404, detail="Metadata not found for CheckoutRequestID")

#         # Create RADIUS user
#         result = create_radius_user(
#             metadata["phone"],
#             metadata["amount"],
#             metadata["bandwidth"],
#             metadata["session_time"],
#             metadata["devices"]
#         )

#         print(f"RADIUS user created successfully: {result}")
#         return {
#             "status": "success",
#             "message": "Callback processed successfully",
#             "radius_result": result
#         }

#     except Exception as e:
#         print("Callback Error:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

