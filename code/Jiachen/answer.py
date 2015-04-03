#!/usr/bin/env python

import os, sys
import math
import numpy as np
import nltk
from nltk.parse import stanford
from nltk.stem.snowball import SnowballStemmer
import nltk.data

# configuration for the stanford parser
os.environ['STANFORD_PARSER'] = '../'
os.environ['STANFORD_MODELS'] = '../'
MODEL_PATH = '../englishPCFG.ser.gz'
parser = stanford.StanfordParser(model_path=MODEL_PATH)
stemmer = SnowballStemmer("english", ignore_stopwords=True)


#sentences = parser.raw_parse("NLP is a great course, we all love it.")
#print sentences
#print sentences[0].pos()
# GUI
#for sentence in sentences:
#    sentence.draw()


# global params
sent_text = []
sent_feat = []
ques_text = []
ques_feat = []

def main(args):

    # Preprocess the input, get sentence representation
    # of the whole article. Extract sentence and question
    # features as stemmed token sequence (uni/bi-gram)
    preprocess(args)

    # Question answering routine:
    # loop over all questions in the main function
    for idx in xrange(len(ques_text)):
        match_idx = sent_matching(idx)
        print ques_text[idx]
        print sent_text[match_idx]

        question_answer(ques_text[idx], sent_text[match_idx])
        break
        


# ---- start of question answering functions -------------
def question_answer(question, text):
    # parse the question first
    q_tree = parser.raw_parse(question)[0]
    # q_tree should be the root node
    assert q_tree.label() == 'ROOT'

    # debug
    print q_tree

    # obtain the question type Y/N or WH first
    q_type = get_question_type(q_tree)

    if q_type == 'Y/N':
        pass
    elif q_type.startswith('WH'):
        ans = answer_whq(q_type, q_tree, text)

    print 'ans:', ans, '\n'


def answer_whq(q_type, q_tree, text):
    s_tree = parser.raw_parse(text)[0]
    print s_tree
    ans = ''
    if q_type == 'WHO':
        ans = ans_who(s_tree[0], q_tree)
    elif q_type == 'WHEN':
        pass
    elif q_type == 'WHERE':
        pass
    elif q_type == 'WHAT':
        pass
    elif q_type == 'HOW':
        # not sure whether how should be here
        pass
    return ans

def ans_who(s_tree, q_tree):
    ans = []
    for child in s_tree:
        if not child.label().startswith('N'): # find name in N-label
            continue
        nes = nltk.ne_chunk(child.pos())
        for ne in nes:
            if type(ne) == nltk.tree.Tree:
                if ne.label() == 'PERSON':
                    name = []
                    for n in ne.leaves():
                        name.append(n[0])
                    ans.append(' '.join(name))
    return ', '.join(ans)




# question type set
SBARQ_set = set(['WHPP', 'WHNP', 'WHADJP', 'WHAVP', 'WHADVP'])
WH_set = set(['WP', 'WDT', 'WP$', 'WRB'])
#SQ_set = set(['IS', 'WAS', 'AM', 'ARE', 'WERE', 'DO', 'DOES', 'DID'])

def get_question_type(root):
    label = root[0].label()

    if label == 'SBARQ':
        # direct question introduced by a wh-word or a wh-phrase.
        for child in root[0]:
            if child.label() in SBARQ_set:
                for (token, tag) in child.pos():
                    if tag in WH_set:
                        head = token.encode('UTF-8', 'ignore').upper()
                        return head
    elif label == 'SQ':
        # inverted yes/no question
        return 'Y/N'
    else:
        print 'Unknown clause level type:', label
        return None


# ---- end of question answering functions ---------------




# ---- start of sentence matching functions -------------
def sent_matching(idx): # idx is the question index
    # locate corresponding question feature
    q_feat = ques_feat[idx]
    
    match_list = []

    # loop over all sentences
    for j in xrange(len(sent_feat)):
        score = get_match_score(sent_feat[j], q_feat)
        match_list.append((score, j))

    match_list = sorted(match_list, key=lambda x:x[0], reverse=True)
    print match_list[0:5]

    if len(match_list) > 0:
        return match_list[0][1]
    else:
        return None
        

