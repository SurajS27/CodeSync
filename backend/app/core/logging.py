import logging
import sys

from app.core.config import settings

logger = logging.getLogger("codesync")


def setup_logging() -> None:
    """Configures structured and standardized logging across the application."""
    log_format = "%(asctime)s - %(levelname)s - [%(name)s:%(metadata)s] - %(message)s"
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Custom Formatter to easily inject dynamic context if needed, or keep it standard
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            # Fallback metadata if not provided
            if not hasattr(record, "metadata"):
                record.metadata = f"{record.filename}:{record.lineno}"
            return super().format(record)

    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomFormatter(log_format)
    handler.setFormatter(formatter)

    # Root Logger Configuration
    root_logger = logging.getLogger()
    # Remove default handlers to prevent duplicate logs
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Apply configuration to third-party loggers
    for lib_logger_name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy.engine",
    ]:
        lib_logger = logging.getLogger(lib_logger_name)
        lib_logger.handlers = []
        lib_logger.addHandler(handler)
        lib_logger.setLevel(log_level)
        lib_logger.propagate = False


def log_startup() -> None:
    """Log startup status of the application."""
    logger.info(
        "Initializing CodeSync API backend foundation...", extra={"metadata": "startup"}
    )
    logger.info(f"Environment: {settings.ENV}", extra={"metadata": "startup"})
    logger.info(
        f"Log Level set to: {settings.LOG_LEVEL}", extra={"metadata": "startup"}
    )


def log_shutdown() -> None:
    """Log shutdown status of the application."""
    logger.info(
        "Shutting down CodeSync API backend gracefully...",
        extra={"metadata": "shutdown"},
    )
