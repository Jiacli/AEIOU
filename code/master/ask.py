#!/usr/bin/env python

import sys
import os
import re
import string
import generateQuestion
import preprocess
import evaluation
import operator

# gloabl control variables
verbose = True
# os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
# os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

# main routine
def main(args):
    # read article, return a list of valid sentences with 
    # certain length (50<length<300) and upper-case letter
    # starting.

    # parse the html file and return the raw text filename
    filename = parse_html_file(args[1])

    sentences = preprocess.read_article_asking(filename)
    questions = ask(sentences, args[2])

    # clean up the temp raw text file
    os.system('rm ' + filename)
    
def parse_html_file(filename):
    title = ''
    sent_list = []
    with open(filename) as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            if line.startswith('<title>'):
                tmp = re.sub('<[^>]+>', '', line.strip())
                title = re.sub(r'\s+', '_', tmp)
                print 'title:', title
            elif line.startswith('<p>'):
                line = re.sub('<[^>]+>', '', line.strip())
                if len(line) > 0:
                    sent_list.append(line)
    newfilename = filename + '.txt'
    with open(newfilename, 'w') as g:
        for line in sent_list:
            g.write(line + '\n')
    return newfilename

def ask(sentences, number):
    # generate questions based on valid sentence list
    q_list_what_who = dict()
    q_list_easy = dict()
    what_who_rst = []
    easy_rst = []
    counter = 0
    count = int(number)
    evaluationModel = evaluation.interpolateModel()

    for sentence in sentences:
        
        # catch unexpected error
        try:
            # generate easy questions
            easy_rst.append(generateQuestion.generateEasyQuestion(sentence))
            # generate 'who' qustions
            what_who_rst.append(generateQuestion.generateWhoAndWhat(sentence, False))
        except UnicodeDecodeError:
            continue

        for sent in easy_rst:
            if len(sent) > 0:
                # counter += 1
                perplexity = evaluationModel.sentencePerp(sent)
                q_list_easy[sent] = perplexity
                # print sent, perplexity

        for sent in what_who_rst:
            if len(sent) > 0:
                # counter += 1
                perplexity = evaluationModel.sentencePerp(sent)
                q_list_what_who[sent] = perplexity
                # print sent, perplexity

    q_what_who_sort = sorted(q_list_what_who.items(), key=operator.itemgetter(1))
    q_easy_sort = sorted(q_list_easy.items(), key=operator.itemgetter(1))

    # print top n sentences
    index = 0
    for sent in q_what_who_sort:
        index += 1
        print sent[0]
        if index >= count / 2:
            break

    index = 0
    for sent in q_easy_sort:
        index += 1
        print sent[0]
        if index >= count / 2:
            break
    # return q_list

    
# article reading control parameters    
valid_sents_length_lo = 50
valid_sents_length_hi = 250




if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: ./ask article.txt count'
        exit(-1)
    main(sys.argv)