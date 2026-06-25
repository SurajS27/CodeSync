import asyncio
import sys
from sqlalchemy import select
from app.database.session import SessionLocal
from app.models.user import User
from app.models.repository import Repository

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(User).where(User.github_username == "Suraj2707"))
        user = res.scalars().first()
        if not user:
            print("User Suraj2707 not found in DB.")
            return
        print(f"User found: ID={user.id}, Username={user.github_username}")
        
        res_repos = await db.execute(select(Repository).where(Repository.user_id == user.id))
        repos = res_repos.scalars().all()
        print(f"Repositories count: {len(repos)}")
        for r in repos:
            print(f"- {r.repo_name} (ID: {r.id}, Status: {r.bootstrap_status})")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
