import os
import pathlib
import sqlite3
from . import plog


def integrity_check(wdir, keysa, keysb): 
    print('Building file structure...')
    data_path =  data_path_check(wdir)
    paginated_files_check(data_path, keysa, keysb)
    progresslog_check(data_path)
    crash_recovery(data_path)
    database_check(data_path)


def data_path_check(wdir):
    print('Building data folder...')
    data_path = pathlib.Path(os.path.join(wdir, 'data'))
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path

def paginated_files_check(wdir, keysa, keysb):
    print('Building paginated folder...')
    for keya in keysa:
        for keyb in keysb:
            key_path = pathlib.Path(os.path.join(wdir, 'paginated', keya, keyb))
            key_path.mkdir(parents=True, exist_ok=True)

def crash_recovery(wdir):
    print('Checking for interrupted downloads...', end='', flush=True)
    count = 0 
    for path in pathlib.Path(wdir).rglob('pericles_exported_citations.txt'):
        os.remove(path)
        count+=1
    print('Removed {} files'.format(count))

def progresslog_check(wdir):
    log_path = os.path.join(wdir, 'progress.log')
    try:
        print('Checking log...', end='', flush=True)
        with plog.ProgressLog(log_path):
            print('Successful')
    except FileNotFoundError:
        print('failed, creating')
        plog.ProgressLog.create(log_path)

def database_check(wdir):
    db_path = os.path.join(wdir, 'wiley.db')
    try:
        print('Checking database integrity...', end='', flush=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''SELECT * FROM wiley''')
        conn.close()
        print('Successful')
    except sqlite3.OperationalError :
        print('failed, creating')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(''' CREATE TABLE wiley
                      (keya text, keyb text, title text, authors text, keywords text, doi text, url text, year integer, type text)
        ''')
        conn.close()
