import mysql.connector
import csv
import os

def connect_db():
    """Connect to MySQL server"""
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )

def create_database(connection):
    """Create ALX_prodev database"""
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()

def connect_to_prodev():
    """Connect to ALX_prodev database"""
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database="ALX_prodev"
    )

def create_table(connection):
    """Create user_data table"""
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(10,2) NOT NULL
        )
    """)
    cursor.close()

def insert_data(connection, csv_file):
    """Insert data from CSV"""
    cursor = connection.cursor()
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT IGNORE INTO user_data 
                VALUES (%s, %s, %s, %s)
            """, (row['user_id'], row['name'], row['email'], row['age']))
    connection.commit()
    cursor.close()
