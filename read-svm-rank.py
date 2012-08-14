import sys
from operator import itemgetter

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


allRankings = []
lineRanking = []
curr_qid = 1
#change input filenames
for line1,line2 in zip(open('test-input'),open(sys.argv[1])):
	word = line1.split('#')[1][:-1]
	score = float(line2)
	
	qid = int(line1.split('qid:')[1].split()[0])
	if qid > curr_qid:
		allRankings.append(sorted(lineRanking, key=itemgetter(1), reverse=True))
		lineRanking = [(word,score)]
		curr_qid += 1
	else:
		lineRanking.append((word,score))
		
allRankings.append(sorted(lineRanking, key=itemgetter(1), reverse=True))
#change output file name if wanted
printProper(allRankings,open(sys.argv[2],'w'))