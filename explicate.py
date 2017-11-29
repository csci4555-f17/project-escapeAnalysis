#Given an ast, return an explicated ast
import compiler
from compiler.ast import *
from Closure import *

WHITE = "\x1B[0m"
RED = "\x1B[31m"
MAGENTA = "\x1B[35m"
YELLOW = "\x1B[33m"
GREEN = "\x1B[32m"
CYAN = "\x1B[36m"

def ColorPrint(expr,color):
    print color+str(expr)+WHITE

def case(expr,Class):
    return isinstance(expr,Class)

def isIrreducible(expr):
    return case(expr,Const) or case(expr,List) or case(expr,Bool)

def isIrreducibleInjectedSmall(expr):
    return (case(expr,InjectFrom) and expr.typ == 'INT') or (case(expr,InjectFrom) and expr.typ == 'BOOL')
def isIrreducibleInjectedBig(expr):
    return (case(expr,InjectFrom) and expr.typ == 'BIG')
def isIrreducibleInjected(expr):
    return (case(expr,InjectFrom) and expr.typ == 'INT') or (case(expr,InjectFrom) and expr.typ == 'BOOL') or (case(expr,InjectFrom) and expr.typ == 'BIG')

#Stack size counter. Determine stack size for each new stack frame.
stackFrame = {"main":0}
stackCounter = [0]
currentFunction = "main"

LAMBDA = "lambda_"
lambdaCounter = [0]

def requestLambdaVarName():
    name = LAMBDA+str(lambdaCounter[0])
    lambdaCounter[0] += 1
    #Moving stack placement to the responsibility of compile

    return name

#Extend the AST node with booleans
class Bool():
    def __init__(self,expr):
        self.expr = expr
    def __repr__(self):
        return 'Bool(\'%s\')' % self.expr

#AddList
class AddList():
    def __init__(self,expr):
        self.left = expr[0]
        self.right = expr[1]
    def __repr__(self):
        return 'AddList((%s,%s))' % (self.left, self.right)

#GetTag AST node
class GetTag():
    def __init__(self,arg):
        self.arg = arg
    def __repr__(self):
        return 'GetTag(%s)' % self.arg

#InjectFrom
class InjectFrom():
    def __init__(self,typ,arg):
        self.typ = typ
        self.arg = arg
    def __repr__(self):
        return 'InjectFrom(\'%s\',%s)' % (self.typ,self.arg)

#ProjectTo
class ProjectTo():
    def __init__(self,typ,arg):
        self.typ = typ
        self.arg = arg
    def __repr__(self):
        return 'ProjectTo(\'%s\',%s)' % (self.typ,self.arg)

#Let
class Let():
    def __init__(self,var,rhs,body):
        self.var = var
        self.rhs = rhs
        self.body = body
    def __repr__(self):
        return 'Let(%s,%s,%s)' % (self.var, self.rhs, self.body)

#TruthIdentity is a helper node for IfExp. Given a value of any type, it returns a boolean for the truthfulness of the value.
class TruthIdentity():
    def __init__(self,expr):
        self.expr = expr
    def __repr__(self):
        return 'TruthIdentity(%s)' % self.expr

def entry(ast):
    return (explicate(ast), stackFrame)
