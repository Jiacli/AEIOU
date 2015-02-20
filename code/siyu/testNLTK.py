import os
from nltk.parse import stanford
import nltk


os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

# GUI
# for sentence in sentences:
#     sentence.draw()
def generateEasyQuestion(originalSentence):
    tokens = nltk.word_tokenize(originalSentence)
    auxilliarySet = set(['is','are','was','were','did','does','did'])
    question = ""
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

   # print "this time question ", question.strip()
    if len(question) > 0:
        rst = question[0].upper() + question[1:-2] + "?"
    else:
        rst = question
    return rst
    
def main():
    print "hello word!"
    os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
    os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

    parser = stanford.StanfordParser(model_path="/Users/sirrie/Desktop/11611/project/jars/model/englishPCFG.ser.gz")
    originalSentence = "For the embattled Woods, this week is about getting back to his roots, and that does not mean a return to Buddhism."
   # sentence = parser.raw_parse(originalSentence)
    #print "the result of the sentence", sentence
    
    print generateEasyQuestion(originalSentence)


    #sentence.draw()
       
    

if __name__ == "__main__":
    main()