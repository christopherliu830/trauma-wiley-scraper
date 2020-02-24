import os

keywords = [[],[]]

if __name__ == '__main__':
    with open('keys-a.txt', 'r', encoding='utf-8') as fd:
        keywords[0] = fd.read().split('\n')
    with open('keys-b.txt', 'r', encoding='utf-8') as fd:
        keywords[1] = fd.read().split('\n')

    for key_a in keywords[0]:

        with open('final/final.txt', 'r', encoding='utf-8') as checklist:
            if key_a in checklist.read():
                continue

        path = 'final/Chris_Wiley_{}'.format(key_a)
        results_file_path = 'results/Chris_Wiley_{}.txt'.format(key_a)
        with open(results_file_path, 'r', encoding='utf-8') as results_file:
            results = results_file.read().split('\n')
        if not os.path.exists(path):
            os.mkdir('final/Chris_Wiley_{}'.format(key_a))
        for result in results:
            split = result.split(', ')
            if len(split) == 1:
                break
            a, key_b, count = split

            print(result)
            count = int(count)
            if count % 20 == 0:
                pages = count // 20
            else:
                pages = count // 20 + 1
            if pages > 100:
                pages = 100
            final_csv_path = path + '/Chris_Wiley_{} and {}.txt'.format(key_a, key_b)
            with open(final_csv_path, 'w', encoding='utf-8') as final_csv:
                for i in range(pages):
                    csv_path = 'csv/Chris_Wiley_{}/Chris_Wiley_{} and {}_{}.txt'.format(key_a, key_a, key_b, i)
                    with open(csv_path, 'r', encoding = 'utf-8') as csv_page:
                        final_csv.write(csv_page.read())
        with open('final/final.txt', 'a', encoding='utf-8') as checklist:
            checklist.write(key_a + '\n')
            


