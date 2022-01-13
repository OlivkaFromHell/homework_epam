with open('data.txt', mode='r', encoding='raw_unicode_escape') as in_file, \
     open('data_utf8.txt', mode='w', encoding='utf-8') as out_file:

    # A file is iterable
    # We can read each line with a simple for loop
    for line in in_file:
        out_file.write(line)
