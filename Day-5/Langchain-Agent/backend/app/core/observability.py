from __future__ import annotations

from contextlib import contextmanager
import logging
import os
import random
from typing import Iterator, Optional
from uuid import UUID

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    from app.core.config import ENV_FILE

    load_dotenv(ENV_FILE)
    os.environ.setdefault(
        "LANGFUSE_TRACING_ENVIRONMENT",
        os.getenv("LANGFUSE_ENVIRONMENT", "development"),
    )
except ImportError:
    pass

try:
    from langfuse import get_client, propagate_attributes
    from langfuse.langchain import CallbackHandler
except ImportError:  # Keep local development usable before optional setup.
    get_client = None
    propagate_attributes = None
    CallbackHandler = None


def langfuse_configured() -> bool:
    settings = get_settings()
    return bool(
        get_client
        and CallbackHandler
        and settings.langfuse_public_key
        and settings.langfuse_secret_key
    )


def langfuse_enabled() -> bool:
    settings = get_settings()
    return (
        langfuse_configured()
        and 0 < settings.langfuse_sample_rate
        and random.random() <= settings.langfuse_sample_rate
    )


def flush_langfuse() -> None:
    if not langfuse_configured():
        return
    get_client().flush()


@contextmanager
def trace_chat_request(
    user_id: UUID,
    chat_id: UUID,
    prompt: str,
) -> Iterator[tuple[Optional[object], Optional[object]]]:
    if not langfuse_enabled():
        yield None, None
        return

    try:
        settings = get_settings()
        client = get_client()
        observation_context = client.start_as_current_observation(
            as_type="span",
            name="chat-response",
            input={"prompt": prompt},
        )
        observation = observation_context.__enter__()
        attributes_context = propagate_attributes(
            user_id=str(user_id),
            session_id=str(chat_id),
            metadata={
                "chat_id": str(chat_id),
                "environment": settings.langfuse_environment,
            },
            tags=["production-ai-agent", "chat"],
        )
        attributes_context.__enter__()
        handler = CallbackHandler()
    except Exception as error:
        logger.warning("Langfuse tracing disabled for request: %s", type(error).__name__)
        yield None, None
        return

    try:
        yield handler, observation
    except Exception as error:
        observation.update(
            output={"status": "error"},
            metadata={"error_type": type(error).__name__},
        )
        raise
    finally:
        attributes_context.__exit__(None, None, None)
        observation_context.__exit__(None, None, None)