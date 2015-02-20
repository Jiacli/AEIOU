import os
from nltk.parse import stanford
os.environ['STANFORD_PARSER'] = '/Users/sirrie/Desktop/11611/project/jars'
os.environ['STANFORD_MODELS'] = '/Users/sirrie/Desktop/11611/project/jars'

parser = stanford.StanfordParser(model_path="/Users/sirrie/Desktop/11611/project/jars/model/englishPCFG.ser.gz")
sentences = parser.raw_parse_sents(("Her first duties with the newly formed navy were to provide protection for American merchant shipping during the Quasi-War with France and to help defeat the Barbary pirates in the First Barbary War.", "how can you play?"))
print sentences

# GUI
for sentence in sentences:
    sentence.draw()
