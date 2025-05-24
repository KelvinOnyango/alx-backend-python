import asyncio
import aiosqlite

async def async_fetch_users():
    """Fetch all users from the database"""
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("All users fetched")
            return results

async def async_fetch_older_users():
    """Fetch users older than 40 from the database"""
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            print("Older users fetched")
            return results

async def fetch_concurrently():
    """Run both queries concurrently"""
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return results

if __name__ == "__main__":
    all_users, older_users = asyncio.run(fetch_concurrently())
    print("\nAll users:", len(all_users))
    print("Users older than 40:", len(older_users))
