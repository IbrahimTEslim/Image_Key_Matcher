import os, base64
from flask import Flask, render_template, redirect, flash, request
from lib import  allowed_file, calc_statistics, get_cache_config, get_capacity, get_last_10_min_stat, get_miss, get_path, get_policies, get_replace_policy, get_served_requests, get_size, increment_hit_or_miss, increment_served_request, insert_pair, get_keys, key_exist, save_mem_config, update_pair, update_pair

from mem_cache import Cache

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.config.update(SECRET_KEY=os.urandom(24))


cache = Cache()


@app.route("/")
def index():
    return redirect('/add_pair',code=302)

@app.route("/add_pair", methods=['GET'])
def add_pair_get(): return render_template('add_pair.html') 

@app.route("/add_pair", methods=['POST'])
def add_pair_post():
    # print('request.method', request.method)
    # print('request.args', request.args)
    # print('request.form', request.form)
    # print('request.files', request.files)


    if 'image' not in request.files:
        flash('No File Sumitted','error')
        return redirect(request.url)

    if 'key' not in request.form:
        flash('No Key Added','error')
        return redirect(request.url)
    # print("--------------degub Lineee----------------")

    file = request.files['image']
    key = request.form['key']
    # print("Type:::: ", type)
    if file is None or file.filename == '':
        flash('No File Selected', 'error')
        return redirect(request.url)

    if key == '':
        flash('No Key Added', 'error')
        return redirect(request.url)
        
    exist = key_exist(key)

    if exist: msg = "Updated"
    else: msg = "Created"

    if file and allowed_file(file.filename):
        #filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], key)
        file.save(file_path)
        size = (os.stat(file_path).st_size / 1000000)
        if exist:
            if update_pair(key,file_path,size): flash('Updated Successfully','msg')
            else: flash('Could not Update','error')
        else: 
            if insert_pair(key,file_path, size): flash(f'\nThe Key: {key} {msg} Successfully','msg')
            else: flash('Could not Save','error')
        
        cache.invalidate_key(key)
        
        f = open(file_path, 'rb', buffering=0)
        
        saved = cache.put(key,file_path,size,base64.b64encode(f.read()).decode('ascii'))
        
        if not saved: flash('Image Size > Cache Cpacity, Can not Save', 'error')

        f.close
        
        return redirect(request.url)
    else:
        flash('File Type Not Supported.', 'error')
        return redirect(request.url)


@app.route("/show_keys", methods=['GET'])
def show_keys_get(): return render_template('show_keys.html',keys=get_keys())

@app.route("/show_cache", methods=['GET'])
def show_cache_get(): 
    # print("Cache List: ",cache.get_cache())
    return render_template('show_cache.html',cache=cache.get_cache())

# @app.route("/edit_pair", methods=['GET'])
# def edit_pair_get(): return render_template('edit_pair.html')

# @app.route("/edit_pair", methods=['POST'])
# def edit_pair_post():
#     if 'image' not in request.files:
#         flash('No File Sumitted','error')
#         return redirect(request.url)

#     if 'key' not in request.form:
#         flash('No Key Added','error')
#         return redirect(request.url)
#     # print("--------------degub Lineee----------------")

#     file = request.files['image']
#     key = request.form['key']

#     if file.filename == '':
#         flash('No File Selected', 'error')
#         return redirect(request.url)

#     if key == '':
#         flash('No Key Added', 'error')
#         return redirect(request.url)

#     if not key_exist(key):
#         flash('Unused Key','error')
#         return redirect(request.url)

#     if file and allowed_file(file.filename):
#             # filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], key)
#             if update_pair(key,file_path):
#                 file.save(file_path)
#                 flash('Updated Successfully','msg')
#             else: flash('Could not Update','error')
#     return redirect(request.url)

@app.route("/get_pair", methods=['GET'])
def get_pair_get(): return render_template('get_pair.html') 

@app.route("/get_pair", methods=['POST'])
def get_pair_post():
    # print('request.method', request.method)
    # print('request.args', request.args)
    # print('request.form', request.form)
    # print('request.files', request.files)


    if 'key' not in request.form:
        flash('No Key Added','error')
        return redirect(request.url)
    # print("--------------degub Lineee----------------")

    key = request.form['key']

    if key == '':
        flash('No Key Added', 'error')
        return redirect(request.url)

    if not key_exist(key):
        flash('Unused Key','error')
        return redirect(request.url)

    if cache.exists(key):
        print("Fetched from Cache.....................")
        return render_template('get_pair.html',user_image = cache.get(key)[1])
        
    else:
        saved = cache.put(key, miss=True)
        if not saved: flash('Image Size > Cache Cpacity, Can not Save', 'error')

        f = open(get_path(key),'rb',buffering=0)
        data = base64.b64encode(f.read()).decode('ascii')
        f.close()
        return render_template('get_pair.html',user_image = data)
    #return send_from_directory(app.config['UPLOAD_FOLDER'],path.split('/')[-1],as_attachment=True)


@app.route("/cache_config", methods=['GET'])
def cache_config_get():
    # print("Policies: ", get_policies())
    data = get_cache_config()
    return render_template('cache_config.html', data = data)


@app.route("/cache_config", methods=['POST'])
def cache_config_post():
    data = get_cache_config()
    if 'policy' not in request.form:
        flash('No Policy Added','error')
        return render_template('cache_config.html', data = data)

    if 'capacity' not in request.form: capacity = get_capacity()
    else: capacity = request.form['capacity']

    policy = request.form['policy']

    if save_mem_config(policy,capacity): flash("Settings Saved",'msg')
    else: flash("Could not save setting.",'error')

    cache.refresh_config()
    flash("Cache Refreshed",'msg')

    data['capacity'] = capacity
    data['current_policy_id'] = int(policy)
    # print("Data: ",data)
    return render_template('cache_config.html', data = data)

@app.route("/statictics", methods=['GET'])
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

@app.route("/clear_cache", methods=['GET'])
def clear_cache(): 
    data = get_cache_config()
    cache.clear()
    flash('Cache Cleared Successfully.', 'msg')
    return render_template('cache_config.html',data = data)

@app.route("/invalidate_key", methods=["POST"])
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

    cache.invalidate_key(key)
    flash('Key Invalidated Successfully', 'msg')
    return render_template('cache_config.html', data = data)


@app.route("/put_key", methods=["POST"])
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
    app.run(host='0.0.0.0', port='8888', debug=True)














