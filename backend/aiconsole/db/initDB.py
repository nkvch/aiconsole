import sqlite3
def get_db_connection():
    conn = sqlite3.connect("materials.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS materials")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        version TEXT,
        usage TEXT,
        content_type TEXT,
        content TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()


