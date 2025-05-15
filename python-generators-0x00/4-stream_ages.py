import mysql.connector
import os

def stream_user_ages():
    """Generator for user ages"""
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database="ALX_prodev"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data")
    
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row[0]
    
    cursor.close()
    conn.close()

def calculate_average_age():
    """Calculate average age using generator"""
    total = 0
    count = 0
    
    for age in stream_user_ages():
        total += age
        count += 1
    
    if count == 0:
        return 0
    return total / count

if __name__ == "__main__":
    avg = calculate_average_age()
    print(f"Average age of users: {avg:.2f}")
