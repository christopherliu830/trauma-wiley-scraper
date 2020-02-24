import os


if __name__ == '__main__':
    with open('keys-a.txt', 'r', encoding='utf-8') as fd:
        keywords_a = fd.read().split('\n')
    with open('keys-b.txt', 'r', encoding='utf-8') as fd:
        keywords_b = fd.read().split('\n')
    directory = os.path.join(os.getcwd(), 'results')
    a_to_b_count = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            results = file.read().split('\n')
            for result in results:
                split = result.split(', ')
                if len(split) == 1:
                    continue

                a, b, count = split
                if a not in a_to_b_count:
                    a_to_b_count[a] = {keywords_b.index(b) : count}
                else:
                    a_to_b_count[a][keywords_b.index(b)] = count 
    with open('csv_file.csv', 'w', encoding='utf-8') as csv_file:
        csv_file.write(',') # empty csv
        for key_b in keywords_b:
            csv_file.write(str(key_b) + ',')
        csv_file.write('\n')

        for key_a in keywords_a:
            csv_file.write(key_a + ',')
            for idx, key_b in enumerate(keywords_b):
                if key_a in a_to_b_count and idx in a_to_b_count[key_a]:
                    csv_file.write(str(a_to_b_count[key_a][idx]) + ',')
                else:
                    csv_file.write('-1,')
            csv_file.write('\n')