#Given an ast, return explicated-ast
def explicate(expr):
    global currentFunction
    #Const
    if case(expr,Const):
        return InjectFrom('INT',expr)
        #return expr
    #Bool
    elif case(expr,Name) and expr.name in ['True','False']:
        return InjectFrom('BOOL',Bool(expr.name))
        #return Bool(expr.name)
    #Name
    elif case(expr,Name):
        return Name(expr.name)
    #InjectFrom
    elif case(expr,InjectFrom):
        return expr
    #Module
    elif case(expr,Module):
        val = explicate(expr.node)
        return Module(None,val)
    #Stmt
    elif case(expr, Stmt):
        explicatedStmt = []
        for i in range(0,len(expr.nodes)):
            val = explicate(expr.nodes[i])
            explicatedStmt.append(val)
        return Stmt(explicatedStmt)
    #Printnl
    elif case(expr, Printnl):
        explicatedPrintStmt = []
        for i in range(0,len(expr.nodes)):
            val = explicate(expr.nodes[i])
            explicatedPrintStmt.append(val)
        return Printnl(explicatedPrintStmt,None)
    #AssName
    elif case(expr, AssName):
        return expr
    #Assign
    elif case(expr, Assign):
        stackFrame[currentFunction] += 1
        val = explicate(expr.expr)
        #Bind site for lambda, subsitute name
        if case(expr.expr, Lambda):
            val = val.expr
            lambdaCounter[0] -= 1

        nodes = explicate(expr.nodes[0])
        #varName = expr.nodes[0].name
        return Assign([nodes],val)
    #CallFunc
    elif case(expr,CallFunc):
        name = explicate(expr.node)
        args = map(lambda x: explicate(x), expr.args)
        return CallFunc(name,args,None,None)
    #UnarySub
    elif case(expr, UnarySub):
        val = explicate(expr.expr)
        return InjectFrom('INT',UnarySub(val))
    #Not
    elif case(expr,Not):
        val = explicate(expr.expr)
        return InjectFrom('BOOL',Not(val))

    #List
    elif case(expr,List):
        l = []
        for i in range(0,len(expr.nodes)):
            val = explicate(expr.nodes[i])
            l.append(val)
        return InjectFrom('BIG',List(l))
        #return List(l)
    #Dict
    elif case(expr,Dict):
        d = []
        for i in range(0,len(expr.items)):
            key = explicate(expr.items[i][0])
            val = explicate(expr.items[i][1])
            d.append((key,val))
        return InjectFrom('BIG',Dict(d))
        #return Dict(d)

    #Discard
    elif case(expr,Discard):
        val = explicate(expr.expr)
        return Discard(val)

    #IfExp
    elif case(expr, IfExp):
        condition = explicate(expr.test)
        then = explicate(expr.then)
        elseC = explicate(expr.else_)
        return IfExp(condition,then,elseC)

    #Subscript
    elif case(expr, Subscript):
        l = []
        for i in range(0,len(expr.subs)):
            val = explicate(expr.subs[i])
            l.append(val)
        return Subscript(expr.expr, expr.flags, l)

    #Compare - induct
    elif case(expr,Compare):
        lft = explicate(expr.expr)
        rgt = explicate(expr.ops[0][1])
        operator = expr.ops[0][0] #Operator can be ==, !=, is
        return InjectFrom('BOOL',Compare(lft,[(operator,rgt)]))

    #Add induct
    elif case(expr,Add):
        lft = explicate(expr.left)
        rgt = explicate(expr.right)

        c = InjectFrom('BOOL',Compare(GetTag(lft),[('==',InjectFrom('INT',Const(0)))]))
        d = InjectFrom('BOOL',Compare(GetTag(lft),[('==',InjectFrom('INT',Const(1)))]))
        #return IfExp(TruthIdentity(lftRgtIsPrim),InjectFrom('INT',Add((lft,rgt))), IfExp(TruthIdentity(lftRgtIsBig),InjectFrom('BIG',AddList((lft,rgt))),CallFunc(Name('abort'),[],None,None)))
        return IfExp(Or([c,d]), InjectFrom('INT',Add((lft,rgt))), InjectFrom('BIG',AddList((lft,rgt))))

    #Or
    elif case(expr,Or):
        orStmt = []
        for i in range(0,len(expr.nodes)):
            val = explicate(expr.nodes[i])
            orStmt.append(val)
        return Or(orStmt)

    #And
    elif case(expr,And):
        andStmt = []
        for i in range(0,len(expr.nodes)):
            val = explicate(expr.nodes[i])
            andStmt.append(val)
        return And(andStmt)

    #function
    elif case(expr, Function):
        return Assign([AssName(expr.name, 'OP_ASSIGN')], Lambda(expr.argnames, expr.defaults, expr.flags, explicate(expr.code) ))

    #lambda
    elif case(expr, Lambda):
        name = requestLambdaVarName()
        return Assign([AssName(name, 'OP_ASSIGN')], Lambda(expr.argnames, expr.defaults, expr.flags, explicate(expr.code)))

    #Return
    elif case(expr, Return):
        return Return(explicate(expr.value))

    #Function Lift
    elif case(expr, FunctionLift):
        name = expr.expr.nodes[0].name
        stackFrame[name] = 0
        tmp = currentFunction
        currentFunction = name
        rtn = FunctionLift(explicate(expr.expr))
        currentFunction = tmp
        return rtn
    #CreateClosure
    elif case(expr, CreateClosure):
        e = map(lambda x: explicate(Name(x)), expr.freeVars)
        return InjectFrom('BIG', CreateClosure(expr.function, e))
    #GetFunPtr
    elif case(expr, GetFunPtr):
        return GetFunPtr(explicate(expr.function))
    #GetFreeVar
    elif case(expr, GetFreeVar):
        return GetFreeVar(explicate(expr.freeVars))
    #If
    elif case(expr, If):
        test = explicate(expr.tests[0][0])
        then = explicate(expr.tests[0][1])
        else_ = explicate(expr.else_)
        return If([(test,then)], else_)
    #Raise exception
    else:
        ColorPrint("Error: Uncaught node in explicate: "+str(expr),CYAN)
        raise Exception()
