import os, re
import ask
import string
import nltk.data


def read_article_asking(filename, verbose=False):
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
                if len(s) > ask.valid_sents_length_lo \
                    and len(s) < ask.valid_sents_length_hi \
                    and (s[0] in string.ascii_uppercase):
                    sentences.append(s)
    # debug
    if verbose:
        i = 0
        for sent in sentences:
            print i, sent
            i += 1
    return sentences

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
                if len(sent) > ask.valid_sents_length_lo \
                    and len(sent) < ask.valid_sents_length_hi \
                    and (sent[0] in string.ascii_uppercase):
                    sentences.append(sent)
    # debug
    if verbose:
        i = 0
        for sent in sentences:
            print i, sent
            i += 1
    return sentences