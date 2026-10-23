import sqlite3
from datetime import datetime

DB_NAME = "records.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            record_type TEXT,
            confidence REAL,
            extracted_text TEXT,
            department TEXT,
            upload_date TEXT,
            status TEXT DEFAULT 'Active'
        )
    """)

    conn.commit()
    conn.close()

def add_record(filename, original_name, record_type, confidence,
               extracted_text, department):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO records
        (filename, original_name, record_type, confidence,
         extracted_text, department, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        original_name,
        record_type,
        confidence,
        extracted_text,
        department,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def search_records(query):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM records
        WHERE original_name LIKE ?
           OR record_type LIKE ?
           OR department LIKE ?
           OR extracted_text LIKE ?
        ORDER BY id DESC
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))

    results = cursor.fetchall()
    conn.close()
    return results

def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM records ORDER BY id DESC")
    results = cursor.fetchall()
    conn.close()
    return results