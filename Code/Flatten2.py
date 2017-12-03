import compiler
from compiler.ast import *
from Declassify import CreateClass, Setattr

VARNAME = "var"
varNameCounter = [0]

#Stack to handle recursive flatten statements
statementStack = [[]]

# class Setattr():
#     def __init__(self,tmp, name, expr):
#         self.tmp = tmp
#         self.name = name
#         self.expr = expr
#     def __repr__(self):
#         return 'Setattr(%s, %s, %s)' % (self.tmp, self.name, self.expr)

# class CreateClass():
#     def __init__(self, parent):
#         self.parent = parent
#     def __repr__(self):
#         return 'CreateClass(%s)' % self.parent

def Sequence(stmt):
    statementStack[-1].append(stmt)

def requestTmpVarName():
    #Make a new name
    name = VARNAME+str(varNameCounter[0])
    varNameCounter[0] += 1

    return name

def case(expr, classes):
    return isinstance(expr, classes)

def flatten(expr):
    if case(expr, Const):
        return expr
    elif case(expr, Name):
        return expr
    elif case(expr, Module):
        return Module(expr.doc, flatten(expr.node))
    elif case(expr, Stmt):
        #statementStack.append([])
        map(lambda x: flatten(x), expr.nodes)
        return Stmt(statementStack.pop())
    elif case(expr, Printnl):
        Sequence(Printnl([flatten(expr.nodes[0])], expr.dest))
    elif case(expr, Add):
        lft = flatten(expr.left)
        rgt = flatten(expr.right)
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Add((lft,rgt))))
        return Name(tmpVar)
    elif case(expr, Assign):
        if case(expr.nodes[0], Subscript):
            Sequence(Assign([Subscript(expr.nodes[0].expr, 'OP_ASSIGN', [flatten(expr.nodes[0].subs[0])])], flatten(expr.expr)))
            return
        Sequence(Assign(expr.nodes, flatten(expr.expr)))
    elif case(expr, AssName):
        return expr
    elif case(expr, Discard):
        Sequence(Discard(flatten(expr.expr)))
    elif case(expr, UnarySub):
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], UnarySub(expr.expr)))
        return Name(tmpVar)
    elif case(expr, CallFunc):
        flatArg = map(lambda x: flatten(x), expr.args)
        return CallFunc(flatten(expr.node), flatArg, None, None)
    elif case(expr, Compare):
        tmpVar = requestTmpVarName()
        lft = flatten(expr.expr)
        op = expr.ops[0][0]
        rgt = flatten(expr.ops[0][1])
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Compare(lft, [(op, rgt)])))
        return Name(tmpVar)
    elif case(expr, Or):
        tmpVar = requestTmpVarName()
        lft = flatten(expr.nodes[0])
        rgt = flatten(expr.nodes[1])
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Or([lft, rgt])))
        return Name(tmpVar)
    elif case(expr, And):
        tmpVar = requestTmpVarName()
        lft = flatten(expr.nodes[0])
        rgt = flatten(expr.nodes[1])
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], And([lft, rgt])))
        return Name(tmpVar)
    elif case(expr, Not):
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Not(flatten(expr.expr))))
        return Name(tmpVar)
    elif case(expr, List):
        tmpVar = requestTmpVarName()
        flatList = map(lambda x: flatten(x), expr.nodes)
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], List(flatList)))
        return Name(tmpVar)
    elif case(expr, Dict):
        tmpVar = requestTmpVarName()
        flatDict = []
        for item in expr.items:
            subItem0 = flatten(item[0])
            subItem1 = flatten(item[1])
            flatDict.append((subItem0, subItem1))
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Dict(flatDict)))
        return Name(tmpVar)
    elif case(expr, Subscript):
        return Subscript(flatten(expr.expr), expr.flags, [flatten(expr.subs[0])])
    elif case(expr, IfExp):
        tmpVar = requestTmpVarName()
        testStmt = flatten(expr.test)

        thenStmt = flatten(expr.then)

        elseStmt = flatten(expr.else_)

        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], \
        IfExp(testStmt, thenStmt, elseStmt)))
        return Name(tmpVar)
    elif case(expr, Function):
        statementStack.append([])
        code = flatten(expr.code)
        Sequence(Function(expr.decorators, expr.name, expr.argnames, expr.defaults, \
        expr.flags, expr.doc, code))
    elif case(expr, Lambda):
        statementStack.append([])
        rtnCode = [Return(flatten(expr.code))]
        code = Stmt(statementStack.pop()+rtnCode)
        return Lambda(expr.argnames, expr.defaults, expr.flags, code)
    elif case(expr, Return):
        Sequence(Return(flatten(expr.value)))
    elif case(expr, If):
        test = flatten(expr.tests[0][0])

        then = flatten(expr.tests[0][1])

        else_ = flatten(expr.else_)

        Sequence(If([(test, then)], else_))
    elif case(expr, While):
        body = flatten(expr.body)
        Sequence(While(expr.test, body, expr.else_))

    elif case(expr, CreateClass):
        return CreateClass(flatten(expr.parent))

    elif case(expr, Setattr):
        Sequence(Setattr(expr.tmp, expr.name, flatten(expr.expr)))

    elif case(expr, Getattr):
        return expr

    else:
        raise Exception("Flatten experienced an unknown node:"+str(expr))

# ast = compiler.parseFile("/Users/michaeltang/Desktop/xfc.py")
# print flatten(ast)
