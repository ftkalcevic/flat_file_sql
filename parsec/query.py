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

class Where:
    def __init__(self, clause):
        pass

    def match(self, buf, t):
        return True


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
        raise Exception("File is not a multiple of recordsize")

    outputFieldNames(fields)
    with open( file["dataFile"], "rb" ) as f:
        while True:
            buf = f.read(recordSize)
            if not buf:
                break
            if where != None:
                if not where.match(buf,t):
                    continue
            outputFields(fields, buf)


def findQueryColumns(node):
    if node.getdata() == "[FIELD]":
        return [node.getchildren()[0].getdata()]
    else:
        lst = []
        for c in node.getchildren():
            lst.extend( findQueryColumns(c) )
        return lst


if __name__ == "__main__":

    #sql = Sql("Select index, mi, MY_STRUCT.why.b, why.c, * from MY_STRUCT where index = 4 or index = 7")
    #sql = Sql("Select index, mi, why.* from MY_STRUCT where index = 4 or index = 7 and mi in (1,2,3) or msa[1].simp2 between 1 and 5")
    sql = Sql("Select index, mi, why.* from MY_STRUCT where msa[1].simp2 = 1")

    node = sql.findNode( "[TABLE]" )

    if node == None:
        raise Exception( "table not specified in query")

    # Find and verify table name
    tableNode = node.getchildren()[0]
    tableName = tableNode.getdata()

    tableData = tables[tableName]
    if tableData == None:
        raise Exception( "Unknown table '" + tableName + "'")

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
        raise Exception( "Unknown table '" + tableName + "'")

    # Find the columns
    columns = findQueryColumns(sql.findNode("[FIELDS]"))
    Log("columns")
    Log( columns )

    columnFields = t.findFields( columns )
    Log("fields")
    Log(columnFields)


    # Find the where
    whereNode = sql.findNode("[WHERE]")
    where = Where(whereNode)
    Log("where")
    Log(whereNode)

    where = None
    # 
    executeQuery(tableName,t, columnFields, where)
    

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