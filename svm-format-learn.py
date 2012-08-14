import re
import sys

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
				currentContextRanking[word] = counter + 1
			rest = match.group(2)
			counter += 1
		
		allContextRankings.append(currentContextRanking)
		
	return allContextRankings


gold = getSystemRankings(open(sys.argv[1]))

features = []
for i in range(2,len(sys.argv)):
	features.append(getSystemRankings(open(sys.argv[i])))
	
feature_vals = []
for i in range(len(features[0])):
	current_val = []
	for f in features:
		current_val.append(f[i])
	feature_vals.append(current_val)

f_Out = open('model-input','w')

qid = 0
for g,fs in zip(gold,feature_vals):
	qid += 1
	for key in g:
		lineOut = str(1/float(g[key])) + ' qid:' + str(qid) + ' '
		f_count = 0
		for f in fs:
			f_count += 1
			lineOut += str(f_count) + ':' + str(1/float(f[key])) + ' '
		lineOut += '#' + key
		f_Out.write(lineOut + '\n')
		
f_Out.close()