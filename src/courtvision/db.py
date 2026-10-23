from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from courtvision.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_schema() -> None:
    from courtvision import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
