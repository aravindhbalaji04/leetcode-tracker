import sqlite3

# Connect to SQLite database (creates database.db if it doesn't exist)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table to store daily problem-solving data
cursor.execute("""
CREATE TABLE IF NOT EXISTS leetcode_stats (
    username TEXT PRIMARY KEY,
    solved_problems INTEGER,
    last_updated TEXT
)
""")

conn.commit()
conn.close()
print("✅ Database setup complete! database.db file has been created.")
