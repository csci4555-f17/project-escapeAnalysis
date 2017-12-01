import compiler
from compiler.ast import *

def case(expr, Class):
    return isinstance(expr, Class)

#Extend the AST node with booleans
class Bool():
    def __init__(self,expr):
        self.expr = expr
    def __repr__(self):
        return 'Bool(\'%s\')' % self.expr

def reduceLambda(expr,acc):
    if case(expr, Const):
        acc += str(expr.value)
        return acc
    elif case(expr, Bool):
        acc += str(expr.expr)
        return acc
    elif case(expr, Name):
        acc += str(expr.name)
        return acc
    elif case(expr, Add):
        lft = reduceLambda(expr.left,acc)
        rgt = reduceLambda(expr.right,acc)
        rtn = lft+"+"+rgt
        return rtn
    elif case(expr, UnarySub):
        val = reduceLambda(expr.expr,acc)
        rtn = "-"+val
        return rtn

    elif case(expr, Or):
        x = str(reduceLambda(expr.nodes[0],acc))+" or "+str(reduceLambda(expr.nodes[1],acc))
        for i in range(2, len(expr.nodes)):
            x += " or "+str(reduceLambda(expr.nodes[i],acc))
        return x

    elif case(expr, And):
        x = str(reduceLambda(expr.nodes[0],acc))+" and "+str(reduceLambda(expr.nodes[1],acc))
        for i in range(2, len(expr.nodes)):
            x += " and "+str(reduceLambda(expr.nodes[i],acc))
        return x

    elif case(expr, Not):
        val = str(reduceLambda(expr.expr, acc))
        return "not "+val

    else:
        print "Reduce Lambda experienced a uncaught node: "+str(expr)
