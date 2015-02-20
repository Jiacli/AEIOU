import os
from nltk.parse import stanford

class parser:
	def __init__(self):
		self.path = '/Users/XiaoqiuHuang/Google_Drive/11-411/AEIOU/code/Xiaoqiu/jars/'
		os.environ['STANFORD_PARSER'] = self.path
		os.environ['STANFORD_MODELS'] = self.path

		self.parser = stanford.StanfordParser(model_path=self.path+"englishPCFG.ser.gz")

	def generateWho(self, sents):
		ques = []
		sentences = self.parser.raw_parse_sents(sents)
		#sentences[1].draw()
		print sentences[1].subtrees()[0].label()
		#self.dfs(sentences[0], ques)
		print ques


	def dfs(self, sentences, ques):
		for subtree in sentences.subtrees():
			ques.append(subtree.label())
			self.dfs(subtree, ques)


if __name__=="__main__":
	model = parser()
	model.generateWho(("USS Constitution is a wooden-hulled, three-masted heavy frigate of the U.S. Navy.","He also likes eating sausage, based on the assumption."))