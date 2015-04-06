#author siyuchen
import os
from nltk.parse import stanford
from nltk.stem.snowball import SnowballStemmer
import nltk
from nltk.tree import Tree

path = '../../../jars/'
os.environ['STANFORD_PARSER'] = path
os.environ['STANFORD_MODELS'] = path
parser = stanford.StanfordParser(model_path=path+"englishPCFG.ser.gz")
stemmer = SnowballStemmer("english", ignore_stopwords=True)

def checkAuxiliary(auxSet, tokens):
    for token in tokens:
        if token in auxSet:
           return True
    return False

def generateEasyQuestion(originalSentence):
    stemmer = SnowballStemmer("english")
    originalSentence = originalSentence[0].lower() + originalSentence[1:]
    tokens = nltk.word_tokenize(originalSentence)
    auxiliarySet = set(['is','are','was','were','did','does','did','must','may','can','could','should','will','would','has','have'])
    verbSet = set(['VB','VBD','VBG','VBP','VBZ'])
    question = ""
    # in this case we will move the verb to the first and generate new question
    if checkAuxiliary(auxiliarySet, tokens):
        findAuxiliary = False
        for index in xrange(len(tokens)):
            word = tokens[index]
           
            # if we find the auxilliary verb , move it to the front of the sentence
            if word in auxiliarySet :
                for subSentence in originalSentence.split(","):
                    if word not in subSentence :
                        question += subSentence
                        
                    elif not findAuxiliary:
                        newSubSentence = ""
                        for token in nltk.word_tokenize(subSentence):
                            if token == '.':
                                break
                            elif token != word or findAuxiliary:
                                newSubSentence += token + " "
                            elif not findAuxiliary:
                                newSubSentence = token + " " + newSubSentence
                                findAuxiliary = True
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

#-- generate questions based on four basic rules.
# 1. It is assumed that subject appears at the begining of sentences.
# 2. PP which appears at the begining of sentences will be deleted.
# 3. SBAR and ADTP which appears at the end will be deleted.
# 4. When scaning parse tree which contains comma, all words after
# comma will be deleted if NP, VP, NP have already all appear before.

def checkPersonName(root, verbose=True):
    is_person = True
    nes = nltk.ne_chunk(root.pos())
    if verbose:
        print nes
    for ne in nes:
        if type(ne) == nltk.tree.Tree:
            if ne.label() != 'PERSON':
                is_person = False
        else:
            is_person = False

    return is_person

def generateWhoAndWhat(sents, verbose=True):
        ques = ''
        sentences = parser.raw_parse(sents)
        # stack indicates main component: NP, VP, NP
        stack = ['NP', 'V']
        is_who = False
        is_what = False

        root = sentences[0][0]
        if verbose:
            print root
            # f.write(str(root)+'\n')

        # drop PP subsentence
        if root[0].label() == 'PP' and root[1].label() == ',':
            if root[2].label() == 'NP':
                if checkPersonName(root[0], verbose):
                    is_who = True
                else:
                    is_what = True

                [ques, flag] = dfs(root, 0, 3, stack)
        elif root[0].label() == 'NP':
            if checkPersonName(root[0], verbose):
                is_who = True
            else:
                is_what = True
            
            [ques, flag] = dfs(root, 0, 1, stack)
        else:
            return ques

        # generate questions which are not null
        if ques != '':
            if is_who:
                ques = 'Who'+ques+'?'
            else:
                ques = 'What'+ques+'?'
            return ques
        else:
            return ''

DATE_set = set(['January', 'February', 'March', 'April', 'May', 'June',\
    'July', 'August', 'September', 'October', 'November', 'December', 'Jan.',\
    'Feb.', 'Mar.', 'Apr.', 'Jun.', 'Jul.', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',\
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

BE_set = set(['is', 'am', 'are', 'was', 'were'])
def generateWhen(sents, verbose=False):
    ques = ''
    s_tree = parser.raw_parse(sents)[0]
    print s_tree
    nodes = []
    q = []
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
        q.append((node.leaves(), s))

    # check whether can form any question
    if len(q) > 0:
        q = sorted(q, key=lambda x:x[1], reverse=True)
        print q
        if q[0][1] > 3.0:
            q_token = q[0][0]
            # now come up with the question
            s_pos = s_tree.pos()
            for idx in xrange(len(s_pos)):
                if q_token[0] == s_pos[idx][0]:
                    index = idx
                    for j in xrange(1, len(q_token)):
                        if q_token[j] != s_pos[idx+j][0]:
                            index = -1
                            break
                    if index > 0:
                        break
            sent = []
            done = False
            if index != 0:
                for idx in xrange(index):
                    token = s_pos[idx][0]
                    tag = s_pos[idx][1]
                    if idx == 0:
                        token = token.lower()
                    if tag.startswith('VB') and not done:
                        done = True                        
                        token = token.lower()
                        if token in BE_set:
                            ques = 'When ' + token + ' '
                        else:
                            ques = 'When did '
                            sent.append(stemmer.stem(token))
                    else:
                        sent.append(token)
            ques += ' '.join(sent) + '?'
    print ques

    return ques 

def find_treenode_given_tag(root, tag, nodes):
    # the results are stored in the nodes list
    for child in root:
        if type(child) != nltk.tree.Tree:
            continue
        if child.label() == tag:
            nodes.append(child)
        find_treenode_given_tag(child, tag, nodes)


def dfs(sentences, level, begin, main_component):
    ques = ''
    index = 0
    for child in sentences:
        if index < begin:
            index += 1
            continue           
        elif isinstance(child, Tree):
            # drop SBAR subsentence
            if child.label() == 'SBAR' and len(main_component) == 0:
                continue

            # if comma appears when main components all appear, ignore others
            if len(main_component) == 0 and child.label() == ',':
                return [ques, True]

            [temp, flag] = dfs(child, level+1, 0, main_component)
            ques += temp
            # ignore subsentece after comma
            if flag:
                return [ques, True]

            if len(main_component) != 0 and \
                child.label().startswith(main_component[len(main_component)-1]):
                #print child.label()
                main_component.pop()

        else:
            # print child
            ques += ' '+child
        index += 1
    return [ques, False]


if __name__ == '__main__':
    # used for function test
    #generateWhen('I left Beijing and moved to Pittsburgh in July 21st, 2014.', True)

