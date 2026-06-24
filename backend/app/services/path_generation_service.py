class PathGenerationService:
    """Utility service for mapping coding platform metadata to GitHub repository paths and filenames."""

    # Supported language mappings to match file extensions
    LANGUAGE_MAPPING = {
        "python": "solution.py",
        "javascript": "solution.js",
        "typescript": "solution.ts",
        "java": "Solution.java",
        "cpp": "solution.cpp",
        "c": "solution.c",
        "go": "solution.go",
        "rust": "solution.rs",
        "csharp": "Solution.cs"
    }

    @staticmethod
    def generate_problem_directory(platform: str, difficulty: str, problem_slug: str) -> str:
        """Generates the folder directory structure for a challenge submission."""
        clean_platform = platform.strip().lower()
        clean_difficulty = difficulty.strip().lower()
        clean_slug = problem_slug.strip().lower()
        return f"{clean_platform}/{clean_difficulty}/{clean_slug}/"

    @classmethod
    def generate_solution_filename(cls, language: str) -> str:
        """Determines the appropriate solution filename with file extension for a given language."""
        clean_lang = language.strip().lower()
        if clean_lang not in cls.LANGUAGE_MAPPING:
            raise ValueError(f"Unsupported programming language: '{language}'")
        return cls.LANGUAGE_MAPPING[clean_lang]

    @staticmethod
    def generate_readme_path(directory: str) -> str:
        """Generates the absolute path to the problem description README file."""
        base_dir = directory if directory.endswith("/") else f"{directory}/"
        return f"{base_dir}README.md"
