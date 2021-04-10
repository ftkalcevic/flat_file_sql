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
    def __init__(self, node):

        pass

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

    def processTypeDecl(self,parser,node, bitsize=0, arraySize=0):

        name = node.declname

        if type(node.type) == c_ast.IdentifierType:
            
            identifier = node.type
            if identifier.names[0] in ('char', 'short', 'int', 'long', 'float', 'double', 'signed', 'unsigned' ):
                if len(identifier.names) == 1:
                    datatype = identifier.names[0]
                    size = getTypeSize(identifier.names[0])
                elif len(identifier.names) == 2 and identifier.names[0] in ('signed', 'unsigned' ):
                    datatype = identifier.names[0] + " " + identifier.names[1]
                    size = getTypeSize(identifier.names[1])
                elif len(identifier.names) == 2 and identifier.names[0] == 'long' and identifier.names[1] == 'long':
                    datatype = identifier.names[0] + " " + identifier.names[1]
                    size = 8
                else:
                    raise Exception( "Unknown type - " + str(identifier.names))

                parser.addField( size, datatype, name, bitsize=bitsize, arraySize=arraySize )

            elif len(identifier.names) == 1 and identifier.names[0] in parser.typedefs:
                self.makeType( parser, parser.typedefs[identifier.names[0]] )
            else:
                raise Exception("Unknown identifier type - " + str(identifier.names))

        elif type(node.type) == c_ast.Struct:

            struct = node.type;

            if struct.decls == None:
                if struct.name in parser.structs:
                    struct = parser.structs[struct.name]
                else:
                    raise Exception("Unknown Struct - " + struct.name)

            for decl in struct.decls:
                self.processDecl(parser,decl)

        else:
            raise Exception("Unknown typedecl subtype - " + str(type(node.type)) )


    def processDecl(self,parser,node):

        name = node.name
        bitsize = 0
        if node.bitsize != None:
            bitsize = int(node.bitsize.value)

        if type(node.type) == c_ast.TypeDecl:
            self.processTypeDecl(parser, node.type, bitsize)

        elif type(node.type) == c_ast.Struct:

            struct = node.type;

            if struct.decls == None:
                if struct.name in parser.structs:
                    struct = parser.structs[struct.name]
                else:
                    raise Exception("Unknown Struct - " + struct.name)

            for decl in struct.decls:
                self.processDecl(parser,decl)

        elif type(node.type) == c_ast.ArrayDecl:

            arr = node.type
            arraySize = self.getArraySize(arr.dim)
            parser.addField( 0, "", name, arraySize=arraySize )
            self.processTypeDecl(parser,arr.type, arraySize=arraySize)

        else:
            raise Exception("Unknown typedecl subtype - " + str(type(node.type)) )

        datatype = node.type

    def makeType(self,parser,node,arraySize=0,level=1):

        if type(node) == c_ast.Typedef:
            if type(node.type.type) == c_ast.Struct:
                struct = node.type.type;
                for decl in struct.decls:
                    self.makeType(parser,decl,arraySize, level)
            elif type(node.type.type) == c_ast.Union:
                raise Exception("Unions not supported");
            elif type(node.type.type) == c_ast.IdentifierType:
                self.makeType(parser, node.type.type, arraySize, level)
            elif type(node.type.type) == c_ast.Enum:
                pass
            else:
                raise Exception("Unknown typedef node.type.type - " + str(type(node.type.type)) )

        elif type(node) == c_ast.Decl:
            self.processDecl(parser,node, level)

#        elif type(node) == c_ast.ArrayDecl:
#            arraySize = self.getArraySize(node.dim)
#            self.makeType(parser,node.type, arraySize = arraySize)

        elif type(node) == c_ast.IdentifierType:
            pass

        else:
            raise Exception("Unknown node - " + str(type(node)) )
             
        pass

class StructParser:
    """ Parsing class """

    def __init__(self, *args, **kwargs):
        self.typedefs = {}
        self.unions = {}
        self.structs = {}
        self.fields = []
        return super().__init__(*args, **kwargs)


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
        else:
            for i,c in node.children():
                self.extract_types(c)

    def addField( self, size, datatype, name, arraySize=None, bitsize=None ):
        desc = str(size) + " " + datatype
        if arraySize != None:
            desc = desc + "[" + str(arraySize) + "]"
        if bitsize != None:
           if bitsize > 0:
                desc = desc + ":" + str(bitsize)
        desc += " " + name
        print(desc)

        field = { 'offset':0, 'size':size, 'datatype':datatype, 'arraySize': arraySize, 'bitsize': bitsize}
        self.fields.append(field)

        return field

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

        node.show(attrnames=True,showcoord=True)
        self.extract_types( node )    

    def MakeType(self, typename):

        node = self.typedefs[typename]

        t = CType(self, node)


if __name__ == "__main__":

    #if len(sys.argv) > 1:
    #    c_decl = sys.argv[1]
    #else:
    #    c_decl = "char *(*(**foo[][8])())[];"

    parser = StructParser()
    parser.Parse("test.h")

    print( "typedefs" )
    for k in parser.typedefs:
        print("    "+k)
    print( "structs" )
    for k in parser.structs:
        print("    "+k)
    print( "unions" )
    for k in parser.unions:
        print("    "+k)

    parser.MakeType("T1")



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


