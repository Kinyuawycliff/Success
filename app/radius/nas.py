import pymysql
from app.config import DB_CONFIG

def insert_nas(nasname, shortname, secret, description):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO nas (nasname, shortname, type, ports, secret, description)
        VALUES (%s, %s, 'other', NULL, %s, %s)
    """, (nasname, shortname, secret, description))

    conn.commit()
    conn.close()
