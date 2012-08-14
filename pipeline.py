#!/usr/bin/env python
# encoding: utf-8
"""
combine.py

Created by Sujay Kumar Jauhar on 2012-07-21.
"""

import sys
import getopt
import re
import os
from operator import itemgetter


help_message = '''
$ python pipeline.py -g <goldFileStub> -f <feature1Stub,feature2Stub,etc.> [-c <c-param-value>] [-m <gamma-value>] [-h]
-g or --gold to specify path to gold filename stub
-f or --features to specify path to feature filename stubs (paths are separated by commas)
-c or --c-param to specify the c-parameter used in SVM training
-m or --gamma to specify the gamma parameter used in the rbf kernel of the SVM
-h or --help (this message is displayed)
'''

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def readCommandLineInput(argv):
	try:
		try:
			#specify the possible option switches
			opts, args = getopt.getopt(argv[1:], "hg:f:c:m:", ["help", "gold=", "features=", "c-param=", "gamma"])
		except getopt.error, msg:
			raise Usage(msg)

		#default values
		gold = None
		features = None
		c_param = 1.0
		gamma = 0.1

		# option processing
		for option, value in opts:
			if option in ("-h", "--help"):
				raise Usage(help_message)
			elif option in ("-g", "--gold"):
				gold = value
			elif option in ("-f", "--features"):
				features = value
			elif option in ("-c", "--c-param"):
				c_param = value
			elif option in ("-m", "--gamma"):
				gamma = value
			else:
				raise Usage(help_message)

		if (gold==None) or (features==None):
			raise Usage(help_message)
		else:
			return (gold,features,c_param,gamma)

	except Usage, err:
		print str(err.msg)
		return 2


def getScore(gold, features, c, g):
	gold_trial_string = gold + '-trial'
	gold_test_string = gold + '-test'
	
	feature_stubs = features.split(',')
	trial_feature_string = ''
	test_feature_string = ''
	for feat in feature_stubs:
		trial_feature_string += feat + '-trial '
		test_feature_string += feat + '-test '	
	trial_feature_string = trial_feature_string[:-1]
	test_feature_string = test_feature_string[:-1]
	
	
	os.system('python svm-format-learn.py '+gold_trial_string+' '+trial_feature_string)
	os.system('python svm-format-classify.py '+test_feature_string)
	modelFName = ' model'
	predFName = ' pred'
	outFName = ' out'
	os.system('./svm_learn -z p -t 2 -c '+str(c)+' -g '+str(g)+' model-input'+modelFName+' -v 0 >& log')
	os.system('./svm_classify test-input'+modelFName+predFName+' -v 0 >& log')
	os.system('python read-svm-rank.py'+predFName+outFName)
	print 'Score:', os.popen('python scorer.py -g '+gold_test_string+' -i'+outFName).readline()
	os.system('rm'+modelFName)
	os.system('rm'+predFName)



if __name__ == "__main__":
	#parse command line input
	commandParse = readCommandLineInput(sys.argv)
	#failed command line input
	if commandParse==2:
		sys.exit(2)
	
	getScore(commandParse[0],commandParse[1],commandParse[2],commandParse[3])