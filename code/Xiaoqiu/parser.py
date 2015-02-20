import os
from nltk.parse import stanford
os.environ['STANFORD_PARSER'] = '/Users/XiaoqiuHuang/Google_Drive/11-411/QAsystem/jars/'
os.environ['STANFORD_MODELS'] = '/Users/XiaoqiuHuang/Google_Drive/11-411/QAsystem/jars/'

parser = stanford.StanfordParser(model_path="/Users/XiaoqiuHuang/Google_Drive/11-411/QAsystem/jars/englishPCFG.ser.gz")
sentences = parser.raw_parse_sents(("I want to go to the party tomorrow"))
print sentences[0]