import seed

def lazy_paginate(page_size):
    """Lazily load paginated data"""
    offset = 0
    while True:
        page = seed.paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
