import mysql.connector
import os

def stream_users():
    """Generator to stream users one by one"""
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row
    
    cursor.close()
    conn.close()
