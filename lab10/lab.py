"""6.009 Lab 10: Snek Interpreter Part 2"""

import sys
sys.setrecursionlimit(5000)

import doctest
# NO ADDITIONAL IMPORTS!


###########################
# Snek-related Exceptions #
###########################

class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass

class Environment():
    def __init__(self, bindings=None, parent=None):
        self.bindings = bindings if bindings else {}
        self.parent = parent

    def lookup(self, var):
        if var in self.bindings:
            return self.bindings[var]
        else:
            # If the name does not have a binding in the environment and the environment has a parent, we look up the name in the parent environment (following these same steps).
            if self.parent:
                return self.parent.lookup(var)
            else:
                raise SnekNameError

    def update(self, var, value):
        if var in self.bindings:
            self.bindings[var] = value
            return self.bindings[var]
        else:
            # If the name does not have a binding in the environment and the environment has a parent, we look up the name in the parent environment (following these same steps).
            if self.parent:
                return self.parent.update(var, value)
            else:
                raise SnekNameError

class Function():
    def __init__(self, params, env, expr):
        self.params = params
        self.env = env
        self.expr = expr

    def __call__(self, args):
        new_env = Environment(parent = self.env)
        if len(args) != len(self.params):
            raise SnekEvaluationError
        for i in range(len(self.params)):
            new_env.bindings[self.params[i]] = args[i]
        return evaluate(self.expr, new_env)

class Pair():
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        return '( ' + str(self.car) + ',' + str(self.cdr) + ' )'


############################
# Tokenization and Parsing #
############################

def parens(s):
    """
    given a string with parens, build tokens list separating parens appropriately
    """
    tokens = []
    t = ''
    for x in s:
        if x == '(':
            tokens += [x]
        elif x == ')':
            if t != '':
                tokens += [t, x]
                t = ''
            else:
                tokens += [x]
        else:
            t += x
    if t != '':
        tokens += [t]
    return tokens

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    # remove comments, aka anything between two chars ; and \n
    semi = source.find(';')
    while semi != -1:
        space = source[semi:].find('\n') if source[semi:].find('\n') != -1 else len(source)-1
        source = source[:semi] + source[semi+space+1:]
        semi = source.find(';')
    split = source.split()
    tokens = []
    for t in split:
        # replace with correct number of parens as separate list elements
        if '(' in t or ')' in t:
            tokens += parens(t)
        else:
            tokens += [t]
    return tokens

def is_valid_var(s):
    if type(s) != str:
        return False
    return not(s.isdigit() or '(' in s or ')' in s or ' ' in s)

def is_valid_func_params(l):
    if type(l) != list:
        return False
    for x in l:
        if type(x) != str:
            return False
    return True

def check_syntax(inside_list):
    if inside_list[0] == ':=':
        if len(inside_list) != 3:
            raise SnekSyntaxError
        # for new short func def, raise error if element after := is not list of strings
        if type(inside_list[1]) == list:
            if len(inside_list[1]) < 1:
                raise SnekSyntaxError
            for x in inside_list[1]:
                if type(x) != str:
                    raise SnekSyntaxError
        else:
            if not is_valid_var(inside_list[1]):
                raise SnekSyntaxError
    # check syntax of function
    if inside_list[0] == 'function' and (len(inside_list) != 3 or not is_valid_func_params(inside_list[1])):
        raise SnekSyntaxError


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    # need to take into account expressions that should have () but dont
    if len(tokens) > 1 and (tokens.count('(') == 0 or tokens.count(')') == 0):
        raise SnekSyntaxError
    # put all tokens onto stack until close paren reached, then format inner expressions. meanwhile, keep track of parens opened and closed.
    stack = []
    parens = 0
    for t in tokens:
        if t == '(':
            parens += 1
            stack.append(t)
        elif t == ')':
            # pop off the stack until reach the last opening bracket
            parens -= 1
            if parens < 0:
                raise SnekSyntaxError
            top = stack.pop()
            inside_list = []
            while top != '(':
                inside_list = [top] + inside_list
                top = stack.pop()
            # check syntax of var or short func def
            if len(inside_list) > 0 and (inside_list[0] == ':=' or inside_list[0] == 'function'):
                check_syntax(inside_list)
            stack.append(inside_list)
        # int case
        elif (t[0] == '-' and len(t)>1 and t.count('-')==1 and t[1:].isdigit()) or t.isdigit():
            stack.append(int(t))
        # float case
        elif t.count('-')<2 and t.count('.')==1 and t!='.':
            stack.append(float(t))
        # var or func name or keyword or op case
        else:
            stack.append(t)
    if parens != 0:
        raise SnekSyntaxError
    if len(stack) == 1:
        return stack[0]
    return stack


