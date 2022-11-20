from collections import OrderedDict
from datetime import datetime
from lib import get_capacity, get_path, get_replace_policy, get_size, insert_stat, set_hit_or_miss_value, set_mem_size, set_num_of_items, set_served_request_value
import threading,base64, tempfile
from Custom_DS import ListDict
from s3 import S3
class Cache():
    def __init__(self) -> None:
        self.__cache = OrderedDict()
        self.__list_dict = ListDict() # to apply random remove in O(1)
        self.__size = 0.0 # In MB unit
        self.__count = 0 
        self.hit = 0 
        self.miss = 0 
        self.served_requests = 0 
        self.__replacement_policy = get_replace_policy()
        self.__capacity = get_capacity() # In MB unit
        self.__s3 = S3()
        threading.Timer(5,self.store_statistics).start()
    
    def put(self, key: str, path = None, size = None, miss = False, image = None) -> bool:
        if not path: path = get_path(key)
        if not size: size = float(get_size(key))
        if not image:
            tf = tempfile.TemporaryFile()
            self.__s3.download(key,tf)
            tf.seek(0)
            image = base64.b64encode(tf.read()).decode('ascii')
            tf.close()
                
        if miss:
            self.served_requests += 1
            self.miss += 1

        if not self.is_validate_size(size): return False
        
        while self.__size + size > self.__capacity:
            self.__remove_record()
            
        self.__cache[key] = (path, size, image)
        self.__size += size
        self.__count += 1
        self.__cache.move_to_end(key)
        self.__list_dict.add_key(key)
        return True

    def clear(self):
        self.__cache = OrderedDict()
        self.__list_dict.clear()
        self.__size = 0.0
        self.__count = 0
        return True
        
    def refresh_config(self):
        self.__replacement_policy = get_replace_policy()
        self.__capacity = get_capacity()
        self.__reformat_cache()
    
    def get(self, key: str) -> tuple:
        self.served_requests += 1
        if key in self.__cache:
            self.__cache.move_to_end(key)
            self.hit += 1
            return (self.__cache[key][0], self.__cache[key][2])
        else:
            self.miss += 1
            return None

    def invalidate_key(self, key: str):
        if key in self.__cache:
            self.__size -= float(self.__cache[key][1])
            self.__cache.pop(key)
            self.__count -= 1
            self.__list_dict.remove_key(key)
    
    def exists(self, key: str) -> bool:
        return True if key in self.__cache else False

    def __remove_random(self):
        rand_key = self.__list_dict.choose_random_key() # O(1)
        self.__count -= 1
        self.__size -= float(self.__cache[rand_key][1])
        self.__cache.pop(rand_key)
        self.__list_dict.remove_key(rand_key)

    def __remove_lru(self):
        lru_key = self.__cache.popitem(last = False)
        print("LRU Key: ",lru_key[0])
        self.__count -= 1
        self.__size -= float(lru_key[1][1])
        self.__list_dict.remove_key(lru_key[0])
        # self.__cache.popitem(last = False)
    
    def __remove_record(self):
        if self.__replacement_policy == 'random': self.__remove_random()
        else: self.__remove_lru()

    def __reformat_cache(self):
        while self.__size > self.__capacity:
            self.__remove_record()

    def get_cache(self):
        records =  list(self.__cache.items())
        for i in range(len(records)):
            temp = list(records[i][1])
            temp.pop()
            records[i] = (records[i][0], temp)
        return records

    def store_statistics(self):
        if self.served_requests > 0:
            print("Saving...")
            insert_stat(self.served_requests, self.hit, self.miss)
            # set_num_of_items(val=self.__count)
            # set_mem_size(val=self.__size)
            self.clear_stat()
            print("Saved. Timestamp: ", datetime.now(),end="\n---------------------------------------------------\n")
        threading.Timer(5,self.store_statistics).start()

    def clear_stat(self):
        self.served_requests = 0
        self.hit = 0
        self.miss = 0

    def is_validate_size(self, size):
        return True if size <= self.__capacity else False