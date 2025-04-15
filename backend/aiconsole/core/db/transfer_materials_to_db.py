import os
from pathlib import Path

import tomllib
from sqlalchemy import create_engine

from aiconsole.core.db.database import Base, db_provider
from aiconsole.core.db.models import Material

Base.metadata.drop_all(db_provider.engine)
Base.metadata.create_all(db_provider.engine)

session = db_provider.SessionLocal()

try:
    materials_dir = Path.cwd()/'backend'/'aiconsole'/'preinstalled'/'materials'
    project_dir = Path.cwd()/'materials'

    for dir_path in [materials_dir, project_dir]:
        for filename in os.listdir(dir_path):
            if filename.endswith(".toml"):
                filepath = os.path.join(dir_path, filename)

                with open(filepath, "rb") as toml_file:
                    config = tomllib.load(toml_file)

                asset = Material(id=os.path.splitext(os.path.basename(filename))[0], name=config["name"])

                for key, value in config.items():
                    if hasattr(asset, key):
                        setattr(asset, key, value)
                
                session.add(asset)
                session.commit()
finally:
    session.close()
