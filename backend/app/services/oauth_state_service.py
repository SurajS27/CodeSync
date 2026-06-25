import secrets
import time

from app.core.config import settings

# In-memory dictionary storing: state_token -> expiration_epoch_seconds
# TODO: Replace this in-memory store with Redis in production to support horizontal scaling.
_state_store: dict[str, float] = {}


class OAuthStateService:
    """Manages the generation, validation, and single-use deletion of OAuth state parameters."""

    @staticmethod
    def create_state() -> str:
        """Generates a random secure state token, registers it in the store, and returns it."""
        state = secrets.token_urlsafe(32)
        # Calculate expiration time
        expiration = time.time() + (settings.OAUTH_STATE_EXPIRE_MINUTES * 60)
        _state_store[state] = expiration
        return state

    @staticmethod
    def validate_state(state: str) -> bool:
        """Validates that a state is present, valid, and not expired.

        Enforces single-use.
        """
        if not state:
            return False

        expiration = _state_store.get(state)
        if not expiration:
            return False

        # Enforce single-use by removing the state token immediately
        del _state_store[state]

        # Verify expiration
        if time.time() > expiration:
            return False

        return True

    @staticmethod
    def delete_state(state: str) -> None:
        """Deletes a state from the store if it exists."""
        if state in _state_store:
            del _state_store[state]
