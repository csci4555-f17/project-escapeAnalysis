import compiler
from compiler.ast import *
from free_vars import *

#Const to make tmpvar names
VARNAME = "var"
varNameCounter = [0]
#Variable to keep track of varNames -> StackLocation
stackLocation = [1]
#Map between variable names and their location on the stack
varMap = {}
# Dict to map function name to free vars set
freeMap = {}
# Dict to map fuction name to bound vars set
boundMap = {}
# Doct to map function name to its arg list
argMap = {}
# Counter to count function depth
statementsLeftInFunction = 0
# Counter for the depth of nested functions.
nestedFunctionDepth = 0
# Dict to map a function's name to its stmt list
functionNameToStmtsMap = {}
# Name of the current function.
currentFunctionName = [None]
# Bool to see if we're in a Lambda.
inLambda = False
# Bool to see if we're in a class.
inClass = False
# String to keep track of if we're in an if, and if so, if we're in tests or else_
inIf = "False"
# List for current Lambda stmt list
lambdaStmtList = []
# List for current class stmts
classStmtList = []
# List for If tests stmts
ifTestsStmtList = []
# List for If else_ stmts
ifElse_StmtList = []
# Bool to see if we're in a function.
inFunction = False
# Bool to see if we're in a while
inWhile = False
# List for while stmts
whileStmtList = []

#Michael definition (Sequence Point AST operation):
#A moment in time of the evaluation of the ast
#where there exists an assignment of a temp variable to a complex expression or a node with possible
#subnodes that may have sub-assignments.

#Statement list to control the sequence of assignment under flatten
flatStatements = []

def appendNestedFunction(name):
    global nestedFunctionDepth
    nestedFunctionDepth += 1
    currentFunctionName.append(name)

def popNestedFunction():
    global nestedFunctionDepth
    nestedFunctionDepth -= 1
    return currentFunctionName.pop()

def requestTmpVarName():
    #Make a new name
    name = VARNAME+str(varNameCounter[0])
    varNameCounter[0] += 1
    #Map name to stack location
    varMap[name] = stackLocation[0]
    stackLocation[0] += 1

    return name

def Sequence(stmt):
    flatStatements[len(flatStatements) - 1].append(stmt)
    return

def case(expr, Class):
    return isinstance(expr, Class)

