import sqlite3
def init_db():
    # Initialize the database and create the materials table if it doesn't exist
    conn = sqlite3.connect("materials.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY,
        name TEXT,
        version TEXT,
        usage TEXT,
        defined_in TEXT,
        content_type TEXT,
        content TEXT,
        status TEXT
    );
    """)

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect("materials.db")
    conn.row_factory = sqlite3.Row
    return conn
