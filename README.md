# Sentence-Parser

This program will read a probabilistic/stochastic context free grammar (PCFG) and a sentence (format see below) as input, and generate the most likely parsing of this sentence using the Viterbi algorithm and dump the syntax tree.

This program will scan the input and divide into tokens. The output contains one token per line including the token (as string), its type (INT, DOUBLE, STRING, OP, or ENDFILE), line number where the token appears, and the base form if not the same as the token.

Example Input:
S : NP VP 1.0;  
NP : NP PP 0.4  
| astronomer 0.1   
| ear 0.18  
| saw 0.04  
| star 0.18  
| telescope 0.1;   
PP : P NP 1.0;  
VP : V NP 0.7  
| VP PP 0.3;   
P : with 1.0;  
V : see 1.0;  
W = Astronomers saw stars with ears.  

Example Output:  
Stemmer:  
S STRING 1  
: OP 1  
NP STRING 1  
VP STRING 1  
1.0DOUBLE 1  
; OP 1  
...  
Astronomers STRING 13 astronomer   
saw STRING 13 see saw  
stars STRING 13 star  
with STRING 13  
ears STRING 13 ear  
. OP 13  
ENDFILE  

Parsed Tree:  
S 1.0  
| NP 0.1  
| | Astronomers | VP 0.7  
| | V 1.0  
| | | saw  
| | NP 0.4  
| | | NP 0.18  
| | | | stars  
| | | PP 1.0  
| | | | P 1.0  
| | | | | with  
| | | | NP 0.18  
| | | | | ears  
P(W) = 1.0 * 0.1 * 0.7 * 1.0 * 0.4 * 0.18 * 1.0 * 1.0 * 0.18 = 0.0009072  
