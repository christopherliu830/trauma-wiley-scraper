import pickle
import pprint
import json
import threading

class ProgressLog:
    def __init__(self, wdir):
        self.log = {'1':'2', '3':'4'}
        self.wdir = wdir
        self.lock = threading.Lock()
    
    @staticmethod
    def create(wdir):
        with open(wdir, 'wb') as fd:
            pickle.dump({'pagenos': { }}, fd)
            pass
    
    def get_pageno(self, keya, keyb):
        with self.lock:
            try:
                return self.log['pagenos'][keya][keyb]
            except KeyError:
                if 'pagenos' not in self.log:
                    self.log['pagenos'] = { }
                if keya not in self.log['pagenos']:
                    self.log['pagenos'][keya] = { }
                if keyb not in self.log['pagenos'][keya]:
                    self.log['pagenos'][keya][keyb] = 0
                return self.log['pagenos'][keya][keyb]
    
    def set_pageno(self, keya, keyb, val):
        with self.lock:
            try:
                self.log['pagenos'][keya][keyb] = val
            except KeyError:
                self.get_result_count(keya, keyb) # initialize log structure
                self.log['pagenos'][keya][keyb] = val
    
    def get_result_count(self, keya, keyb):
        with self.lock:
            try:
                return self.log['results'][keya][keyb]
            except KeyError:
                if 'results' not in self.log:
                    self.log['results'] = { }
                if keya not in self.log['results']:
                    self.log['results'][keya] = { }
                if keyb not in self.log['results'][keya]:
                    self.log['results'][keya][keyb] = None
                return self.log['results'][keya][keyb]

    def set_result_count(self, keya, keyb, val):
        with self.lock:
            try:
                self.log['results'][keya][keyb] = val
                return val
            except KeyError:
                self.get_result_count(keya, keyb) # initialize log structure
                self.log['results'][keya][keyb] = val
                return val

    def __enter__(self):
        with open(self.wdir, 'r+b') as fd:
            self.log = pickle.load(fd)
        return self

    def __exit__(self, type, value, traceback):
        with open(self.wdir, 'wb') as fd:
            pickle.dump(self.log, fd)
    
    def __str__(self):
        return json.dumps(self.log, sort_keys=True, indent=2)
        