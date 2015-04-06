import os
import ask
import string


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