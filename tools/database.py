import sqlite3
import os
import time
from . import plog, integrity

keywords = [[],[]]
dup = 0

class ArticleData:
    ''' Container for information of a single article. '''

    def __init__(self, key_a, key_b):
        self.key_a = key_a
        self.key_b = key_b
        self.title = ''
        self.authors = []
        self.keywords = []
        self.doi = ''
        self.url = ''
        self.year = -1
        self.type = ''
    
    def __str__(self):
        return '''{} {} - {}'''.format(self.key_a, self.key_b, self.title)

    def getTuple(self):
        return (self.key_a, 
                self.key_b,    
                self.title, 
                ' '.join(self.authors), 
                ' '.join(self.keywords), 
                self.doi, 
                self.url, 
                self.year, 
                self.type)

def parseAll(in_path, c, keya, keyb, log):
    ''' Parse all citation data files of a key combo and insert into the db '''
    page_count = log.get_pageno(keya, keyb)
    for page in range(page_count):
        path = os.path.join(in_path, keya, keyb, '{}.txt'.format(page))
        with open(path, 'r', encoding='utf-8') as fd:
            fd.readline()
            data = parseOne(fd, keya, keyb)
            while data is not None:
                print(data)
                insert_entry(c, data)
                data = parseOne(fd, keya, keyb)

def parseOne(fd, key_a, key_b):
    ''' Parse one citation data file into an ArticleData instance. ''' 
    a = ArticleData(key_a, key_b)
    line = fd.readline().rstrip('\n')
    if line == '':
        return None
    while line != '': # Not empty and not EOF

        t, d = line.split('  - ') # lines come in two parts: a type, and the data.
                                  # For example, a line from the file could be:
                                  # AU  - Cuckle, Howard S.
                                  # t = 'AU' and d = 'Cuckle, Howard S.' in this case.
        
        # Populate article_data fields with switch statment based on read in line.
        if t == 'AU':
            a.authors.append(d)
        elif t == 'TI':
            a.title = d
        elif t == 'UR':
            a.url = d
        elif t == 'DO':
            a.doi = d
        elif t == 'KW':
            a.keywords.append(d)
        elif t == 'PY':
            a.year = int(d)
        elif t == 'TY':
            a.type = d

        line = fd.readline()
        if not line: # Did we reach end of file?
            break

        line = line.rstrip('\n')

    return a

def insert_entry(c, article_data) :
    fields = article_data.getTuple()
    c.execute('''INSERT INTO wiley VALUES (?,?,?,?,?,?,?,?,?)''', fields)

def clean(c):
    print('Cleaning...')

    # Remove duplicates
    c.execute('''DELETE FROM wiley
                 WHERE rowid NOT IN (
                     SELECT MIN(rowid)
                     FROM wiley
                     GROUP BY doi
                 )''')
    
    # Remove no-author entries
    c.execute('''DELETE FROM wiley
                 WHERE authors = '' ''')
    
    # Remove book chapters
    c.execute('''DELETE FROM wiley WHERE doi LIKE '%.ch%' ''')

def export(import_path, export_path, keysa, keysb, log):
    ''' export the paginated files into a database file '''

    conn = sqlite3.connect(export_path)
    for keya in keysa:
        for keyb in keysb:
            with conn:
                c = conn.cursor()
                parseAll(import_path, c, keya, keyb, log)

    with conn:
        clean(c)
    