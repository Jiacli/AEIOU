import os
from nltk.parse import stanford
from nltk.tree import Tree

class parser:
	def __init__(self):
		self.path = '/Users/XiaoqiuHuang/Google_Drive/11-411/AEIOU/code/Xiaoqiu/jars/'
		os.environ['STANFORD_PARSER'] = self.path
		os.environ['STANFORD_MODELS'] = self.path

		self.parser = stanford.StanfordParser(model_path=self.path+"englishPCFG.ser.gz")

	def generateWho(self, sents):
		ques = ''
		sentences = self.parser.raw_parse(sents)
		root = sentences[0][0]
		if root[0].label() == 'PP' and root[1].label() == ',':
			if root[2].label() == 'NP':
				ques = self.dfs(root, 0, 3)
		elif root[0].label() == 'NP':
				ques = self.dfs(root, 0, 1)
		else:
			return ques

		quesWho = 'Who'+ques
		quesWhat = 'What'+ques
		print quesWho
		print quesWhat
		return ques


	def dfs(self, sentences, level, begin):
		ques = ''
		index = 0
		for child in sentences:
			if index < begin:
				index += 1
				continue
			if level == 0 and child.label() == '.':
				ques += '?'
				return ques				
			elif isinstance(child, Tree):
				ques += self.dfs(child, level+1, 0)
			else:
				ques += ' '+child
			index += 1
		return ques


if __name__=="__main__":
	model = parser()
	#model.generateWho(("USS Constitution is a wooden-hulled, three-masted heavy frigate of the U.S. Navy."))
	model.generateWho(("Not like him, my dog also likes eating sausage."))