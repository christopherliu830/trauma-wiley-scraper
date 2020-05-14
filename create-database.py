import sqlite3
import os
import time
from threading import Thread, Semaphore, Lock

keywords = [[],[]]
dup = 0

class ArticleData:
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

def parseAll(c, key_a, key_b):
    folder_path = 'final/Chris_Wiley_{}/'.format(key_a)
    filename = 'Chris_Wiley_{} and {}.txt'.format(key_a, key_b)
    with open(folder_path + filename, 'r', encoding='utf-8') as fd:
        parseOne(fd, key_a, key_b) # Clear an empty data at the beginning
        data = parseOne(fd, key_a, key_b)
        while data is not None:
            print(data)
            insert_entry(c, data)
            data = parseOne(fd, key_a, key_b)

def parseOne(fd, key_a, key_b):
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
    #c.execute('''
    #    INSERT INTO wiley (keya, keyb, title, authors, keywords, doi, url, year, type)
    #    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ? 
    #    WHERE NOT EXISTS(SELECT 1 FROM wiley WHERE doi=?);
    #    ''', (*fields, article_data.doi))
    c.execute('''INSERT INTO wiley VALUES (?,?,?,?,?,?,?,?,?)''', fields)

def search_key(key_a):
    with open('database.txt', 'r+', encoding='utf-8') as log:
        contents = log.read()
        conn = sqlite3.connect('wiley2.db')
        with conn:
            for key_b in keywords[1]:
                if '{},{}'.format(key_a, key_b) not in contents:
                    parseAll(conn, key_a, key_b)
                    with open('database.txt', 'a', encoding='utf-8') as log:
                        log.write('{},{}\n'.format(key_a, key_b))
        conn.close()


if __name__ == '__main__':

    with open('keys-a.txt', 'r', encoding='utf-8') as fd:
        keywords[0] = fd.read().split('\n')
    with open('keys-b.txt', 'r', encoding='utf-8') as fd:
        keywords[1] = fd.read().split('\n')

        for key_a in keywords[0]:
            search_key(key_a)

    print('done')
