import asyncio
import sys
from sqlalchemy import delete
from app.database.session import SessionLocal
from app.models.user import User

async def main():
    username = input("Enter GitHub username to delete: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
        
    async with SessionLocal() as db:
        # Check if user exists
        from sqlalchemy import select
        res = await db.execute(select(User).where(User.github_username == username))
        user = res.scalars().first()
        if not user:
            print(f"User '{username}' not found in the database.")
            return

        await db.execute(delete(User).where(User.github_username == username))
        await db.commit()
        print(f"Successfully deleted user '{username}' from the database.")

if __name__ == "__main__":
    # Ensure event loop policy on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
