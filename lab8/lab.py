import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    def __add__(self, b):
        return Add(self, b)
    def __radd__(self, b):
        return Add(b, self)
    def __sub__(self, b):
        return Sub(self, b)
    def __rsub__(self, b):
        return Sub(b, self)
    def __mul__(self, b):
        return Mul(self, b)
    def __rmul__(self, b):
        return Mul(b, self)
    def __truediv__(self, b):
        return Div(self, b)
    def __rtruediv__(self, b):
        return Div(b, self)


class Var(Symbol):
    prec = 0
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'

    def deriv(self, var):
        if var == self.name:
            return Num(1)
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return mapping[self.name] if self.name in mapping else self

class Num(Symbol):
    prec = 0
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

    def deriv(self, var):
        return Num(0)

    def simplify(self):
        return self

    def eval(self, mapping):
        return self.n

class BinOp(Symbol):
    def __init__(self, left, right):
        if type(left) == int or type(left) == float:
            self.left = Num(left)
        elif type(left) == str:
            self.left = Var(left)
        else:
            self.left = left
        if type(right) == int or type(right) == float:
            self.right = Num(right)
        elif type(right) == str:
            self.right = Var(right)
        else:
            self.right = right

    def __repr__(self):
        return self.repr_string + '(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def __str__(self):
        left = str(self.left)
        right = str(self.right)
        # special case of precedence for subs and divs
        if (self.repr_string == 'Sub' or self.repr_string == 'Div') and self.right.prec == self.prec:
            right = '(' + right + ')'
        if self.left.prec > self.prec:
            left = '(' + left + ')'
        if self.right.prec > self.prec:
            right = '(' + right + ')'
        return left + ' ' + self.str_string + ' ' + right

def is_zero(sym):
    """
    given a Symbol, checks if it is a Num with value 0
    """
    return type(sym) == Num and sym.n == 0

def is_one(sym):
    """
    given a Symbol, checks if it is a Num with value 1
    """
    return type(sym) == Num and sym.n == 1

class Add(BinOp):
    repr_string = 'Add'
    prec = 2
    str_string = '+'

    def deriv(self, var):
        return Add(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if type(left) == Num and type(right) == Num:
            return Num(left.n + right.n)
        # cases of adding with 0 
        if is_zero(left):
            return right
        if is_zero(right):
            return left
        return Add(left, right)

    def eval(self, mapping):
        left = self.left.eval(mapping)
        right = self.right.eval(mapping)
        return left + right

class Sub(BinOp):
    repr_string = 'Sub'
    prec = 2
    str_string = '-'

    def deriv(self, var):
        return Sub(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if type(left) == Num and type(right) == Num:
            return Num(left.n - right.n)
        # case of sub zero from smth
        if is_zero(right):
            return left
        return Sub(left, right)

    def eval(self, mapping):
        left = self.left.eval(mapping)
        right = self.right.eval(mapping)
        return left - right

class Mul(BinOp):
    repr_string = 'Mul'
    prec = 1
    str_string = '*'
    def deriv(self, var):
        one = Mul(self.left, self.right.deriv(var))
        two = Mul(self.right, self.left.deriv(var))
        return Add(one, two)

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if type(left) == Num and type(right) == Num:
            return Num(left.n * right.n)
        # cases of mult by 1
        if is_one(left):
            return right
        if is_one(right):
            return left
        # case of mult by 0
        if is_zero(left) or is_zero(right):
            return Num(0)
        return Mul(left, right)

    def eval(self, mapping):
        left = self.left.eval(mapping)
        right = self.right.eval(mapping)
        return left * right

class Div(BinOp):
    repr_string = 'Div'
    prec = 1
    str_string = '/'
    def deriv(self, var):
        one = Mul(self.right, self.left.deriv(var))
        two = Mul(self.left, self.right.deriv(var))
        num = Sub(one, two)
        denom = Mul(self.right, self.right)
        return Div(num, denom)

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if type(left) == Num and type(right) == Num:
            return Num(left.n / right.n)
        # case of dividing by 1
        if is_one(right):
            return left
        # case of 0 getting divided by smth
        if is_zero(left):
            return Num(0)
        return Div(left, right)

    def eval(self, mapping):
        left = self.left.eval(mapping)
        right = self.right.eval(mapping)
        return left / right

def tokenize(sym):
    split = sym.split(' ')
    tokens = []
    for t in split:
        # replace with correct number of parens as separate list elements
        if '(' in t:
            tokens += ['('] * t.count('(') + [t.replace('(', '')]
        elif ')' in t: 
            tokens += [t.replace(')', '')] + [')'] * t.count(')')
        else:
            tokens += [t]
    return tokens

def parse(tokens):
    def parse_expression(index):
        # var case
        if tokens[index].isalpha():
            return Var(tokens[index]), index + 1
        # parenthesis case
        if tokens[index] == '(':
            # print('left start', tokens[index+1])
            left, op_i = parse_expression(index + 1)
            # print('left', left, tokens[op_i])
            op = tokens[op_i]
            right, beyond_i = parse_expression(op_i + 1)
            # print(tokens[beyond_i])
            if op == '+':
                return Add(left, right), beyond_i + 1
            elif op == '-':
                return Sub(left, right), beyond_i + 1
            elif op == '*':
                return Mul(left, right), beyond_i + 1
            elif op == '/':
                return Div(left, right), beyond_i + 1
        # int case
        else:
            return Num(int(tokens[index])), index + 1
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def sym(exp):
    tokens = tokenize(exp)
    return parse(tokens)

if __name__ == '__main__':
    doctest.testmod()

    sym = '(-101 * x)'
    print(tokenize(sym))
    print(parse(tokenize(sym)))
