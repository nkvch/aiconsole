import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import OperationalError


logger = logging.getLogger(__name__)


class Database:
    """A class that manages the database connection"""

    def __init__(self, db_url: str, retry_attempts: int = 5, retry_delay: float = 2.0):
        """Initializes the database

        Args:
            db_url (str): URL of the database
            retry_attempts (int, optional): Number of connection retries in case of error. Defaults to 5.
            retry_delay (float, optional): Time between retries (in seconds). Defaults to 2.0.
        """

        self.db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        self.engine = create_async_engine(self.db_url, echo=False, future=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init_db(self) -> None:
        """It initializes the database and creates tables if there are none."""
        attempt = 0
        while attempt < self.retry_attempts:
            try:
                async with self.engine.begin() as conn:
                    await conn.run_sync(SQLModel.metadata.create_all)

                logger.info("✅ The database has been initialized")
                return

            except OperationalError as e:
                attempt += 1
                logger.warning(f"⚠️ Attempt {attempt}/{self.retry_attempts}: Database connection error: {e}")
                await asyncio.sleep(self.retry_delay)
        logger.error("❌ Failed to connect to database after maximum number of attempts.")

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Contextual database session manager

        :yield: Asynchronous SQLAlchemy session.
        """

        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    async def shutdown(self) -> None:
        """Close database connection with timeout safety"""
        try:
            await asyncio.wait_for(self.engine.dispose(), timeout=5.0)
            logger.info("✅ Database connection closed gracefully")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Database disposal timed out - forcing shutdown")
            self.engine.sync_engine.dispose()
