# From https://github.com/mastermay/sql-parser/tree/master/py-sql-parser

class node:
 
    def __init__(self, data):
        self._data = data
        self._children = []
 
    def getdata(self):
        return self._data
 
    def getchildren(self):
        return self._children
 
    def add(self, node):
        self._children.append(node)
 
    def find(self,name):
        if self._data == name:
            return self
        else:
            for c in self._children:
                match = c.find(name)
                if match != None:
                    return match
        return None

    def print_node(self, prefix):
        print( '  '*prefix,'+',self._data)
        for child in self._children:
            child.print_node(prefix+1)
