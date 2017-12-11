import compiler
from compiler.ast import *
from explicate import *

def case(n, Class):
    return isinstance(n, Class)

escapeSet = set([])
def traverse(G):
    global escapeSet
    #print G
    #Add return escape point
    if 'return' in G:
        for i in range(len(G['return'])):
            removedVal = G['return'][i]
            if case(removedVal, Name):
                removedVal = removedVal.name
            elif case(removedVal, Const):
                removedVal = removedVal.value
            elif case(removedVal, Bool):
                removedVal = removedVal.expr
            escapeSet |= set([removedVal])
        del G['return']
    
    
    complete = False
    while not complete:
        complete = True
        for node in G:
            #print node, G[node][0]
            raw = G[node][0]
            if case(raw, Name):
                raw = raw.name
            else:
                continue
            if node.name in escapeSet and raw not in escapeSet:
                escapeSet |= set([raw])
                complete = False


    return escapeSet
