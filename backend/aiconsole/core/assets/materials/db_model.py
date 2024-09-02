from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field, validator
from typing import Optional

from aiconsole.core.project.paths import get_project_directory, get_project_directory_safe

# sqlalchemy model is created based on json model already existing in the project
Base = declarative_base()

class DbMaterial(Base):
    __tablename__ = 'materials'

    id = Column(Text, primary_key=True)
    name = Column(Integer, unique=True, index=True)
    version = Column(String)
    usage = Column(String)
    usage_examples = Column(Text)
    defined_in = Column(Text)
    status = Column(Text)
    content_type = Column(Text)
    content = Column(Text)

    __table_args__ = (
        CheckConstraint(
            "content_type IN ('static_text', 'dynamic_text', 'api')", 
            name='type_check'
        ),
    )

# tables are created in project initialization
