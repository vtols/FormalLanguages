import copy

class Nonterminal:
    def __init__(self, name):
        self.name = name

class Rule:
    def __init__(self, nterm, sequence):
        self.nterm = nterm
        self.sequence = sequence
    
    def __eq__(self, other):
        return self.nterm == other.nterm and self.sequence == other.sequence

class RuleWithDot:
    def __init__(self, rule, position=0):
        self.rule = rule
        self.position = position
    
    def __eq__(self, other):
        return self.position == other.position and self.rule == other.rule

    def end(self, positions_before=0):
        return self.position + positions_before >= len(self.rule.sequense)
    
    def at(self, offset=0):
        return drule.rule.sequence[drule.position + offset]
    
    def accept_here(self, gr, tran):
        cur = self.at()
        if cur == tran[0] and not self.end(1):
            after_cur = drule.at(1)
            acc_term_after_cur = False
            if type(after_cur) is str and after_cur == tran[1]:
                acc_term_after_cur = after_cur
            else:
                acc_term_after_cur = tran[1] in gr.follow(after_cur)
            return acc_term_after_cur
        return false
    
    def move(self):
        self.position += 1

class Grammar:
    def __init__(self, rules):
        self.rules = rules

    def first(self, nt, stack=[]):
        if nt in stack:
            return set()
        stack += [nt]
        f = set()
        for rule in self.rules:
            if rule.nterm == nt:
                seq = rule.sequence
                for el in seq:
                    if type(el) is str:
                        f = f | {el}
                    else:
                        f = f | self.first(el, stack)
        return f
    
    def follow(self, nt, stack=[]):
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
                if type(el) is str:
                    t += [el]
        return t
    
    def nonterminals(self):
        t = []
        for rule in self.rules:
            for el in rule.sequence:
                if type(el) is Nonterminal:
                    t += [el]
        return t
    
    def trace(self):
        r = RuleWithDot(self.rules[0])
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
                    sets += rset_tran[1]
                trans_from += [(rset_tran[0], k)]
            trans += [trans_from]
            i += 1
        return (sets, trans)

class RuleSet:
    def __init__(self, grammar, base):
        self.rset = []
        for base_element in base:
            if not base_element in base:
                base += [base_element]
        self.gr = grammar
        self.expand()
    
    def __eq__(self, other):
        return self.rset == other.rset
    
    def expand(self):
        for drule in self.rset:
            if not drule.end():
                t = drule.at()
                if type(t) is Nonterminal:
                    for rule in self.gr.rules and rule.nterm == t:
                        ndrule = RuleWithDot(rule)
                        if not ndrule in self.rset:
                            self.rset += [RuleWithDot(rule)]
    
    def transitions(self):
        t = self.gr.terminals()
        p = t + self.gr.nonterminals()
        trans = []
        for fst in p:
            for snd in t:
                nbase = []
                tran = (fst, snd)
                for drule in self.rset:
                    if not drule.end() and drule.accept_here(self.gr, tran):
                        moved_drule = copy.copy(drule)
                        moved_drule.move()
                        nbase += moved_rule
                nrset = RuleSet(self.gr, nbase)
                trans += [(tran, nrset)]
        return trans

Sp = Nonterminal('S\'')
S = Nonterminal('S')
A = Nonterminal('A')

r = [
    Rule(Sp, [S]),
    Rule(S, [S,'-',A]),
    Rule(S, [A]),
    Rule(A, ['-',S]),
    Rule(A, ['(',S,')']),
    Rule(A, ['(','(',S,')',')']),
    Rule(A, ['1'])
]

G = Grammar(r)

print(r[0].sequence)
print(G.follow(A))
print(G.trace())
