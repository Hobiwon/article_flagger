import os
import oracledb

dsn = "oracle/XEPDB1"

def get_connection():
    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"), 
        dsn=dsn
    )
    return conn