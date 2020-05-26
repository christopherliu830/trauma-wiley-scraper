Requirements:
Python
Selenium
Chrome webdriver

## usage
run wiley.py [location of keys_a.txt] [location of keys_b.txt]

## options
-l, --log : print the current log data 
-r, --results : scrape result counts only
-p, --procs (default 8) : how many simultaneous selenium processes
-d, --database (default False) : take current scraped data and export. If false, will finish scraping before export.


## version 1.1
new features -
    crash recovery, integrity checks
    automatic structuring of files
    more robust logging system
