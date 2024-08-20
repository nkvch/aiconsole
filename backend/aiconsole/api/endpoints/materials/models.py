"""
This file defines the `Material` model for SQLAlchemy ORM, representing the `materials` table in the database.
"""
from sqlalchemy import Column, Integer, String, Text, Enum, ARRAY
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Material(Base):
    __tablename__ = 'materials'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String)
    usage = Column(Text)
    usage_examples = Column(ARRAY(Text))
    content_type = Column(Enum('api', 'dynamic_text', 'static_text', name='materialcontenttype'))
    content = Column(Text)
    content_static_text = Column(Text)
    default_status = Column(String)
