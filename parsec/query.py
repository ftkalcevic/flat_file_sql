import copy
import sys
import io
import struct

from pathlib import Path
from parsec import StructParser
#from sql import Sql
from yacc import Sql

tables = { 
    "MY_STRUCT": { "sourceFile": "test.h", "dataFile": "test.data" },
           "T1": { "sourceFile": "test.h", "dataFile": "t1.data" } 
           }

order = 'little'

def extractData( buf, t, offset):

    if t.dataType in ("char" ) and t.arraySize > 0:
        s = ""
        for i in range(offset,offset+t.arraySize):
            if buf[i] == 0:
                break;
            else:
                s += chr(buf[i])
        return s

    elif t.dataType in ("char" ):
        s = chr(buf[offset])
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
        n = struct.unpack( 'f', fbuf )
        return n

    elif t.dataType in ("double" ):
        fbuf = buf[offset:offset+8]
        n = struct.unpack( 'd', fbuf )
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
            print( t.name+"="+str(v))

def dump(buf, t, baseOffset=0):

    _dump(buf,t,baseOffset,t.arraySize)

def readData(structName, t):
    file = tables[structName]

    recordSize = t.getDataSize()
    fileSize = Path(file).stat().st_size

    if int(fileSize/recordSize)*recordSize != fileSize:
        raise Exception("File is not a multiple of recordsize")

    with open( file, "rb" ) as f:
        while True:
            buf = f.read(recordSize)
            break

    # Dump the record
    dump(buf, t)


def findQueryColumns(node):
    if node.getdata() == "[FIELD]":
        return [node.getchildren()[0].getdata()]
    else:
        lst = []
        for c in node.getchildren():
            lst.extend( findQueryColumns(c) )
        return lst

if __name__ == "__main__":

    #if len(sys.argv) > 1:
    #    c_decl = sys.argv[1]
    #else:
    #    c_decl = "char *(*(**foo[][8])())[];"

    s = Sql("Select index, mi, * from MY_STRUCT where index = 4 or index = 7")

    node = s.findNode( "[TABLE]" )

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

    #print( "typedefs" )
    #for k in parser.typedefs:
    #    print("    "+k)
    #print( "structs" )
    #for k in parser.structs:
    #    print("    "+k)
    #print( "unions" )
    #for k in parser.unions:
    #    print("    "+k)


    t = parser.MakeType(tableName)
    if t == None:
        raise Exception( "Unknown table '" + tableName + "'")

    # Find the columns
    columns = findQueryColumns(s.findNode("[FIELDS]"))
    print( columns )
    fields = t.findFields( columns )
    print(fields)


    # Find the where
    readData(tableName,t)

r''' 

* - gets every column, [colname, offset], 
        arrays (non-char) will be field[0], field[1], field[2], etc
                structs will be field[0].s1, field[0].s2, etc
struct_name.*
array_member.*
array[number].*
    
each "column" will be a class instance, keeping a pointer to the internal structure.
when it comes time to output, we'll take as an input, the byte array of the structure, then we can iterate from where we are?
Or do we expand the query into a list of individual fields, with type + offset.  Arrays will be expanded.
'''