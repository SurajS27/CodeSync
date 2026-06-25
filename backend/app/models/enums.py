from enum import Enum


class BootstrapStatus(str, Enum):
    """Lifecycle states of repository initialization."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncStatus(str, Enum):
    """Execution status of challenge sync workflows."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DifficultyLevel(str, Enum):
    """Difficulty classifications for synchronized problems."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
