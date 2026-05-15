import sqlite3

# Connect database
conn = sqlite3.connect("curatrix.db")

# Cursor
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT
)
""")

# Save changes
conn.commit()

# Close connection
conn.close()

print("Database Created Successfully")