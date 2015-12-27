import grammarparser
import lrparser

f = open('in.txt', 'r')
gp = grammarparser.GrammarParser(f)
r = gp.parse()
g = lrparser.Grammar(r)
p = lrparser.Parser(g)
res = p.parse("bbca")
if not p.error:
    lrparser.print_res(res)