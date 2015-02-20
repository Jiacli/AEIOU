#!/usr/bin/env python

# command line : python ./ask.py ml.txt output.txt
import sys
import re
import string
import testNLTK

# gloabl control variables
verbose = True

# main routine
def main(args):
    # read article, return a list of valid sentences with 
    # certain length (50<length<300) and upper-case letter
    # starting.
    sentences = read_article(args[1])
    questions = ask(sentences)
    

def ask(sentences):
    # generate questions based on valid sentence list
    q_list = []
    for sentence in sentences:
        rst = testNLTK.generateEasyQuestion(sentence)
        if len(rst) > 0:
            q_list.append(rst)
    print q_list
    return q_list


    
# article reading control parameters    
valid_sents_length_lo = 50
valid_sents_length_hi = 300

def read_article(filename):
    sentences = []
    with open(filename) as f:
        for line in f.readlines():
            # for empty lines
            if len(line) == 0:
                continue
            # check invalid line e.g., without any punctuation,
            # maybe it is just a title or something else
            if line.count('.') == 0:
                continue
            sents = line.strip().split('.')
            for str in sents:
                s = str.strip()
                # validation rules
                if len(s) > valid_sents_length_lo \
                    and len(s) < valid_sents_length_hi \
                    and (s[0] in string.ascii_uppercase):
                    sentences.append(s)
    # debug
    if verbose:
        i = 0
        for sent in sentences:
            print i, sent
            i += 1
    return sentences


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: ./ask article.txt questions'
        exit(-1)
    main(sys.argv)