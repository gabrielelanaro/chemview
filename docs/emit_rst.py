'''Module to read a python module and emit restructuredText documentation.

This module is based on ast.

Requires codegen
'''

import ast
import codegen
import textwrap

class CallCollector(ast.NodeVisitor):
    '''Collect documentation members as ast nodes'''
    
    def __init__(self):
        ''' Initialization '''
        self.elements = []
        self.calls = []
        self.current = ''

    def visit_FunctionDef(self, node):
        # Function definition
        self.elements.append({'type': 'function',
                              'docstring': ast.get_docstring(node),
                              'name': node.name,
                              'node': node})

    def visit_ClassDef(self, node):
        self.elements.append({'type': 'class',
                              'name': node.name,
                              'node': node,
                              'docstring': ast.get_docstring(node)})

        
    def generic_visit(self, node):
        if self.current is not None:
            # print "warning: {} node in function expression not supported".format(
            #     node.__class__.__name__)
            pass
        super(CallCollector, self).generic_visit(node)


def indent(text, amount=4):
    return '\n'.join(amount * ' ' + line for line in text.splitlines())
        
def format_function(node):
    template = textwrap.dedent('''
    .. py:function:: {name}({arguments})
    
    {documentation}
    ''')
    doc = ast.get_docstring(node)
    doc = indent(doc) if doc else ''
    
    return template.format(name=node.name,
                           arguments=codegen.to_source(node.args),
                           documentation=doc)

def format_method(name, node):
    template = textwrap.dedent('''
    .. py:method:: {name}({arguments})
    
    {documentation}
    ''')
    doc = ast.get_docstring(node)
    doc = indent(doc) if doc else ''
    return template.format(name=name,
                           arguments=codegen.to_source(node.args),
                           documentation=doc)
import fnmatch

def format_class(node, exclude=['_*']):
    template = textwrap.dedent('''
    .. py:class:: {name}
    {documentation}
    ''')

    methods = []
    for attr_node in node.body:
        if isinstance( attr_node, ast.FunctionDef):
            if any(fnmatch.fnmatch(attr_node.name, ex)
                   for ex in exclude):
                continue
            # adding the method to the rendered part
            methods.append(
                format_method(node.name + '.' + attr_node.name,
                              attr_node))
    doc = ast.get_docstring(node)
    doc = indent(doc) if doc else ''
    ret =  template.format(name=node.name,
                           documentation=doc)

    ret += '\n'.join(methods)
    return ret


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    tree = ast.parse(open(filename).read())

    cc = CallCollector()
    cc.visit(tree)

    for e in cc.elements:
        if e['type'] == 'function':
            print format_function(e['node'])
        if e['type'] == 'class':
            print format_class(e['node'])
