import compiler
from compiler.ast import *
from free_vars import *

def case(expr, Node):
    return isinstance(expr, Node)

#freeMap is a mapping between function names and its list of permutated arguments
freeMap = {}

#Need heap. A set of variable names that need to be heaped
heapMeh = set([])
reduceSet = set([])

def listify(s):
    return list(s)

#heap(ast) is the entry point. It returns an ast with heapified variables
def heap(ast):
    global reduceSet
    heapifyAST = heapify(ast)
    reduceSet = heapMeh.copy()
    return transform(heapifyAST)

#Heapify calculates
def heapify(expr):
    global heapMeh
    if case(expr, Const):
        return expr
    elif case(expr, Name):
        return expr
    elif case(expr, Add):
        return Add((heapify(expr.left), heapify(expr.right)))
    elif case(expr, CallFunc):
        return CallFunc(expr.node, expr.args, None, None)
    elif case(expr, Module):
        return Module(None, heapify(expr.node))
    elif case(expr, Stmt):
        h = map(lambda x: heapify(x), expr.nodes)
        return Stmt(h)
    elif case(expr, Printnl):
        h = map(lambda x: heapify(x), expr.nodes)
        return Printnl(h, None)
    elif case(expr, Assign):
        val = heapify(expr.expr)
        nodes = heapify(expr.nodes[0])
        return Assign([nodes],val)
    elif case(expr, AssName):
        return expr
    elif case(expr, Discard):
        return Discard(heapify(expr.expr))
    elif case(expr, UnarySub):
        return UnarySub(heapify(expr.expr))
    elif case(expr, Compare):
        lft = heapify(expr.expr)
        rgt = heapify(expr.ops[0][1])
        operator = expr.ops[0][0] #Operator can be ==, !=, is
        return Compare(lft,[(operator,rgt)])
    elif case(expr, Lambda):
        (free, bound) = free_vars(expr,set([]))
        heapMeh |= free
        return Lambda(expr.argnames, expr.defaults, expr.flags, heapify(expr.code))
    elif case(expr, Function):
        (free, bound) = free_vars(expr,set([]))
        heapMeh |= free
        return Function(expr.decorators, expr.name, expr.argnames, expr.defaults, expr.flags, expr.doc, heapify(expr.code))
    elif case(expr, Return):
        return Return(heapify(expr.value))
    elif case(expr, Or):
        h = map(lambda x:heapify(x), expr.nodes)
        return Or(h)
    elif case(expr, And):
        h = map(lambda x:heapify(x), expr.nodes)
        return And(h)
    elif case(expr, List):
        h = map(lambda x:heapify(x), expr.nodes)
        return List(h)
    elif case(expr, Not):
        return Not(heapify(expr.expr))
    elif case(expr, Dict):
        d = []
        for i in range(0,len(expr.items)):
            key = heapify(expr.items[i][0])
            val = heapify(expr.items[i][1])
            d.append((key,val))
        return Dict(d)
    elif case(expr, Subscript):
        l = map(lambda x:heapify(x), expr.subs)
        return Subscript(expr.expr, expr.flags, l)
    elif case(expr, IfExp):
        condition = heapify(expr.test)
        then = heapify(expr.then)
        elseC = heapify(expr.else_)
        return IfExp(condition,then,elseC)
    elif case(expr, If):
        test = heapify(expr.tests[0][0])
        then = heapify(expr.tests[0][1])
        else_ = heapify(expr.else_)
        return If([(test,then)], else_)
    elif case(expr, While):
        print expr.test
    else:
        print "heapify experienced an unknown node called: "+str(expr)
        return None

#Takes in a heapified ast and preforms the translation of static to heap
def transform(expr):
    global reduceSet
    if case(expr, Const):
        return expr
    elif case(expr, Name):
        if expr.name in heapMeh:
            return Subscript(Name(expr.name), 'OP_APPLY', [Const(0)])
        return expr
    elif case(expr, Add):
        return Add((transform(expr.left), transform(expr.right)))
    elif case(expr, CallFunc):
        return CallFunc(expr.node, expr.args, None, None)
    elif case(expr, Module):
        return Module(None, transform(expr.node))
    elif case(expr, Stmt):
        f = []
        c = reduceSet.copy()
        for elem in c:
            f.append(Assign([AssName(elem, 'OP_ASSIGN')], List([Const(0)])))
            reduceSet -= set([elem])
        h = map(lambda x: transform(x), expr.nodes)
        return Stmt(f+h)
    elif case(expr, Printnl):
        h = map(lambda x: transform(x), expr.nodes)
        return Printnl(h, None)
    elif case(expr, Assign):
        if case(expr.nodes[0], Subscript):
            return Assign([transform(expr.nodes[0])], transform(expr.expr))
        lvalue = expr.nodes[0].name
        if lvalue in heapMeh:
            return Assign([Subscript(Name(lvalue), 'OP_ASSIGN', [Const(0)])], transform(expr.expr))
        val = transform(expr.expr)
        nodes = transform(expr.nodes[0])
        return Assign([nodes],val)

    elif case(expr, AssName):
        return expr
    elif case(expr, Discard):
        return Discard(transform(expr.expr))
    elif case(expr, UnarySub):
        return UnarySub(transform(expr.expr))
    elif case(expr, Compare):
        lft = transform(expr.expr)
        rgt = transform(expr.ops[0][1])
        operator = expr.ops[0][0] #Operator can be ==, !=, is
        return Compare(lft,[(operator,rgt)])
    elif case(expr, Lambda):
        return Lambda(expr.argnames, expr.defaults, expr.flags, transform(expr.code))
    elif case(expr, Function):
        return Function(expr.decorators, expr.name, expr.argnames, expr.defaults, expr.flags, expr.doc, transform(expr.code))
    elif case(expr, Return):
        return Return(transform(expr.value))
    elif case(expr, Or):
        h = map(lambda x:transform(x), expr.nodes)
        return Or(h)
    elif case(expr, And):
        h = map(lambda x:transform(x), expr.nodes)
        return And(h)
    elif case(expr, List):
        h = map(lambda x:transform(x), expr.nodes)
        return List(h)
    elif case(expr, Not):
        return Not(transform(expr.expr))
    elif case(expr, Dict):
        d = []
        for i in range(0,len(expr.items)):
            key = transform(expr.items[i][0])
            val = transform(expr.items[i][1])
            d.append((key,val))
        return Dict(d)
    elif case(expr, Subscript):
        l = map(lambda x:transform(x), expr.subs)
        return Subscript(expr.expr, expr.flags, l)
    elif case(expr, IfExp):
        condition = transform(expr.test)
        then = transform(expr.then)
        elseC = transform(expr.else_)
        return IfExp(condition,then,elseC)
    elif case(expr, If):
        test = transform(expr.tests[0][0])
        then = transform(expr.tests[0][1])
        else_ = transform(expr.else_)
        return If([(test,then)], else_)
    else:
        print "heapify experienced an unknown node called: "+str(expr)
        return None

# ast = compiler.parseFile("/Users/michaeltang/Desktop/xfc.py")
# print heap(ast)
# print heapMeh
