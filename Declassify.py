import compiler
from compiler.ast import *


VARNAME = "class"
varClassNameCounter = [0]

#Stack to handle recursive flatten statements
statementStack = [[]]
classStack = []

def requestClassTmpVarName():
    #Make a new name
    name = VARNAME+str(varClassNameCounter[0])
    varClassNameCounter[0] += 1
    return name
#Set tmp class name
def pushClassStack(name):
    classStack.append(name)
def popClassStack():
    return classStack.pop() if len(classStack) > 0 else None
def peekClassStack():
    return classStack[-1] if len(classStack) > 0 else None

class Setattr():
    def __init__(self,tmp, name, expr):
        self.tmp = tmp
        self.name = name
        self.expr = expr
    def __repr__(self):
        return 'Setattr(%s, %s, %s)' % (self.tmp, self.name, self.expr)

class CreateClass():
    def __init__(self, parent):
        self.parent = parent
    def __repr__(self):
        return 'CreateClass(%s)' % self.parent

class isClass():
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'isClass(%s)' % self.name

class CreateObject():
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'CreateObject(%s)' % self.name

# class GetAttr():
#     def __init__(self,tmp, name):
#         self.tmp = tmp
#         self.name = name
#     def __repr__(self):
#         return 'GetAttr(%s, %s)' % (self.tmp, self.name)

def Sequence(stmt):
    statementStack[-1].append(stmt)

def case(expr, classes):
    return isinstance(expr, classes)

def declassify(expr):
    if case(expr, Const):
        return expr
    elif case(expr, Name):
        if peekClassStack() != None:
            return Getattr(peekClassStack(), expr)
        return expr
    elif case(expr, Module):
        return Module(expr.doc, declassify(expr.node))
    elif case(expr, Stmt):
        d = []
        for node in expr.nodes:
            if case(node, Class):
                (a, b, c) = declassify(node)
                d.append(a)
                d.extend(b.nodes)
                d.append(c)
            elif case(node, Function):
                (a, b) = declassify(node)
                d.append(a)
                if b != None:
                    d.append(b)
            else:
                d.append(declassify(node))
        return Stmt(d)
    elif case(expr, Printnl):
        return Printnl([declassify(expr.nodes[0])], expr.dest)
    elif case(expr, Add):
        lft = declassify(expr.left)
        rgt = declassify(expr.right)
        return Add((lft,rgt))
    elif case(expr, Assign):
        if case(expr.nodes[0], Subscript):
            if peekClassStack() != None:
                return Setattr(peekClassStack(), Subscript(expr.nodes[0].expr, 'OP_ASSIGN', [declassify(expr.nodes[0].subs[0])]), declassify(expr.expr))
            return Assign([Subscript(expr.nodes[0].expr, 'OP_ASSIGN', [declassify(expr.nodes[0].subs[0])])], declassify(expr.expr))
        if peekClassStack() != None:
            #Inside a class
            return Setattr(peekClassStack(), Name(expr.nodes[0].name), declassify(expr.expr))
        return Assign(expr.nodes, declassify(expr.expr))
    elif case(expr, AssName):
        return expr
    elif case(expr, Discard):
        return Discard(declassify(expr.expr))
    elif case(expr, UnarySub):
        return UnarySub(declassify(expr.expr))
    elif case(expr, CallFunc):
        declassArg = map(lambda x: declassify(x), expr.args)
        beingCalled = declassify(expr.node)
        if case(beingCalled, Getattr):
            declassArg = declassArg
        return CallFunc(beingCalled, declassArg, None, None)
    elif case(expr, Compare):
        lft = declassify(expr.expr)
        op = expr.ops[0][0]
        rgt = declassify(expr.ops[0][1])
        return Compare(lft, [(op, rgt)])
    elif case(expr, Or):
        lft = declassify(expr.nodes[0])
        rgt = declassify(expr.nodes[1])
        return Or([lft, rgt])
    elif case(expr, And):
        lft = declassify(expr.nodes[0])
        rgt = declassify(expr.nodes[1])
        return And([lft, rgt])
    elif case(expr, Not):
        return Not(declassify(expr.expr))
    elif case(expr, List):
        print expr
        declassList = map(lambda x: declassify(x), expr.nodes)
        return List(declassList)
    elif case(expr, Dict):
        flatDict = []
        for item in expr.items:
            subItem0 = flatten(item[0])
            subItem1 = flatten(item[1])
            flatDict.append((subItem0, subItem1))
        return Dict(flatDict)
    elif case(expr, Subscript):
        return Subscript(declassify(expr.expr), expr.flags, [declassify(expr.subs[0])])
    elif case(expr, IfExp):
        testStmt = declassify(expr.test)
        thenStmt = declassify(expr.then)
        elseStmt = declassify(expr.else_)
        return IfExp(testStmt, thenStmt, elseStmt)
    elif case(expr, Function):
        #code = declassify(expr.code)
        f = Function(expr.decorators, expr.name, expr.argnames, expr.defaults, \
        expr.flags, expr.doc, expr.code)
        if peekClassStack() == None:
            return (f, None)
        s = Setattr(peekClassStack(), Name(expr.name), Name(expr.name))
        return f,s
    elif case(expr, Lambda):
        return Lambda(expr.argnames, expr.defaults, expr.flags, expr.code)
    elif case(expr, Return):
        return Return(declassify(expr.value))
    elif case(expr, If):
        test = declassify(expr.tests[0][0])
        then = declassify(expr.tests[0][1])
        else_ = declassify(expr.else_)
        return If([(test, then)], else_)
    elif case(expr, While):
        body = declassify(expr.body)
        return While(expr.test, body, expr.else_)
    elif case(expr, Class):
        #Declassify a class. Request tmp name and assign tmp = create_class([bases])
        classTmpName = requestClassTmpVarName()

        rtn = Assign([AssName(classTmpName, 'OP_ASSIGN')], CreateClass(List(expr.bases)))
        pushClassStack(Name(classTmpName))

        classBody = declassify(expr.code)

        classAssignTmp = Assign([AssName(expr.name, 'OP_ASSIGN')], Name(classTmpName))
        popClassStack()

        return rtn, classBody, classAssignTmp
    elif case(expr, Getattr):
        return expr
    else:
        raise Exception("Declassify experienced an unknown node:"+str(expr))
