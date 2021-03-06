import copy
import sys
import io
import re
import os
import common
from common import Log

from pycparser import c_parser, c_ast, parse_file

def getTypeSize(t):
    if t in ('char'):
        return 1
    elif t in ('short'):
        return 2
    elif t in ('int','long','float'):
        return 4
    elif t in ('double'):
        return 8
    else:
        raise Exception("Unknown type - " + t)

class FieldInstance:
    def __init__(self, name, ctype, offset ):
        self.name = name
        self.offset = offset
        self.ctype = ctype

class CType:
    lastBitField = None

    def __init__(self, parser, node):
        self.fields = []
        self.arraySize = 0
        self.bitFieldSize = 0
        self.dataType = ""
        self.dataSize = 0
        self.name = ""
        self.offset = 0
        self.parser = parser
        self.allFields = None

        if type(node) == c_ast.Typedef:

            if type(node.type.type) == c_ast.Struct:
                self.name = node.name
                self.dataType =  "Struct"
                struct = node.type.type;
                self.dataSize = 0
                for decl in struct.decls:
                    t = CType(parser,decl)
                    self.fields.append( t )
                    self.dataSize += t.getDataSize()

            elif type(node.type.type) == c_ast.Union:
                self.name = node.name
                self.dataType =  "Union"
                struct = node.type.type;
                self.dataSize = 0
                for decl in struct.decls:
                    t = CType(parser,decl)
                    self.fields.append( t )
                    size = t.getDataSize()
                    if size > self.dataSize:
                        self.dataSize = size

            elif type(node.type.type) == c_ast.IdentifierType:
                self.fields.append( CType(parser,node.type.type) )

            elif type(node.type.type) == c_ast.Enum:
                pass

            else:
                raise Exception("Unknown typedef node.type.type - " + str(type(node.type.type)) )

        elif type(node) == c_ast.Decl:
            self.processDecl(node)

        elif type(node) == c_ast.TypeDecl:
            self.processTypeDecl(node)

        else:
            raise Exception("Unknown node - " + str(type(node)) )

    def getDataSize(self):

        size = self.dataSize

        if self.arraySize > 0:
            size *= self.arraySize

        return size

    def computeOffsets(self, offset = 0):

        if self.bitFieldSize > 0:
            if self.bitFieldSibling == None:
                self.offset = offset
            else:
                self.offset = self.bitFieldSibling.offset
            return

        self.offset = offset
        if self.dataType == "Struct":
            baseOffset = 0
            for f in self.fields:
                f.computeOffsets(baseOffset)
                baseOffset += f.getDataSize()

    def print(self,indent=0):
        print(" " * indent + str(self.offset) + " " + self.name + " " + self.dataType + " " + str(self.dataSize) + (" [" + str(self.arraySize) + "]" if self.arraySize != 0  else "") + " " + str(self.getDataSize()) +(" :" + str(self.bitFieldSize) if self.bitFieldSize != 0  else ""))

        for f in self.fields:
            f.print(indent+4)

    def evaluateBinaryOp(self, dim):
        pass

    def processTypeDecl(self,node):

        if self.name == "":
            self.name = node.declname

        if type(node.type) == c_ast.IdentifierType:
        
            identifier = node.type
            if identifier.names[0] in ('char', 'short', 'int', 'long', 'float', 'double', 'signed', 'unsigned' ):
                if len(identifier.names) == 1:
                    self.dataType = identifier.names[0]
                    self.dataSize = getTypeSize(identifier.names[0])
                elif len(identifier.names) == 2 and identifier.names[0] in ('signed', 'unsigned' ):
                    self.dataType = identifier.names[0] + " " + identifier.names[1]
                    self.dataSize = getTypeSize(identifier.names[1])
                elif len(identifier.names) == 2 and identifier.names[0] == 'long' and identifier.names[1] == 'long':
                    self.dataType = identifier.names[0] + " " + identifier.names[1]
                    self.dataSize = 8
                else:
                    raise Exception( "Unknown type - " + str(identifier.names))

            elif len(identifier.names) == 1 and identifier.names[0] in self.parser.typedefs:
                self.processTypeDecl( self.parser.typedefs[identifier.names[0]].type )

            else:
                raise Exception("Unknown identifier type - " + str(identifier.names))

        elif type(node.type) == c_ast.Enum:
            self.dataType = "int"
            self.dataSize = getTypeSize(self.dataType)

        elif type(node.type) == c_ast.Struct:

            struct = node.type;

            if struct.decls == None:
                if struct.name in self.parser.structs:
                    struct = self.parser.structs[struct.name]
                else:
                    raise Exception("Unknown Struct - " + struct.name)

            if self.name == "":
                self.name = struct.name
            self.dataType =  "Struct"

            self.dataSize = 0
            for decl in struct.decls:
                t = CType(self.parser,decl)
                self.fields.append( t )
                self.dataSize += t.getDataSize()

        elif type(node.type) == c_ast.Union:

            union = node.type;

            if union.decls == None:
                if union.name in self.parser.unions:
                    union = self.parser.unions[union.name]
                else:
                    raise Exception("Unknown Union - " + union.name)

            if self.name == "":
                self.name = union.name
            self.dataType =  "Union"

            self.dataSize = 0
            for decl in union.decls:
                t = CType(self.parser,decl)
                self.fields.append( t )
                size = t.getDataSize()
                if size > t.dataSize:
                    self.dataSize = size


        else:
            raise Exception("Unknown typedecl subtype - " + str(type(node.type)) )


    def processDecl(self,node):

        self.name = node.name

        if node.bitsize != None:
            self.bitFieldSize = int(node.bitsize.value)
            self.underlyingBitFieldType = node.bitsize.type
            self.processTypeDecl(node.type)
            if CType.lastBitField == None:
                self.bitFieldOffset = 0
            else:
                self.bitFieldOffset = CType.lastBitField.bitFieldOffset + CType.lastBitField.bitFieldSize
                self.dataSize = 0
            self.bitFieldSibling = CType.lastBitField
            CType.lastBitField = self

        else:
            if type(node.type) == c_ast.TypeDecl:
                self.processTypeDecl(node.type )

            elif type(node.type) == c_ast.Struct:

                struct = node.type;

                if struct.decls == None:
                    if struct.name in self.parser.structs:
                        struct = self.parser.structs[struct.name]
                    else:
                        raise Exception("Unknown Struct - " + struct.name)

                self.dataSize = 0
                for decl in struct.decls:
                    self.fields.append( CType(self.parser,decl) )
                    self.dataSize += decl.getDataSize()

            elif type(node.type) == c_ast.ArrayDecl:

                arr = node.type
                self.arraySize = self.parser.evaluate(arr.dim)
                self.processTypeDecl( arr.type )

            else:
                raise Exception("Unknown typedecl subtype - " + str(type(node.type)) )

            CType.lastBitField = None

    def _findAllFields(self, name, offset, arraySuffix = ""):
        lst = []
        name = name + '.' + self.name + arraySuffix
        if not (self.dataType == 'Struct' or self.dataType == 'Union'):
            field = FieldInstance( name, self, offset)
            lst.append( field )

        for f in self.fields:
            lst.extend( f._findAllFields( name, offset + f.offset ) )
        return lst

    # Process * (or struct.*, etc)
    def findAllFields(self):
        if self.allFields == None:
            lst = []
            name = self.name
            for f in self.fields:
                if f.arraySize > 0 and f.dataType != 'char':
                    for i in range(0,f.arraySize):
                        lst.extend( f._findAllFields( name, f.offset + i * f.dataSize, "[" + str(i) + "]" ) ) # array element
                else:
                    lst.extend( f._findAllFields( name, f.offset ) )  # field
            self.allFields = lst
        return self.allFields

    def match( self, fieldName, columnName):
        if fieldName == columnName:
            return True
        else:
            return False

    def findField(self, column ):

        # Main structure name is optional, but we require it for matching

        if column[0:len(self.name)] != self.name:
            columnExpr = self.name + "." + column
        else:
            columnExpr = column

        rexText = self.makeRegexp( columnExpr )
        rex = re.compile(rexText)
        fields = []
        for f in self.findAllFields():
            if re.match( rex, f.name ):
                fields.append( f )
        return fields

    def makeRegexp( self, exp ):
        s = ""
        for c in exp:
            if c in ('.', '?', '[', ']'):
                s += '\\' + c
            elif c == '*':
                s += '.*'
            else:
                s += c

        return s

    def findFields( self, columns ):

        fields = []
        for c in columns:
            l = self.findField(c)
            if len(l) == 0:
                raise Exception("Unknown column name '{0}'".format(c))
            fields.extend( self.findField(c) )

        return fields


