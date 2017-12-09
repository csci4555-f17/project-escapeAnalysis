import compiler
from compiler.ast import *
from explicate import Bool
from uniquify import *
from Flatten2 import *
from Declassify import declassify

connectionGraph = {}
dictOfConnectionGraphs = {}
globalVars = {"inAssign": False, "objectCounter": 0, "inClass": False, "inReturn": False, "inFunction": False}
classNamesToAttributes = {}
nameList = [{}]
functionClassNameList = []
nameCounter = 0

def addToConnectionGraph(varName, val):
    print varName, val
    if isinstance(val, Const):
        val = val.value
    if isinstance(val, List):
        val = val.nodes
    if varName in connectionGraph and val not in connectionGraph[varName]:
        if isinstance(val, list):
            connectionGraph[varName].extend(val)
        else:
            connectionGraph[varName].append(val)
    else:
        connectionGraph[varName] = [val]
    #print connectionGraph

def finishConnectionGraphForCurrentScope(name, graph):
    dictOfConnectionGraphs[name] = graph

def createNewInstance(obj):
    name = obj + "_" + str(globalVars["objectCounter"])
    if name not in connectionGraph:
        connectionGraph[name] = []
    return name

def createNewAttributeInstances(attributes):
    returnList = []
    for pair in attributes:
        tmpName = pair[0] + "_" + str(globalVars["objectCounter"])
        returnList.append(tmpName)
        addToConnectionGraph(tmpName, pair[1])
        
    return returnList

def escapify(n):
    global nameDictionary
    global nameCounter

    if isinstance(n, Const):
        pass

    elif isinstance(n, Module):
        escapify(n.node)

    elif isinstance(n, Stmt):
        for i in range(0,len(n.nodes)):
            escapify(n.nodes[i])

    elif isinstance(n, Bool):
        pass

    elif isinstance(n, Name):
        if globalVars["inReturn"] != False:
            addToConnectionGraph("return", n.name)

    elif isinstance(n, Add):
        escapify(n.left)
        escapify(n.right)

    elif isinstance(n, CallFunc):
        # If we're creating a class.
        if n.node.name in classNamesToAttributes:
            if globalVars["inAssign"] != False:
                varName = globalVars["inAssign"]
                newName = createNewInstance(n.node.name)
                addToConnectionGraph(varName, newName)
                newAttributes = createNewAttributeInstances(classNamesToAttributes[n.node.name])
                addToConnectionGraph(newName, newAttributes)
                globalVars["objectCounter"] += 1

        escapify(n.node)
        for i in range(0,len(n.args)):
            escapify(n.args[i])

    elif isinstance(n, Printnl):
        for i in range(0,len(n.nodes)):
            escapify(n.nodes[i])

    elif isinstance(n, Assign):  
        if isinstance(n.nodes[0], AssName):
            globalVars["inAssign"] = n.nodes[0].name
            if globalVars["inClass"] != False:
                classNamesToAttributes[globalVars["inClass"]].append([n.nodes[0].name, n.expr])
            if globalVars["inFunction"] != False:
                res = n.expr
                if isinstance(n.expr, Name):
                    res = n.expr.name
                addToConnectionGraph(n.nodes[0].name, res)
        elif isinstance(n.nodes[0], AssAttr):
            globalVars["inAssign"] = n.nodes[0].expr.name
            #classNamesToAttributes[]

        else:
            raise Exception("In Assign node. Hit unhandled node case.")
        escapify(n.nodes[0])
        escapify(n.expr)
        globalVars["inAssign"] = False

    elif isinstance(n, AssName):
        pass

    elif isinstance(n, Discard):
        escapify(n.expr)

    elif isinstance(n, UnarySub):
        escapify(n.expr)

    elif isinstance(n, Compare):
        escapify(n.expr)
        escapify(n.ops[0][1])

    elif isinstance(n, List):
        nodes = []
        for node in n.nodes:
            escapifiedNode = escapify(node)
            nodes.append(escapifiedNode)
        '''
        if globalVars["inAssign"] != False:
            removedConstNodes = list(map(lambda x: x.value, nodes))
            varName = globalVars["inAssign"]
            addToConnectionGraph(varName, removedConstNodes)
        '''

    elif isinstance(n, Function):
        globalVars["inFunction"] = n.name
        escapify(n.code)
        globalVars["inFunction"] = False

    elif isinstance(n, Lambda):
        escapify(n.code)

    elif isinstance(n, IfExp):
        escapify(n.test)
        escapify(n.then)
        escapify(n.else_)

    elif isinstance(n, Return):
        globalVars["inReturn"] = True
        escapify(n.value)
        globalVars["inReturn"] = False

    elif isinstance(n, Class):
        globalVars["inClass"] = n.name
        if n.name not in classNamesToAttributes:
            classNamesToAttributes[n.name] = []
        escapify(n.code)
        globalVars["inClass"] = False
        
    elif isinstance(n, AssAttr):
        if globalVars["inAssign"] != False:
            varName = globalVars["inAssign"]
            tmp = connectionGraph[varName][0]
            addToConnectionGraph(tmp, n.attrname)

    elif isinstance(n, Getattr):
        pass

    elif isinstance(n, If):
        escapify(n.tests[0][1])
        escapify(n.else_)

    elif isinstance(n, While):
        escapify(n.body)
        escapify(n.else_)

