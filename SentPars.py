import ParsFunc



# read input, split it into tokens 
# store the grammar part in lined_tokens[] seperate each line by ';'
# store the word in sentence into org_sentence[]
# generate Terminal while scanning

lined_tokens = [[]]
org_sentence = []
T = dict()

ParsFunc.ManageInput(lined_tokens, org_sentence, T)

# generate Non-terminal NT[] from grammar (lined_tokens)

NT = dict()

for line in lined_tokens:
	for token in line:
		if token.isalpha() and not token.islower():
			NT[token] = 0


# rewrite grammar to regular form
# note: rule for name new_NT not perfect, need improve


ParsFunc.NormalizeGrammar(lined_tokens, NT)


# check bad input using regular expression
# generate paragram lex, syn for later use
# check if all prob for each NT add up to 1.0
# store the prob for each Terminal in T[]

lex, syn = dict(), dict()

ParsFunc.GeneLexSyn(lex, syn, lined_tokens, NT, T)

# use stemmer generate roots for each word in org_sentence 
# check if the roots has intersection with T[], if not exit exc
# store roots in sentence[]
# print the result

sentence = []

ParsFunc.ManageSentence(org_sentence, sentence, T)


# generate result using viterbi algorithm
# when generate delta, if sentence[i] has more than one word, 
# choose the word with highest prob

delta = {}
chart = {}
ParsFunc.viterbi(NT, sentence, lex, syn, delta, chart)


# print output in tree form and final prob for parsing

ParsFunc.dump_tree(delta, chart, 0, len(sentence) - 1, NT, lex, syn, org_sentence)


