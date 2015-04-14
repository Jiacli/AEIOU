#author siyuchen
import os
from nltk.parse import stanford
from nltk.stem.snowball import SnowballStemmer
import nltk
from nltk.tree import Tree
from nltk.stem.wordnet import WordNetLemmatizer
from pattern.en import superlative

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

def generateEasyQuestion(originalSentence, parse_tree):
    sentenceStrucutreStack = ['NP','V','NP']
  #  print "original parrse_tree,",parse_tree
    originalSentence = dfs(parse_tree, 0, 0, sentenceStrucutreStack)[0].strip()
   # print "processed original sentence,",originalSentence
    stemmer = SnowballStemmer("english")
    originalSentence = originalSentence[0].lower() + originalSentence[1:]
    tokens = nltk.word_tokenize(originalSentence)
    tags = nltk.pos_tag(tokens)
   # print "see the whole sentence tokens, ",tags
    auxiliarySet = set(['is','are','was','were','did','does','did','must','may','can','could','should','will','would','has','have'])
    verbSet = set(['VB','VBD','VBG','VBP','VBZ'])
    question = ""
    verbExist = False
    # in this case we will move the verb to the first and generate new question
    if checkAuxiliary(auxiliarySet, tokens):
        findAuxiliary = False
        for index in xrange(len(tokens)):
            word = tokens[index]
            
            # if we find the auxilliary verb , move it to the front of the sentence
            if word in auxiliarySet :
                for subSentence in originalSentence.split(","):
                    if word not in subSentence :
                        subTokens = nltk.word_tokenize(subSentence)
                        subTags = nltk.pos_tag(subTokens)
                        tempSubSentence = ""
                        for i in xrange(len(subTags)):
                            word, tag = subTags[i]
                            if tag == 'JJ':
                                word = "the " + superlative(word)
                            tempSubSentence += word + " "
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
                        
                    question += ","  
                verbExist = True
                break
    else:   
    # in this case we will keep the verb at the place it is, change it into its original form and add auxiliary verb
        findVerb = False
        
        subSentences = originalSentence.split(",")
        for index in xrange(len(subSentences)):
            subSentence = subSentences[index]
            subTokens = nltk.word_tokenize(subSentence)
            subTagged = nltk.pos_tag(subTokens)
           # print "the sentence tags,",subTagged
            newSubSentence = ""
            for i in xrange(len(subTagged)):
                word, tag = subTagged[i]
               # print "the sentence tag tree word ",word, ",", tag

                if not findVerb and tag in verbSet and i > 0:
                    verbExist = True
                    if tag == 'VBD':
                        origianlForm = stemmer.stem(word)
                        newSubSentence = "did " + newSubSentence + " " + origianlForm + subSentence[(subSentence.index(word) + len(word)):]
                    elif tag == 'VBP' or tag == 'VBZ':
                        origianlForm = stemmer.stem(word)
                        newSubSentence = "does " + newSubSentence + " " + origianlForm + subSentence[(subSentence.index(word) + len(word)):]
                    elif tag == 'VB':
                        newSubSentence = "do " + newSubSentence + " " + word + subSentence[(subSentence.index(word) + len(word)):]
                    findVerb = True
                    break
                elif not findVerb:
                    if tag == 'JJ':
                        word = "the " + superlative(word)
                    newSubSentence += word + " "
                elif len(subSentence)== 0 and len(subSentences) > 1 and tag == 'PP':
                    break
                else:
                    newSubSentence = subSentence
                    break
            question += newSubSentence + ","

    if not verbExist:
        return ""
  #  print "the original question,",question
    if len(question) > 0:
        question = question.rstrip('.,?! ')
        newTokens = nltk.word_tokenize(question)
        newTags = nltk.pos_tag(newTokens)
        tempQuestion = ""
        changeAdj = False
        for index in xrange(len(newTags)):
            word, tag = newTags[index]
            if tag == 'JJ':

                if (index - 1) > 0 :
                    lastWord, lastTag = newTags[index - 1]

                    if len(tempQuestion) > 2 and lastTag == 'TD' :
                        if lastWord == 'a':
                            tempQuestion = tempQuestion[0:-2]
                        elif  len(tempQuestion) > 4 and (lastWord == 'the' or lastWord == 'The'):
                            tempQuestion = tempQuestion[0:-4]
                if not changeAdj and lastTag != 'RB' and lastWord != "the":
                    word = "the " + superlative(word)
                    changeAdj = True

            tempQuestion += word + " "

        rst = tempQuestion[0].upper() + tempQuestion[1: ] + "?"
       # rst = question[0].upper() + question[1 : ] + "?"
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

def generateWhoAndWhat(sents, parse_tree, verbose=False):
        ques = ''
        # sentences = parser.raw_parse(sents)
        sentences = parse_tree[:]
        # stack indicates main component: NP, VP, NP
        stack = ['NP', 'V']
        is_who = False
        is_what = False

        root = list(sentences)[0][0]
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
def generateWhen(sents, parse_tree, verbose=False):
    ques = ''
    sentence = parse_tree
    # sentence = parser.raw_parse(sents)
    s_tree = list(sentence)[0]
    #print s_tree
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
        #print q
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
            keepV = False
            if index != 0:
                for idx in xrange(index):
                    token = s_pos[idx][0]
                    tag = s_pos[idx][1]
                    if idx == 0 and token != 'I':
                        token = token.lower()
                    if tag == ',':
                        sent = []
                        continue
                    if tag.startswith('VB'):
                        if done:
                            if not keepV:
                                sent.append(WordNetLemmatizer().lemmatize(token, 'v'))
                            else:
                                sent.append(token)
                            continue
                        done = True                        
                        token = token.lower()
                        if token in BE_set:
                            keepV = True
                            ques = 'When ' + token + ' '
                        else:
                            ques = 'When did '
                            sent.append(WordNetLemmatizer().lemmatize(token, 'v'))
                    else:
                        sent.append(token)
                ques += ' '.join(sent) + '?'

    return ques 

