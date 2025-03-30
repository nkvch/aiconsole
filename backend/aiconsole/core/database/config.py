from typing import Callable, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from aiconsole.core.project.paths import get_project_directory_safe

Base = declarative_base()


class DatabaseConfig:
    _instance: Optional["DatabaseConfig"] = None
    _engine: Optional[Engine] = None
    _SessionLocal: Optional[Callable[[], Session]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._initialize_engine()

    def _initialize_engine(self) -> None:
        project_dir = get_project_directory_safe()
        if project_dir is None:
            raise ValueError("Project directory is not initialized")

        db_path = project_dir / "aiconsole.db"

        # Create SQLite database URL
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

        # Create engine
        self._engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # Needed for SQLite
        )

        # Create session factory
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._initialize_engine()
        assert self._engine is not None
        return self._engine

    @property
    def SessionLocal(self) -> Callable[[], Session]:
        if self._SessionLocal is None:
            self._initialize_engine()
        assert self._SessionLocal is not None
        return self._SessionLocal

    def get_db(self):
        if self._SessionLocal is None:
            self._initialize_engine()
        assert self._SessionLocal is not None
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self) -> None:
        if self._engine is None:
            self._initialize_engine()
        assert self._engine is not None
        Base.metadata.create_all(bind=self._engine)
