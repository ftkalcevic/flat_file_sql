# https://github.com/mastermay/sql-parser/tree/master/py-sql-parser
# (without aggregates and sort)

import ply.lex as lex
import ply.yacc as yacc
import re
from math import *
from node import node
import common


keywords=('SELECT','FROM','WHERE','AND','OR','BETWEEN','IN','AS', 'LIKE')
#TOKENS
tokens=keywords + ('NAME','COMMA','LP','RP','NUMBER', 'STRING', 'DOT', 'GE', 'LE', 'NE' )
  

literals = ['=','+','-','*', '^','>','<' ] 
#DEFINE OF TOKENS

def t_NAME(t):
    #r'[A-Za-z]+|[a-zA-Z_][a-zA-Z0-9_]*|[A-Z]*\.[A-Z]$'
    r'[a-zA-Z_][a-zA-Z0-9_.[*\]]*'
    if t.value.upper() in keywords:
        t.type = t.value.upper()
    return t

def t_GE(t):
    r'\>\='
    return t

def t_LE(t):
    r'\<\='
    return t

def t_NE(t):
    r'\<\>|\!\='
    return t

def t_LP(t):
    r'\('
    return t

def t_DOT(t):
    r'\.'
    return t

def t_AS(t):
    r'AS'
    return t

def t_LIKE(t):
    r'LIKE'
    return t

def t_RP(t):
    r'\)'
    return t

def t_BETWEEN(t):
    r'BETWEEN'
    return t

def t_IN(t):
    r'IN'
    return t

def t_SELECT(t):
    r'SELECT'
    return t

def t_FROM(t):
    r'FROM'
    return t

def t_WHERE(t):
    r'WHERE'
    return t

def t_OR(t):
    r'OR'
    return t

def t_AND(t):
    r'AND'
    return t

def t_COMMA(t):
    r','
    return t

def t_NUMBER(t):
    r'[+-]?([0-9]*[.])?[0-9]+'
    return t

def t_STRING(t):
    r'\'[^\']*\''
    return t

# IGNORED
t_ignore = " \t\n"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# LEX ANALYSIS   
lex.lex(reflags=re.IGNORECASE+re.VERBOSE)

#PARSING
def p_query(t):
    '''query :  select 
            | LP query RP
                '''
    if len(t)==2:
        t[0]=t[1]
    else:
        t[0]=t[2]

def p_select(t):
    '''select :   SELECT list FROM table WHERE lst
                | SELECT list FROM table '''
    if len(t)==7:
        t[0]=node('[QUERY]')
        s = node('[SELECT]')
        t[0].add(s)
        s.add(t[2])
        f = node('[FROM]')
        t[0].add(f)
        f.add(t[4])
        w = node('[WHERE]')
        t[0].add(w)
        w.add(t[6])
    else:
        t[0]=node('QUERY')
        s = node('[SELECT]')
        t[0].add(s)
        s.add(t[2])
        f = node('[FROM]')
        t[0].add(f)
        f.add(t[4])

def p_table(t):
    '''table : NAME
            | LP query RP
            | NAME AS NAME
            | table AS NAME'''
    if len(t)==2:
        t[0]=node('[TABLE]')
        t[0].add(node(t[1]))
    elif t[2].upper()=='AS' and isinstance(t[1], node):
        t[0]=node('[TABLE]')
        t[0].add(t[1])
        t[0].add(node('AS'))
        t[0].add(node(t[3]))
    elif t[2].upper()=='AS' and not isinstance(t[1], node):
        t[0]=node('[TABLE]')
        t[0].add(node(t[1]))
        t[0].add(node('AS'))
        t[0].add(node(t[3]))
    else :
        t[0]=node('[TABLE]')
        t[0].add(t[2])
        
def p_const_list(t):
    ''' const_list  : const_list COMMA NUMBER
                    | NUMBER
                    '''
    if len(t)==2:
        t[0] = node("[NUMBER_LIST]")
        t[0].add( t[1] )
    else:
        t[0] = t[1]
        t[0].add( t[3] )

def p_string_list(t):
    ''' string_list  : string_list COMMA STRING
                     | STRING
                     '''
    if len(t)==2:
        t[0] = node("[STRING_LIST]")
        t[0].add( t[1] )
    else:
        t[0] = t[1]
        t[0].add( t[3] )

def p_lst(t):
    ''' lst  : condition
             | lst AND condition
             | lst OR condition
              '''
    
    if len(t)==2:
        t[0]=t[1]
    elif t[2].upper()=='AND':
        t[0]=node('[AND]')
        t[0].add(t[1])
        t[0].add(t[3])
    elif t[2].upper()=='OR':
        t[0]=node('[OR]')
        t[0].add(t[1])
        t[0].add(t[3])
    else:
        t[0]=node('')
        

def p_condition(t):
    ''' condition : NAME '>' NUMBER
                  | NAME '<' NUMBER
                  | NAME '=' NUMBER
                  | NAME '=' STRING
                  | NAME GE NUMBER
                  | NAME LE NUMBER
                  | NAME NE NUMBER
                  | NAME '>' NAME
                  | NAME '<' NAME
                  | NAME '=' NAME
                  | NAME GE NAME
                  | NAME LE NAME
                  | NAME NE NAME
                  | list '>' list
                  | list '<' list
                  | list '=' list
                  | list '>' NUMBER
                  | list '<' NUMBER
                  | list '=' NUMBER  
                  | NAME BETWEEN NUMBER AND NUMBER
                  | NAME IN LP const_list RP
                  | NAME IN LP string_list RP
                  | NAME LIKE STRING
                  '''
    if len(t) == 4:
        t[0]=node(t[2])
        t[0].add(node(str(t[1])))
        t[0].add(node(str(t[3])))
    elif t[2].upper()=='BETWEEN':
        temp='%s >= %s & %s <= %s'%(t[1],str(t[3]),t[1],str(t[5]))
        t[0]=node('[BETWEEN]')
        t[0].add(node(t[1]))
        t[0].add(node(t[3]))
        t[0].add(node(t[5]))
    elif t[2].upper()=='IN':
        t[0]=node('[IN]')
        t[0].add(node(t[1]))
        if t[4].getdata() == '[NUMBER_LIST]':
            l = [int(x) for x in t[4].getchildren()]
            t[0].add(node(l))
        else:
            l = [x.upper() for x in t[4].getchildren()]
            t[0].add(node(l))

def p_list(t):
    ''' list : '*'
             | NAME
             | NAME DOT NAME 
             | list COMMA list
             '''
    if len(t)==2:
        t[0]=node('[FIELDS]')
        t[0].add(node(t[1]))
    elif t[2]==',':
        n = node('[FIELDS]')
        for c in t[1].getchildren():
            n.add( c )
        for c in t[3].getchildren():
            n.add( c )        
        t[0] = n
    else:
        temp='%s.%s'%(t[1],t[3])
        t[0]=node(temp)
    
def p_error(t):
    print("Syntax error at pos "+str(t.lexpos)+" - '"+t.value+"'" )

yacc.yacc()


class Sql:

    def __init__(self, query):
        self.parse=yacc.parse(query,debug=common.doLog)
        if common.doLog:
            self.parse.print_node(0)

    def findNode(self, name):
        return self.parse.find(name)

        


