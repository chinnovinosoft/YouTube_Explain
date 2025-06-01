import sqlite3

conn = sqlite3.connect("interviews.db")
c = conn.cursor()

for row in c.execute("SELECT * FROM interviews"):
    print(row)

conn.close()
