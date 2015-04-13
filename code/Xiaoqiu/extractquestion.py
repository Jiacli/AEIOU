import json
import re

question = open('../data/questions', 'r')
result = dict()

for sentence in question:
	list = sentence.split(", ")
	print list[3].split(": ")[1][2:-2]+' ?'