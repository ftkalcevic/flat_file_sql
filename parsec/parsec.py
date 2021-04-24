import copy
import sys
import io

from pycparser import c_parser, c_ast

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

class CType:
    def __init__(self, parser, node):
        self.fields = []
        self.arraySize = 0
        self.bitFieldSize = 0
        self.dataType = ""
        self.dataSize = 0
        self.name = ""
        self.offset = 0
        self.parser = parser

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
                raise Exception("Unions not supported");

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

    def getArraySize(self,dim):
        
        if type(dim) == c_ast.Constant:
            assert dim.type == "int"
            return int(dim.value)
        elif type(dim) == c_ast.BinaryOp:

            if dim.op == '+':
                return self.getArraySize(dim.left) + self.getArraySize(dim.right)
            elif dim.op == '-':
                return self.getArraySize(dim.left) - self.getArraySize(dim.right)
            elif dim.op == '*':
                return int(self.getArraySize(dim.left) * self.getArraySize(dim.right))
            elif dim.op == '/':
                return int(self.getArraySize(dim.left) / self.getArraySize(dim.right))
            else:
                raise Exception("Unkown binaryOp type - " + dim.op )

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

        else:
            raise Exception("Unknown typedecl subtype - " + str(type(node.type)) )


    def processDecl(self,node):

        self.name = node.name

        if node.bitsize != None:
            assert node.bitsize == None
            self.bitFieldSize = int(node.bitsize.value)

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

    def _findAllFields(self, name):
        lst = []
        name = name + '.' + self.name
        lst.extend( [name, self.offset] )
        for f in self.fields:
            lst.extend( f._findAllFields( name ) )
        return lst

    def findAllFields(self):
        lst = []
        name = self.name
        for f in self.fields:
            lst.extend( f._findAllFields( name ) )
        return lst

    def findFields( self, columns ):

        fields = []
        for c in columns:
            if c == '*':
                fields.extend( self.findAllFields() )

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
            assert node.type == "int"
            return int(node.value)
        elif type(node) == c_ast.BinaryOp:
            if node.op == '+':
                return self.evaluate(node.left) + self.evaluate(node.right)
            elif node.op == '-':
                return self.evaluate(node.left) - self.evaluate(node.right)
            elif node.op == '*':
                return int(self.evaluate(node.left) * self.evaluate(node.right))
            elif node.op == '/':
                return int(self.evaluate(node.left) / self.evaluate(node.right))
            else:
                raise Exception("Unkown binaryOp type - " + node.op )
        elif type(node) == c_ast.ID:
            name = node.name;
            return self.enumValues[name]
        else:
            raise Exception("evaluate unknown node type - " + node )

    def addEnumValues(self,node):
        value = 0
        for e in node.values.enumerators:
            name = e.name

            if e.value != None:
                value = self.evaluate(e.value);

            self.enumValues[name] = value
            print( e.name, value )
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

        with io.open(filename) as f:
            text = f.read()

        try:
            parser = c_parser.CParser()
            node = parser.parse(text, filename)
        except c_parser.ParseError:
            e = sys.exc_info()[1]
            raise Exception("Parse error:" + str(e))

        if (not isinstance(node, c_ast.FileAST) or not isinstance(node.ext[-1], c_ast.Decl)):
            raise Exception("Not a valid declaration")

        node.show()
        self.extract_types( node )    

    def MakeType(self, typename):

        node = self.typedefs[typename]

        t = CType(self, node)
        t.computeOffsets()
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