def outerEscapify(n):
    global nameDictionary
    global nameCounter

    if isinstance(n, Const):
        return n

    elif isinstance(n, Module):
        return Module(None, outerEscapify(n.node))

    elif isinstance(n, Stmt):
        escapifiedStmt = []
        for i in range(0,len(n.nodes)):
            val = outerEscapify(n.nodes[i])
            escapifiedStmt.append(val)
        return Stmt(escapifiedStmt)

    elif isinstance(n, Bool):
        return Bool(outerEscapify(n.expr))

    elif isinstance(n, Name):
        return n

    elif isinstance(n, Add):
        lft = outerEscapify(n.left)
        rgt = outerEscapify(n.right)
        return Add((lft, rgt))

    elif isinstance(n, CallFunc):
        name = outerEscapify(n.node)
        args = []
        for i in range(0,len(n.args)):
            val = outerEscapify(n.args[i])
            args.append(val)
        return CallFunc(name, args, None, None)

    elif isinstance(n, Printnl):
        escapifiedPrintStmt = []
        for i in range(0,len(n.nodes)):
            val = outerEscapify(n.nodes[i])
            escapifiedPrintStmt.append(val)
        return Printnl(escapifiedPrintStmt,None)

    elif isinstance(n, Assign):  
        nodes = outerEscapify(n.nodes[0])
        val = outerEscapify(n.expr)
        return Assign([nodes],val)

    elif isinstance(n, AssName):
        return n

    elif isinstance(n, Discard):
        return Discard(outerEscapify(n.expr))

    elif isinstance(n, UnarySub):
        return UnarySub(outerEscapify(n.expr))

    elif isinstance(n, Compare):
        return Compare(outerEscapify(n.expr), [(n.ops[0][0], outerEscapify(n.ops[0][1]))])

    elif isinstance(n, List):
        nodes = []
        for node in n.nodes:
            escapifiedNode = outerEscapify(node)
            nodes.append(escapifiedNode)

        return List(nodes) if len(nodes) is not 0 else List([])

    elif isinstance(n, Function):
        escapify(n)
        code = outerEscapify(n.code)
        return Function(n.decorators, n.name, n.argnames, n.defaults, n.flags, n.doc, code)

    elif isinstance(n, Lambda):
        escapify(n)
        return Lambda(n.argnames, [], 0, outerEscapify(n.code))

    elif isinstance(n, IfExp):
        return IfExp(outerEscapify(n.test), outerEscapify(n.then), outerEscapify(n.else_))

    elif isinstance(n, Return):
        ret = outerEscapify(n.value)
        return Return(ret)

    elif isinstance(n, Class):
        escapify(n)
        code = outerEscapify(n.code)
        return Class(n.name, n.bases, n.doc, code)
        
    elif isinstance(n, AssAttr):
        return n

    elif isinstance(n, Getattr):
        return n

    elif isinstance(n, Setattr):
        return n

    elif isinstance(n, If):
        return If([(n.tests[0][0], outerEscapify(n.tests[0][1]))], outerEscapify(n.else_))

    elif isinstance(n, While):
        return While(n.test, outerEscapify(n.body), outerEscapify(n.else_))

    elif isinstance(n, Subscript):
        pass

    elif isinstance(n, CreateClass):
        return n

    

ast = compiler.parseFile("/Users/rb/GoogleDrive/School/Dropbox/CSCI4555/project-escapeAnalysis/Code/mytests/test16.py")
print "orig: " + str(ast)
uniquifiedAST = uniquify(ast)
print "uniq: " + str(uniquifiedAST)
#print "Orig: " + str(uniquifiedAST)
declassifiedAST = declassify(uniquifiedAST)
print "decl: " + str(declassifiedAST)
flattenedAST = flatten(declassifiedAST)
print "Flat: " + str(flattenedAST)
print "Escp: " + str(outerEscapify(flattenedAST))
print "Graph: " + str(connectionGraph)