import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open a new database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection as the first argument if not already provided
            if 'conn' not in kwargs and not (args and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            # Call the decorated function
            result = func(*args, **kwargs)
            return result
        finally:
            # Ensure the connection is closed even if an error occurs
            conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)
