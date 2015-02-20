#author siyuchen
import os
from nltk.parse import stanford
from nltk.stem.snowball import SnowballStemmer
import nltk


os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

def checkAuxiliary(auxSet, tokens):
    for token in tokens:
        if token in auxSet:
           return True
    return False

def generateEasyQuestion(originalSentence):
    stemmer = SnowballStemmer("english")
    originalSentence = originalSentence[0].lower() + originalSentence[1:]
    tokens = nltk.word_tokenize(originalSentence)
    auxiliarySet = set(['is','are','was','were','did','does','did','must','may','can','could','should','will','would'])
    verbSet = set(['VB','VBD','VBG','VBP','VBZ'])
    question = ""
    # in this case we will move the verb to the first and generate new question
    if checkAuxiliary(auxiliarySet, tokens):
        for index in xrange(len(tokens)):
            word = tokens[index]
            # if we find the auxilliary verb , move it to the front of the sentence
            if word in auxiliarySet:
                for subSentence in originalSentence.split(","):
                    if word not in subSentence:
                        question += subSentence
                    else:
                        newSubSentence = ""
                        for token in nltk.word_tokenize(subSentence):
                            if token == '.':
                                break
                            elif token != word:
                                newSubSentence += token + " "
                            else:
                                newSubSentence = token + " " + newSubSentence
                        question += newSubSentence[0:-1]
                    question += ", "  
                break
    else:   
    # in this case we will keep the verb at the place it is, change it into its original form and add auxiliary verb
        findVerb = False
        subSentences = originalSentence.split(",")
        for index in xrange(len(subSentences)):
            subSentence = subSentences[index]
            subTokens = nltk.word_tokenize(subSentence)
            subTagged = nltk.pos_tag(subTokens)
            newSubSentence = ""
            for i in xrange(len(subTagged)):
                word, tag = subTagged[i]
                if not findVerb and tag in verbSet and i > 0:
                    if tag == 'VBD':
                        origianlForm = stemmer.stem(word)
                        newSubSentence = "did " + newSubSentence + " " + origianlForm + subSentence[(subSentence.index(word) + len(word)):]
                    elif tag == 'VBP' or tag == 'VPZ':
                        origianlForm = stemmer.stem(word)
                        newSubSentence = "does " + newSubSentence + " " + origianlForm + subSentence[(subSentence.index(word) + len(word)):]
                    else:
                        newSubSentence = "do " + newSubSentence + " " + word + subSentence[(subSentence.index(word) + len(word)):]
                    findVerb = True
                    break
                elif not findVerb:
                    newSubSentence += word + " "
                else:
                    newSubSentence = subSentence
                    break
            question += newSubSentence + ", "

    if len(question) > 0:
        question = question.rstrip('.,?! ')
        rst = question[0].upper() + question[1 : ] + "?"
    else:
        rst = question
    return rst