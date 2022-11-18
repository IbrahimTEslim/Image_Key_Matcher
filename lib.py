import psycopg2
import psycopg2.extras
from decouple import config

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection_and_cursor():
    conn = psycopg2.connect(
        host=config("Endpoint"),
        database=config("Database"),
        user='postgres',
        password=config("Password"),
        port=config("Port"),
    )

    # conn.row_factory = make_dicts
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn, cursor

def get_keys():
    conn, cur = get_db_connection_and_cursor()
    cur.execute('select key from pairs')
    keys = cur.fetchall()
    conn.close()
    return keys

def key_exist(key: str) -> bool:
        conn, cur = get_db_connection_and_cursor()
        cur.execute('select * from pairs where key = %s',(key,))
        res = cur.fetchall()
        # print("--------------degub LIB Lineee----------------")
        conn.close()
        # print("Result: ", res)
        return True if res else False

def insert_pair(key: str, path: str, size: float) -> bool:
    # print("--------------degub LIB Lineee----------------")
    # print("Key: ",key)
    # print("path", path)
    try:
        conn, cur = get_db_connection_and_cursor()
        cur.execute('insert into pairs (key, path, size, created_at) values (%s , %s, %s, CURRENT_TIMESTAMP)',(key,path, size))
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
        conn, cur = get_db_connection_and_cursor()
        cur.execute("update pairs set path = %s, size = %s where key = %s",(path,size,key))
        # print("--------------degub LIB Lineee----------------")

        conn.commit()
        conn.close()
        return True
    except: return False

def get_path(key: str) -> str:
    conn, cur = get_db_connection_and_cursor()
    cur.execute('select path from pairs where key = %s',(key,))
    path = cur.fetchall()
    conn.close()
    # print("Path:: ",path)
    return path[0]['path']

def get_capacity() -> float:
    conn, cur = get_db_connection_and_cursor()
    # cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select capacity from mem_cache')
    capacity = cur.fetchall()
    # print("Capacity:: ", capacity)
    # print("Capacity:: ", capacity[0]['capacity'])
    conn.close()
    return capacity[0]['capacity']

def save_mem_config(policy_id: int, capacity: float) -> bool:
    try:
        conn, cur = get_db_connection_and_cursor()
        cur.execute('update mem_cache set replace_policy = %s, capacity = %s where id = %s',(policy_id,capacity,1))
        conn.commit()
        conn.close()
        return True
    except: return False

def get_served_requests() -> int:
    conn, cur = get_db_connection_and_cursor()
    cur.execute('select requests from mem_cache')
    served_requests = cur.fetchall()
    conn.close()
    return 0 if served_requests[0]['requests'] is None else int(served_requests[0]['requests'])

def get_hit() -> int:
    conn, cur = get_db_connection_and_cursor()
    cur.execute('select hit from mem_cache')
    served_requests = cur.fetchall()
    conn.close()
    return 0 if served_requests[0]['hit'] is None else int(served_requests[0]['hit'])

def get_miss() -> int:
    conn, cur = get_db_connection_and_cursor()
    cur.execute('select miss from mem_cache')
    served_requests = cur.fetchall()
    conn.close()
    return 0 if served_requests[0]['miss'] is None else int(served_requests[0]['miss'])

def get_replace_policy() -> str:
    return get_replace_policy_by_id(get_replace_policy_id())

def get_replace_policy_id() -> int:
    conn, cur = get_db_connection_and_cursor()
    # cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select replace_policy from mem_cache')
    replace_policy = cur.fetchall()
    print("How Postgres Lig Return Data: ", replace_policy)
    conn.close()
    return replace_policy[0]['replace_policy']

def get_replace_policy_by_id(id: int) -> str:
    id = get_replace_policy_id()
    conn, cur = get_db_connection_and_cursor()
    # cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cur.execute('select policy_name from policies where id = %s',(id,))
    policy = cur.fetchall()
    conn.close()
    return policy[0]['policy_name']

def get_size(key: str) -> float:
    # print("\n\n\n",key,"\n\n\n")
    conn, cur = get_db_connection_and_cursor()
    cur.execute("select size from pairs where key = %s",(key,))
    size = cur.fetchall()
    conn.close()
    return float(size[0]['size'])

def increment_hit_or_miss(hit: bool) -> bool:
    try:
        field = 'hit' if hit else 'miss'
        old_val = get_hit() if hit else get_miss()
        query = f"update mem_cache set {field} = %s where id = %s"
        conn, cur = get_db_connection_and_cursor()
        cur.execute(query,(old_val + 1, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def increment_served_request() -> bool:
    try:
        old_val = get_served_requests()
        conn, cur = get_db_connection_and_cursor()
        cur.execute("update mem_cache set requests = %s where id = %s",(old_val + 1, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_hit_or_miss_value(hit: bool, val: int) -> bool:
    try:
        field = 'hit' if hit else 'miss'
        query = f"update mem_cache set {field} = %s where id = %s"
        conn, cur = get_db_connection_and_cursor()
        cur.execute(query,(val, 1,))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_served_request_value(val: int) -> bool:
    try:
        conn, cur = get_db_connection_and_cursor()
        cur.execute("update mem_cache set requests = %s where id = %s",(val, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_num_of_items(val: int) -> bool:
    try:
        conn, cur = get_db_connection_and_cursor()
        cur.execute("update mem_cache set num_of_items = %s where id = %s",(val, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def set_mem_size(val: float) -> bool:
    try:
        conn, cur = get_db_connection_and_cursor()
        cur.execute("update mem_cache set mem_size = %s where id = %s",(val, 1))
        conn.commit()
        conn.close()
        return True
    except: return False

def insert_stat(served_req: int, hit: int, miss: int) -> bool:
    try:
        conn, cur = get_db_connection_and_cursor()
        cur.execute("insert into statistics (requests, hit, miss, created_at) values (%s, %s, %s, CURRENT_TIMESTAMP)", (served_req, hit, miss))
        conn.commit()
        conn.close
        return True
    except: return False

def get_policies() -> list:
    conn, cur = get_db_connection_and_cursor()
    cur.execute('select id, policy_name, policy_name_view from policies order by id')
    policies = cur.fetchall()
    conn.close()
    return list(policies)

def get_cache_config() -> dict:
    return {'capacity' : get_capacity(), 'current_policy_id' : get_replace_policy_id(), 'policies' : get_policies()}

def get_last_10_min_stat():
    conn, cur = get_db_connection_and_cursor()
    cur.execute("select * from statistics where created_at >= (CURRENT_TIMESTAMP - (10 * interval '1 minute')) and (requests > 0 and hit > 0 or miss > 0)")
    stat = cur.fetchall()
    conn.close()
    return stat

def calc_statistics(stat_list: list) -> tuple:
    served_req, hit, miss = 0, 0, 0
    for record in stat_list:
        served_req += record['requests']
        hit += record['hit']
        miss += record['miss']
    return served_req, hit, miss