import copy

class Singleton(type):
    obj = None
    def __call__(self, *args, **kwargs):
        if Singleton.obj is None:
            Singleton.obj = type.__call__(self, *args)
        return Singleton.obj

class End(metaclass=Singleton):
    pass

class Empty(metaclass=Singleton):
    pass

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
    def __init__(self, rule, lookup=End(), position=0):
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
            elif type(el) is End:
                s += '$'
            else:
                s += el.name
        if self.position == len(self.rule.sequence):
            s += '.'
        if self.lookup == End():
            s += ',  $'
        else:
            s += ',  ' + self.lookup
        return s

class Grammar:
    def __init__(self, rules, start=None):
        if start is None:
            start = rules[0].nterm
        self.rules = [Rule(Nonterminal(''), [start, End()])] + rules

    def first(self, nt, stack=None):
        if type(nt) in [str, End]:
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
                        if type(enext) in [str, End]:
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
                if type(el) is End:
                    s += '$'
                else:
                    s += el.name
            s += '\n'
        return s
    
    def terminals(self):
        t = set()
        for rule in self.rules:
            for el in rule.sequence:
                if type(el) in [str, End]:
                    t |= {el}
        return list(t)
    
    def nonterminals(self):
        t = set()
        for rule in self.rules:
            for el in rule.sequence:
                if type(el) is Nonterminal:
                    t |= {el}
        return list(t)

    def items(self):
        r = RuleWithDot(self.rules[0], End())
        sets = [RuleSet(self, [r])]
        terms = self.terminals()
        nterms = self.nonterminals()
        i = 0
        while i < len(sets):
            goto_sets = sets[i].goto_all()
            for goto_set in goto_sets:
                if goto_set not in sets:
                    sets += [goto_set]
            i += 1
        return sets

class RuleSet:
    def __init__(self, grammar, base):
        self.rset = []
        for base_element in base:
            if not base_element in self.rset:
                self.rset += [base_element]
        self.gr = grammar
        self.make_closure()
    
    def __eq__(self, other):
        return self.rset == other.rset
    
    def make_closure(self):
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

    def goto_all(self):
        t = self.gr.terminals()
        p = self.gr.nonterminals() + t
        trans = []
        for tran in p:
            if tran != End():
                go = self.goto(tran)
                if go is not None:
                    trans += [go]
        return trans

    def goto(self, x):
        goto_set = None
        if x != End():
            nbase = []
            for drule in self.rset:
                if not drule.end() and drule.at() == x:
                    moved_drule = copy.copy(drule)
                    moved_drule.move()
                    nbase += [moved_drule]
            "It can be empty set"
            goto_set = RuleSet(self.gr, nbase)
        return goto_set

    def __str__(self):
        s = ''
        for rule in self.rset:
            s += str(rule) + '\n'
        return s

class ParserTable:
    def __init__(self, grammar):
        items = grammar.items()
        size = len(items)

        "Action table"
        self.a = [dict() for i in range(size)]
        "Goto table"
        self.g = [dict() for i in range(size)]
        self.conflict = False
        
        for i in range(len(items)):
            item = items[i]
            for dot_rule in item.rset:
                if dot_rule.end():
                    if dot_rule.lookup in self.a[i]:
                        self.conflict = True
                    else:
                        self.a[i][dot_rule.lookup] = ('R', dot_rule.rule)
                else:
                    at_dot = dot_rule.at()
                    if at_dot == End():
                        self.a[i][End()] = ('A', None)
                    elif type(at_dot) is str:
                        go = item.goto(at_dot)
                        if go is not None:
                            goto_index = items.index(go)
                            if at_dot in self.a[i]:
                                self.conflict = True
                            "Always SHIFT if conflict happens"
                            self.a[i][at_dot] = ('S', goto_index)
            for nterm in grammar.nonterminals():
                go = item.goto(nterm)
                if go is not None:
                    self.g[i][nterm] = items.index(go)

class Parser:
    def __init__(self, grammar):
        self.g = grammar
        self.t = ParserTable(grammar)
        self.reset()

    def reset(self):
        self.state_stack = [0]
        self.error = False
        self.done = False
        self.symbol = []

    def state(self):
        return self.state_stack[-1]

    def parse(self, s):
        self.reset()
        for c in s:
            self.put(c)
        return self.end()

    def put(self, c):
        if c not in self.t.a[self.state()]:
            self.error = True
        """
        Maybe there is action for this input,
        but error prevously occured
        """
        if self.error:
            return
        while True:
            act = self.t.a[self.state()][c]
            if act[0] == 'R':
                self.reduce(act[1])
            elif act[0] == 'S':
                self.shift(c, act[1])
                break
            elif act[0] == 'A':
                self.done = True
                break

    def end(self):
        self.put(End())
        if self.error:
            return None
        return self.symbol[0]

    def shift(self, c, i):
        self.symbol += [c]
        self.state_stack += [i]

    def reduce(self, rule):
        rlen = len(rule.sequence)
        sym = (rule.nterm.name, self.symbol[-rlen:])
        x = rule.nterm
        self.symbol = self.symbol[:-rlen] + [sym]
        self.state_stack = self.state_stack[:-rlen]
        self.state_stack += [self.t.g[self.state()][x]]

def print_res(res, ind=0):
    print(' ' * ind + res[0])
    for it in res[1]:
        if type(it) is tuple:
            print_res(it, ind + 1)
        else:
            print(' ' * (ind + 1) + it)
