#!/usr/bin/env python
# encoding: utf-8
"""
scorer.py
Created by Sujay Kumar Jauhar on 2011-11-27.
"""

import sys
import getopt
import re
import itertools


help_message = '''
$ python scorer.py -i <systemFile> -g <goldFile> [-v] [-h]
-i or --input to specify path to system generated responses
-g or --gold to specify path to gold file
-v or --verbose to set verbose to True (verbose is False by default)
-h or --help (this message is displayed)
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def readCommandLineInput(argv):
	try:
		try:
			#specify the possible option switches
			opts, args = getopt.getopt(argv[1:], "hi:g:v", ["help", "input=", "gold=", "verbose"])
		except getopt.error, msg:
			raise Usage(msg)
		
		#default values
		inputFile = None
		goldFile = None
		verbose = False
		
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			elif option in ("-h", "--help"):
				raise Usage(help_message)
			elif option in ("-i", "--input"):
				inputFile = value
			elif option in ("-g", "--gold"):
				goldFile = value
			else:
				raise Usage(help_message)
				
		if (inputFile==None) or (goldFile==None):
			raise Usage(help_message)
		else:
			return (inputFile,goldFile,verbose)
	
	except Usage, err:
		print str(err.msg)
		return 2

#function to read system produced ranking file
def getSystemRankings(file):
	#pattern to recognize rankings in output file
	pattern = re.compile('.*?\{(.*?)\}(.*)')
	
	#extract rankings
	allContextRankings = []
	for line in file:
		rest = line
		currentContextRanking = {}
		counter = 0
		while rest:
			match = pattern.search(rest)
			currentRank = match.group(1)
			individualWords = currentRank.split(', ')
			for word in individualWords:
				word = re.sub('\s$','',word)
				currentContextRanking[word] = counter
			rest = match.group(2)
			counter += 1
		
		allContextRankings.append(currentContextRanking)
		
	return allContextRankings

#comparator function
def compare(val1, val2):
	if (val1 < val2):
		return -1
	elif (val1 > val2):
		return 1
	else:
		return 0

#function to score system with reference to gold
#function is based on kappa with rank correlation
def getScore(system, gold, verbose):
	
	#intialize vars
	totalPairCount = 0
	agree = 0
	equalAgree = 0
	#greaterAgree = 0
	#lesserAgree = 0
	
	contextCount = 0
	#go through contexts parallely
	for (sysContext, goldContext) in zip(system, gold):
		contextCount += 1
		if verbose:
			print 'Looking at context', contextCount
		#go through each combination of substitutions
		for pair in itertools.combinations(sysContext.keys(), 2):
			totalPairCount += 1
			#find ranking order given by system and gold for current pair
			sysCompareVal = compare(sysContext[pair[0]],sysContext[pair[1]])
			goldCompareVal = compare(goldContext[pair[0]],goldContext[pair[1]])
			
			#print verbose information
			if verbose:
				print '\tCurrent pair of words: "' + pair[0] + '" & "' + pair[1] + '"'
				print '\t\tSystem says rank of: "' + pair[0] + '" is',
				if sysCompareVal == -1:
					print 'lesser than "' + pair[1] + '"'
				elif sysCompareVal == 1:
					print 'greater than "' + pair[1] + '"'
				else:
					print 'equal to "' + pair[1] + '"'
					
				print '\t\tGold says rank of: "' + pair[0] + '" is',
				if goldCompareVal == -1:
					print 'lesser than "' + pair[1] + '"'
				elif goldCompareVal == 1:
					print 'greater than "' + pair[1] + '"'
				else:
					print 'equal to "' + pair[1] + '"'
			
			#system and gold agree
			#add appropriate counts to agree count
			if (sysCompareVal) == (goldCompareVal):
				agree += 1
				if verbose:
					print "\tAgreement count incremented by 1"
					
			#add count if at least one of them tied candidate pair
			if sysCompareVal == 0:
					equalAgree += 1
					if verbose:
						print "\tEqualTo count incremented by 1"
			if goldCompareVal == 0:
					equalAgree += 1
					if verbose:
						print "\tEqualTo count incremented by 1"
						
			if verbose:
				print '\n'
	
	equalAgreeProb = float(equalAgree)/float(totalPairCount*2)
	
	#P(A) and P(E) values	
	absoluteAgreement = float(agree)/float(totalPairCount)
	chanceAgreement = (3*pow(equalAgreeProb,2)-2*equalAgreeProb+1.0)/2.0
	
	#return kappa score
	return (absoluteAgreement - chanceAgreement)/(1.0 - chanceAgreement)
	

if __name__ == "__main__":
	#parse command line input
	commandParse = readCommandLineInput(sys.argv)
	#failed command line input
	if commandParse==2:
		sys.exit(2)
	
	#try opening the specified files	
	try:
		systemRespFile = open(commandParse[0])
		goldFile = open(commandParse[1])
	except:
		print "ERROR opening files. One of the paths specified was incorrect."
		sys.exit(2)
	
	#get system rankings and store in structure
	systemRankings = getSystemRankings(systemRespFile)
	goldRankings = getSystemRankings(goldFile)
	
	if len(systemRankings) == len(goldRankings):
		score = getScore(systemRankings, goldRankings, commandParse[2])
	else:
		score = -2.0
	
	print 'Normalized system score:', score
