L = [[],  ["1", "2"]]
with open("D:/code/Python/Class_GraduationProject/HET-MC-main/data_preprocessing/data/crawl_data/test.txt", 'w') as f:
    for i in range(len(L)):
        if L[i] != []:
            f.write(''.join(L[i]))
        else:
            f.write("\n")