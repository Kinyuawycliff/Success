# from fastapi import FastAPI
# from app.mpesa.callback import router as mpesa_router

# app = FastAPI(title="ISP Billing System")

# app.include_router(mpesa_router, prefix="/mpesa")



# main.py
from fastapi import FastAPI
from app.config import test_db_connection
from fastapi.middleware.cors import CORSMiddleware
from app.mpesa.callback import router as mpesa_router
from app.mpesa.daraja import router as daraja_router
from app.radius.voucher import router as radius_router

app = FastAPI(title="ISP Billing System")


# ---- CORS SETUP --------
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        test_db_connection()
    except Exception as e:
        print("Startup DB connection test failed:", e)


app.include_router(mpesa_router, prefix="/mpesa")
app.include_router(daraja_router, prefix="/daraja")
app.include_router(radius_router, prefix="/radius")

@app.get("/")
async def root():
    return {"message": "Welcome to the ISP Billing System API"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)

