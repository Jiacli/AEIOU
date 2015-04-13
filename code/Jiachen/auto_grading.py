#!/usr/bin/env python
# automatic grading script for answering

import sys, os


DATA_ROOT = '../data/raw_project_data/'

all_yn = 0
correct_yn = 0

for idx in xrange(2, 40):
    cmd = 'python answer.py ' + DATA_ROOT + str(idx) + '.txt ' + DATA_ROOT + 'q' + str(idx) \
        + '.txt'
    os.system(cmd)
    with open('tmp_ans') as g:
        myans = map(lambda x:x.strip().lower(), g.readlines())
    with open(DATA_ROOT + 'a' + str(idx) + '.txt') as f:
        ans = map(lambda x:x.strip().lower(), f.readlines())
    file_all = 0
    file_correct = 0
    for (his, me) in zip(ans, myans):
        if his.startswith('yes') or his.startswith('no'):
            all_yn += 1
            file_all += 1
            if his[:2] == me[:2]:
                correct_yn += 1
                file_correct += 1
    print file_correct, file_all
    print 'file acc:', float(file_correct) / file_all

print 'acc:', float(correct_yn) / all_yn

