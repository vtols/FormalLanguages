import lrparser

def char_range(a, b):
    return list(map(chr, list(range(ord(a),ord(b)+1))))

class GrammarLexer:

    Eof = 0
    Id = 1
    Colon = 2
    Bar = 3
    Semicolon = 4
    Str = 5
    
    wh = [' ', '\t', '\n']
    letters = char_range('a', 'z') + char_range('A', 'Z') 

    def __init__(self, f):
        self.f = f
        self.c = ''
        self.move()
        self.token()
    
    def clear(self):
        self.value = ''

    def move(self):
        if self.c:
            self.value += self.c
        self.c = self.f.read(1)

    def token(self):
        while self.c in GrammarLexer.wh:
            self.move()
        if not self.c:
            self.tok = GrammarLexer.Eof
            self.value = None
            return
        self.clear()
        if self.c == '"':
            self.move()
            while self.c != '"':
                self.move()
            self.move()
            self.tok = GrammarLexer.Str
        elif self.c == ';':
            self.move()
            self.tok = GrammarLexer.Semicolon
        elif self.c == ':':
            self.move()
            self.tok = GrammarLexer.Colon
        elif self.c == '|':
            self.move()
            self.tok = GrammarLexer.Bar
        elif self.c in GrammarLexer.letters:
            self.move()
            while self.c in GrammarLexer.letters + ['_']:
                self.move()
            self.tok = GrammarLexer.Id

class GrammarParser:
    def __init__(self, f):
        self.lex = GrammarLexer(f)
        self.rules = []
        self.nterms = dict()

    def parse(self):
        while self.lex.tok != GrammarLexer.Eof:
            self.rules += self.parse_rules()
        return self.rules

    def current(self):
        return self.lex.tok

    def lookup_id(self):
        value = self.match(GrammarLexer.Id)
        if value not in self.nterms:
            self.nterms[value] = lrparser.Nonterminal(value)
        return self.nterms[value]

    def match(self, tok):
        v = self.lex.value
        if tok == self.lex.tok:
            self.lex.token()
            return v
        return None

    def parse_rules(self):
        self.nt = self.lookup_id()
        self.match(GrammarLexer.Colon)
        rules = []
        while True:
            rules += [self.parse_rule()]
            if self.current() == GrammarLexer.Bar:
                self.match(GrammarLexer.Bar)
            else:
                self.match(GrammarLexer.Semicolon)
                break
        return rules

    def parse_rule(self):
        seq = []
        while True:
            if self.current() == GrammarLexer.Id:
                seq += [self.lookup_id()]
            elif self.current() == GrammarLexer.Str:
                seq += [self.match(GrammarLexer.Str)]
            else:
                break
        print(seq)
        return lrparser.Rule(self.nt, seq)
