from calendar import c
import sqlite3
from time import time

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = make_dicts
    return conn

def get_keys():
    conn = get_db_connection()
    keys = conn.execute('select key from pairs').fetchall()
    conn.close()
    return keys

def key_exist(key: str) -> bool:
        conn = get_db_connection()
        res = conn.execute('select * from pairs where key = ?',(key,)).fetchall()
        # print("--------------degub LIB Lineee----------------")
        conn.close()
        # print("Result: ", res)
        return True if res else False

def insert_pair(key: str, path: str, size: float) -> bool:
    # print("--------------degub LIB Lineee----------------")
    # print("Key: ",key)
    # print("path", path)
    try:
        conn = get_db_connection()
        conn.cursor().execute('insert into pairs (key, path, size, created_at) values (? , ?, ?, CURRENT_TIMESTAMP)',(key,path, size))
        # print("--------------degub LIB Lineee----------------")

        conn.commit()
        conn.close()
        return True
    except: return False


def update_pair(key: str, path: str, size: float) -> bool:
    # print("--------------degub LIB Lineee----------------")
    # print("Key: ",key)
    # print("path", path)
    try:
        conn = get_db_connection()
        conn.cursor().execute('update pairs set path = ?, size = ? where key = ?',(path,key,size))
        # print("--------------degub LIB Lineee----------------")

        conn.commit()
        conn.close()
        return True
    except: return False

def get_path(key: str) -> str:
    conn = get_db_connection()
    path = conn.execute('select path from pairs where key = ?',(key,)).fetchall()
    conn.close()
    print("Path:: ",path)
    return path[0]['path']

def get_capacity() -> float:
    conn = get_db_connection()
    capacity = conn.execute('select capacity from mem_cache').fetchall()
    conn.close()
    return capacity[0]['capacity']

def save_mem_config(policy_id: int, capacity: float) -> bool:
    try:
        conn = get_db_connection()
        conn.cursor().execute('update mem_cache set replace_policy = ?, capacity = ? where id = ?',(policy_id,capacity,1))
        conn.commit()
        conn.close()
        return True
    except: return False

def get_served_requests() -> int:
    conn = get_db_connection()
    served_requests = conn.execute('select requests from mem_cache').fetchall()
    conn.close()
    return 0 if served_requests[0]['requests'] is None else int(served_requests[0]['requests'])

def get_hit() -> int:
    conn = get_db_connection()
    served_requests = conn.execute('select hit from mem_cache').fetchall()
    conn.close()
    return 0 if served_requests[0]['hit'] is None else int(served_requests[0]['hit'])

def get_miss() -> int:
    conn = get_db_connection()
    served_requests = conn.execute('select miss from mem_cache').fetchall()
    conn.close()
    return 0 if served_requests[0]['miss'] is None else int(served_requests[0]['miss'])

def get_replace_policy() -> str:
    return get_replace_policy_by_id(get_replace_policy_id())

def get_replace_policy_id() -> int:
    conn = get_db_connection()
    replace_ploicy = conn.execute('select replace_policy from mem_cache').fetchall()
    conn.close()
    return replace_ploicy[0]['replace_policy']

def get_replace_policy_by_id(id: int) -> str:
    id = get_replace_policy_id()
    conn = get_db_connection()
    policy = conn.execute('select policy_name from policies where id = ?',(id,)).fetchall()
    conn.close()
    return policy[0]['policy_name']

def get_size(key: str) -> float:
    # print("\n\n\n",key,"\n\n\n")
    conn = get_db_connection()
    size = conn.execute("select size from pairs where key = ?",(key,)).fetchall()
    conn.close()
    return float(size[0]['size'])

def increment_hit_or_miss(hit: bool) -> bool:
    try:
        field = 'hit' if hit else 'miss'
        old_val = get_hit() if hit else get_miss()
        query = f"update mem_cache set {field} = ? where id = ?"
        conn = get_db_connection()
        conn.cursor().execute(query,(old_val + 1, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def increment_served_request() -> bool:
    try:
        old_val = get_served_requests()
        conn = get_db_connection()
        conn.cursor().execute("update mem_cache set requests = ? where id = ?",(old_val + 1, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_hit_or_miss_value(hit: bool, val: int) -> bool:
    try:
        field = 'hit' if hit else 'miss'
        query = f"update mem_cache set {field} = ? where id = ?"
        conn = get_db_connection()
        conn.cursor().execute(query,(val, 1,))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_served_request_value(val: int) -> bool:
    try:
        conn = get_db_connection()
        conn.cursor().execute("update mem_cache set requests = ? where id = ?",(val, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_num_of_items(val: int) -> bool:
    try:
        conn = get_db_connection()
        conn.cursor().execute("update mem_cache set num_of_items = ? where id = ?",(val, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_mem_size(val: float) -> bool:
    try:
        conn = get_db_connection()
        conn.cursor().execute("update mem_cache set mem_size = ? where id = ?",(val, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def insert_stat(served_req: int, hit: int, miss: int) -> bool:
    try:
        conn = get_db_connection()
        conn.cursor().execute("insert into statistics (requests, hit, miss, created_at) values (?, ?, ?, CURRENT_TIMESTAMP)", (served_req, hit, miss))
        conn.commit()
        conn.close
        return True
    except: return False

def get_policies() -> list:
    conn = get_db_connection()
    policies = conn.execute('select id, policy_name, policy_name_view from policies order by id').fetchall()
    conn.close()
    return list(policies)

def get_cache_config() -> dict:
    return {'capacity' : get_capacity(), 'current_policy_id' : get_replace_policy_id(), 'policies' : get_policies()}

def get_last_10_min_stat():
    conn = get_db_connection()
    stat = conn.execute("select * from statistics where created_at >= Datetime('now', '-10 minutes') and (requests > 0 and hit > 0 or miss > 0)").fetchall()
    conn.close()
    return stat

def calc_statistics(stat_list: list) -> tuple:
    served_req, hit, miss = 0, 0, 0
    for record in stat_list:
        served_req += record['requests']
        hit += record['hit']
        miss += record['miss']
    return served_req, hit, miss