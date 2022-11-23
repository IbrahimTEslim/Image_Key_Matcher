import os, base64, tempfile
from random import randint
from flask import Flask, render_template, redirect, flash, request
from lib import  allowed_file, calc_statistics, delete_images_data, get_cache_config, get_capacity, get_last_10_min_stat, get_miss, get_path, get_policies, get_replace_policy, get_served_requests, get_size, increment_hit_or_miss, increment_served_request, insert_pair, get_keys, key_exist, save_mem_config, update_pair, update_pair
from AWS.s3 import S3
from AWS.ec2 import EC2
from mem_cache import Cache

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.config.update(SECRET_KEY=os.urandom(24))


cache = Cache(saving_stat = False)
s3 = S3()
ec2 = EC2()


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

    # msg = "Updated" if exist else "Created"

    if file and allowed_file(file.filename):
        file_path = 's3:\\' + key
        file.seek(0, os.SEEK_END)
        size = (file.tell() / 1000000)
        file.seek(0)
        file_data = file.read() # i read it here cause i don't know why it closed after the s3.upload()
        file.seek(0)
        uploaded_to_s3 = s3.upload(file, key)
        
        if not uploaded_to_s3: flash('Could not Save','error')

        if exist and uploaded_to_s3:
            if update_pair(key,file_path,size): flash('Updated Successfully','msg')
            else: flash('Could not Update','error')
        elif not exist and uploaded_to_s3: 
            if insert_pair(key,file_path, size): flash(f'\nThe Key: {key} {msg} Successfully','msg')
            else: flash('Could not Create Pair','error')
        else: flash('Could not Save to S3','error')
        
        cache.invalidate_key(key)
        
        saved = cache.put(key,file_path,size,base64.b64encode(file_data).decode('ascii'))
        if not saved: flash('Image Size > Cache Cpacity, Can not Save', 'error')

        file.close()
        
        del file_data # remove file data from memory right now
        
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

@app.route("/get_pair", methods=['GET'])
def get_pair_get(): return render_template('get_pair.html') 

@app.route("/get_pair", methods=['POST'])
def get_pair_post():

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
        flash('Fetched From Memory Cache','msg')
        return render_template('get_pair.html',user_image = cache.get(key)[1])
        
    else:
        saved = cache.put(key, miss=True)
        if not saved:
            flash('Image Size > Cache Cpacity, Can not Save', 'error')

            fp = tempfile.TemporaryFile()

            if not s3.download(key,fp): flash('Can not fetch image from S3 resource', 'error')
            else: flash('Image Fetched From S3 Successfully', 'msg')
            
            fp.seek(0)
            data = base64.b64encode(fp.read()).decode('ascii')
            
            fp.close()
            return render_template('get_pair.html',user_image = data)
        else:
            flash('Inserted Into Memory Cache','msg')
            return render_template('get_pair.html',user_image = cache.get(key)[1])


@app.route("/app_config", methods=['GET'])
def cache_config_get():
    # print("Policies: ", get_policies())
    data = get_cache_config()
    data['random1'] = [randint(1,9999) for x in range(30)]
    data['random2'] = [randint(1,9999) for x in range(30)]
    data['random3'] = [randint(1,9999) for x in range(30)]
    data['random4'] = [randint(1,9999) for x in range(30)]
    data['random5'] = [randint(1,9999) for x in range(30)]
    return render_template('cache_config.html', data = data)

@app.route("/app_config", methods=['POST'])
def cache_config_post():
    data = get_cache_config()
    if 'policy' not in request.form:
        flash('No Policy Added','error')
        return render_template('cache_config.html', data = data)

    old_capacity = int(get_capacity())
    if 'capacity' not in request.form: capacity = old_capacity
    else: 
        capacity = int(request.form['capacity'])
        res = ec2.start_instance(int(capacity))
    if res: 
        if capacity > old_capacity: flash("Instances Lunched Successfully", 'msg')
        elif capacity < old_capacity: flash("Instances Stopped Successfully", 'msg')
    else: flash("Faild Accessing Instances", 'error')
    
    policy = request.form['policy']
    mem_policy = request.form['mem_policy']

    if save_mem_config(policy,mem_policy,capacity): flash("Settings Saved",'msg')
    else: flash("Could not save setting.",'error')

    cache.refresh_config()
    flash("Cache Refreshed",'msg')

    data['capacity'] = capacity
    data['current_policy_id'] = int(policy)
    data['current_memcache_policy_id'] = int(mem_policy)
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

@app.route("/clear_app_data", methods=['GET'])
def clear_app_data(): 
    data = get_cache_config()
    clear_app_cache()
    flash('Cache Cleared Successfully.', 'msg')
    
    if delete_images_data(): flash('App Data Cleared Successfully.', 'msg')
    else: flash('Can not Clear App Data :(', 'error') 

    if s3.clear_bucket(): flash('S3 Objects Deleted Successfully', 'msg')
    else: flash('Could Not Delete S3 Objects Successfully', 'error')
    
    return render_template('cache_config.html',data = data)






def clear_app_cache():
    print("Cleared!!!!!!!!")
    print("Before", cache.get_cache())
    cache.clear()
    print("After: ", cache.get_cache())

def invalidate_key_in_app_cache(key):
    cache.invalidate_key(key)

def put_key_in_app_cache(key):
    path = get_path(key)
    size = float(get_size(key))

    cache.invalidate_key(key)
    
    return cache.put(key,path,size)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8888', debug=True)














