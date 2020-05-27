import argparse
import sys
import os
from tools import integrity, page_scraper, database, plog 

def read_keys(keys_path):
    with open(keys_path, 'r', encoding='utf-8') as keyfile:
        return [line.strip() for line in keyfile]

def main():
    parser = argparse.ArgumentParser(description='Wiley Online Library scraping interface.')
    parser.add_argument('a', metavar='keys-a', type=str)
    parser.add_argument('b', metavar='keys-b', type=str)
    parser.add_argument('-l', '--log', help='print current log', action='store_true')
    parser.add_argument('-r', '--results', help='get result count only', action='store_true')
    parser.add_argument('-p', '--procs', type=int, help='number of simultaneous selenium processes', default=8)
    parser.add_argument('-d', '--database', help='skip scraping and export to database', action='store_true')

    args = parser.parse_args()
    keysa = read_keys(args.a)
    keysb = read_keys(args.b)
    
    integrity.integrity_check(os.getcwd(), keysa, keysb)

    with plog.ProgressLog('data/progress.log') as log:
        if args.log:
            print(log)
            return
        paginated_path = os.path.join(os.getcwd(), 'data', 'paginated')
        database_path = os.path.join(os.getcwd(), 'data', 'wiley.db')
        if not args.database:
            page_scraper.start(paginated_path, keysa, keysb, log, results_only=args.results, procs=args.procs)
        database.export(paginated_path, database_path, keysa, keysb, log)

if __name__ == '__main__':
    main()