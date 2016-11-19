import sys
import re
from nltk.corpus import wordnet
from functools import reduce
EPS = 1e-8



def ManageInput(lined_tokens, org_sentence, T):
	line_num = 1
	before_sentence = True
	print('Stemmer:')
	pattern = re.compile('[A-Z]+[a-zA-Z]*|[a-z]+|\d*\.\d*|[^ \t\r\n]')
	line = sys.stdin.readline()
	while line:
		Split = re.findall(pattern, line)
		for token in Split:
			if token == '#':
				break

			if before_sentence:
				if token.isalpha():
					if token.islower():
						T[token] = 0
					print(token, 'STRING', line_num)

				elif token[0].isdigit() or token[-1].isdigit():
					if '.' in token:
						print(token, 'DOUBLE', line_num)
					else:
						print(token, 'INT', line_num)

				else:
					print(token, 'OP', line_num)
					if token == ';':
						lined_tokens.append([])
						continue
					if token == '|':
						lined_tokens.append(lined_tokens[-1][:2])
						continue

					if token == '=' and lined_tokens[-1] and lined_tokens[-1][-1].lower() == 'w':
						before_sentence = False
						lined_tokens[-1].pop()
						if not lined_tokens[-1]:
							lined_tokens.pop()
						continue
					elif token == '=':
						sys.exit("error: wrong input form (arround '=')")

				lined_tokens[-1].append(token)

			elif token.isalpha():
				org_sentence.append((token, line_num))
				

		line_num += 1
		line = sys.stdin.readline()




def NormalizeGrammar(lined_tokens, NT):
	# convert to NT: NT NT prob
	new_grammar = []
	for i in range(len(lined_tokens)):
		while len(lined_tokens[i]) > 5:
			appendix = 'a'
			while lined_tokens[i][3] + appendix in NT:
				appendix = chr(ord(appendix) + 1)
			new_NT = lined_tokens[i][3] + appendix
			NT[new_NT] = 0
			new_grammar.append(lined_tokens[i][:3] + [new_NT] + [lined_tokens[i][-1]])
			lined_tokens[i] = [new_NT, ':'] + lined_tokens[i][3:-1] + ['1.0']

	lined_tokens.extend(new_grammar)

	new_grammar = []
	start = 0
	while True:
		for i in range(start, len(lined_tokens)):
			if len(lined_tokens[i]) > 4:
				# if NT:NT T prob, convert to NT: NT NT prob
				for j in range(2, len(lined_tokens[i]) - 1):
					if lined_tokens[i][j].islower():
						appendix = 'a'
						while lined_tokens[i][j].upper() + appendix in NT:
							appendix = chr(ord(appendix) + 1)
						new_NT = lined_tokens[i][j].upper() + appendix
						NT[new_NT] = 0
						new_grammar.append([new_NT, ':', lined_tokens[i][j],'1.0'])
						lined_tokens[i][j] = new_NT

			if len(lined_tokens[i]) == 4 and not lined_tokens[i][2].islower():
				# if NT: NT prob, convert to NT: T or NT: NT NT
				# print(lined_tokens[i])
				find = False
				for each_grammar in lined_tokens:
					if each_grammar and each_grammar[0] == lined_tokens[i][2]:
						new_grammar.append(lined_tokens[i][:2] + each_grammar[2:-1] + \
							[str(float(lined_tokens[i][-1]) * float(each_grammar[-1]))])
						find = True
				if not find:
					sys.exit("error: missing rule for '" + lined_tokens[i][2]+ "' (or wrong input form)")
				lined_tokens[i] = []
		if new_grammar:
			start = len(lined_tokens)
			lined_tokens.extend(new_grammar)
		else:
			break
		new_grammar = []



def GeneLexSyn(lex, syn, lined_tokens, NT, T):
	re_lex = re.compile("^[A-Z]+[a-zA-Z]* : [a-z]+ \d+\.?\d*|[A-Z]+[a-z]* : [a-z]+ \.\d+$")
	re_syn = re.compile("^[A-Z]+[a-zA-Z]* : ([A-Z]+[a-z]* ){2}\d+\.?\d*|[A-Z]+[a-z]* : ([A-Z]+[a-z]* ){2}\.\d+$")

	for each_grammar in lined_tokens:
		if each_grammar:
			cur_grammar = ' '.join(each_grammar)
			if re_lex.match(cur_grammar):
				a, b, prob = each_grammar[0], each_grammar[2], float(each_grammar[3])
				if a not in lex:
					lex[a] = dict()
				if b in lex[a]:
					sys.exit("error: duplicate lex grammar: " + cur_grammar)
				lex[a][b] = prob
				T[b] = max(T[b], prob)
			
			elif re_syn.match(cur_grammar):
				a, b, c, prob = each_grammar[0], each_grammar[2], each_grammar[3], float(each_grammar[4])
				if a not in syn:
					syn[a] = dict()
				if b not in syn[a]:
					syn[a][b] = dict()
				if c in syn[a][b]:
					sys.exit("error: duplicate syn grammar: " + cur_grammar)
				syn[a][b][c] = prob
			else:
				sys.exit("error: Wrong grammar: " + cur_grammar + ' (or wrong input form)')

			NT[each_grammar[0]] += float(each_grammar[-1])	# add prob to NT

	for key in NT:
		if abs(NT[key]) < EPS:
			sys.exit("error: missing rule for '" + key + "' (or wrong input form)")
		if abs(NT[key] - 1.0) > EPS:
			sys.exit(key + " not sum up to 1.0" + '(or wrong input form)')



