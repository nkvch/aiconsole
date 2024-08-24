from sqlalchemy import Column, Integer, String, Enum, Boolean, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class DefinedInEnum(str, enum.Enum):
    AICONSOLE = "aiconsole"
    PROJECT = "project"


class TypeEnum(str, enum.Enum):
    AGENT = "agent"
    MATERIAL = "material"


class StatusEnum(str, enum.Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    FORCED = "forced"


class ContentTypeEnum(str, enum.Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"


class Material(Base):
    __tablename__ = 'materials'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    version = Column(String, default="0.0.1", nullable=False)
    usage = Column(String, nullable=False)
    usage_examples = Column(ARRAY(Text))
    defined_in = Column(Enum(DefinedInEnum), nullable=False)
    type = Column(Enum(TypeEnum), default=TypeEnum.MATERIAL, nullable=False)
    default_status = Column(Enum(StatusEnum), default=StatusEnum.ENABLED, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.ENABLED, nullable=False)
    override = Column(Boolean, nullable=False)
    content_type = Column(Enum(ContentTypeEnum), default=ContentTypeEnum.STATIC_TEXT, nullable=False)
    content = Column(String, nullable=True)