# generate how question
# find NP VP NP through/by in one subsentece, then generate how question
def generateHow(sents, parse_tree, verbose=False):
    ques = ''
    sentence = parse_tree
    # stack indicates main component: NP, VP, NP
    stack = ['NP', 'V']
    stack1 = ['NP', 'V']

    # raw tree
    root = list(sentence)[0][0]
    if verbose:
        print root

    # drop PP subsentence
    find = False
    if root[0].label() == 'PP' and root[1].label() == ',':
        if root[2].label() == 'NP':
            [ques, find] = dfs_how(root, 0, 3, stack, stack1, find)
    elif root[0].label() == 'NP':
        [ques, find] = dfs_how(root, 0, 0, stack, stack1, find)
    else:
        return ques

    # print ques, find
    if ques != '' and find:
        ques = ques.strip()[0].lower()+ques.strip()[1:]
        ques_word = ques.split(" ")

        # find verb in sentence
        # tokenized and pos
        tokens = nltk.word_tokenize(ques)
        tagged = nltk.pos_tag(tokens)
        index = 0
        normal = True
        for word in ques_word:
            if word in BE_set:
                break
            elif tagged[index][1].startswith('V'):
                ques_word[index] = WordNetLemmatizer().lemmatize(ques_word[index], 'v')
                normal = False
                break
            index += 1

        # print normal, index
        if normal:
            return 'How '+ques_word[index]+' '+' '.join(ques_word[:index])+' '+' '.join(ques_word[index+1:])+'?'
        else:
            return 'How did '+' '.join(ques_word)+'?'

    else:
        return ''

    return ques


# How long questions
DURATION_set = set(['year', 'years', 'days', 'day', 'hours', 'hour', 'month', 'months', 'decades', 'decade'])
H_set = set(['have', 'has', 'had'])

def generateHowLong(text, parse_tree):
    # no for in this sentence, drop it
    if ' for ' not in text:
        return ''
    ques = ''
    s_tree = list(parse_tree)[0]

    nodes = []
    q = []
    # find all nodes with PP tag
    find_treenode_given_tag(s_tree, 'PP', nodes)
    for node in nodes:
        nodepos = node.pos()
        if nodepos[0][0] != 'for':
            continue
        s = 0.0
        # eval
        for (token, tag) in nodepos:
            if token in DURATION_set:
                s += 2.0
            elif tag == 'CD':
                s += 1.5
        if s > 0.0:
            q.append((node.leaves(), s))

    if len(q) > 0:
        q = sorted(q, key=lambda x:x[1], reverse=True)
        pp = q[0][0]

        tokens = s_tree.leaves()
        labels = [0] * len(tokens)
        first_idx = -1
        for idx in xrange(len(tokens)):
            token = tokens[idx]
            if token == pp[0]:
                ct = 1
                for i in xrange(1,len(pp)):
                    if tokens[idx+i] == pp[i]:
                        ct += 1
                    else:
                        break
                if ct == len(pp):
                    for i in xrange(idx, len(tokens)):
                        labels[i] = -1
                    for j in xrange(idx-1, -1, -1):
                        if tokens[j] != ',' and tokens[idx] != ';':
                            labels[j] = 1
                        else:
                            break
                    break
        findh = ''
        for idx in xrange(len(labels)):
            if labels[idx] == 1:
                if tokens[idx] in H_set:
                    findh = tokens[idx]
                    labels[idx] = -1
                    break
        # merge sentence
        if len(findh) > 0:
            pre = ''
            suf = ''
            for i in xrange(len(labels)):
                if labels[i] == 0:
                    pre += tokens[i] + ' '
                elif labels[i] == 1:
                    suf += tokens[i] + ' '
            if len(pre) > 0:
                ques = pre + 'how long ' + findh + ' ' + suf + '?'
            else:
                ques = 'How long ' + findh + ' ' + suf + '?'
    if ques == None:
        ques = ''
    return ques

def find_treenode_given_tag(root, tag, nodes):
    # the results are stored in the nodes list
    for child in root:
        if type(child) != nltk.tree.Tree:
            continue
        if child.label() == tag:
            nodes.append(child)
        find_treenode_given_tag(child, tag, nodes)

# extract the main component of sentences
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

# extract main component of sentences
def dfs_how(sentences, level, begin, main_component, original_component, find):
    ques = ''
    index = 0
    for child in sentences:
        if index < begin:
            index += 1
            continue           
        elif isinstance(child, Tree):
            # if comma appears when main components all appear, ignore others
            if child.label() == ',' and not find:
                main_component = original_component[:]

            [temp, find] = dfs_how(child, level+1, 0, main_component, original_component, find)
            ques += temp
            # ignore subsentece after comma
            if find:
                return [ques, True]

            if len(main_component) != 0 and \
                child.label().startswith(main_component[len(main_component)-1]):
                #print child.label()
                main_component.pop()

        else:
            # print child
            if child == 'through':# or child == 'by':
                if len(main_component) == 0:
                    return [ques, True]

            ques += ' '+child
            # print ques

        index += 1
    return [ques, False]

if __name__ == '__main__':
    # used for function test
    print generateHow('The language also influenced early on the Old Norse language through Viking invasions in the 9th and 10th centuries.', True)
    pass
