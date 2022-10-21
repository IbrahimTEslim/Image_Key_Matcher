from functools import cache
import unittest
from unittest import TestCase
from mem_cache import Cache
import lib


class Testing(TestCase):
    
    def test_insert_db(self):
        lib.insert_pair("test","test",3.5)
        self.assertEqual(lib.key_exist("test"), True)
        self.assertEqual(lib.get_path("test"), "test")
        self.assertEqual(lib.get_size("test"), 3.5)
    
    def test_update_db(self):
        lib.update_pair("test","temp_path",1.8)
        self.assertEqual(lib.key_exist("test"), True)
        self.assertEqual(lib.get_path("test"), "temp_path")
        self.assertEqual(lib.get_size("test"), 1.8)
        
    def test_cache_insert(self):
        cache = Cache()
        cache.put("test","test",1.8,False,None)
        res = cache.get("test")
        self.assertEqual(res[0],"test")
        del cache
    
    def test_cache_remove(self):
        cache = Cache()
        cache.invalidate_key("test")
        res = cache.get("test")
        self.assertEqual(res,None)
        del cache
    
    def test_mem_cache_config(self):
        self.assertEqual(lib.get_capacity(), 10)
        self.assertEqual(lib.get_replace_policy_id(), 1)
        lib.save_mem_config(2,8)
        self.assertEqual(lib.get_capacity(), 8)
        self.assertEqual(lib.get_replace_policy_id(), 2)
        
        
        
if __name__ == "__main__":
    unittest.main()