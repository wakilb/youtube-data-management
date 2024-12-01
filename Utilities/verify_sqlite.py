import sqlite3

try:
    conn = sqlite3.connect("youtube_regions.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("Tables in the database:")
        for table in tables:
            print(table[0])
    else:
        print("No tables found in the database.")

    conn.close()

except Exception as e:
    print("Error connecting to SQLite database:", e)
