from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

print(DB_NAME)

# SQLAlchemy Database URL
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database_and_table():
    print("This function is called to create the database and table.")

    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(
        sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;"),
        [DB_NAME]
    )
    db_exists = cursor.fetchone()

    if db_exists:
        print(f"Database '{DB_NAME}' already exists. Skipping creation.")
        cursor.close()
        conn.close()
        return

    # Create a new database if it doesn't exist
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(
        sql.Identifier(DB_NAME)
    ))
    print(f"Database '{DB_NAME}' created successfully.")

    cursor.close()
    conn.close()

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # Create the materials table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            version VARCHAR(50),
            usage TEXT,
            usage_examples TEXT[],
            content_type VARCHAR(50) NOT NULL,
            content TEXT,
            content_static_text TEXT,
            default_status VARCHAR(50)
        );
        """)
        print(f"Table 'materials' created successfully.")
        conn.commit()

        cursor.execute("""
        CREATE TYPE materialcontenttype AS ENUM ('api', 'dynamic_text', 'static_text');
        """)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()
