import os
from nltk.parse import stanford
from nltk.stem.snowball import SnowballStemmer
import nltk


os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

# GUI
# for sentence in sentences:
#     sentence.draw()
def checkAuxilliary(auxSet, tokens):
    for token in tokens:
        if token in auxSet:
           return True
    return False
def generateEasyQuestion(originalSentence):
    stemmer = SnowballStemmer("english")
    originalSentence = originalSentence[0].lower() + originalSentence[1:]
    tokens = nltk.word_tokenize(originalSentence)
    auxilliarySet = set(['is','are','was','were','did','does','did','must','may','can','could','should','will'])
    verbSet = set(['VB','VBD','VBG','VBP','VBZ'])
    question = ""
    if checkAuxilliary(auxilliarySet, tokens):
        for index in xrange(len(tokens)):
            word = tokens[index]
            if word in auxilliarySet:
               # print "haha ", word , " we start create new easy questions"
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
    else:    # print "we generate verb questions ", originalSentence  
        findVerb = False
        subSentences = originalSentence.split(",")
        for index in xrange(len(subSentences)):
            subSentence = subSentences[index]
            subTokens = nltk.word_tokenize(subSentence)
            subTagged = nltk.pos_tag(subTokens)
            newSubSentence = ""
            for i in xrange(len(subTagged)):
                word, tag = subTagged[i]
              #  print word, " , ", tag, " status ",findVerb
                if not findVerb and tag in verbSet and i > 0:
                    if tag == 'VBD':
                        origianlForm = stemmer.stem(word)
                        # print "index ", subSentence,
                        # print "  +++  ", subSentence.index(word)
                        newSubSentence = "did " + newSubSentence + " " + origianlForm + subSentence[(subSentence.index(word) + len(word)):]
                    elif tag == 'VBP' or tag == 'VPZ':
                        origianlForm = stemmer.stem(word)
                        # print "index ", subSentence,
                        # print  "  +++  ", subSentence.index(word)
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

        #question = question[0:-1]
       # print "this turn ", question

            
   # print "this time question ", question.strip()
    if len(question) > 0:
        rst = question[0].upper() + question[1:-3] + "?"
    else:
        rst = question
    return rst
    
def main():
    print "hello word!"
    os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
    os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

    parser = stanford.StanfordParser(model_path="/Users/sirrie/Desktop/11611/project/jars/model/englishPCFG.ser.gz")
    originalSentence = "In reinforcement learning, a computer program interacts with a dynamic environment in which it perform a certain goal (such as driving a vehicle), without a teacher explicitly telling it whether it has come close to its goal or not."
    sentence = parser.raw_parse(originalSentence)
    # for s in sentence:
    #     s.draw()
    #print "the result of the sentence", sentence
    
    print generateEasyQuestion(originalSentence)


    #sentence.draw()
       
    

if __name__ == "__main__":
    main()