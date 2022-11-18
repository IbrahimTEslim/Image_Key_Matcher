import os, psycopg2
from decouple import config

connection = psycopg2.connect(
        host=config("Endpoint"),
        database=config("Database"),
        user='postgres',
        password=config("Password"),
        port=config("Port"),
    )

with open('schema.sql') as f:
    connection.cursor().execute(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO policies (policy_name, description, policy_name_view, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
    ('random','remove random element','Random'))
cur.execute("INSERT INTO policies (policy_name, description, policy_name_view, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
    ('lru','remove lru element','Least recently Used (LRU)'))

cur.execute("INSERT INTO mem_cache (replace_policy, capacity, created_at) VALUES (%s,%s, CURRENT_TIMESTAMP)",('1','10'))

connection.commit()
connection.close()

try:
    os.mkdir("static/uploads/")
except FileExistsError: pass