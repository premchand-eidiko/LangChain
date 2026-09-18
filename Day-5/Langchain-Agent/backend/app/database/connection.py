from sqlalchemy import create_engine

from app.core.config import get_settings


engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False}
    if get_settings().database_url.startswith("sqlite")
    else {},
)
