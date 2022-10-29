import random

class ListDict(object):
    def __init__(self):
        self.__key_to_index = {}
        self.__keys = []

    def add_key(self, key):
        if key in self.__key_to_index:
            return
        self.__keys.append(key)
        self.__key_to_index[key] = len(self.__keys)-1

    def remove_key(self, key):
        if key not in self.__key_to_index: return
        index = self.__key_to_index.pop(key)
        last_item = self.__keys.pop()
        if index != len(self.__keys):
            self.__keys[index] = last_item
            self.__key_to_index[last_item] = index

    def choose_random_key(self):
        return random.choice(self.__keys)
    
    def clear(self):
        self.__key_to_index = {}
        self.__keys = []