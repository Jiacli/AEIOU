#!/usr/bin/env python

import sys, os
import re
import string
import generateQuestion as genQ
import evaluation
import operator
import nltk.data
from nltk.parse import stanford
import nltk

# gloabl control variables
verbose = False

# stanford parser
path = '../../../jars/'
os.environ['STANFORD_PARSER'] = path
os.environ['STANFORD_MODELS'] = path
parser = stanford.StanfordParser(model_path=path+"englishPCFG.ser.gz")

# main routine
def main(args):
    # read article, return a list of valid sentences with 
    # certain length (50<length<300) and upper-case letter
    # starting.

    # parse the html file and return the raw text filename
    filename = parse_html_file(args[1])

    sentences = sent_segment(filename)
    
    questions = ask(sentences, args[2])

    # clean up the temp raw text file
    os.system('rm ' + filename)

def ask(sentences, number):
    # generate questions based on valid sentence list
    q_list_wh = []
    q_list_easy = []
    q_list_what = []
    wh_rst = []
    what_rst = []
    easy_rst = []
    counter = 0
    count = int(number)
    evaluationModel = evaluation.interpolateModel()

    for sentence in sentences:
        # catch unexpected error
        if sentence.endswith('.'):
            sentence = sentence[:-1]
        try:
            # print sentence
            parse_tree = parser.raw_parse(sentence)
            # generate easy questions
            easy_rst.append(genQ.generateEasyQuestion(sentence, parse_tree[:]))
            # generate 'who' qustions
            what_rst.append(genQ.generateWhoAndWhat(sentence, parse_tree[:]))
            # generate 'when' questions
            wh_rst.append(genQ.generateWhen(sentence, parse_tree[:]))
            # generate 'how' questions
            wh_rst.append(genQ.generateHow(sentence, parse_tree[:]))
            # generate 'how long' questions
            wh_rst.append(genQ.generateHowLong(sentence, parse_tree[:]))
        except Exception:
            continue

        for sent in easy_rst:
            if len(sent) > 0:
                # counter += 1
                perplexity = evaluationModel.sentencePerp(sent)
                q_list_easy.append(sent, perplexity)

        for sent in what_rst:
            if len(sent) > 0:
                # counter += 1
                perplexity = evaluationModel.sentencePerp(sent)
                q_list_what.append(sent, perplexity)

        for sent in wh_rst:
            if len(sent) > 0:
                # counter += 1
                perplexity = evaluationModel.sentencePerp(sent)
                q_list_wh.append(sent, perplexity)

    q_what_sort = sorted(q_list_what, key=lambda x:x[1], reverse=True)
    q_wh_sort = sorted(q_list_wh, key=lambda x:x[1], reverse=True)
    q_easy_sort = sorted(q_list_easy, key=lambda x:x[1], reverse=True)

    # print top n sentences
    index = 0
    for sent in q_easy_sort:
        index += 1
        print sent[0]
        if index > count / 3:
            break

    for sent in q_wh_sort:
        index += 1
        print sent[0]
        if index > (count / 3)*2:
            break

    for sent in q_what_sort:
        index += 1
        print sent[0]
        if index > count:
            break

    
# article reading control parameters    
valid_sents_length_lo = 100
valid_sents_length_hi = 200


# preprocess function - sentence parser
SENT_DETECTOR = 'tokenizers/punkt/english.pickle'
def sent_segment(filename, verbose=False):
    # configure nltk package
    sent_detector = nltk.data.load(SENT_DETECTOR)

    sentences = []
    with open(filename) as f:
        for line in map(lambda x:x.strip(), f.readlines()):
            # for empty lines
            if len(line) == 0:
                continue
            # check invalid line e.g., without any punctuation,
            try:
                sents = sent_detector.tokenize(line)
            except Exception, e:
                continue            
            for sent in sents:
                sent = re.sub('\([^\)]+\)', '', sent)
                if len(sent) > valid_sents_length_lo \
                    and len(sent) < valid_sents_length_hi \
                    and (sent[0] in string.ascii_uppercase):
                    sentences.append(sent)
    # debug
    if verbose:
        i = 0
        for sent in sentences:
            print i, sent
            i += 1
    return sentences

# html parser
def parse_html_file(filename):
    sent_list = []
    with open(filename) as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            if line.startswith('<title>'):
                tmp = re.sub('<[^>]+>', '', line.strip())
                title = re.sub(r'\s+', '_', tmp)
            elif line.startswith('<p>'):
                line = re.sub('<[^>]+>', '', line.strip())
                if len(line) > 0:
                    sent_list.append(line)
    newfilename = 'tmp_raw_text'
    with open(newfilename, 'w') as g:
        for line in sent_list:
            g.write(line + '\n')
    return newfilename


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: ./ask article.htm count'
        exit(-1)
    main(sys.argv)