def flatten(expr):
    # Making counters global.
    global statementsLeftInFunction, nestedFunctionDepth, currentFunctionName, \
    functionNameToStmtsMap, lambdaStmtList, inLambda, inClass, classStmtList, ifTestsStmtList, \
    ifElse_StmtList, inWhile, whileStmtList, inFunction
    # ------------------ Start of P0 nodes ------------------

    #Const
    if case(expr, Const):
        return expr

    #Name
    elif case(expr, Name):
        return expr

    #Module
    elif case(expr, Module):
        return Module(expr.doc, flatten(expr.node))

    #Stmt
    # Updated for P2
    elif case(expr, Stmt):
        flatStatements.append([])
        map(lambda x: flatten(x), expr.nodes)
        tmpFlatStatements = flatStatements[len(flatStatements) - 1]
        flatStatements.pop()
        return Stmt(tmpFlatStatements)

    #Printnl *Sequence Point
    elif case(expr, Printnl):
        Sequence(Printnl([flatten(expr.nodes[0])], expr.dest))

    #Add *Sequence Point
    elif case(expr, Add):
        lft = flatten(expr.left)
        rgt = flatten(expr.right)
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Add((lft, rgt))))
        return Name(tmpVar)

    #Assign *Sequence Point
    elif case(expr, Assign):
        if case(expr.nodes[0], Subscript):
            Sequence(Assign([Subscript(expr.nodes[0].expr, 'OP_ASSIGN', [flatten(expr.nodes[0].subs[0])])], flatten(expr.expr)))
            return
        Sequence(Assign(expr.nodes, flatten(expr.expr)))

    #AssName
    elif case(expr, AssName):
        return expr

    #Discard *Sequence Point
    elif case(expr, Discard):
        Sequence(Discard(flatten(expr.expr)))

    #UnarySub *Sequence Point
    elif case(expr, UnarySub):
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], UnarySub(expr.expr)))
        return Name(tmpVar)

    #CallFunc *Sequence Point
    elif case(expr, CallFunc):
        flatArg = map(lambda x: flatten(x), expr.args)
        # If we're not in a function:
        if inFunction == False:
            tmpVar = requestTmpVarName()
            Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], CallFunc(flatten(expr.node), flatArg, None, None)))
            return Name(tmpVar)
        else:
            return CallFunc(flatten(expr.node), flatArg, None, None)

    # ------------------ End of P0 nodes ------------------
    # ------------------ Start of P1 nodes ------------------
    #Compare
    elif case(expr, Compare):
        tmpVar = requestTmpVarName()
        lft = flatten(expr.expr)
        op = expr.ops[0][0]
        rgt = flatten(expr.ops[0][1])
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Compare(lft, [(op, rgt)])))
        return Name(tmpVar)
    #Or
    elif case(expr, Or):
        tmpVar = requestTmpVarName()
        lft = flatten(expr.nodes[0])
        rgt = flatten(expr.nodes[1])
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Or([lft, rgt])))
        return Name(tmpVar)
    #And
    elif case(expr, And):
        tmpVar = requestTmpVarName()
        lft = flatten(expr.nodes[0])
        rgt = flatten(expr.nodes[1])
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], And([lft, rgt])))
        return Name(tmpVar)

    #Not *Sequence Point
    elif case(expr, Not):
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Not(flatten(expr.expr))))
        return Name(tmpVar)

    #List
    elif case(expr, List):
        tmpVar = requestTmpVarName()
        flatList = map(lambda x: flatten(x), expr.nodes)
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], List(flatList)))
        return Name(tmpVar)

    #Dict
    elif case(expr, Dict):
        tmpVar = requestTmpVarName()
        flatDict = []
        for item in expr.items:
            subItem0 = flatten(item[0])
            subItem1 = flatten(item[1])
            flatDict.append((subItem0, subItem1))
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], Dict(flatDict)))
        return Name(tmpVar)

    #Subscript
    elif case(expr, Subscript):
        #Wrong to Sequence subscript since it could be an lvalue
        #tmpVar = requestTmpVarName()
        #Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], \
        return Subscript(flatten(expr.expr), expr.flags, [flatten(expr.subs[0])])

    #IfExp
    elif case(expr, IfExp):
        tmpVar = requestTmpVarName()
        Sequence(Assign([AssName(tmpVar, 'OP_ASSIGN')], \
        IfExp(flatten(expr.test), flatten(expr.then), flatten(expr.else_))))
        return Name(tmpVar)

    # ------------------ End of P1 nodes ------------------
    # ------------------ Start of P2 nodes -------------------------

    # CallFunc case in P0... need to be refactored?

    elif case(expr, Function):
        appendNestedFunction(expr.name)
        functionNameToStmtsMap[currentFunctionName[nestedFunctionDepth]] = []
        inFunction = True
        code = flatten(expr.code)
        inFunction = False
        popNestedFunction()
        #nestedFunctionDepth -= 1
        Sequence(Function(expr.decorators, expr.name, expr.argnames, expr.defaults, \
        expr.flags, expr.doc, code))


    #Lambda
    elif case(expr, Lambda):
        flatStatements.append([])
        inLambda = True
        flatCode = flatten(expr.code)
        inLambda = False
        tmpFlatStatements = flatStatements[len(flatStatements) - 1]
        print tmpFlatStatements
        flatStatements.pop()
        tmpLambdaStmtList = lambdaStmtList
        lambdaStmtList = []
        tmpLambdaStmtList = tmpLambdaStmtList + tmpFlatStatements
        if tmpLambdaStmtList == []:
            return Lambda(expr.argnames, expr.defaults, expr.flags, Stmt([flatCode] + tmpLambdaStmtList))
        else:
            return Lambda(expr.argnames, expr.defaults, expr.flags, Stmt(tmpLambdaStmtList))

    #Return
    elif case(expr, Return):
        Sequence(Return(flatten(expr.value)))

    # ------------------ End of P2 nodes -------------------------
    # ------------------ START of P3 nodes -------------------------

    elif case(expr, Class):
        inClass = True
        flatCode = flatten(expr.code)
        inClass = False
        tmpClassStmtList = classStmtList
        classStmtList = []
        Sequence(Class(expr.name, expr.bases, expr.doc, Stmt(tmpClassStmtList)))

    elif case(expr, AssAttr):
        # Already done in Assign?
        pass

    elif case(expr, Getattr):
        return expr

    elif case(expr, If):
        flatStmtsTest = flatten(expr.tests[0][1])
        flatStmtsElse = flatten(expr.else_)
        newTests = [(expr.tests[0][0], flatStmtsTest)]
        Sequence(If(newTests, flatStmtsElse))

    elif case(expr, While):
        body = flatten(expr.body)
        if expr.else_ != None:
            else_ = flatten(expr.else_)
        else:
            else_ = None
        Sequence(While(expr.test, body, else_))


    # ------------------ End of P3 nodes -------------------------

    else:
        raise Exception("Flatten caught an unexpected node: "+str(expr))
