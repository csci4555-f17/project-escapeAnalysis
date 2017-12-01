import compiler
from compiler.ast import *
from free_vars import *

#Closure map. A dict mapping function names to its free vars
closureMap = {}
#Free var adoption. A stack data structure for potential lambdas
adoptionStack = []
#List of new order of statements where functions are promoted in position
promotionStmt = []


LAMBDA = "lambda_"
lambdaCounter = [0]

class CreateClosure():
    def __init__(self,f,fvs):
        self.function = f
        self.freeVars = fvs
    def __repr__(self):
        return 'CreateClosure(%s, %s)' % (self.function, self.freeVars)
class GetFunPtr():
    def __init__(self,f):
        self.function = f
    def __repr__(self):
        return 'GetFunPtr(%s)' % (self.function)
class GetFreeVar():
    def __init__(self,fvs):
        self.freeVars = fvs
    def __repr__(self):
        return 'GetFreeVar(%s)' % (self.freeVars)
class FunctionLift():
    def __init__(self,e):
        self.expr = e
    def __repr__(self):
        return 'FunctionLift(%s)' % (self.expr)

def requestLambdaVarName():
    name = LAMBDA+str(lambdaCounter[0])
    lambdaCounter[0] += 1
    #Moving stack placement to the responsibility of compile

    return name

def Sequence(stmt):
    promotionStmt.append(stmt)

def pushFree(s):
    adoptionStack.append(s)
def popFree():
    return adoptionStack.pop() if len(adoptionStack) > 0 else set([])


FREEVAR = "freeVar"
freeVarListCounter = [0]
def requestFreeVarListName():
    name = FREEVAR+str(freeVarListCounter[0])
    freeVarListCounter[0] += 1
    return name

def case(expr, Node):
    return isinstance(expr, Node)

#TODO: Assignment to lambda needs to point to a create_closure node. CallFunc needs get_fun_ptr and get_closure node. Figure a
#way to bringup lambda as top level at the stmt list

def close(ast):
    close = closure(ast)
    lift = liftFunction(close)
    return (lift, closureMap)

