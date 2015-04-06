from nltk.corpus import wordnet as wn

def main():
    wordList = ['good','bad','terrific']
    synomymsRst = []
    targetWord = 'dog'
    # for word in wordList:
    #     syn_sets = wn.synsets(word)
    #     if len(syn_sets) > 0:
    #         temp = []
    #         for synset in syn_sets:
    #             for lemma in synset.lemmas:
    #                 print lemma.name,
    #             print ""

    #         synomymsRst.append(temp)
    # print "the synomyms result ",synomymsRst

    for synset in wn.synsets('swap'):
        print synset.

if __name__ == '__main__':
    main()
  