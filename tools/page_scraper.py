from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import os
import threading
import time
from multiprocessing.pool import ThreadPool
from itertools import product

MAX_THREADS = 8

def rename(paginated_dir, keya, keyb, pageno, timeout):
    filename = os.path.join(paginated_dir, keya, keyb, 'pericles_exported_citations.txt')
    new_filename = os.path.join(paginated_dir, keya, keyb, '{}.txt'.format(pageno))
    for _ in range(10):
        try:
            os.rename(filename, new_filename)
            return True
        except PermissionError:
            pass # Keep trying
        except FileNotFoundError:
            pass
        time.sleep(timeout/10)
    return False

def download_csv(driver):
    elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'selectAllCitation')))

    while True: 
        try: 
            driver.execute_script("document.getElementsByClassName('selectAllCitation')[0].style.left = 0;")
            elem.click() 
            break
        except ElementNotInteractableException: pass
    
    elem = driver.find_element_by_class_name('articles-toolbar-option')
    elem.click()

    elem = driver.find_element_by_id('radio-format-1')
    while True: 
        try: 
            driver.execute_script("document.getElementById('radio-format-1').style.left = 0;")
            elem.click() 
            break
        except ElementNotInteractableException: pass

    elem.submit()

    elem = driver.find_element_by_xpath("//div[@class='modal__footer-right']//button[@data-dismiss='modal']")
    elem.click()

def start_driver(dlpath, keya, keyb):
    options = webdriver.ChromeOptions()
    prefs = {
        'download.default_directory' : os.path.join(os.getcwd(), dlpath, keya, keyb),
        'safebrowsing.disable_download_protection' : True
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def search_combo(args):
    paginated_dir, keya, keyb, log, results_only = args

    pageno = log.get_pageno(keya, keyb)
    result_count = log.get_result_count(keya, keyb)

    driver = None # Don't instantiate the driver until we need to
    if result_count is None:
        driver = start_driver(paginated_dir, keya, keyb)
        result_count = get_result_count(keya, keyb, driver)
        log.set_result_count(keya, keyb, result_count)

    if results_only:
        if driver: driver.quit()
        return
    
    while pageno < 100 and pageno * 20 < result_count : 
        if not driver: 
            driver = start_driver(paginated_dir, keya, keyb)

        base = 'https://onlinelibrary.wiley.com/action/doSearch?field1=AllField'
        text1 = '&text1="{}" "{}" AND NOT (Traumatic brain injury OR Post Traumatic Stress Disorder'.format(keya, keyb).replace(' ', '+')
        startPage = '&pageSize=20&startPage={}'.format(pageno) if pageno > 0 else ''
        url = base + text1 + startPage
        driver.get(url)

        # ----- Results Page -----
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'result__sep')))
        except TimeoutException:
            print(keya, keyb, ': Timed out waiting for results. Trying again...')

        download_csv(driver)
        if not rename(paginated_dir, keya, keyb, pageno, 5):
            print('download error, trying again', keya, keyb)
            continue

        log.set_pageno(keya, keyb, pageno+1)
        pageno += 1

    if driver: 
        driver.quit()

def get_result_count(keya, keyb, driver):

    base = 'https://onlinelibrary.wiley.com/action/doSearch?field1=AllField'
    text1 = '&text1="{}" "{}" AND NOT (Traumatic brain injury OR Post Traumatic Stress Disorder'.format(keya, keyb).replace(' ', '+')
    url = base + text1
    driver.get(url)

    # ----- Results Page -----
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'result__sep')))
    except TimeoutException:
        print(keya, keyb, ': Timed out waiting for results. Trying again...')

    try: # 0 elements
        results = int(driver.find_element_by_xpath("//span[@class='result__current']").text)
    except NoSuchElementException: # nonzero
        results = int(driver.find_element_by_xpath("//span[@class='result__count']").text.replace(',',''))

    return results

def start(absolute_page_path, keysa, keysb, log, procs, results_only=False):
    pool = ThreadPool(procs)

    combos = product(keysa, keysb)
    pool.map(search_combo,  ( (absolute_page_path, *combo, log, results_only) for combo in combos) )
    pool.close()
    pool.join()