def closure(expr):
    if case(expr, Const):
        return expr
    elif case(expr, Name):
        return expr
    elif case(expr, Add):
        return Add((closure(expr.left), closure(expr.right)))
    elif case(expr, CallFunc):
        val = closure(expr.node)
        if case(expr.node, Lambda):
            functionName = val.function
            p = popFree()
            closureMap[functionName] = p
            return CallFunc(GetFunPtr(Name(functionName)), [GetFreeVar(Name(functionName))]+expr.args, None, None)
        return CallFunc(GetFunPtr(Name(expr.node.name)), [GetFreeVar(Name(expr.node.name))]+expr.args, None, None)
    elif case(expr, Module):
        return Module(None, closure(expr.node))
    elif case(expr, Stmt):
        h = map(lambda x: closure(x), expr.nodes)
        return Stmt(h)
    elif case(expr, Printnl):
        h = map(lambda x: closure(x), expr.nodes)
        return Printnl(h, None)
    elif case(expr, Assign):
        val = closure(expr.expr)
        nodes = closure(expr.nodes[0])
        if case(expr.expr, Lambda):
            functionName = val.function
            p = popFree()
            closureMap[functionName] = p
            closureMap[nodes.name] = p

            val = CreateClosure(functionName, list(closureMap[functionName]))

        return Assign([nodes],val)
    elif case(expr, AssName):
        return expr
    elif case(expr, Discard):
        val = closure(expr.expr)
        if case(expr.expr, Lambda):
            p = popFree()
            closureMap[val.nodes[0].name] = p
            Sequence(FunctionLift(val)) #Capture function and replace it with a closure
            val = CreateClosure(val.nodes[0].name, list(closureMap[val.nodes[0].name]))
        return Discard(val)
    elif case(expr, UnarySub):
        return UnarySub(closure(expr.expr))
    elif case(expr, Compare):
        lft = closure(expr.expr)
        rgt = closure(expr.ops[0][1])
        operator = expr.ops[0][0] #Operator can be ==, !=, is
        return Compare(lft,[(operator,rgt)])
    #Note that lambda now break python rules
    elif case(expr, Lambda):
        (free, bound) = free_vars(expr, set([]))
        pushFree(free)
        name = requestFreeVarListName()
        f = []
        i = 0
        for elem in free:
            f.append( Assign([AssName(elem, 'OP_ASSIGN')], Subscript(Name(name), 'OP_APPLY', [Const(i)])) )
            i += 1
        expr.argnames = [name]+expr.argnames if expr.argnames != () else [name]

        fname = requestLambdaVarName()
        closureMap[fname] = free

        #Returnify. Need to explicaitiy search and return the last calculated node
        exprCode = returnify(expr.code)

        Sequence(FunctionLift(Assign([AssName(fname, 'OP_ASSIGN')], Lambda(expr.argnames, expr.defaults, expr.flags, Stmt(f+[closure(exprCode)])))))
        Sequence(Assign([AssName(fname, 'OP_ASSIGN')], CreateClosure(fname, list(free))))
        return CreateClosure(fname, list(free))
        # (free, bound) = free_vars(expr,set([]))
        # pushFree(free)
        # name = requestFreeVarListName()
        # f = []
        # i = 0
        # for elem in free:
        #     f.append( Assign([AssName(elem, 'OP_ASSIGN')], Subscript(Name(name), 'OP_APPLY', [Const(i)])) )
        #     i += 1
        # expr.argnames = [name]+expr.argnames if expr.argnames != () else [name]
        #
        # fname = requestLambdaVarName()
        # closureMap[fname] = free
        # return Assign([AssName(fname, 'OP_ASSIGN')], Lambda(expr.argnames, expr.defaults, expr.flags, Stmt(f+[closure(expr.code)])))
    elif case(expr, Function):
        #Find free vars
        (free, bound) = free_vars(expr,set([]))
        name = requestFreeVarListName()
        fname = requestLambdaVarName()
        f = []
        i = 0
        #add statements to get free vars
        for elem in free:
            f.append( Assign([AssName(elem, 'OP_ASSIGN')], Subscript(Name(name), 'OP_APPLY', [Const(i)])) )
            i += 1
        body = closure(expr.code)
        recursiveClosure = [Assign([AssName(expr.name, 'OP_ASSIGN')], CreateClosure(fname, list(free)))]
        body = Stmt(f+recursiveClosure+body.nodes)
        expr.argnames = [name]+expr.argnames if expr.argnames != () else [name]

        #Connect name with free set
        closureMap[fname] = free
        closureMap[expr.name] = free
        #Map lambda name with the function body
        Sequence( FunctionLift(Assign([AssName(fname, 'OP_ASSIGN')], Lambda(expr.argnames, expr.defaults, expr.flags, body ))) )

        #Assign original function name to closure
        return Assign([AssName(expr.name, 'OP_ASSIGN')], CreateClosure(fname, list(free)))
    elif case(expr, Return):
        return Return(closure(expr.value))
    elif case(expr, Or):
        h = map(lambda x:closure(x), expr.nodes)
        return Or(h)
    elif case(expr, And):
        h = map(lambda x:closure(x), expr.nodes)
        return And(h)
    elif case(expr, List):
        h = map(lambda x:closure(x), expr.nodes)
        return List(h)
    elif case(expr, Not):
        return Not(closure(expr.expr))
    elif case(expr, Dict):
        d = []
        for i in range(0,len(expr.items)):
            key = closure(expr.items[i][0])
            val = closure(expr.items[i][1])
            d.append((key,val))
        return Dict(d)
    elif case(expr, Subscript):
        l = map(lambda x:closure(x), expr.subs)
        return Subscript(expr.expr, expr.flags, l)
    elif case(expr, IfExp):
        condition = closure(expr.test)
        then = closure(expr.then)
        elseC = closure(expr.else_)
        return IfExp(condition,then,elseC)
    elif case(expr, If):
        test = closure(expr.tests[0][0])
        then = closure(expr.tests[0][1])
        else_ = closure(expr.else_)
        return If([(test,then)], else_)
    else:
        print "closure experienced an unknown node called: "+str(expr)
        return None

def liftFunction(expr):
    if case(expr, Module):
        return Module(None, liftFunction(expr.node))
    elif case(expr, Stmt):
        return Stmt(promotionStmt+expr.nodes)

def returnify(expr):
    last = expr.nodes[0]
    for node in expr.nodes:
        if case(node, Name) or case(node, Assign):
            last = expr.nodes[0]
    if case(last, Name):
        last = Return(last)
    elif case(last, Assign):
        name = Name(last.nodes[0].name)
        last = Return(name)

    return Stmt( expr.nodes + [last] )

# ast = compiler.parseFile("/Users/michaeltang/Desktop/xfc.py")
# print close(ast)
# print closureMap
