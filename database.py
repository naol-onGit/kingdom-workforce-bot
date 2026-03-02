import sqlite3

def init_db():
    conn = sqlite3.connect("workers.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        profession TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        registration_date TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()