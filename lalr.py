import copy

class Nonterminal:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Rule:
    def __init__(self, nterm, sequence):
        self.nterm = nterm
        self.sequence = sequence
    
    def __eq__(self, other):
        return self.nterm == other.nterm and self.sequence == other.sequence

class RuleWithDot:
    def __init__(self, rule, lookup='#', position=0):
        self.rule = rule
        self.lookup = lookup
        self.position = position
    
    def __eq__(self, other):
        return self.position == other.position and self.rule == other.rule and self.lookup == other.lookup

    def end(self, positions_before=0):
        return self.position + positions_before >= len(self.rule.sequence)
    
    def at(self, offset=0):
        return self.rule.sequence[self.position + offset]
    
    def accept_here(self, tran):
        cur = self.at()
        return cur == tran[0] and tran[1] == self.lookup
    
    def move(self):
        self.position += 1

    def __str__(self):
        s = ''
        s += self.rule.nterm.name + ' -> '
        for i in range(len(self.rule.sequence)):
            el = self.rule.sequence[i]
            if (i == self.position):
                s += '.'
            if type(el) is str:
                s += el
            else:
                s += el.name
        if self.position == len(self.rule.sequence):
            s += '.'
        s += ',  ' + self.lookup
        return s

class Grammar:
    def __init__(self, rules):
        self.rules = rules

    def first(self, nt, stack=None):
        if type(nt) is str:
            return [nt]
        if stack == None:
            stack = []
        if nt in stack:
            return set()
        stack += [nt]
        f = set()
        for rule in self.rules:
            if rule.nterm == nt:
                seq = rule.sequence
                if len(seq) > 0:
                    el = seq[0]
                    if type(seq[0]) is str:
                        f = f | {el}
                    else:
                        f = f | self.first(el, stack)
        return f
    
    def follow(self, nt, stack=None):
        if stack == None:
            stack = []
        if nt in stack:
            return set()
        stack += [nt]
        f = set()
        for rule in self.rules:
            seq = rule.sequence
            for i in range(len(seq)):
                el = seq[i]
                if el == nt:
                    if i < len(seq) - 1:
                        enext = seq[i + 1]
                        if type(enext) is str:
                            f = f | {enext}
                        else:
                            f = f | self.first(enext)
                    else:
                        f = f | self.follow(rule.nterm, stack)
        return f
    
    def __str__(self):
        s = ''
        for rule in self.rules:
            s += rule.nterm.name + ' -> '
            for el in rule.sequence:
                if type(el) is str:
                    s += el
                else:
                    s += el.name
            s += '\n'
        return s
    
    def terminals(self):
        t = []
        for rule in self.rules:
            for el in rule.sequence:
                if type(el) is str and el not in t:
                    t += [el]
        return t
    
    def nonterminals(self):
        t = []
        for rule in self.rules:
            for el in rule.sequence:
                if type(el) is Nonterminal and el not in t:
                    t += [el]
        return t
    
    def trace(self):
        r = RuleWithDot(self.rules[0], '#')
        sets = [RuleSet(self, [r])]
        trans = []
        terms = self.terminals()
        nterms = self.nonterminals()
        i = 0
        while i < len(sets):
            trans_from = []
            rset = sets[i]
            rset_trans = rset.transitions()
            for rset_tran in rset_trans:
                k = None
                for j in range(len(sets)):
                    if sets[j] == rset_tran[1]:
                        k = j
                        break
                if k == None:
                    k = len(sets)
                    sets += [rset_tran[1]]
                trans_from += [(rset_tran[0], k)]
            trans += [trans_from]
            i += 1
        return (sets, trans)

class RuleSet:
    def __init__(self, grammar, base):
        self.rset = []
        for base_element in base:
            if not base_element in self.rset:
                self.rset += [base_element]
        self.gr = grammar
        self.expand()
    
    def __eq__(self, other):
        return self.rset == other.rset
    
    def expand(self):
        for drule in self.rset:
            if not drule.end():
                t = drule.at()
                if type(t) is Nonterminal:
                    for rule in self.gr.rules:
                        if rule.nterm == t:
                            lookup_set = None
                            if drule.end(1):
                                lookup_set = [drule.lookup]
                            else:
                                lookup_set = self.gr.first(drule.at(1))
                            for lookup in lookup_set:
                                ndrule = RuleWithDot(rule, lookup)
                                if not ndrule in self.rset:
                                    self.rset += [ndrule]
    
    def transitions(self):
        t = self.gr.terminals()
        p = self.gr.nonterminals() + t
        trans = []
        for tran in p:
            if tran == '#':
                continue
            nbase = []
            for drule in self.rset:
                if not drule.end() and drule.at() == tran:
                    moved_drule = copy.copy(drule)
                    moved_drule.move()
                    nbase += [moved_drule]
            if len(nbase) > 0:
                nrset = RuleSet(self.gr, nbase)
                trans += [(tran, nrset)]
        return trans

    def __str__(self):
        s = ''
        for rule in self.rset:
            s += str(rule) + '\n'
        return s

Sp = Nonterminal('S\'')
S = Nonterminal('S')
A = Nonterminal('A')

r = [
    Rule(Sp, [S,'#']),
    Rule(S, [S,'-',A]),
    Rule(S, [A]),
    Rule(A, ['-',S]),
    Rule(A, ['(',S,')']),
    Rule(A, ['(','(',S,')',')']),
    Rule(A, ['1'])
]

G = Grammar(r)

print(r[0].sequence)
print(G.first(S))
print(G.follow(S))
trs = G.trace()

f = open('out.txt', 'w')
for i in range(len(trs[0])):
    f.write('[' + str(i) + ']\n')
    f.write(str(trs[0][i]))
    f.write('\n\n')
    for tr_to in trs[1][i]:
        a = tr_to[0]
        c = tr_to[1]
        f.write(str(a) + '  >->  ' + str(c) + '\n')
    f.write('******\n')
