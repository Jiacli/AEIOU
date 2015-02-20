#!/usr/bin/env python

import os
from nltk.parse import stanford

os.environ['STANFORD_PARSER'] = r'C:\Users\Jiachen\Documents\GitHub\AEIOU\code'
os.environ['STANFORD_MODELS'] = r'C:\Users\Jiachen\Documents\GitHub\AEIOU\code'
os.environ['JAVAHOME'] = r'C:\Root\Tools\Java\jdk1.8.0_25\bin'

parser = stanford.StanfordParser(model_path=r"C:\Users\Jiachen\Documents\GitHub\AEIOU\code\englishPCFG.ser.gz")
sentences = parser.raw_parse("he drops more than six courses, it's amazing!")
print sentences
print sentences[0].pos()
# GUI
for sentence in sentences:
    sentence.draw()