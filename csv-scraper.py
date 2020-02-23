from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import psutil
import time
import os
from threading import Thread, Lock
import logging


keywords = [[],[]]
mutexes = [Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock(), Lock()]
logging.basicConfig(level=logging.ERROR,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

def file_downloading(fpath):
    try:
        with open(fpath, 'r'):
            pass
        return False
    except FileNotFoundError:
        return True
    except PermissionError:
        return True

def download_csv(driver, path):
    elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'selectAllCitation')))
    while True:
        try:
            driver.execute_script("document.getElementsByClassName('selectAllCitation')[0].style.left = 0;")
            elem.click()
            elem = driver.find_element_by_class_name('articles-toolbar-option')
            elem.click()

            elem = driver.find_element_by_id('radio-format-1')
            driver.execute_script("document.getElementById('radio-format-1').style.left = 0;")
            elem.click()
            elem.submit()

            elem = driver.find_element_by_xpath("//div[@class='modal__footer-right']//button[@data-dismiss='modal']")
            elem.click()

            break
        except ElementNotInteractableException:
            pass
        


def start_driver(dlpath):
    options = webdriver.ChromeOptions()
    prefs = {
        'download.default_directory' : os.getcwd() + '\\' + dlpath,
        'safebrowsing.disable_download_protection' : True
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)
    return driver

def search_keys(threadno):
    key_a = keywords[0][threadno]
    with mutexes[threadno % 8]:

        current_results = ''
        path = 'results/Chris_Wiley_{}.txt'.format(key_a)
        if os.path.exists(path):
            logging.error(path)
            with open(path, 'r', encoding='utf-8') as results_file:
                current_results = results_file.read()

        driver = start_driver('csv\\Chris_Wiley_{}'.format(key_a))

        with open(path, 'a', encoding='utf-8') as results_file:
            for key_b in keywords[1]:
                if '{}, {}'.format(key_a, key_b) in current_results:
                    continue
                driver.get('https://onlinelibrary.wiley.com/search/advanced')

                if os.path.exists('csv/Chris_Wiley_{}/pericles_exported_citations (1).txt'.format(key_a)):
                    print('error has occurred')
                    break

                # Advanced Search Page
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'searchArea1')))
                except TimeoutException:
                    print('timed out on search')
                    break

                elem = driver.find_element_by_id('text1')
                elem.send_keys('"{}" "{}"'.format(key_a, key_b) + Keys.RETURN)

                # Results Page
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'result__sep')))
                except TimeoutException:
                    print ('Timed out waiting for results')
                    continue

                try: # 0 elements
                    results = int(driver.find_element_by_xpath("//span[@class='result__current']").text)
                except NoSuchElementException: # nonzero
                    results = driver.find_element_by_xpath("//span[@class='result__count']").text
                    results = results.replace(',','')
                    results = int(results)

                if results != 0:
                    try:
                        page = 0
                        while True:
                            if os.path.exists('csv/Chris_Wiley_{}/pericles_exported_citations.txt'.format(key_a)):
                                os.remove('csv/Chris_Wiley_{}/pericles_exported_citations.txt'.format(key_a))

                            if not os.path.exists('csv/Chris_Wiley_{}/Chris_Wiley_{} and {}_{}.txt'.format(key_a, key_a, key_b, page)):
                                download_csv(driver, page)
                                while (file_downloading('csv/Chris_Wiley_{}/pericles_exported_citations.txt'.format(key_a))):
                                    time.sleep(0.1)

                                os.rename(
                                    'csv/Chris_Wiley_{}/pericles_exported_citations.txt'.format(key_a), 
                                    'csv/Chris_Wiley_{}/Chris_Wiley_{} and {}_{}.txt'.format(key_a, key_a, key_b, page)
                                )
                            elem = driver.find_element_by_class_name('pagination__btn--next')
                            driver.get(elem.get_attribute('href'))
                            page += 1
                    except NoSuchElementException:
                        pass
                    except TimeoutException:
                        print('timed out')

                results_file.write('{}, {}, {}\n'.format(key_a, key_b, results))
                results_file.flush()

def test(a):
    print(a)
if __name__ == '__main__':
    with open('keys-a.txt', 'r', encoding='utf-8') as fd:
        keywords[0] = fd.read().split('\n')
    with open('keys-b.txt', 'r', encoding='utf-8') as fd:
        keywords[1] = fd.read().split('\n')

    for i in range(len(keywords[0])):
        t = Thread(target=search_keys, args=(i,))
        t.daemon = True
        t.start()
    while True:
        time.sleep(1)


