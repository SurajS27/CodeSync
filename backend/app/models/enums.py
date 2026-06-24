from enum import Enum


class BootstrapStatus(str, Enum):
    """Lifecycle states of repository initialization."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
