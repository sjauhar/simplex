#!/usr/bin/env python
# encoding: utf-8
"""
no-change-rankings.py
Created by Sujay Kumar Jauhar on 2011-12-19.
"""

import sys
import getopt
import re
import random
from operator import itemgetter


help_message = '''
$ python scorer.py -i <refFile> -o <outFile> [-h]
-i or --input to specify path to input (gold) responses
-o or --output to specify path to output file
-h or --help (this message is displayed)
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def readCommandLineInput(argv):
	try:
		try:
			#specify the possible option switches
			opts, args = getopt.getopt(argv[1:], "hi:o:", ["help", "input=", "output="])
		except getopt.error, msg:
			raise Usage(msg)
		
		#default values
		inputFile = None
		outFile = None
		verbose = False
		
		# option processing
		for option, value in opts:
			if option in ("-h", "--help"):
				raise Usage(help_message)
			elif option in ("-i", "--input"):
				inputFile = value
			elif option in ("-o", "--out"):
				outFile = value
			else:
				raise Usage(help_message)
				
		if (inputFile==None) or (outFile==None):
			raise Usage(help_message)
		else:
			return (inputFile,outFile)
	
	except Usage, err:
		print str(err.msg)
		return 2


#get the rankings in the gold file
def getSystemRankings(inFile):
	allRankings = []
	#go through the file and extract the (word, score) pairs
	for line in inFile:
		lineParts = line.split()
		words = []
		#give the original substitue a highest possible score of 6 by default
		words.append((lineParts[0].split('.')[0],6))
		subs = line.split(':: ')[1].split(';')
		
		for token in subs[:len(subs)-1]:
			n = len(token)-1
			words.append((token[:n-1],int(token[n])))
			
		allRankings.append(words)
		
	return allRankings

#randomize rankings line by line
def randomizeList(rankingList):
	randomRankList = []
	#go through each list of rankings
	for i in rankingList:
		currentLine = []
		#go through each (word, score) pair
		for item in i:
			#copy word and create new (word, rand_score) pair
			currentLine.append((item[0],random.randint(1,6)))
		
		#sort list according to new rand_score
		currentLineCopy = sorted(currentLine, key=itemgetter(1), reverse=True)
		randomRankList.append(currentLineCopy)
		
	return randomRankList
		

#print in format appropriate for evaluation
def printProper(rankingList, f_Out):
	count = 1
	for i in rankingList:
		flag = 1
		score = 0
		for item in i:
			#according to cases decide whether to club substitutions or not
			if flag:
				f_Out.write('Sentence ' + str(count) + ' rankings: {'+ item[0])
				score = item[1]
				flag = 0
				count += 1
			elif item[1] < score:
				f_Out.write('} {' + item[0])
				score = item[1]
			else:
				f_Out.write(', ' + item[0])
		f_Out.write('}\n')


if __name__ == "__main__":
	#parse command line input
	commandParse = readCommandLineInput(sys.argv)
	#failed command line input
	if commandParse==2:
		sys.exit(2)
	
	#try opening the specified files	
	try:
		systemRespFile = open(commandParse[0])
		outFile = open(commandParse[1], 'w')
	except:
		print "ERROR opening files. One of the paths specified was incorrect."
		sys.exit(2)
	
	#print to file
	printProper(randomizeList(getSystemRankings(systemRespFile)), outFile)