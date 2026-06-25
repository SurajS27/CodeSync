import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BOOTSTRAP_VERSION
from app.models.enums import BootstrapStatus
from app.models.repository import Repository
from app.models.user import User
from app.services.github_content_service import GitHubContentService
from app.services.repository_service import RepositoryService

logger = logging.getLogger("codesync.services.bootstrap")


class RepositoryBootstrapService:
    """Manages structural initialization (templates and directories) of GitHub repositories."""

    @staticmethod
    async def bootstrap_repository(
        db: AsyncSession, user: User, repo: Repository, force: bool = False
    ) -> bool:
        """Initializes the repository with the default CodeSync structure.

        Deploys:
        - README.md (with dynamic repo name)
        - .gitignore
        - metadata/config.json
        - Platform subdirectories placeholders (leetcode/easy/medium/hard)

        Features state tracking, idempotence checks, and error logging.
        """
        # 1. Enforce hardened idempotence logic
        if (
            repo.bootstrap_status == BootstrapStatus.COMPLETED
            and repo.bootstrapped_at is not None
            and not force
        ):
            logger.info(
                f"Repository '{repo.repo_full_name}' is already successfully bootstrapped. Bypassing execution."
            )
            return True

        logger.info(
            f"Starting repository bootstrap sequence for: {repo.repo_full_name} (force={force})"
        )

        # 2. Transition status to RUNNING, set attempt timestamp, and clear previous errors
        await RepositoryService.update_repository_record(
            db,
            repo.id,
            {
                "bootstrap_status": BootstrapStatus.RUNNING,
                "bootstrap_error": None,
                "last_bootstrap_attempt_at": datetime.now(timezone.utc),
            },
        )
        await db.refresh(repo)

        try:
            # 3. Define files and contents dynamically
            readme_content = (
                f"# {repo.repo_name}\n\n"
                "Welcome to my CodeSync solutions repository!\n\n"
                "This repository automatically synchronizes my accepted coding challenge submissions from LeetCode to GitHub using the CodeSync Chrome Extension.\n\n"
                "### How it works\n\n"
                "1. **Solve**: Complete a challenge on LeetCode.\n"
                "2. **Detect**: CodeSync automatically captures the accepted submission.\n"
                "3. **Sync**: The solution code and structured problem description files are committed directly to this repository.\n\n"
                "---\n"
                f"Repository Bootstrap Version: {BOOTSTRAP_VERSION}\n\n"
                "Generated automatically using CodeSync.\n"
            )

            gitignore_content = (
                "# Local configuration files\n"
                ".env\n"
                "*.log\n"
                ".idea/\n"
                ".vscode/\n"
                "__pycache__/\n"
                "*.pyc\n"
            )

            config_content = json.dumps(
                {
                    "version": BOOTSTRAP_VERSION,
                    "platforms": {
                        "leetcode": True,
                        "hackerrank": False,
                        "codeforces": False,
                        "geeksforgeeks": False,
                    },
                },
                indent=2,
            )

            files_to_create = {
                "README.md": readme_content,
                ".gitignore": gitignore_content,
                "metadata/config.json": config_content,
                "leetcode/easy/.gitkeep": "",
                "leetcode/medium/.gitkeep": "",
                "leetcode/hard/.gitkeep": "",
            }

            # TODO: Future optimization:
            # Replace multiple GitHub Contents API commits with a single Git Tree API commit
            # to reduce API calls and repository commit noise.

            # 4. Sequential upload to GitHub API
            for path, content in files_to_create.items():
                sha = await GitHubContentService.check_file_exists(
                    user, repo.repo_full_name, path
                )
                await GitHubContentService.create_or_update_file(
                    user=user,
                    repo_full_name=repo.repo_full_name,
                    path=path,
                    content=content,
                    commit_message=f"docs: bootstrap CodeSync layout [{path}]",
                    sha=sha,
                )

            # 5. Transition status to COMPLETED and record timestamp
            update_data = {
                "bootstrapped_at": datetime.now(timezone.utc),
                "bootstrap_version": BOOTSTRAP_VERSION,
                "bootstrap_status": BootstrapStatus.COMPLETED,
                "bootstrap_error": None,
            }
            await RepositoryService.update_repository_record(db, repo.id, update_data)
            await db.refresh(repo)
            logger.info(
                f"Repository bootstrap completed successfully for: {repo.repo_full_name}"
            )
            return True

        except Exception as e:
            # Truncate error message to 2000 characters to prevent oversized database writes
            error_message = str(e)[:2000]
            logger.error(
                f"Error provisioning paths during bootstrap of '{repo.repo_full_name}': {error_message}"
            )

            # 6. Transition status to FAILED and record details in database before re-raising
            try:
                await RepositoryService.update_repository_record(
                    db,
                    repo.id,
                    {
                        "bootstrap_status": BootstrapStatus.FAILED,
                        "bootstrap_error": error_message,
                    },
                )
                await db.refresh(repo)
            except Exception as db_err:
                logger.error(
                    f"Failed to persist failure status for '{repo.repo_full_name}': {str(db_err)}"
                )

            raise
