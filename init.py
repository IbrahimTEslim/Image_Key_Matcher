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

cur.execute("INSERT INTO policies (policy_name, policy_for, description, policy_name_view, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)",
    ('random', '1','remove random element','Random'))
cur.execute("INSERT INTO policies (policy_name, policy_for, description, policy_name_view, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)",
    ('lru', '1','remove lru element','Least recently Used (LRU)'))

cur.execute("INSERT INTO policies (policy_name, policy_for, description, policy_name_view, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)",
    ('manual', '2','change cache pool size manual','Manual Mode'))
cur.execute("INSERT INTO policies (policy_name, policy_for, description, policy_name_view, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)",
    ('automatic', '2','change cache pool size automatically','Automatic Mode'))

cur.execute("INSERT INTO mem_cache (replace_policy, memcache_pool_policy, capacity, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",('1', '3','10'))

connection.commit()
connection.close()

try:
    os.mkdir("static/uploads/")
except FileExistsError: pass