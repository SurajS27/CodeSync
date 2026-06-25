import asyncio
import sys
from datetime import datetime
from sqlalchemy import select
from app.database.session import SessionLocal
from app.models.user import User
from app.services.github_repository_service import GitHubRepositoryService
from app.services.repository_service import RepositoryService
from app.services.repository_bootstrap_service import RepositoryBootstrapService

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(User).where(User.github_username == "Suraj2707"))
        user = res.scalars().first()
        if not user:
            print("User Suraj2707 not found in DB.")
            return
            
        print("Testing auto-provisioning block...")
        try:
            default_repo_name = "codesync-solutions"
            unique_name = await GitHubRepositoryService.generate_unique_repository_name(db, user, default_repo_name)
            print(f"Generated unique name: {unique_name}")
            
            github_data = await GitHubRepositoryService.create_github_repository(
                user,
                unique_name,
                is_private=True
            )
            print(f"GitHub repo created: {github_data.get('repo_name')}")
            
            github_created = datetime.fromisoformat(github_data["created_at"].replace("Z", "+00:00"))
            github_updated = datetime.fromisoformat(github_data["updated_at"].replace("Z", "+00:00"))

            new_repo_data = {
                "github_repo_id": github_data["id"],
                "repo_name": github_data["name"],
                "repo_full_name": github_data["full_name"],
                "repo_url": github_data["html_url"],
                "owner_github_username": github_data["owner"]["login"],
                "default_branch": github_data["default_branch"],
                "is_private": github_data["private"],
                "github_created_at": github_created,
                "github_updated_at": github_updated
            }
            
            new_repo = await RepositoryService.create_repository_record(db, user.id, new_repo_data)
            print(f"DB repo record created: {new_repo.id}")
            await RepositoryBootstrapService.bootstrap_repository(db, user, new_repo)
            print("Bootstrap completed successfully!")
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
