import grammarparser
import lrparser
import io

str_grammar = ('S : A "b" | B "a" | S S;\n'
               'A : "b";\n'
               'B : "c";\n')
str_io = io.StringIO(str_grammar)
grparser = grammarparser.GrammarParser(str_io)
rules = grparser.parse()
grammar = lrparser.Grammar(rules)
parser = lrparser.Parser(grammar)
result = parser.parse("bbca")
if not parser.error:
    lrparser.print_res(result)