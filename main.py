import sys
import ply.lex as lex
import ply.yacc as yacc


#  tokens
tokens = (
    'ID', 'NUMBER', 'STRING',
    'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'COMMA', 'SEMICOLON',
    'IF', 'ELSE', 'WHILE', 'PRINT', 'CAT'
)

# Reserved words
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'print': 'PRINT',
    'cat': 'CAT'
}

# regex for token
t_ASSIGN  = r'<-'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MOD     = r'%%'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_GT      = r'>'
t_LT      = r'<'
t_GE      = r'>='
t_LE      = r'<='
t_EQ      = r'=='
t_NE      = r'!='
t_COMMA   = r','
t_SEMICOLON = r';'

# ignore space and tab
t_ignore  = ' \t'

# handl identifier and keyword
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# handle int
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# handle string 
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1] # remove quote
    t.value = t.value.replace(r'\n', '\n')
    return t

# handle new line
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# handle comment
def t_COMMENT(t):
    r'\#.*'
    pass

# handle error
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# PEMDAS
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'GT', 'LT', 'GE', 'LE', 'EQ', 'NE'),
)

# Grammar Rules

def p_program(p):
    '''program : statements'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statement
                  | statement statements'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

# define statement types
def p_statement(p):
    '''statement : assignment
                 | print_stmt
                 | cat_stmt
                 | if_stmt
                 | while_stmt
                 | statement SEMICOLON''' 
    p[0] = p[1]

def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    p[0] = ('assign', p[1], p[3])

def p_print_stmt(p):
    '''print_stmt : PRINT LPAREN expression RPAREN'''
    p[0] = ('print', p[3])

def p_cat_stmt(p):
    '''cat_stmt : CAT LPAREN args RPAREN'''
    p[0] = ('cat', p[3])

def p_args(p):
    '''args : expression
            | expression COMMA args'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_if_stmt(p):
    '''if_stmt : IF LPAREN condition RPAREN block
               | IF LPAREN condition RPAREN block ELSE block'''
    if len(p) == 6:
        p[0] = ('if', p[3], p[5])
    else:
        p[0] = ('if_else', p[3], p[5], p[7])

def p_while_stmt(p):
    '''while_stmt : WHILE LPAREN condition RPAREN block'''
    p[0] = ('while', p[3], p[5])

def p_block(p):
    '''block : LBRACE statements RBRACE'''
    p[0] = p[2]

def p_condition(p):
    '''condition : expression GT expression
                 | expression LT expression
                 | expression GE expression
                 | expression LE expression
                 | expression EQ expression
                 | expression NE expression'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = ('num', p[1])

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = ('str', p[1])

def p_expression_id(p):
    '''expression : ID'''
    p[0] = ('var', p[1])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()


env = {}

def run(node):
    if not node: return

    if isinstance(node, list):
        for stmt in node:
            run(stmt)
        return

    ntype = node[0]

    if ntype == 'assign':
        var_name = node[1]
        val = run(node[2])
        env[var_name] = val

    elif ntype == 'print':
        val = run(node[1])
        print(val)

    elif ntype == 'cat':
        args = node[1]
        for arg in args:
            val = run(arg)
            print(val, end='') 

    elif ntype == 'if':
        condition = run(node[1])
        if condition:
            run(node[2])

    elif ntype == 'if_else':
        condition = run(node[1])
        if condition:
            run(node[2])
        else:
            run(node[3])

    elif ntype == 'while':
        while run(node[1]):
            run(node[2])

    elif ntype == 'binop':
        op = node[1]
        left = run(node[2])
        right = run(node[3])
        
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/': return int(left / right)
        if op == '%%': return left % right
        if op == '>': return left > right
        if op == '<': return left < right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        if op == '==': return left == right
        if op == '!=': return left != right

    elif ntype == 'num':
        return node[1]
    
    elif ntype == 'str':
        return node[1]

    elif ntype == 'var':
        var_name = node[1]
        if var_name in env:
            return env[var_name]
        else:
            print(f"Error: Variable '{var_name}' not defined.")
            return 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                data = f.read()
            
            result = parser.parse(data)
            run(result)
            
        except FileNotFoundError:
            print(f"File {filename} not found.")
    else:
        print("Usage: python Rscript.py <filename.r>")