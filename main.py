import grammarparser
import lrparser

f = open('in.txt', 'r')
gp = grammarparser.GrammarParser(f)
r = gp.parse()
print(r)
