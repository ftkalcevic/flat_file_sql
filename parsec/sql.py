import re
import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'select' : 'SELECT',
    'from' : 'FROM'
 }
tokens = (
    'SELECT',
    'FROM',
    'ASTERISK',
    'COMMA',
    'NAME'
    )

# Tokens

t_ASTERISK = r'\*'
t_COMMA = r','

#def t_NUMBER(t):
#    r'\d+'
#    try:
#        t.value = int(t.value)
#    except ValueError:
#        print("Integer value too large %d", t.value)
#        t.value = 0
#    return t
def t_SELECT(t):
    r'SELECT'
    return t

def t_FROM(t):
    r'FROM'
    return t

def t_NAME(t):
    r'[A-Za-z0-9._]+'
    try:
        t.value = t.value
    except ValueError:
        t.value = ""
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Ignored characters
t_ignore = " \t\n"

# Build the lexer
lexer = lex.lex(reflags=re.IGNORECASE)

def p_query_specification(p):
    '''query_specification : SELECT select_list FROM table_expression'''
    pass

def p_select_list(p):
    '''select_list  : ASTERISK
                    | NAME
                    | select_list COMMA select_list
                    '''
    pass

def p_table_expression(p):
    '''table_expression : NAME'''
    pass

def p_error(t):
    print("Syntax error at '%s'" % t.value)


parser = yacc.yacc()


class Sql:

    def __init__(self, query):
        parser.parse(query)
        