def ManageSentence(org_sentence, sentence, T):
	for word, line_num in org_sentence:
		roots = set(wordnet._morphy(word.lower(), wordnet.NOUN) + \
			    wordnet._morphy(word.lower(), wordnet.VERB))
		if not roots:
			roots.add(word.lower())

		for root in roots:
			if root in T:
				break
		else:
			sys.exit("error: missing rule for '" + word + "' (or wrong input form)")
		
		if {word} != roots:
			print(word, 'STRING', ' '.join(roots), line_num)
		else:
			print(word, 'STRING', line_num)
		sentence.append(roots)

	print('ENDFILE\n\n')



class resultInfo(object):
	def __init__(self, sentence_idx, right_NT1, right_NT2):
		self.right_NT1 = right_NT1
		self.right_NT2 = right_NT2
		self.sentence_idx = sentence_idx



def viterbi(NT, sentence, lex, syn, delta, chart):	
	for i in range(len(sentence)):
		for a in NT:
			delta[(i, i, a)] = max([lex.get(a, dict()).get(word, 0) for word in sentence[i]])

	for span in range(1, len(sentence)):
		for begin in range(len(sentence) - span):
			end = begin + span		
			#print(begin, end)
			for middle in range(begin, end):
				for a in syn.keys():
					for b in syn[a].keys():
						for c in syn[a][b].keys():
							p = syn[a][b][c] * delta.get((begin, middle, b), 0)* delta.get((middle + 1, end, c), 0)
							if p > delta.get((begin, end, a), 0):
								delta[(begin, end, a)] = p
								chart[(begin, end, a)] = resultInfo(middle, b, c)
	'''	
	print('delta:')
	for key in sorted(delta.keys()):
		print(key, ':', delta[key])
	

	print('chart:')
	for key in sorted(chart.keys()):
		print(key, ':', chart[key].sentence_idx, chart[key].right_NT1, chart[key].right_NT2)
	'''



def dump_tree(delta, chart, stat, end, NT, lex, syn, org_sentence):
	try:
		stack = [max([(stat, end, Non_terminal, 0) for Non_terminal in NT if (stat, end, Non_terminal) in delta], key = lambda key: delta[key[:-1]])]
	except Exception:
		sys.exit("Abort! \nSorry, can not parse correctly, maybe check the grammar or stemmer? \n"
			  "You know this program is not 100 percent garanted")
	
	prob = []
	while stack:
		cur_begin, cur_end, cur_left_NT, hight = stack.pop()
		if (cur_begin, cur_end, cur_left_NT) in chart:
			cur_info = chart[(cur_begin, cur_end, cur_left_NT)]
		else:
			sys.exit("Abort! \nSorry, can not parse correctly, maybe check the grammar or stemmer? \n"
			  "You know this program is not 100 percent garanted")

		print(' | ' * hight, cur_left_NT, syn[cur_left_NT][cur_info.right_NT1][cur_info.right_NT2])
		prob.append(str(syn[cur_left_NT][cur_info.right_NT1][cur_info.right_NT2]))

		if cur_begin == cur_info.sentence_idx:
			print(' | ' * (hight + 1), cur_info.right_NT1, delta[(cur_begin, cur_begin, cur_info.right_NT1)])
			prob.append(str(delta[(cur_begin, cur_begin, cur_info.right_NT1)]))
			print(' | ' * (hight + 2), org_sentence[cur_begin][0])
		
		if cur_end - cur_info.sentence_idx == 1:
			print(' | ' * (hight + 1), cur_info.right_NT2, delta[(cur_end, cur_end, cur_info.right_NT2)])
			prob.append(str(delta[(cur_end, cur_end, cur_info.right_NT2)]))
			print(' | ' * (hight + 2), org_sentence[cur_end][0])
		
		if cur_end - cur_info.sentence_idx != 1:
			stack.append((cur_info.sentence_idx + 1, cur_end, cur_info.right_NT2, hight + 1))
		
		if cur_begin != cur_info.sentence_idx:
			stack.append((cur_begin, cur_info.sentence_idx, cur_info.right_NT1, hight + 1))

	print('P(W) =', " * ".join(prob), "=", reduce(lambda x,y: float(x) * float(y) ,prob))





