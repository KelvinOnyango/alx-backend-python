import sqlite3

class ExecuteQuery:
    def __init__(self, query, params=None, db_name='users.db'):
        self.query = query
        self.params = params or ()
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Open connection and execute query when entering context"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Using the context manager with our specific query
with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as cursor:
    results = cursor.fetchall()
    for row in results:
        print(row)
