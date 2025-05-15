import mysql.connector
import os

def stream_users_in_batches(batch_size):
    """Yield batches of users"""
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database="ALX_prodev"
    )
    offset = 0
    
    while True:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user_data LIMIT %s OFFSET %s",
            (batch_size, offset)
        )
        batch = cursor.fetchall()
        cursor.close()
        
        if not batch:
            break
            
        yield batch
        offset += batch_size
    
    conn.close()

def batch_processing(batch_size):
    """Process batches to filter users > 25"""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