######################
# Built-in Functions #
######################

def mult(args):
    prod = 1
    for x in args:
        prod *= x
    return prod

def div(args):
    if len(args) < 1:
        raise SnekEvaluationError
    quo = args[0]
    for x in args[1:]:
        quo /= x
    return quo

def eq(args):
    if not args:
        return True
    for x in args:
        if not x == args[0]:
            return False
    return True

def greater(args):
    if not args:
        return True
    for x in range(len(args)-1):
        if args[x] <= args[x+1]:
            return False
    return True

def geq(args):
    if not args:
        return True
    for x in range(len(args)-1):
        if args[x] < args[x+1]:
            return False
    return True

def lesser(args):
    if not args:
        return True
    for x in range(len(args)-1):
        if args[x] >= args[x+1]:
            return False
    return True

def leq(args):
    if not args:
        return True
    for x in range(len(args)-1):
        if args[x] > args[x+1]:
            return False
    return True

def car(args):
    if len(args) != 1:
        raise SnekSyntaxError
    if type(args[0]) != Pair:
        raise SnekEvaluationError
    return args[0].car

def cdr(args):
    if len(args) != 1:
        raise SnekSyntaxError
    if type(args[0]) != Pair:
        raise SnekEvaluationError
    return args[0].cdr

def make_list(args):
    if not args:
        return None
    if len(args) == 1:
        return Pair(args[0], None)
    return Pair(args[0], make_list(args[1:]))

def list_length(args):
    if type(args) == list and args != []:
        args = args[0]
    if args == [] or args == None:
        return 0
    if type(args) != Pair:
        print('ono')
        raise SnekEvaluationError
    return 1 + list_length(args.cdr)

def index(args):
    if not len(args) == 2:
        raise SnekSyntaxError
    i = args[1]
    l = args[0]
    if i == 0 and type(l) == Pair:
        return l.car
    if type(l) != Pair or (type(l.cdr) != Pair and i != 0) or i <= 0:
        raise SnekEvaluationError
    return index([l.cdr, i-1])

def copy(p):
    """
    given a list, makes a copy of it and returns it
    """
    if not p:
        return None
    if not type(p) == Pair:
        raise SnekEvaluationError
    new_right = copy(p.cdr)
    return Pair(p.car, new_right)

def concat(args):
    if not args:
        return None
    if (len(args) >= 1 and not args[0]):
        return concat(args[1:])
    if not type(args[0]) == Pair:
        raise SnekEvaluationError
    old = copy(args[0])
    if len(args) < 2:
        return old
    # find the last node and set the last node's cdr to recursive concat call
    cur = old
    for i in range(list_length([old])-1):
        cur = cur.cdr
    cur.cdr = concat(args[1:])
    return old

def map_list(args):
    if len(args) != 2 or (not callable(args[0])) or (type(args[1]) != Pair and args[1] != None):
        raise SnekEvaluationError
    func, listed = args
    if not listed:
        return None
    return Pair(func([listed.car]), map_list([func, listed.cdr]))

def filter_list(args):
    if len(args) != 2 or (not callable(args[0])) or (type(args[1]) != Pair and args[1] != None):
        raise SnekEvaluationError
    func, listed = args
    if not listed:
        return None
    if func([listed.car]):
        return Pair(listed.car, filter_list([func, listed.cdr]))
    return filter_list([func, listed.cdr])

def reduce_list(args):
    if len(args) != 3 or (not callable(args[0])) or (type(args[1]) != Pair and args[1] != None):
        raise SnekEvaluationError
    func, listed, val = args
    if not listed:
        return val
    return reduce_list([func, listed.cdr, func([val, listed.car])])

def begin(args):
    return args[-1]


snek_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mult,
    '/': div,
    '=?': eq,
    '>': greater,
    '>=': geq,
    '<': lesser,
    '<=': leq,
    'car': car,
    'cdr': cdr,
    'list': make_list,
    'length': list_length,
    'elt-at-index': index,
    'concat': concat,
    'map': map_list,
    'filter': filter_list,
    'reduce': reduce_list,
    'begin': begin,
}


##############
# Evaluation #
##############


