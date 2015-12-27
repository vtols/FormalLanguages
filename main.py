import grammarparser
import lrparser
import sys

if __name__ == "__main__":
    fgrammar = open(sys.argv[1], 'r')
    finput = open(sys.argv[2], 'r')

    grparser = grammarparser.GrammarParser(fgrammar)
    rules = grparser.parse()

    grammar = lrparser.Grammar(rules)

    parser = lrparser.Parser(grammar)
    result = parser.parse(''.join(finput.readlines()))
    if not parser.error:
        lrparser.print_res(result)
