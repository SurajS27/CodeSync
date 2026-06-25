import datetime
from typing import Optional

from app.services.path_generation_service import PathGenerationService


class READMEGenerationService:
    """Service responsible for generating professional, informative, and formatted Markdown READMEs for synchronized LeetCode problems."""

    # Proper language display mapping
    LANGUAGE_MAP = {
        "cpp": "C++",
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "go": "Go",
        "rust": "Rust",
        "c": "C",
        "csharp": "C#",
    }

    @classmethod
    def get_language_display(cls, language: str) -> str:
        """Translates language keys to proper display names (e.g. cpp -> C++)."""
        clean_lang = language.strip().lower()
        return cls.LANGUAGE_MAP.get(clean_lang, language.capitalize())

    @classmethod
    def generate_readme(
        cls,
        problem_title: str,
        problem_slug: str,
        difficulty: str,
        language: str,
        runtime: Optional[str] = None,
        memory: Optional[str] = None,
        commit_sha: Optional[str] = None,
    ) -> str:
        """Generates standard GitHub-friendly README markdown for a solved problem."""

        # Format variables
        lang_display = cls.get_language_display(language)
        difficulty_cap = difficulty.strip().capitalize()
        difficulty_lower = difficulty.strip().lower()
        slug_lower = problem_slug.strip().lower()

        # Link and path variables
        problem_url = f"https://leetcode.com/problems/{slug_lower}/"
        repo_location = f"leetcode/{difficulty_lower}/{slug_lower}/"

        try:
            solution_file = PathGenerationService.generate_solution_filename(language)
        except Exception:
            solution_file = "solution.cpp"  # Safe default fallback

        # Current UTC sync timestamp
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        sync_time_str = now_utc.strftime("%Y-%m-%d %H:%M UTC")

        # 1. Base details sections
        markdown = (
            f"# {problem_title}\n\n"
            f"## Problem Information\n\n"
            f"| Field | Value |\n"
            f"|---------|---------|\n"
            f"| Platform | LeetCode |\n"
            f"| Difficulty | {difficulty_cap} |\n"
            f"| Language | {lang_display} |\n\n"
            f"## Problem Link\n\n"
            f"{problem_url}\n\n"
            f"## Repository Location\n\n"
            f"{repo_location}\n\n"
            f"## Solution\n\n"
            f"The implementation can be found in:\n\n"
            f"{solution_file}\n\n"
        )

        # 2. Optional Metrics section (skip if None, empty, or "N/A" values)
        has_runtime = runtime and runtime.strip() and runtime.strip().upper() != "N/A"
        has_memory = memory and memory.strip() and memory.strip().upper() != "N/A"

        if has_runtime or has_memory:
            markdown += (
                "## Submission Metrics\n\n| Metric | Value |\n|----------|----------|\n"
            )
            if has_runtime:
                markdown += f"| Runtime | {runtime.strip()} |\n"
            if has_memory:
                markdown += f"| Memory | {memory.strip()} |\n"
            markdown += "\n"

        # 3. Optional GitHub Commit SHA section
        if commit_sha and commit_sha.strip():
            markdown += (
                f"## GitHub Commit\n\n" f"Commit SHA:\n" f"{commit_sha.strip()}\n\n"
            )

        # 4. Sync Information footer
        markdown += (
            f"## Sync Information\n\n"
            f"Generated automatically using CodeSync.\n\n"
            f"## Metadata\n\n"
            f"- Synced At: {sync_time_str}\n"
            f"- Language: {lang_display}\n"
            f"- Difficulty: {difficulty_cap}\n\n"
            f"---\n\n"
            f"\u2b50 Synced with CodeSync\n"
        )

        return markdown
