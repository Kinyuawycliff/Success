import pymysql
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from typing import Optional, Annotated
from app.config import DB_CONFIG
from app.utils.credentials import generate_voucher
from app.utils.time import convert_session_time_to_seconds

router = APIRouter()



# Input schema
class VoucherInput(BaseModel):
    amount: int
    bandwidth: Annotated[str, constr(pattern=r"^\d+[KMG]?/\d+[KMG]?$")]
    session_time: Annotated[str, constr(pattern=r"^\d+[smh]$")]
    devices: int
    phone: Optional[str] = None

@router.post("/voucher")
def create_voucher(data: VoucherInput):
    """
    Create a FreeRADIUS voucher with default password and optional phone.
    """
    try:
        session_time_seconds = convert_session_time_to_seconds(data.session_time)
        username = generate_voucher(length=6)
        password = "123456"  # Default password

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert user data
        cursor.execute(
            "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)",
            (username, password)
        )
        cursor.execute(
            "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Simultaneous-Use', ':=', %s)",
            (username, str(data.devices))
        )
        cursor.execute(
            "INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Session-Timeout', ':=', %s)",
            (username, str(session_time_seconds))
        )
        cursor.execute(
            "INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Mikrotik-Rate-Limit', ':=', %s)",
            (username, data.bandwidth)
        )

        conn.commit()
        conn.close()

        voucher_data = {
            "username": username,
            "password": password,
            "amount": data.amount,
            "bandwidth": data.bandwidth,
            "session_time": data.session_time,
            "devices": data.devices,
            "phone": data.phone
        }

        # 🔍 Log the created voucher
        print("🎫 Voucher created:", voucher_data)

        return voucher_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
