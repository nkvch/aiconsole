"""
NOT FINISHED FULLY.

BUG: SOME TOML FILES ARE NOT FORMATED RIGHT, SO NOT ALL TOML FILES ARE PARSED WHEN IT GETS ERROR IT GOES FOR NEXT TOML FILE.
TODO: SOME TOML FILES SHOW CONTENT IN PYTHON FILE SHOULD ADD CODE TO READ INSIDE OF PYTHON FILES.
"""
import toml
from pathlib import Path
from sqlalchemy.orm import Session
from aiconsole.api.endpoints.materials.models import Material
from aiconsole.api.endpoints.materials.database import SessionLocal

def load_toml_files(directory: str):
    """Load all TOML files from the specified directory."""
    absolute_directory = Path(directory).resolve()
    print(f"Searching for TOML files in: {absolute_directory}")

    toml_data = []
    toml_files_found = list(Path(directory).glob('*.toml'))

    if not toml_files_found:
        print("No TOML files found in the directory.")
        return toml_data

    for toml_file in toml_files_found:
        try:
            with open(toml_file, 'r') as file:
                data = toml.load(file)
                print(f"Loaded data from {toml_file.name}: {data}")
                toml_data.append(data)
        except toml.TomlDecodeError as e:
            print(f"Error decoding TOML file {toml_file.name}: {e}")
        except Exception as e:
            print(f"Error reading TOML file {toml_file.name}: {e}")

    return toml_data

def transform_toml_to_db_data(toml_data):
    """Transform TOML data into a format suitable for the database."""
    db_data = []
    for item in toml_data:
        material_data = {
            "name": item.get("name"),
            "version": item.get("version"),
            "usage": item.get("usage"),
            "usage_examples": item.get("usage_examples", []),
            "content_type": item.get("content_type"),
            "content": item.get("content"),
            "content_static_text": item.get("content_static_text"),
            "default_status": item.get("default_status", "enabled"),
        }
        db_data.append(material_data)
    return db_data

def insert_data_into_db(data, db: Session):
    """Insert transformed data into the database."""
    for item in data:
        try:
            db_material = Material(**item)
            db.add(db_material)
        except Exception as e:
            print(f"Error inserting data into the database: {e}")
            continue
    try:
        db.commit()
    except Exception as e:
        print(f"Error committing data to the database: {e}")
        db.rollback()

def main():
    """Main function to load, transform, and insert TOML data into the database."""

    toml_files = load_toml_files('../../../preinstalled/materials/')

    if not toml_files:
        print("No TOML files were processed.")
        return

    print("Processing TOML files...")

    transformed_data = transform_toml_to_db_data(toml_files)

    # Insert data into PostgreSQL
    db = SessionLocal()
    try:
        insert_data_into_db(transformed_data, db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
