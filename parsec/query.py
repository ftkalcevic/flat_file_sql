import copy
import sys
import io
import struct

from pathlib import Path
from parsec import StructParser
#from sql import Sql
from yacc import Sql
from common import Log

tables = { 
    "MY_STRUCT": { "sourceFile": "test.h", "dataFile": "test.data" },
           "T1": { "sourceFile": "test.h", "dataFile": "t1.data" } 
           }

order = 'little'

class QueryException(Exception):
    pass

class WhereNode:
    def __init__(self, clause, t):
        self.children = []

        for c in clause.getchildren():
            if c.getdata() == '[OR]' or c.getdata() == '[AND]':
                self.children.append( ConditionalWhereNode(c,t) )
            elif c.getdata() == '[IN]':
                self.children.append( InWhereNode(c,t) )
            elif c.getdata() == '[BETWEEN]':
                self.children.append( BetweenWhereNode(c,t) )
            else:
                self.children.append( LogicalWhereNode(c,t) )

    def match(self, buf):
        return self.children[0].match(buf)

class InWhereNode(WhereNode):
    def __init__(self, clause, t):
        self.type = clause.getdata()
        self.value = ValueWhereNode( clause.getchildren()[0], t)
        self.values = clause.getchildren()[1].getdata()

    def match(self, buf):
        lvalue = self.value.evaluate(buf)
        t = self.value.value[0].ctype
        if t.dataType == "char" and t.arraySize > 0:
            lvalue = lvalue.upper()
        return lvalue in self.values

class BetweenWhereNode(WhereNode):
    def __init__(self, clause, t):
        self.type = clause.getdata()
        self.value = ValueWhereNode(clause.getchildren()[0],t)
        self.min = ValueWhereNode( clause.getchildren()[1], t)
        self.max = ValueWhereNode( clause.getchildren()[2], t)

    def match(self, buf):
        min = self.min.evaluate(buf)
        max = self.max.evaluate(buf)
        lvalue = self.value.evaluate(buf)
        return lvalue >= min and lvalue <= max

class ValueWhereNode(WhereNode):
    NUM = 1
    STR = 2
    VAR = 3

    def __init__(self, clause, t):
        s = clause.getdata()
        if s.isnumeric():
            self.type = ValueWhereNode.NUM
            if "." in clause.getdata():
                self.value = float(clause.getdata())
            else:
                self.value = int(clause.getdata())
        elif s[0] == "'" and s[-1] == "'":
            self.type = ValueWhereNode.STR
            self.value = s[1:-1]
        else:
            self.type = ValueWhereNode.VAR
            self.value = t.findField(s)
            if len(self.value) == 0:
                raise QueryException("Unknown field '{0}' in where clause".format(s))

    def evaluate(self, buf):
        if self.type == ValueWhereNode.NUM or self.type == ValueWhereNode.STR:
            return self.value
        else:
            f = self.value[0]
            return extractData( buf, f.ctype, f.offset)

class LogicalWhereNode(WhereNode):
    def __init__(self, clause, t):
        self.expr = clause.getdata()
        # Supports Name == Name, Name == value, value == Name.  Value can be num, string.
        self.children = []
        self.children.append( ValueWhereNode( clause.getchildren()[0], t ))
        self.children.append( ValueWhereNode( clause.getchildren()[1], t ))

    def match(self, buf):
        lvalue = self.children[0].evaluate(buf)
        rvalue = self.children[1].evaluate(buf)
        if self.children[0].type == ValueWhereNode.STR or self.children[1].type == ValueWhereNode.STR:
            lvalue = lvalue.upper()
            rvalue = rvalue.upper()
        if self.expr == "=":
            return lvalue == rvalue
        elif self.expr == "<>" or self.expr == "!=":
            return lvalue != rvalue
        elif self.expr == "<":
            return lvalue < rvalue
        elif self.expr == ">":
            return lvalue > rvalue
        elif self.expr == "<=":
            return lvalue <= rvalue
        elif self.expr == ">=":
            return lvalue >= rvalue
            

class ConditionalWhereNode(WhereNode):
    def __init__(self, clause, t):
        self.type = clause.getdata()
        WhereNode.__init__(self, clause, t)

    def match(self, buf):
        if self.type == '[OR]':
            if self.children[0].match(buf):
               return True
            elif self.children[1].match(buf):
                return True
            else:
                return False
        elif self.type == '[AND]':
            return self.children[0].match(buf) and self.children[1].match(buf)

class Where:
    def __init__(self, clause, t):
        self.where = None
        if clause != None:
            self.preprocessClause( clause, t)

    def preprocessClause( self, clause, t ):
        assert( clause.getdata() == '[WHERE]' )
        self.where = WhereNode( clause, t )

    def match(self, buf, t):
        if not self.where:
            return True
        else:
            return self.where.match( buf )


def extractData( buf, t, offset):

    if t.dataType in ("char" ) and t.arraySize > 0:
        s = ""
        for i in range(offset,offset+t.arraySize):
            if buf[i] == 0:
                break;
            else:
                s += chr(buf[i])
        return "'" + s + "'"

    elif t.dataType in ("char" ):
        n = buf[offset]
        if n < 32 or n > 127:
            s = "'\\x" + format(n,'x') + "'"
        else:
            s = "'" + chr(n) + "'"
        return s

    elif t.dataType in ("int", "unsigned int", "signed int", 
                        "long", "unsigned long", "signed long",
                        "short", "unsigned short", "signed short" ):
        signed = True
        if t.dataType.split(' ')[0] == "unsigned":
            signed = False
        n = int.from_bytes(buf[offset:offset+t.dataSize], byteorder = order, signed = signed )
        return n