def evaluate(tree, environ=None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if not environ:
        environ = Environment(parent=Environment(snek_builtins))
    # base cases
    if type(tree) == int or type(tree) == float:
        return tree
    if tree == '#t':
        return True
    if tree == '#f':
        return False
    if tree == 'nil':
        return None
    if type(tree) == str:
        return environ.lookup(tree)
    if tree == []:
        raise SnekEvaluationError
    # evaluating := case
    if type(tree) == list and tree[0] and tree[0] == ':=':
        # short func def
        if type(tree[1]) == list:
            # name is tree[1][0]
            params = tree[1][1:] if len(tree[1]) > 1 else []
            new_func = Function(params, environ, tree[2])
            environ.bindings[tree[1][0]] = new_func
            return new_func
        # regular var defs
        else:
            var = tree[1]
            expr = tree[2]
            expr = evaluate(expr, environ)
            environ.bindings[var] = expr
            return expr
    # evaluating function definition case
    if type(tree) == list and tree[0] and tree[0] == 'function':
        new_func = Function(tree[1], environ, tree[2])
        return new_func
    # evaluate logical statements
    if type(tree) == list and tree[0] and tree[0] == 'and':
        for x in range(1, len(tree)):
            if evaluate(tree[x], environ) != True:
                return False
        return True
    if type(tree) == list and tree[0] and tree[0] == 'or':
        for x in range(1, len(tree)):
            if evaluate(tree[x], environ) == True:
                return True
        return False
    if type(tree) == list and tree[0] and tree[0] == 'not':
        if not len(tree) == 2:
            raise SnekSyntaxError
        return not(evaluate(tree[1], environ))
    # evaluate conditionals
    if type(tree) == list and tree[0] and tree[0] == 'if':
        if not len(tree) == 4:
            raise SnekSyntaxError
        if evaluate(tree[1], environ):
            return evaluate(tree[2], environ)
        return evaluate(tree[3], environ)
    # cons func support
    if type(tree) == list and tree[0] and tree[0] == 'cons':
        if not len(tree) == 3:
            raise SnekSyntaxError
        return Pair(evaluate(tree[1], environ), evaluate(tree[2], environ))
    # del support
    if type(tree) == list and tree[0] and tree[0] == 'del':
        if not len(tree) == 2:
            raise SnekSyntaxError
        if tree[1] not in environ.bindings:
            raise SnekNameError
        return environ.bindings.pop(tree[1])
    # let support
    if type(tree) == list and tree[0] and tree[0] == 'let':
        if not len(tree) == 3:
            raise SnekSyntaxError
        _, vs, body = tree
        bindings = {}
        for v in vs:
            bindings[v[0]] = evaluate(v[1], environ)
        new_env = Environment(bindings=bindings, parent=environ)
        return evaluate(body, new_env)
    # set! support
    if type(tree) == list and tree[0] and tree[0] == 'set!':
        if not len(tree) == 3:
            raise SnekSyntaxError
        return environ.update(tree[1], evaluate(tree[2], environ))
    # recursive case: nested lists
    args = [evaluate(x, environ) for x in tree[1:]]
    op = evaluate(tree[0], environ)
    if not callable(op):
        raise SnekEvaluationError
    return op(args)


def result_and_env(tree, environ=None):
    if environ:
        return (evaluate(tree, environ), environ)
    else:
        p = Environment(snek_builtins)
        new_environ = Environment(parent=p)
        return (evaluate(tree, new_environ), new_environ)

def evaluate_file(file, environ=None):
    """
    given file name and optional environment, evaluate file contents wrt the environment
    """
    if not environ:
        environ = Environment(parent=Environment(snek_builtins))
    with open(file) as f:
        return evaluate(parse(tokenize(f.read())), environ)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    # environ = Environment(parent=Environment(snek_builtins))    
    # expr = '(let ((x 5) (y 3)) (+ x y))'
    # x = evaluate(parse(tokenize(expr)), environ)
    # print(x)
    # # expected 0.004629629629629629

    environ = Environment(parent=Environment(snek_builtins))
    for x in sys.argv[1:]:
        evaluate_file(x, environ)
    prev = input('>>>')
    while prev != 'QUIT':
        try:
            print(evaluate(parse(tokenize(prev)), environ))
        # figure out correct printing of error?
        except Exception as e:
            print('ERROR:', e.__class__.__name__)
        prev = input('>>>')
        

