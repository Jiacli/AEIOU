#!/usr/bin/python
from __future__ import division
import string
import re
from collections import Counter
import os
import sys
import math

class interpolateModel:

	def __init__(self):
		argu = sys.argv
		self.lambda0 = 0.25
		self.lambda1 = 0.25
		self.lambda2 = 0.25
		self.lambda3 = 0.25
		self.unigram = dict()
		self.bigram = dict()
		self.trigram = dict()
		self.source = '../data/testing/'
		self.dev = 'dev/'
		self.train = 'train/'
		self.traindest = 'trainprocessed/'
		self.devdest = 'devprocessed/'
		self.threshold = 1e-10
		self.LM = 'LM/'
		self.param = 'config'
		self.wordNum = 0
		self.readPrameter()

	def readPrameter(self):
		model = open(self.source+self.LM+'unigram', 'r')
		self.wordNum = int(model.readline())
		for words in model:
			unigram = words.strip().split('_')
			if len(unigram) == 1:
				continue
			self.unigram[unigram[0]] = int(unigram[1])

		model = open(self.source+self.LM+'bigram', 'r')
		for words in model:
			bigram = words.split('_')
			if len(bigram) == 1:
				continue
			self.bigram[bigram[0]] = int(bigram[1])

		model = open(self.source+self.LM+'trigram', 'r')
		for words in model:
			trigram = words.split('_')
			if len(trigram) == 1:
				continue
			self.trigram[trigram[0]] = int(trigram[1])

		param = open(self.source+self.LM+self.param, 'r')
		argu = param.readline().split(' ')
		self.lambda0 = float(argu[0])
		self.lambda1 = float(argu[1])
		self.lambda2 = float(argu[2])
		self.lambda3 = float(argu[3])

	def countTokens(self):
		# discover stopwords
		total = Counter()
		allWord = []
		filter = [];
		for root, dirnames, filenames in os.walk(self.source+self.train):
			for filename in filenames:
				path = self.source+self.train+filename
				srcfile = open(path, 'r')

				for para in srcfile:
					words = re.split(r' ', para)
					total = total + Counter(words)
					allWord += words

		for word in total:
			if(total[word] <= 2):
				filter.append(word)		
		
		# substitute stopwords with UNKNOWNWORD in the training files
		for root, dirnames, filenames in os.walk(self.source+self.train):
			for filename in filenames:
				srcfile = open(self.source+self.train+filename, 'r')
				dstfile = open(self.source+self.traindest+filename, 'w', os.O_RDWR | os.O_CREAT)
				for para in srcfile:
					index = 0
					words = re.split(r' ', para)
					for word in words:
						#print word
						if word in filter:
							words[index] = 'UNKNOWNWORD'
						index = index + 1

					allText = ' '.join(words)
					dstfile.write('<START> '+'<START> '+allText.strip()+' <END>'+'\n')
				srcfile.close()	
				dstfile.close()

		# substitute stopwords with UNKNOWNWORD in the testing files
		for root, dirnames, filenames in os.walk(self.source+self.dev):
			for filename in filenames:
				srcfile = open(self.source+self.dev+filename, 'r')
				dstfile = open(self.source+self.devdest+filename, 'w', os.O_RDWR | os.O_CREAT)
				for para in srcfile:
					index = 0
					words = re.split(r' ', para)
					for word in words:
						#print word
						if word not in allWord:
							words[index] = 'UNKNOWNWORD'
						index = index + 1

					allText = ' '.join(words)
					dstfile.write('<START> '+'<START> '+allText.strip()+' <END>'+'\n')
				srcfile.close()	
				dstfile.close()


	def countWords(self, temp, gram):
		if(temp not in gram):				
			gram[temp] = 1
		else:
			gram[temp] = gram[temp]+1

	def countNgrams(self, unigram, bigram, trigram):
		wordNum = 0
		startnum = 0;

		# count the number of each ngram
		for root, dirnames, filenames in os.walk(self.source+self.traindest):
			for filename in filenames:
				path = self.source+self.traindest+filename
				textLine = open(path, 'r')
				for words in textLine:
					startnum += 1
					words = re.split(r' ', words)
					for index in range(2, len(words)):
						wordNum += 1
						unitemp = words[index]
						self.countWords(unitemp, unigram)

						bitemp = words[index-1]+' '+words[index]
						self.countWords(bitemp, bigram)

						tritemp = words[index-2]+' '+words[index-1]+' '+words[index]
						self.countWords(tritemp, trigram)

		unigram['<START>'] = startnum
		bigram['<START> <START>'] = startnum
		return wordNum

	def testPerplexity(self, unigram, bigram, trigram, wordNum):
		perplexity = 0.0
		perpUniform = 0.0
		perpUnigram = 0.0
		perpBigram = 0.0
		perpTrigram = 0.0
		totallen = 0
		unilen = len(unigram)
		bilen = len(bigram)
		trilen = len(trigram)

		for root, dirnames, filenames in os.walk(self.source+self.devdest):
			for filename in filenames:
				textLine = open(self.source+self.devdest+filename, 'r')

				# compute the compleixty of testing file
				for words in textLine:
					words = re.split(r' ', words)
					length = len(words)
					for index in range(2, length):
						totallen = totallen + 1
						unitemp = words[index]
						bitemp = words[index-1]+' '+words[index]
						bipi = words[index-1]
						tritemp = words[index-2]+' '+words[index-1]+' '+words[index]
						tripi = words[index-2]+' '+words[index-1]

						interProb = self.lambda0/unilen
						perpUniform += math.log(self.lambda0/unilen)
						if(unitemp in unigram):
							interProb += self.lambda1*unigram[unitemp]/wordNum
							perpUnigram += math.log(self.lambda1*unigram[unitemp]/wordNum)
						if(bitemp in bigram):
							interProb += self.lambda2*bigram[bitemp]/unigram[bipi]
							perpBigram += math.log(self.lambda2*bigram[bitemp]/unigram[bipi])
						if(tritemp in trigram):
							interProb += self.lambda3*trigram[tritemp]/bigram[tripi]
							perpTrigram += math.log(self.lambda3*trigram[tritemp]/bigram[tripi])
						perplexity += math.log(interProb)

		#perplexity = math.exp(-perplexity/totallen)
		#print perplexity
		return [perplexity, perpUniform, perpUnigram, perpBigram, perpTrigram]

	def estimateParameter(self, unigram, bigram, trigram, wordNum):
		perplexity = 0.0
		[perplexity1, perpUniform, perpUnigram, perpBigram, perpTrigram] = self.testPerplexity(unigram, bigram, trigram, wordNum)
		print perplexity1
		# while True:
		while math.fabs(perplexity1-perplexity)/math.fabs(perplexity1) > self.threshold:
			self.lambda0 = perpUniform / perplexity1
			self.lambda1 = perpUnigram / perplexity1
			self.lambda2 = perpBigram / perplexity1
			self.lambda3 = perpTrigram / perplexity1
			perplexity = perplexity1
			[perplexity1, perpUniform, perpUnigram, perpBigram, perpTrigram] = self.testPerplexity(unigram, bigram, trigram, wordNum)
			print perplexity1

		model = open(self.source+self.LM+'unigram', 'w', os.O_RDWR | os.O_CREAT)
		model.write(str(wordNum)+'\n')
		for gram in unigram:
			model.write(gram+'_'+str(unigram[gram])+'\n')

		model = open(self.source+self.LM+'bigram', 'w', os.O_RDWR | os.O_CREAT)
		for gram in bigram:
			model.write(gram+'_'+str(bigram[gram])+'\n')

		model = open(self.source+self.LM+'trigram', 'w', os.O_RDWR | os.O_CREAT)
		for gram in trigram:
			model.write(gram+'_'+str(trigram[gram])+'\n')

		param = open(self.source+self.LM+self.param, 'w', os.O_RDWR | os.O_CREAT)
		param.write(str(self.lambda0)+' '+ str(self.lambda1)+' '+str(self.lambda2)+' '+str(self.lambda3))
		print self.lambda0, self.lambda1, self.lambda2, self.lambda3



	def sentencePerp(self, str):
		# print 'sentence: ' +str
		str = '<START> <START> '+str+' <END>'
		perplexity = 0.0
		totallen = 0
		unilen = len(self.unigram)
		unilen = len(self.bigram)
		trilen = len(self.trigram)

		words = re.split(r' ', str)
		length = len(words)
		for index in range(2, length):
			totallen = totallen + 1
			unitemp = words[index]
			bitemp = words[index-1]+' '+words[index]
			bipi = words[index-1]
			tritemp = words[index-2]+' '+words[index-1]+' '+words[index]
			tripi = words[index-2]+' '+words[index-1]

			interProb = self.lambda0/unilen
			if(unitemp in self.unigram):
				interProb += self.lambda1*self.unigram[unitemp]/self.wordNum
			if(bitemp in self.bigram):
				interProb += self.lambda2*self.bigram[bitemp]/self.unigram[bipi]
			if(tritemp in self.trigram):
				interProb += self.lambda3*self.trigram[tritemp]/self.bigram[tripi]
			perplexity += math.log(interProb)

		perplexity = math.exp(-perplexity/totallen)

		return perplexity

def main():
	model = interpolateModel()
	#preprocess
	model.countTokens()
	
	unigram = Counter()
	bigram = Counter()
	trigram = Counter()

	# training process
	print 'training file:'
	wordNum = model.countNgrams(unigram, bigram, trigram)

	#testing process
	print 'testing file:'
	model.estimateParameter(unigram, bigram, trigram, wordNum)

if __name__ == "__main__":
	main()
	# model = interpolateModel()
	# print "Who also likes eating sausage ?\nperplexity:"
	# print model.sentencePerp("What is the seat of the United Arab Emirates Government ?")
	# print ""
	# print "What also likes eating sausage ?\nperplexity:"
	# print model.sentencePerp(" is the seat of the United Arab Emirates Government ?")
	# print ""
	# print "proper population The city had a of 921,000 in 2013.\nperplexity:"
	# print model.sentencePerp("proper population The city had a of 921,000 in 2013.")
