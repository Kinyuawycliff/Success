# import os
# import pymysql
# from dotenv import load_dotenv

# load_dotenv()


# def connection():
#     try:
#         conn = pymysql.connect(
#             host=DB_CONFIG["DB_HOST"],
#             user=DB_CONFIG["DB_USER"],
#             password=DB_CONFIG["DB_PASSWORD"],
#             database=DB_CONFIG["DB_NAME"],
#             port=DB_CONFIG["DB_PORT"]
#         )
#         print("✅ MySQL connection successful")
#         conn.close()
#     except Exception as e:
#         print("❌ MySQL connection failed:", e)


# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "db": os.getenv("DB_NAME"),
#     "port": int(os.getenv("DB_PORT")),
# }

# MPESA_CONFIG = {
#     "consumer_key": os.getenv("MPESA_CONSUMER_KEY"),
#     "consumer_secret": os.getenv("MPESA_CONSUMER_SECRET"),
#     "shortcode": os.getenv("MPESA_SHORTCODE"),
#     "passkey": os.getenv("MPESA_PASSKEY"),
#     "callback_url": os.getenv("MPESA_CALLBACK_URL"),
# }












# config.py
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
}

MPESA_CONFIG = {
    "CONSUMER_KEY": os.getenv("CONSUMER_KEY"),
    "CONSUMER_SECRET": os.getenv("CONSUMER_SECRET"),
    "BUSINESS_SHORT_CODE": os.getenv("BUSINESS_SHORT_CODE"),
    "PASSKEY": os.getenv("PASSKEY"),
    "CALLBACK_URL": os.getenv("CALLBACK_URL"),


    # Transaction Status-specific
    "INITIATOR_NAME": os.getenv("MPESA_INITIATOR_NAME"),
    "SECURITY_CREDENTIAL": os.getenv("MPESA_SECURITY_CREDENTIAL"),
    "TRANSACTION_RESULT_URL": os.getenv("MPESA_TRANSACTION_RESULT_URL"),
    "TRANSACTION_TIMEOUT_URL": os.getenv("MPESA_TRANSACTION_TIMEOUT_URL"),
}


def test_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ MySQL connection successful")
        conn.close()
    except Exception as e:
        print("❌ MySQL connection failed:", e)
        raise e



