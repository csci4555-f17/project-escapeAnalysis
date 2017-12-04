import compiler
from compiler.ast import *
from explicate import Bool
from uniquify import *
from Flatten2 import *

connectionGraph = {}
dictOfConnectionGraphs = {}
globalVars = {"inAssign": False, "objectCounter": 0, "inClass": False, "inReturn": False, "inFunction": False}
classNamesToAttributes = {}
nameList = [{}]
functionClassNameList = []
nameCounter = 0

def addToConnectionGraph(varName, val):
    if isinstance(val, Const):
        val = val.value
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
        return n

    elif isinstance(n, Module):
        return Module(None, escapify(n.node))

    elif isinstance(n, Stmt):
        nameList.append({})
        escapifiedStmt = []
        for i in range(0,len(n.nodes)):
            val = escapify(n.nodes[i])
            escapifiedStmt.append(val)
            if i == len(n.nodes) - 1:
                addToConnectionGraph(globalVars["inFunction"], connectionGraph)
        nameList.pop()
        return Stmt(escapifiedStmt)

    elif isinstance(n, Bool):
        return Bool(escapify(n.expr))

    elif isinstance(n, Name):
        if globalVars["inReturn"] != False:
            addToConnectionGraph("return", n.name)
        return n

    elif isinstance(n, Add):
        lft = escapify(n.left)
        rgt = escapify(n.right)
        return Add((lft, rgt))

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

        name = escapify(n.node)
        args = []
        for i in range(0,len(n.args)):
            val = escapify(n.args[i])
            args.append(val)
        return CallFunc(name, args, None, None)

    elif isinstance(n, Printnl):
        escapifiedPrintStmt = []
        for i in range(0,len(n.nodes)):
            val = escapify(n.nodes[i])
            escapifiedPrintStmt.append(val)
        return Printnl(escapifiedPrintStmt,None)

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
            print classNamesToAttributes
            #classNamesToAttributes[]

        else:
            raise Exception("In Assign node. Hit unhandled node case.")
        nodes = escapify(n.nodes[0])
        val = escapify(n.expr)
        globalVars["inAssign"] = False
        #varName = expr.nodes[0].name
        return Assign([nodes],val)

    elif isinstance(n, AssName):
        return n

    elif isinstance(n, Discard):
        return Discard(escapify(n.expr))

    elif isinstance(n, UnarySub):
        return UnarySub(escapify(n.expr))

    elif isinstance(n, Compare):
        return Compare(escapify(n.expr), [(n.ops[0][0], escapify(n.ops[0][1]))])

    elif isinstance(n, List):
        nodes = []
        for node in n.nodes:
            escapifiedNode = escapify(node)
            nodes.append(escapifiedNode)
        
        if globalVars["inAssign"] != False:
            removedConstNodes = list(map(lambda x: x.value, nodes))
            varName = globalVars["inAssign"]
            addToConnectionGraph(varName, removedConstNodes)

        return List(nodes) if len(nodes) is not 0 else List([])

    elif isinstance(n, Function):
        globalVars["inFunction"] = n.name
        code = escapify(n.code)
        globalVars["inFunction"] = False
        return Function(n.decorators, n.name, n.argnames, n.defaults, n.flags, n.doc, code)

    elif isinstance(n, Lambda):
        return Lambda(n.argnames, [], 0, escapify(n.code))

    elif isinstance(n, IfExp):
        return IfExp(escapify(n.test), escapify(n.then), escapify(n.else_))

    elif isinstance(n, Return):
        globalVars["inReturn"] = True
        ret = escapify(n.value)
        globalVars["inReturn"] = False
        return Return(ret)

    elif isinstance(n, Class):
        globalVars["inClass"] = n.name
        if n.name not in classNamesToAttributes:
            classNamesToAttributes[n.name] = []
        code = escapify(n.code)
        globalVars["inClass"] = False
        return Class(n.name, n.bases, n.doc, code)
        
    elif isinstance(n, AssAttr):

        if globalVars["inAssign"] != False:
            varName = globalVars["inAssign"]
            tmp = connectionGraph[varName][0]
            addToConnectionGraph(tmp, n.attrname)

        return n

    elif isinstance(n, Getattr):
        return n

    elif isinstance(n, If):
        return If([(n.tests[0][0], escapify(n.tests[0][1]))], escapify(n.else_))

    elif isinstance(n, While):
        return While(n.test, escapify(n.body), escapify(n.else_))

ast = compiler.parseFile("/Users/rb/GoogleDrive/School/Dropbox/CSCI4555/project-escapeAnalysis/Code/mytests/test16.py")
uniquifiedAST = uniquify(ast)

print "Orig: " + str(uniquifiedAST)
flattenedAST = flatten(uniquifiedAST)
print "Flat: " + str(flattenedAST)
print "Escp: " + str(escapify(flattenedAST))
print "Graph: " + str(connectionGraph)