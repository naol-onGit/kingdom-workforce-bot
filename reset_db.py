"""
# This script resets the workers database by deleting all test data and resetting the autoincrement ID.
import sqlite3

# Connect to your workers database
conn = sqlite3.connect("workers.db")
cursor = conn.cursor()

# Delete all rows
cursor.execute("DELETE FROM workers")

# Reset autoincrement ID so next worker starts from 1
cursor.execute("DELETE FROM sqlite_sequence WHERE name='workers'")

conn.commit()
conn.close()

print("✅ All test data deleted and ID reset. Your bot is ready for deployment!")

"""