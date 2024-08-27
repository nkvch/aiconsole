import os
import toml
from sqlalchemy.orm import Session
from aiconsole.database import SessionLocal
from aiconsole.models.material import Material, DefinedInEnum, TypeEnum, StatusEnum, ContentTypeEnum

TOML_DIR = os.path.join(os.path.dirname(__file__), 'preinstalled', 'materials')


def load_toml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return toml.load(file)


def map_toml_to_material(data):
    return Material(
        name=data.get('name', 'Unnamed Material'),
        version=data.get('version', '0.0.1'),
        usage=data.get('usage', ''),
        usage_examples=data.get('usage_examples', []),
        defined_in=DefinedInEnum(data.get('defined_in', 'aiconsole')),
        type=TypeEnum(data.get('type', 'material')),
        default_status=StatusEnum(data.get('default_status', 'enabled')),
        status=StatusEnum(data.get('status', 'enabled')),
        override=data.get('override', False),
        content_type=ContentTypeEnum(data.get('content_type', 'static_text')),
        content=data.get('content', '')
    )


def populate_database():
    db = SessionLocal()

    try:
        for filename in os.listdir(TOML_DIR):
            if filename.endswith('.toml'):
                file_path = os.path.join(TOML_DIR, filename)
                try:
                    toml_data = load_toml_file(file_path)
                except Exception as e:
                    print(f"Error occurred while parsing {file_path}: {e}")
                    continue

                existing_material = db.query(Material).filter(Material.name == toml_data.get('name')).first()
                if existing_material:
                    print(f"Material '{existing_material.name}' already exists. Skipping.")
                    continue

                material = map_toml_to_material(toml_data)
                db.add(material)

        db.commit()
        print("Database populated with materials from TOML files.")

    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
    finally:
        db.close()
