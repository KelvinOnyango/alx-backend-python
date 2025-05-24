import time
import sqlite3
import functools

query_cache = {}

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and not (args and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            result = func(*args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the query from either args or kwargs
        query = kwargs.get('query') or (args[1] if len(args) > 1 else None)
        
        if not query:
            return func(*args, **kwargs)
        
        # Check if query is in cache
        if query in query_cache:
            print("Returning cached result")
            return query_cache[query]
        
        # Execute and cache the result
        result = func(*args, **kwargs)
        query_cache[query] = result
        print("Caching new result")
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
