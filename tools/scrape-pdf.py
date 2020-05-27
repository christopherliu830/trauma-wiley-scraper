import os
import sqlite3
import requests

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

def finish_file():
    pass

def start_driver(*args):
    options = webdriver.ChromeOptions()
    prefs = {
        'download.default_directory' : os.path.join(os.getcwd(), *args),
        'safebrowsing.disable_download_protection' : True
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_one_pdf(record, driver):
    _, _, _, _,  _, doi, _, _, _ = record
    _, suffix = doi.split(':')
    download_url = 'https://onlinelibrary.wiley.com/doi/pdfdirect/{}?download=true'.format(suffix)
    driver.get(download_url)
    while True: pass

def scrape_many_pdf(db, keya, keyb):
    c = db.cursor()

    try:
        os.mkdir('{}'.format(keya))
        os.mkdir('{}/{}'.format(keya, keyb))
    except FileExistsError:
        pass

    driver = start_driver(keya, keyb)
    c.execute('''SELECT * FROM wiley WHERE keya LIKE ? AND keyb LIKE ?''', (keya, keyb))
    records = c.fetchall()
    if records:
        scrape_one_pdf(records[0], driver)

def main():
    keywords = [[],[]]

    with open('keys-a.txt', 'r', encoding='utf-8') as fd:
        keywords[0] = fd.read().split('\n')
    with open('keys-b.txt', 'r', encoding='utf-8') as fd:
        keywords[1] = fd.read().split('\n')

    conn = sqlite3.connect('wiley.db')

    scrape_many_pdf(conn, '(multi)trauma', '(ASS)')

if __name__ == '__main__': main()