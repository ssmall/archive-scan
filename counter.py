#!/usr/local/bin/python2.7

1
3  # +2
2  # -1
4  # +2
5  # +1
7  # +2
6  # -1
8  # +2
9  # +1

DIFF_SEQUENCE = [2, -1, 2, 1]


def page_sequence(start_page):
    diff_index = 0
    cur_page = start_page
    yield cur_page
    while True:
        cur_page += DIFF_SEQUENCE[diff_index % len(DIFF_SEQUENCE)]
        diff_index += 1
        yield cur_page


start_val = int(input("Counter starting value: "))

for page_num in page_sequence(start_val):
    print "Page {}".format(page_num)
    raw_input("")
