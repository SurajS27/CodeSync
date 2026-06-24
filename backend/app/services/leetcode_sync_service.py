import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.enums import SyncStatus
from app.schemas.sync import LeetCodeSyncRequest
from app.services.repository_access_service import RepositoryAccessService
from app.services.sync_history_service import SyncHistoryService
from app.services.path_generation_service import PathGenerationService
from app.services.github_content_service import GitHubContentService

logger = logging.getLogger("codesync.services.leetcode_sync")


class LeetCodeSyncService:
    """Orchestrating sync service coordinating LeetCode submission payloads with GitHub repository contents."""

    @staticmethod
    async def sync_leetcode_submission(
        db: AsyncSession,
        user: User,
        request: LeetCodeSyncRequest
    ) -> dict:
        """Processes the LeetCode submission payload and commits README and code to GitHub safely and idempotently."""
        
        # 1. Validate repository ownership
        repo = await RepositoryAccessService.verify_repository_owner(
            db=db,
            user_id=user.id,
            repository_id=request.repository_id
        )

        # 2. Create initial SyncHistory record (PENDING)
        sync_record = await SyncHistoryService.create_sync_record(
            db=db,
            user_id=user.id,
            repository_id=request.repository_id,
            problem_title=request.problem_title,
            problem_slug=request.problem_slug,
            difficulty=request.difficulty.value,
            language=request.language
        )

        try:
            # 3. Transition status to RUNNING
            sync_record = await SyncHistoryService.update_sync_record(
                db=db,
                sync_id=sync_record.id,
                status=SyncStatus.RUNNING
            )

            # 4. Generate directory paths and filenames
            # TODO: Future metadata integrations to support:
            # - problem_id (e.g. 1)
            # - runtime (e.g. 45 ms)
            # - memory (e.g. 16.2 MB)
            # - submission_id (e.g. 123456789)
            
            prob_dir = PathGenerationService.generate_problem_directory(
                platform="leetcode",
                difficulty=request.difficulty.value,
                problem_slug=request.problem_slug
            )
            
            solution_filename = PathGenerationService.generate_solution_filename(request.language)
            solution_path = f"{prob_dir}{solution_filename}"
            readme_path = PathGenerationService.generate_readme_path(prob_dir)

            # 5. Generate dynamic README content
            readme_content = (
                f"# {request.problem_title}\n\n"
                f"Difficulty: {request.difficulty.value.capitalize()}\n\n"
                f"Platform: LeetCode\n\n"
                f"Language: {request.language.capitalize()}\n\n"
                f"Synced via [CodeSync](https://github.com/SurajS27/CodeSync)\n"
            )

            # 6. Check existing files on GitHub to ensure idempotency
            readme_sha = await GitHubContentService.check_file_exists(
                user=user,
                repo_full_name=repo.repo_full_name,
                path=readme_path
            )
            
            solution_sha = await GitHubContentService.check_file_exists(
                user=user,
                repo_full_name=repo.repo_full_name,
                path=solution_path
            )

            # 7. Commit README file
            readme_commit_msg = f"docs: sync README for {request.problem_title}"
            await GitHubContentService.create_or_update_file(
                user=user,
                repo_full_name=repo.repo_full_name,
                path=readme_path,
                content=readme_content,
                commit_message=readme_commit_msg,
                sha=readme_sha
            )

            # 8. Commit Solution File
            solution_commit_msg = f"code: sync solution for {request.problem_title} in {request.language}"
            github_response = await GitHubContentService.create_or_update_file(
                user=user,
                repo_full_name=repo.repo_full_name,
                path=solution_path,
                content=request.source_code,
                commit_message=solution_commit_msg,
                sha=solution_sha
            )

            # 9. Extract commit metadata details
            commit_sha = github_response.get("commit", {}).get("sha")
            commit_url = github_response.get("commit", {}).get("html_url")

            # 10. Update SyncHistory with COMPLETED status
            sync_record = await SyncHistoryService.update_sync_record(
                db=db,
                sync_id=sync_record.id,
                status=SyncStatus.COMPLETED,
                commit_sha=commit_sha,
                commit_url=commit_url,
                repository_path=prob_dir,
                github_file_path=solution_path
            )

            return {
                "sync_id": sync_record.id,
                "status": sync_record.sync_status,
                "commit_sha": sync_record.commit_sha,
                "commit_url": sync_record.commit_url,
                "repository_path": sync_record.repository_path,
                "github_file_path": sync_record.github_file_path,
                "error_message": None
            }

        except Exception as e:
            logger.error(f"Synchronization pipeline error: {str(e)}", exc_info=True)
            
            # Transition status to FAILED and record error message
            await SyncHistoryService.update_sync_record(
                db=db,
                sync_id=sync_record.id,
                status=SyncStatus.FAILED,
                error_message=str(e)
            )
            # Re-raise the exception so it propagates to API handlers
            raise
