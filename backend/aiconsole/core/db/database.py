from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class DBProvider:

    def __init__(self):
        self.engine = create_engine("postgresql://myuser:mypassword@localhost:5433/mydb")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

db_provider = DBProvider()
