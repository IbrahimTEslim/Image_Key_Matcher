import sqlite3
import os

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO policies (policy_name, description, policy_name_view, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
    ('random','remove random element','Random'))
cur.execute("INSERT INTO policies (policy_name, description, policy_name_view, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
    ('lru','remove lru element','Least recently Used (LRU)'))

cur.execute("INSERT INTO mem_cache (replace_policy, capacity, created_at) VALUES (?,?, CURRENT_TIMESTAMP)",('1','1'))

connection.commit()
connection.close()

try:
    os.mkdir("static/uploads/")
except FileExistsError: pass