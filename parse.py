#!/bin/python3

""" Find all usages of some type
"""

import clang.cindex
from clang.cindex import CursorKind, TypeKind

def pp(node):
    """
    Return str of node for pretty print
    """
    return f'{node.displayname} ({node.kind}) [{node.location}]'

def find(node, kind, verbose=False):
    """
    Return all node's descendants of a certain kind
    """

    if verbose:
        print(pp(node))

    if node.kind == kind:
        yield node
    # Recurse for children of this node
    for child in node.get_children():
        yield from find(child, kind)

from dataclasses import dataclass
from typing import Any
@dataclass
class LocalVariable:
    type: Any = None
    name: Any = None
    children: Any = 0

def local_vars(type, varname):
    """
    Return a list of input variables for type t's fields, down to primitives
    """

    if type.kind == TypeKind.ELABORATED:
        td = type.get_declaration()
        children = list(td.get_children())
        for fd in children:
            yield from local_vars(fd.type, fd.displayname)
        yield LocalVariable(type, varname, len(children))
    elif type.kind == TypeKind.POINTER:
        # TODO: Currently inits all ptrs as single values. What about arrays?
        yield from local_vars(type.get_pointee(), f'{varname}_v')
        yield LocalVariable(type, varname, 1)
    elif type.kind == TypeKind.INT:
        yield LocalVariable(type, varname)
    elif type.kind == TypeKind.CHAR_S:
        yield LocalVariable(type, varname)
    else:
        print('local variables unhandled kind', type.kind)
def main():
    filename = 'main.c'

    index = clang.cindex.Index.create()
    tu = index.parse(filename)
    print('Translation unit:', tu.spelling)
    
    cur = tu.cursor

    funcdefs = find(cur, CursorKind.FUNCTION_DECL)
    last_funcdef = max(funcdefs, key=lambda n: n.location.file.name == filename and n.location.line)
    print(f'last: {pp(last_funcdef)}')

    parmesan = list(find(last_funcdef, CursorKind.PARM_DECL))
    for parm in parmesan:
        locals = list(local_vars(parm.type, parm.displayname))
        print(parm.type.spelling, pp(parm), locals)

if __name__ == "__main__":
    main()
