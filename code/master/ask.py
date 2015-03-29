#!/usr/bin/env python

import sys
import os
import re
import string
import generateQuestion
import preprocess

# gloabl control variables
verbose = True
# os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
# os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

# main routine
def main(args):
    # read article, return a list of valid sentences with 
    # certain length (50<length<300) and upper-case letter
    # starting.
    sentences = read_article_asking(args[1])
    questions = ask(sentences)
    

def ask(sentences):
    # generate questions based on valid sentence list
    q_list = []
    counter = 0
    for sentence in sentences:
        #rst = generateQuestion.generateEasyQuestion(sentence)
        rst = generateQuestion.generateWho(sentence)
        if len(rst) > 0:
            counter += 1
            q_list.append(rst)
            print counter, " , ", rst
    return q_list

    
# article reading control parameters    
valid_sents_length_lo = 50
valid_sents_length_hi = 300




if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: ./ask article.txt questions'
        exit(-1)
    main(sys.argv)