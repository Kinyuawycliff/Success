# # from fastapi import APIRouter, Request
# # from app.radius.radius_utils import create_radius_user

# # router = APIRouter()

# # @router.post("/callback")
# # async def mpesa_callback(request: Request):
# #     data = await request.json()
# #     if data['Body']['stkCallback']['ResultCode'] == 0:
# #         phone = next(i['Value'] for i in data['Body']['stkCallback']['CallbackMetadata']['Item'] if i['Name'] == 'PhoneNumber')
# #         amount = next(i['Value'] for i in data['Body']['stkCallback']['CallbackMetadata']['Item'] if i['Name'] == 'Amount')
# #         return create_radius_user(phone, amount)
# #     return {"status": "failed"}



# #! RECOVERY IF THE CODE BELOW WILL NOT WORK

# # from fastapi import APIRouter, Request
# # from pydantic import BaseModel
# # from app.radius.radius_utils import create_radius_user

# # router = APIRouter()

# # # Pydantic model for validation
# # class RadiusUserRequest(BaseModel):
# #     phone: str
# #     amount: int




# # # Manual test endpoint
# # @router.post("/callback")
# # async def test_radius_user(data: RadiusUserRequest):
# #     return create_radius_user(data.phone, data.amount)






# #! TESTING THIS ONE NOW

# from fastapi import APIRouter, Request
# from pydantic import BaseModel
# from app.radius.radius_utils import create_radius_user

# router = APIRouter()

# # Pydantic model for validation
# class RadiusUserRequest(BaseModel):
#     phone: str
#     amount: int
#     bandwidth: str # eg: "2M/2M"
#     sessionTime: str # e.g., "1h", "30m", "120s"
#     devices: int




# # Manual test endpoint
# @router.post("/callback")
# async def test_radius_user(data: RadiusUserRequest):
#     return create_radius_user(data.phone, data.amount, data.bandwidth, data.sessionTime, data.devices)
# #     # return create_radius_user(data.phone, data.amount)













# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# from app.radius.radius_utils import create_radius_user

# router = APIRouter()

# @router.post("/callback")
# async def mpesa_callback(request: Request):
#     data = await request.json()

#     try:
#         callback = data["Body"]["stkCallback"]
#         result_code = callback["ResultCode"]
#         result_desc = callback["ResultDesc"]

#         # Handle failed or cancelled transactions
#         if result_code != 0:
#             print(f"[M-PESA CALLBACK] Transaction failed or cancelled: {result_desc}")
#             return JSONResponse(status_code=200, content={"status": "failed", "message": result_desc})
        
#         #? Handle successful transaction
#         # CallbackMetadata is present only on success
#         metadata = callback.get("CallbackMetadata", {}).get("Item", [])
        
#         # Extract data
#         amount = next((item["Value"] for item in metadata if item["Name"] == "Amount"), None)
#         phone = next((item["Value"] for item in metadata if item["Name"] == "PhoneNumber"), None)

#         if not phone or not amount:
#             return JSONResponse(status_code=400, content={"status": "error", "message": "Incomplete callback metadata."})

#         # Set default or dynamic values (replace with actual logic if dynamic)
#         bandwidth = "2M/2M" 
#         session_time = "1h"
#         devices = 1

#         # Create Radius user
#         create_radius_user(str(phone), int(amount), bandwidth, session_time, devices)

#         print(f"[M-PESA CALLBACK] User created: Phone: {phone}, Amount: {amount}")
#         return JSONResponse(status_code=200, content={"status": "success", "message": "User created successfully."})

#     except Exception as e:
#         print(f"[M-PESA CALLBACK ERROR] {str(e)}")
#         return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})






# # from fastapi import APIRouter, Request
# # from app.radius.radius_utils import create_radius_user

# # router = APIRouter()

# # @router.post("/callback")
# # async def mpesa_callback(request: Request):
# #     data = await request.json()
# #     if data['Body']['stkCallback']['ResultCode'] == 0:
# #         phone = next(i['Value'] for i in data['Body']['stkCallback']['CallbackMetadata']['Item'] if i['Name'] == 'PhoneNumber')
# #         amount = next(i['Value'] for i in data['Body']['stkCallback']['CallbackMetadata']['Item'] if i['Name'] == 'Amount')
# #         return create_radius_user(phone, amount)
# #     return {"status": "failed"}



# #! RECOVERY IF THE CODE BELOW WILL NOT WORK

# # from fastapi import APIRouter, Request
# # from pydantic import BaseModel
# # from app.radius.radius_utils import create_radius_user

# # router = APIRouter()

# # # Pydantic model for validation
# # class RadiusUserRequest(BaseModel):
# #     phone: str
# #     amount: int




# # # Manual test endpoint
# # @router.post("/callback")
# # async def test_radius_user(data: RadiusUserRequest):
# #     return create_radius_user(data.phone, data.amount)






# #! TESTING THIS ONE NOW

# from fastapi import APIRouter, Request
# from pydantic import BaseModel
# from app.radius.radius_utils import create_radius_user

# router = APIRouter()

# # Pydantic model for validation
# class RadiusUserRequest(BaseModel):
#     phone: str
#     amount: int
#     bandwidth: str # eg: "2M/2M"
#     sessionTime: str # e.g., "1h", "30m", "120s"
#     devices: int




# # Manual test endpoint
# @router.post("/callback")
# async def test_radius_user(data: RadiusUserRequest):
#     return create_radius_user(data.phone, data.amount, data.bandwidth, data.sessionTime, data.devices)
# #     # return create_radius_user(data.phone, data.amount)













from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.radius.radius_utils import create_radius_user
from app.utils.credentials import get_metadata_from_store

router = APIRouter()

@router.post("/callback")
async def mpesa_callback(request: Request):
    data = await request.json()
    print(f"[M-PESA CALLBACK] Received data: {data}")

    try:
        callback = data["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        result_desc = callback["ResultDesc"]

        # Handle failed or cancelled transactions
        if result_code != 0:
            print(f"[M-PESA CALLBACK] Transaction failed or cancelled: {result_desc}")
            return JSONResponse(status_code=200, content={"status": "failed", "message": result_desc})
        
        """  #? Handle successful transaction
        # CallbackMetadata is present only on success
        metadata = callback.get("CallbackMetadata", {}).get("Item", [])
        
        # Extract data
        amount = next((item["Value"] for item in metadata if item["Name"] == "Amount"), None)
        phone = next((item["Value"] for item in metadata if item["Name"] == "PhoneNumber"), None)

        if not phone or not amount:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Incomplete callback metadata."})

        # Set default or dynamic values (replace with actual logic if dynamic)
        bandwidth = "2M/2M" 
        session_time = "1h"
        devices = 1   """




        #? Handle successful transaction testing

        checkout_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        # Retrieve metadata
        user_metadata = get_metadata_from_store(checkout_id)

        if not user_metadata:
            return JSONResponse(status_code=400, content={"status": "error", "message": "User metadata not found."})
        
        # Extract data
        amount = user_metadata["amount"]
        phone = user_metadata["phone"]
        bandwidth = user_metadata["bandwidth"]
        session_time = user_metadata["session_time"]
        devices = user_metadata["devices"]

        if not phone or not amount:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Incomplete callback metadata."})




        # 👤 Create RADIUS user (simulate login access)
        result = create_radius_user(str(phone), int(amount), bandwidth, session_time, devices)

        print(f"[M-PESA CALLBACK] Radius user created for {phone} with {bandwidth} for {session_time}")
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "User created successfully.",
            "radius_result": result
        })


    except Exception as e:
        print(f"[M-PESA CALLBACK ERROR] {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal Server Error"})

