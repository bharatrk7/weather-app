import sqlite3

# 1. Connect to the database
# If the file doesn't exist, this creates it automatically.
connection = sqlite3.connect('database.db')

# 2. Get the "Cursor"
# The cursor is like the pen. We use it to write commands.
cursor = connection.cursor()

# 3. Create the Table (The Structure)
# We are creating a sheet named 'favorites' with one column: 'city'
print("Creating database table...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL
    )
''')

# 4. Save and Close
connection.commit()
connection.close()
print("Database initialized successfully!")