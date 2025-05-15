import mysql.connector
import os

def paginate_users(page_size, offset):
    """Fetch a page of users from the database"""
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM user_data LIMIT %s OFFSET %s",
        (page_size, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def lazy_paginate(page_size):
    """Generator for lazy loading paginated data"""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
