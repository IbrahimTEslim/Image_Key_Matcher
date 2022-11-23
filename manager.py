import os
from random import randint
from flask import Flask, redirect, render_template, flash, request
# from app import clear_app_cache, invalidate_key_in_app_cache, put_key_in_app_cache, refresh_app_cache_config
from app import *
from lib import calc_statistics, delete_images_data, get_cache_config, get_capacity, get_last_10_min_stat, get_path, get_size, key_exist, save_mem_config


flask_app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'

flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
flask_app.config['SESSION_TYPE'] = 'filesystem'
flask_app.config.update(SECRET_KEY=os.urandom(24))


@flask_app.route("/")
def index():
    return redirect('/app_config',code=302)

@flask_app.route("/app_config", methods=['GET'])
def cache_config_get():
    # print("Policies: ", get_policies())
    data = get_cache_config()
    # data['random1'] = [randint(1,9999) for x in range(30)]
    # data['random2'] = [randint(1,9999) for x in range(30)]
    # data['random3'] = [randint(1,9999) for x in range(30)]
    # data['random4'] = [randint(1,9999) for x in range(30)]
    # data['random5'] = [randint(1,9999) for x in range(30)]
    return render_template('cache_config.html', data = data)


@flask_app.route("/app_config", methods=['POST'])
def cache_config_post():
    data = get_cache_config()
    if 'policy' not in request.form:
        flash('No Policy Added','error')
        return render_template('cache_config.html', data = data)

    if 'capacity' not in request.form: capacity = get_capacity()
    else: capacity = request.form['capacity']

    policy = request.form['policy']
    mem_policy = request.form['mem_policy']

    if save_mem_config(policy,mem_policy,capacity): flash("Settings Saved",'msg')
    else: flash("Could not save setting.",'error')

    refresh_app_cache_config()
    flash("Cache Refreshed",'msg')

    data['capacity'] = capacity
    data['current_policy_id'] = int(policy)
    data['current_memcache_policy_id'] = int(mem_policy)
    # print("Data: ",data)
    return render_template('cache_config.html', data = data)

@flask_app.route("/statictics", methods=['GET'])
def statistics_get():
    data = {}
    log = get_last_10_min_stat()
    calculated_stat = calc_statistics(get_last_10_min_stat()) # tuple(requests, hit, miss)
    requests = calculated_stat[0]
    data['served_requests'] = requests
    data['hit_rate'] = float(calculated_stat[1] / requests * 100) if requests > 0 else 0
    data['miss_rate'] = float(calculated_stat[2] / requests * 100) if requests > 0 else 0
    data['log'] = log

    return render_template('statistics.html', data=data)

@flask_app.route("/clear_cache", methods=['GET'])
def clear_cache(): 
    data = get_cache_config()
    # app.clear_app_cache()
    cache.clear()
    flash('Cache Cleared Successfully.', 'msg')
    return render_template('cache_config.html',data = data)

@flask_app.route("/clear_app_data", methods=['GET'])
def clear_app_data(): 
    data = get_cache_config()
    clear_app_cache()
    flash('Cache Cleared Successfully.', 'msg')
    
    if delete_images_data(): flash('App Data Cleared Successfully.', 'msg')
    else: flash('Can not Clear App Data :(', 'error') 

    return render_template('cache_config.html',data = data)


@flask_app.route("/invalidate_key", methods=["POST"])
def invalidate_key():
    data = get_cache_config()
    if 'key' not in request.form:
        flash('No Key Added','error')
        return render_template('cache_config.html', data = data)
    # print("--------------degub Lineee----------------")

    key = request.form['key']

    if key == '':
        flash('No Key Added', 'error')
        return render_template('cache_config.html', data = data)

    if not key_exist(key):
        flash('Unexisted Key','error')
        return render_template('cache_config.html', data = data)

    invalidate_key_in_app_cache(key)
    flash('Key Invalidated Successfully', 'msg')
    return render_template('cache_config.html', data = data)


@flask_app.route("/put_key", methods=["POST"])
def insert_into_cache():
    data = get_cache_config()
    if 'key' not in request.form:
        flash('No Key Added','error')
        return render_template('cache_config.html', data = data)
        
    key = request.form['key']

    if key == '':
        flash('No Key Added', 'error')
        return render_template('cache_config.html', data = data)
    
    if not key_exist(key):
        flash('Not Used Key', 'error')
        return render_template('cache_config.html', data = data)
    
    path = get_path(key)
    size = float(get_size(key))
    cache.invalidate_key(key)
    
    saved = cache.put(key,path,size)
    
    if not saved:
        flash('Image Size > Cache Cpacity, Can not Save', 'error')
        return render_template('cache_config.html', data = data)
    
    flash('Element Inserted Into Memory Cache Successfully', 'msg')
    return render_template('cache_config.html', data = data)



if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port='9999', debug=True)