class StructParser:
    """ Parsing class """

    def __init__(self, *args, **kwargs):
        self.typedefs = {}
        self.unions = {}
        self.structs = {}
        self.enums = {}
        self.enumValues = {}
        self.fields = []
        return super().__init__(*args, **kwargs)

    def evaluate(self, node):
        
        if type(node) == c_ast.Constant:
            if node.type == "int":
                return int(node.value)
            elif node.type == "char":
                return ord(eval(node.value))
            else:
                raise Exception("Unknown constant type - " + node.type )

        elif type(node) == c_ast.BinaryOp:
            if node.op == '+':
                return self.evaluate(node.left) + self.evaluate(node.right)
            elif node.op == '-':
                return self.evaluate(node.left) - self.evaluate(node.right)
            elif node.op == '*':
                return int(self.evaluate(node.left) * self.evaluate(node.right))
            elif node.op == '/':
                return int(self.evaluate(node.left) / self.evaluate(node.right))
            elif node.op == '<<':
                return int(self.evaluate(node.left) << self.evaluate(node.right))
            elif node.op == '>>':
                return int(self.evaluate(node.left) >> self.evaluate(node.right))
            else:
                raise Exception("Unkown binaryOp type - " + node.op )

        elif type(node) == c_ast.ID:
            name = node.name;
            return self.enumValues[name]

        elif type(node) == c_ast.UnaryOp:
            if node.op == '-':
                return -1 * self.evaluate( node.expr)
            else:
                raise Exception("Unkown unaryOp type - " + node.op )
        else:
            raise Exception("evaluate unknown node type - " + node )

    def addEnumValues(self,node):
        value = 0
        for e in node.values.enumerators:
            name = e.name

            if e.value != None:
                value = self.evaluate(e.value);

            self.enumValues[name] = value
            #Log( e.name, value )
            value += 1;
        pass

    def extract_types( self, node ):

        if type(node) == c_ast.Typedef:
            self.typedefs[node.name] = node
            if type(node.type.type) == c_ast.Struct:
                self.structs[node.type.type.name] = node.type.type
            if type(node.type.type) == c_ast.Union:
                self.unions[node.type.type.name] = node.type.type
        elif type(node) == c_ast.Struct:
            self.structs[node.name] = node
        elif type(node) == c_ast.Union:
            self.unions[node.name] = node
        elif type(node) == c_ast.Enum:
            self.addEnumValues(node);
            if ( node.name != None ):
                self.enum[node.name] = node
        else:
            for i,c in node.children():
                self.extract_types(c)

    def Parse(self, filename):

        if not os.path.exists(filename):
            raise Exception("File does not exist '{0}'".format(filename) )

        try:
            node = parse_file( filename, use_cpp = True )
        except c_parser.ParseError:
            e = sys.exc_info()[1]
            raise Exception("Parse error:" + str(e))

        if (not isinstance(node, c_ast.FileAST) or not isinstance(node.ext[-1], c_ast.Decl)):
            raise Exception("Not a valid declaration")

        if common.doLog:
            node.show()
        self.extract_types( node )    

    def MakeType(self, typename):

        node = self.typedefs[typename]

        t = CType(self, node)
        t.computeOffsets()
        if common.doLog:
            t.print()
        return t



# Output...
#   list of ...
#       name, offset, length, type, [bitfield?], [array_len], [enums]

#   bit fields, arrays, enums
#
#  select *
#       ms.simp1, ms.simp2, mi, msa[0].simp1, msa[0].simp2,..., e, sms.simp1, sms.simp2, bf.bf1, bf.bf2, ..., why.a, why.b, why.c, why[0].a, ...,

# 0   int x;
# 4   T2 t2_array[5] (len=5*8)
#     0   int t2int
#     4   short t2long
# 24 char s[20] len=20
# 44 struct x  len=5
#     0 int y;
#     4 char z;


