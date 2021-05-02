
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = "AND AS BETWEEN COMMA DOT FROM LP NAME NUMBER OR RP SELECT WHEREquery :  select \n            | LP query RP\n                select :   SELECT list FROM table WHERE lst\n                | SELECT list FROM table table : NAME\n            | LP query RP\n            | NAME AS NAME\n            | table AS NAME lst  : condition\n             | condition AND condition\n             | condition OR condition\n             | NAME BETWEEN NUMBER AND NUMBER\n               condition : NAME '>' NUMBER\n                  | NAME '<' NUMBER\n                  | NAME '=' NUMBER\n                  | NAME '>' NAME\n                  | NAME '<' NAME\n                  | NAME '=' NAME\n                  | list '>' list\n                  | list '<' list\n                  | list '=' list\n                  | list '>' NUMBER\n                  | list '<' NUMBER\n                  | list '=' NUMBER   list : '*'\n             | NAME\n             | NAME DOT NAME \n             | list COMMA list\n             | list AND NAME\n             | list OR NAME\n             "
    
_lr_action_items = {'LP':([0,3,10,17,],[3,3,17,3,]),'SELECT':([0,3,17,],[4,4,4,]),'$end':([1,2,7,8,9,15,16,18,19,20,21,27,28,30,31,32,42,43,44,45,46,47,48,50,52,53,54,55,56,57,59,],[0,-1,-25,-26,-2,-4,-5,-28,-29,-30,-27,-3,-9,-8,-7,-6,-19,-22,-20,-23,-21,-24,-10,-11,-16,-13,-17,-14,-18,-15,-12,]),'RP':([2,5,7,8,9,15,16,18,19,20,21,25,27,28,30,31,32,42,43,44,45,46,47,48,50,52,53,54,55,56,57,59,],[-1,9,-25,-26,-2,-4,-5,-28,-29,-30,-27,32,-3,-9,-8,-7,-6,-19,-22,-20,-23,-21,-24,-10,-11,-16,-13,-17,-14,-18,-15,-12,]),'*':([4,11,22,33,34,35,36,37,],[7,7,7,7,7,7,7,7,]),'NAME':([4,10,11,12,13,14,22,23,24,33,34,35,36,37,39,40,41,],[8,16,8,19,20,21,29,30,31,8,8,8,49,49,52,54,56,]),'FROM':([6,7,8,18,19,20,21,],[10,-25,-26,-28,-29,-30,-27,]),'COMMA':([6,7,8,18,19,20,21,26,29,42,44,46,49,],[11,-25,-26,11,-29,-30,-27,11,-26,11,11,11,-26,]),'AND':([6,7,8,18,19,20,21,26,28,29,42,43,44,45,46,47,49,51,52,53,54,55,56,57,],[12,-25,-26,12,-29,-30,-27,12,36,-26,12,-22,12,-23,12,-24,-26,58,-16,-13,-17,-14,-18,-15,]),'OR':([6,7,8,18,19,20,21,26,28,29,42,43,44,45,46,47,49,52,53,54,55,56,57,],[13,-25,-26,13,-29,-30,-27,13,37,-26,13,-22,13,-23,13,-24,-26,-16,-13,-17,-14,-18,-15,]),'>':([7,8,18,19,20,21,26,29,49,],[-25,-26,-28,-29,-30,-27,33,39,39,]),'<':([7,8,18,19,20,21,26,29,49,],[-25,-26,-28,-29,-30,-27,34,40,40,]),'=':([7,8,18,19,20,21,26,29,49,],[-25,-26,-28,-29,-30,-27,35,41,41,]),'DOT':([8,29,49,],[14,14,14,]),'WHERE':([15,16,30,31,32,],[22,-5,-8,-7,-6,]),'AS':([15,16,30,31,32,],[23,24,-8,-7,-6,]),'BETWEEN':([29,],[38,]),'NUMBER':([33,34,35,38,39,40,41,58,],[43,45,47,51,53,55,57,59,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'query':([0,3,17,],[1,5,25,]),'select':([0,3,17,],[2,2,2,]),'list':([4,11,22,33,34,35,36,37,],[6,18,26,42,44,46,26,26,]),'table':([10,],[15,]),'lst':([22,],[27,]),'condition':([22,36,37,],[28,48,50,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> query","S'",1,None,None,None),
  ('query -> select','query',1,'p_query','yacc.py',83),
  ('query -> LP query RP','query',3,'p_query','yacc.py',84),
  ('select -> SELECT list FROM table WHERE lst','select',6,'p_select','yacc.py',92),
  ('select -> SELECT list FROM table','select',4,'p_select','yacc.py',93),
  ('table -> NAME','table',1,'p_table','yacc.py',110),
  ('table -> LP query RP','table',3,'p_table','yacc.py',111),
  ('table -> NAME AS NAME','table',3,'p_table','yacc.py',112),
  ('table -> table AS NAME','table',3,'p_table','yacc.py',113),
  ('lst -> condition','lst',1,'p_lst','yacc.py',133),
  ('lst -> condition AND condition','lst',3,'p_lst','yacc.py',134),
  ('lst -> condition OR condition','lst',3,'p_lst','yacc.py',135),
  ('lst -> NAME BETWEEN NUMBER AND NUMBER','lst',5,'p_lst','yacc.py',136),
  ('condition -> NAME > NUMBER','condition',3,'p_condition','yacc.py',162),
  ('condition -> NAME < NUMBER','condition',3,'p_condition','yacc.py',163),
  ('condition -> NAME = NUMBER','condition',3,'p_condition','yacc.py',164),
  ('condition -> NAME > NAME','condition',3,'p_condition','yacc.py',165),
  ('condition -> NAME < NAME','condition',3,'p_condition','yacc.py',166),
  ('condition -> NAME = NAME','condition',3,'p_condition','yacc.py',167),
  ('condition -> list > list','condition',3,'p_condition','yacc.py',168),
  ('condition -> list < list','condition',3,'p_condition','yacc.py',169),
  ('condition -> list = list','condition',3,'p_condition','yacc.py',170),
  ('condition -> list > NUMBER','condition',3,'p_condition','yacc.py',171),
  ('condition -> list < NUMBER','condition',3,'p_condition','yacc.py',172),
  ('condition -> list = NUMBER','condition',3,'p_condition','yacc.py',173),
  ('list -> *','list',1,'p_list','yacc.py',186),
  ('list -> NAME','list',1,'p_list','yacc.py',187),
  ('list -> NAME DOT NAME','list',3,'p_list','yacc.py',188),
  ('list -> list COMMA list','list',3,'p_list','yacc.py',189),
  ('list -> list AND NAME','list',3,'p_list','yacc.py',190),
  ('list -> list OR NAME','list',3,'p_list','yacc.py',191),
]