def get_match_score(s_feat, q_feat):
    featdim = len(q_feat)
    q_match = [0.0] * featdim
    sfeat_set = set(s_feat)

    # boolean match algorithm
    for i in xrange(featdim):
        if q_feat[i] in sfeat_set:
            q_match[i] += 1.0

    # eval the score: normalized by the log of sentence length
    # length discount function is very tricky ... deprecate it currently
    score = np.sum(q_match) / featdim# / math.log(featdim + len(sfeat_set))
    return score
# ---- end of sentence matching functions ---------------



# ---- start of pre-processing functions ----------------
def preprocess(args):

    article = args[1]
    questions = args[2]

    # sentence segmentation
    sentences = sent_segment(article)
    for sent in sentences:
        sent_text.append(sent)
        tokens = nltk.word_tokenize(sent)
        tokens = stemming(tokens)

        feats = sent_feat_extract(tokens)
        sent_feat.append(feats)

    # question feature extraction
    with open(questions) as f:
        for line in map(lambda l:l.strip(), f.readlines()):
            if len(line) == 0:
                continue
            ques_text.append(line)

            # extract question feature (e.g., uni/bi-gram)
            # do tokenization and stemming
            tokens = nltk.word_tokenize(line)
            tokens = stemming(tokens)

            feats = ques_feat_extract(tokens)
            ques_feat.append(feats)

    # result check
    assert len(sent_text) == len(sent_feat)
    assert len(ques_text) == len(ques_feat)

    # the data are loaded in the global variables
    # so there is no return statement

SENT_DETECTOR = 'tokenizers/punkt/english.pickle'

def sent_segment(filename):
    # configure nltk package
    sent_detector = nltk.data.load(SENT_DETECTOR)

    sentences = []
    with open(filename) as f:
        for line in map(lambda x:x.strip(), f.readlines()):
            # for empty lines
            if len(line) == 0:
                continue
            # check invalid line e.g., without any punctuation,
            sents = sent_detector.tokenize(line)
            for sent in sents:
                sentences.append(sent)
    return sentences

def sent_feat_extract(tokens):
    # extract uni/bi-gram features from sentence tokens
    feats = []
    prev_token = ''
    for token in tokens:
        feats.append(token)
        if prev_token != '':
            feats.append(prev_token + ' ' + token)
        prev_token = token
    return feats

def ques_feat_extract(tokens):
    # the tag in dropset will not be considered
    # e.g., which who where when ...
    dropset = set(['.', 'WP', 'WRB', 'WDT', 'WP$'])

    feats = []
    tagged = nltk.pos_tag(tokens)
    #print tagged
    prev_token = ''
    prev_tag = ''
    for idx in xrange(len(tagged)):
        token = tagged[idx][0]
        tag = tagged[idx][1]

        if tag not in dropset:
            feats.append(token)
            if len(prev_token) > 0:
                bifeat = prev_token + ' ' + token
                feats.append(bifeat)
            prev_token = token
            prev_tag = tag
        else:
            prev_token = ''
            prev_tag = ''
    #print feats
    return feats

# list version stemming
def stemming(tokens):
    tokens_stem = []
    for token in tokens:
        try: # in case of special character
            tokens_stem.append(stemmer.stem(token).encode('UTF-8', 'ignore'))
        except Exception, e:
            continue
    return tokens_stem
# ---- end of pre-processing functions ------------------

def func_test(args):
    #sentences = sent_segment(args[1])
    #for sent in sentences:
    #    print sent

    #with open(args[1]) as f:
    #    for line in map(lambda l:l.strip(), f.readlines()):
    #        ques_text.append(line)
    #        tokens = nltk.word_tokenize(line)
    #        tokens = stemming(tokens)
    #        #print tokens
    #        ques_feat_extract(tokens)

    #preprocess(args)

    #print sent_text[0:3]
    #print sent_feat[0:3]
    #print ques_text[0:3]
    #print ques_feat[0:3]
    s_tree = parser.raw_parse('Tom Watson really loves Ben Cook.')[0]
    s_tree.draw()
    sys.exit(-1)
    



if __name__ == '__main__':
    #func_test(sys.argv)
    # ./answer article.txt questions.txt
    if len(sys.argv) != 3:
        print 'Usage: python ./answer article.txt questions.txt'
        sys.exit(-1)
    main(sys.argv)

