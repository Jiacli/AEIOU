#!/usr/bin/env python

import os, sys
import math
import numpy as np
import nltk
from nltk.parse import stanford
from nltk.stem.snowball import SnowballStemmer
import nltk.data

# configuration for the stanford parser
dependency_path = './dependency/'
os.environ['STANFORD_PARSER'] = dependency_path
os.environ['STANFORD_MODELS'] = dependency_path
MODEL_PATH = dependency_path + 'englishPCFG.ser.gz'
parser = stanford.StanfordParser(model_path=MODEL_PATH)
stemmer = SnowballStemmer("english", ignore_stopwords=True)


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
        #print idx, '.', ques_text[idx]
        #print sent_text[match_idx]

        ans = question_answer(ques_text[idx], sent_text[match_idx])
        
        print ans
        


# ---- start of question answering functions -------------
def question_answer(question, text):
    # parse the question first
    q_tree = list(parser.raw_parse(question))[0]
    # q_tree should be the root node
    assert q_tree.label() == 'ROOT'

    # obtain the question type Y/N or WH first
    q_type = get_question_type(q_tree)
    if q_type == None:
        ans = text
    elif q_type == 'Y/N':
        ans = answer_yorn(q_tree, text)
    elif q_type.startswith('WH') or q_type.startswith('HO'):
        ans = answer_whq(q_type, q_tree, text)
    else:
        ans = 'Unknown question->' + q_type

    return ans

def answer_yorn(q_tree, text):
    try:
        s_tree = list(parser.raw_parse(text))[0]
    except Exception, e:
        return  'YES'
    # maybe the most hard part of answering system..
    # using a probabilitic model to eval
    
    q_tokens = stemming(q_tree.leaves())
    q_len = len(q_tokens)
    q_tags = [0] * q_len
    t_tokens = nltk.word_tokenize(text)

    t_tokens_set = set(stemming(t_tokens))
    for idx in xrange(q_len):
        if q_tokens[idx] in t_tokens_set:
            q_tags[idx] = 1

    # overlap score
    overlap_s = float(np.sum(q_tags)) / q_len

    # mismatch score
    mismatch_s = 0
    for idx in xrange(1, q_len-1):
        if q_tags[idx] > 0:
            continue
        if q_tags[idx-1] > 0 and q_tags[idx+1] > 0:
            mismatch_s += 1
            # check what is missing?
            status = word_seq_matching(s_tree, q_tree, idx)
            #print 'have status check at:',idx, ' ', status
            if status == 'N':
                return 'NO'
            else:
                mismatch_s -= 1

    if overlap_s > 0.7:
        return 'YES'

    #print 'return default result NO'
    return 'NO'

def word_seq_matching(s_tree, q_tree, index):
    t_pos = s_tree.pos()
    q_pos = q_tree.pos()
    lastw = q_pos[index-1][0]
    nextw = q_pos[index+1][0]

    for idx in xrange(1, len(t_pos)-1):
        if t_pos[idx-1][0] == lastw and t_pos[idx+1][0] == nextw:
            q_w = stemmer.stem(q_pos[index][0]).encode('UTF-8', 'ignore')
            t_w = stemmer.stem(t_pos[idx][0]).encode('UTF-8', 'ignore')
            if q_w == t_w:
                return 'Y'
            q_tag = q_pos[index][1]
            t_tag = t_pos[idx][1]
            if q_tag[0] != t_tag[0]:
                return 'Y'
            else:
                return 'N'
    return None

def answer_whq(q_type, q_tree, text):
    try:
        s_tree = list(parser.raw_parse(text))[0]
    except Exception, e:
        return  text
    
    #print s_tree
    ans = None
    if q_type == 'WHO':
        ans = ans_who(s_tree[0], q_tree)
    elif q_type == 'WHEN':
        ans = ans_when(s_tree[0], q_tree)
    elif q_type == 'WHERE':
        pass
    elif q_type == 'WHAT':
        pass
    elif q_type == 'HOW':
        # not sure whether how should be here
        pass

    # save me if I cannot find ans
    if ans == None or len(ans) == 0:
        ans = text
    return ans


DATE_set = set(['January', 'February', 'March', 'April', 'May', 'June',\
    'July', 'August', 'September', 'October', 'November', 'December', 'Jan.',\
    'Feb.', 'Mar.', 'Apr.', 'Jun.', 'Jul.', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',\
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

def find_treenode_given_tag(root, tag, nodes):
    # the results are stored in the nodes list
    for child in root:
        if type(child) != nltk.tree.Tree:
            continue
        if child.label() == tag:
            nodes.append(child)
        find_treenode_given_tag(child, tag, nodes)

def ans_when(s_tree, q_tree):
    q_tokens = set(q_tree.leaves())
    ans = []
    nodes = []
    # find all nodes with PP tag
    find_treenode_given_tag(s_tree, 'PP', nodes)
    for node in nodes:
        nodepos = node.pos()
        s = 0.0
        # eval
        for (token, tag) in nodepos:
            if token in DATE_set:
                s += 2.0
            elif tag == 'CD':
                s += 1.5
            elif token.endswith('th') or token.endswith('st') or token.endswith('nd') or token.endswith('rd'):
                s += 0.2
            elif token in q_tokens:
                s -= 0.5
        ans.append((node.leaves(), s))

    # rank
    if len(ans) == 0:
        return None
    else:
        ans = sorted(ans, key=lambda x:x[1], reverse=True)
        return ' '.join(ans[0][0])

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
        #print 'Invalid question:', ' '.join(root[0].leaves())
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
    #print match_list[0:5]

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


PUNC_set = set([',', '.', '?', ':', '!', ';', "'"])
# ---- start of pre-processing functions ----------------
def preprocess(args):

    article = args[1]
    questions = args[2]

    # sentence segmentation
    sentences = sent_segment(article)
    for sent in sentences:
        if len(sent) == 0 or sent[-1] not in PUNC_set:
            continue

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
            try:
                sents = sent_detector.tokenize(line)
            except Exception, e:
                continue            
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
    s_tree = parser.raw_parse('In Feb. 1990s, Tom Watson showed love to Ben Cook.')[0]
    s_tree.draw()
    sys.exit(-1)


if __name__ == '__main__':
    #func_test(sys.argv)
    # ./answer article.txt questions.txt
    if len(sys.argv) != 3:
        print 'Usage: python ./answer article.txt questions.txt'
        sys.exit(-1)
    main(sys.argv)