#    elif t.dataType in ("short", "unsigned short", "signed short" ):
#        if order == 'little':
#            n = buf[offset] | buf[offset+1] << 8
#        else:
#            n = buf[offset+2] << 8 | buf[offset+3]
#        return n

    elif t.dataType in ("long long" ):
        n = int.from_bytes(buf[offset:offset+8], byteorder = order )
        return n

    elif t.dataType in ("float" ):
        fbuf = buf[offset:offset+4]
        n = struct.unpack( 'f', fbuf )[0]
        return n

    elif t.dataType in ("double" ):
        fbuf = buf[offset:offset+8]
        n = struct.unpack( 'd', fbuf )[0]
        return n


def _dump(buf, t, baseOffset=0, arraySize=0):
    if arraySize > 0 and t.dataType != "char":

        for i in range(0,arraySize-1):
            _dump(buf,t, baseOffset + i * t.dataSize, 0)

    else:

        if t.dataType == "Struct":
            for f in t.fields:
                _dump(buf,f, baseOffset + f.offset, f.arraySize)
        else:
            v = extractData( buf, t, baseOffset )
            Log( t.name+"="+str(v))

def dump(buf, t, baseOffset=0):
    _dump(buf,t,baseOffset,t.arraySize)

def outputFieldNames(fields):
    first = True
    for f in fields:
        if not first:
            print(",", end='')
        #print( f.name+":"+str(f.offset), end='' )
        print( f.name, end='' )
        first = False
    print()

def outputFields(fields, buf):
    first = True
    for f in fields:
        value = extractData( buf, f.ctype, f.offset)
        if not first:
            print(",", end='')
        print( value, end='' )
        first = False
    print()

def executeQuery(structName, t, fields, where):
    file = tables[structName]

    recordSize = t.getDataSize()
    fileSize = Path(file["dataFile"]).stat().st_size

    if int(fileSize/recordSize)*recordSize != fileSize:
        raise QueryException("File is not a multiple of recordsize")

    outputFieldNames(fields)
    rowcount = 0
    with open( file["dataFile"], "rb" ) as f:
        while True:
            buf = f.read(recordSize)
            if not buf:
                break
            if where != None:
                if not where.match(buf,t):
                    continue
            outputFields(fields, buf)
            rowcount += 1
    print("({0} row(s) affected)".format(rowcount))


def findQueryColumns(node):
    if node.getdata() == "[FIELDS]":
        return [o.getdata() for o in node.getchildren()]
    return []


if __name__ == "__main__":

    try:
        sqlQuery = ' '.join(sys.argv[1:])
        Log(sqlQuery)
        sql = Sql(sqlQuery)


        #sql = Sql("Select index, mi, MY_STRUCT.why.b, why.c, * from MY_STRUCT where index = 4 or index = 7")
        #sql = Sql("SELECT index, mi, why.*, msa, str from MY_STRUCT where windex >= 2 and mi in (1,2,3) or msa[1].simp2 between 1 and 5 and str = 'test'")
        #sql = Sql("Select index, mi, why.* from MY_STRUCT where index in (1,3,5)")
        #sql = Sql("Select index, mi, why.*, str from MY_STRUCT where str in ('a', 'test')")
        #sql = Sql("Select index, mi, why.*, str from MY_STRUCT where index between 2 and 3")
        sql = Sql("Select index, mi, why2[*].*, str from MY_STRUCT where index between 2 and 3")

        node = sql.findNode( "[TABLE]" )

        if node == None:
            raise QueryException( "table not specified in query")

        # Find and verify table name
        tableNode = node.getchildren()[0]
        tableName = tableNode.getdata()

        if not tableName in tables:
            raise QueryException("Structure '{0}' unknown".format(tableName))
        tableData = tables[tableName]

        # get the structure specification
        parser = StructParser()
        parser.Parse( tableData["sourceFile"] )

        #Log( "typedefs" )
        #for k in parser.typedefs:
        #    Log("    "+k)
        #Log( "structs" )
        #for k in parser.structs:
        #    Log("    "+k)
        #Log( "unions" )
        #for k in parser.unions:
        #    Log("    "+k)

        t = parser.MakeType(tableName)
        if t == None:
            raise QueryException( "Unknown table '" + tableName + "'")

        # Find the columns
        columns = findQueryColumns(sql.findNode("[FIELDS]"))
        #Log("columns")
        #Log( columns )

        # Map the columns to structure fields
        columnFields = t.findFields( columns )
        #Log("fields")
        #Log(columnFields)


        # Find the where
        whereNode = sql.findNode("[WHERE]")
        where = Where(whereNode, t)
        #Log("where")
        #Log(whereNode)

        # 
        executeQuery(tableName,t, columnFields, where)
   
    except QueryException as q:

        print("Error! {0}".format(q) )

r''' 

* - gets every column, [colname, offset], 
        arrays (non-char) will be field[0], field[1], field[2], etc
                structs will be field[0].s1, field[0].s2, etc
struct_name.*
array_member.*
array[number].*
array[*]
array[]
    
each "column" will be a class instance, keeping a pointer to the internal structure.
when it comes time to output, we'll take as an input, the byte array of the structure, then we can iterate from where we are?
Or do we expand the query into a list of individual fields, with type + offset.  Arrays will be expanded.
'''