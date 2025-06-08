# import pymysql
# from datetime import datetime, timedelta
# from app.config import DB_CONFIG
# from app.utils.credentials import generate_credentials

# def create_radius_user(phone: str, amount: int):
#     username, password = generate_credentials()
#     session_end = datetime.now() + timedelta(hours=1)

#     conn = pymysql.connect(**DB_CONFIG)
#     cursor = conn.cursor()

#     cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)", (username, password))
#     cursor.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Session-Timeout', ':=', '3600')", (username,))
#     cursor.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Mikrotik-Rate-Limit', ':=', '2M/2M')", (username,))
#     cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Expiration', ':=', %s)", (username, session_end.strftime('%d %b %Y %H:%M:%S')))

#     conn.commit()
#     conn.close()

#     return {"username": username, "password": password}





#! RECOVERY IF THE CODE BELOW WILL NOT WORK

# import pymysql
# from app.config import DB_CONFIG
# from app.utils.credentials import generate_credentials

# def create_radius_user(phone: str, amount: int):
#     username, password = generate_credentials()


#     conn = pymysql.connect(**DB_CONFIG)
#     cursor = conn.cursor()

#     # Add user credentials
#     cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)", (username, password))

#     # Enforce one device per user
#     cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Simultaneous-Use', ':=', '1')", (username,))

#     # Set session timeout (1 hour)
#     cursor.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Session-Timeout', ':=', '3600')", (username,))

#     # Set bandwidth limit
#     cursor.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Mikrotik-Rate-Limit', ':=', '2M/2M')", (username,))

#     conn.commit()
#     conn.close()

#     return {"username": username, "password": password}





import pymysql
from app.config import DB_CONFIG
from app.utils.credentials import generate_credentials
from app.utils.time import convert_session_time_to_seconds

def create_radius_user(phone: str, amount: int, bandwidth: str, session_time: str, devices: int):
    # Convert session time to seconds
    session_time_seconds = convert_session_time_to_seconds(session_time)


    # Generate user credentials
    username, password = generate_credentials()


    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Add user credentials
    cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)", (username, password))

    # Enforce one device per user
    cursor.execute("INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Simultaneous-Use', ':=', %s)", (username, devices))

    # Set session timeout (1 hour)
    cursor.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Session-Timeout', ':=', %s)", (username, session_time_seconds))

    # Set bandwidth limit
    cursor.execute("INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Mikrotik-Rate-Limit', ':=', %s)", (username, bandwidth))

    conn.commit()
    conn.close()

    # Log user creation
    print(f"User {username} created with password {password}, session time {session_time}, bandwidth {bandwidth}, devices {devices}")
    # Return user credentials and settings
    return {"username": username, "password": password, "session_time": session_time, "bandwidth": bandwidth, "devices": devices}
    
