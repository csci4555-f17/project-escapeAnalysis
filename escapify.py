import compiler
from compiler.ast import *
from explicate import Bool

connectionGraph = {}
globalVars = {"inAssign": False}
nameList = [{}]
functionClassNameList = []
nameCounter = 0

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
        nameList.pop()
        return Stmt(escapifiedStmt)

    elif isinstance(n, Bool):
        return Bool(escapify(n.expr))

    elif isinstance(n, Name):
        return n

    elif isinstance(n, Add):
        lft = escapify(n.left)
        rgt = escapify(n.right)
        return Add((lft, rgt))

    elif isinstance(n, CallFunc):
        name = escapify(n.node)

        if globalVars["inAssign"] != False:
            varName = globalVars["inAssign"]
            connectionGraph[varName] = name.name
        
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
        globalVars["inAssign"] = n.nodes[0].name     
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
            connectionGraph[varName] = removedConstNodes
            print connectionGraph

        return List(nodes) if len(nodes) is not 0 else List(())

    elif isinstance(n, Function):
        return Function(n.decorators, n.name, n.argnames, n.defaults, n.flags, n.doc, escapify(n.code))

    elif isinstance(n, Lambda):
        return Lambda(n.argnames, [], 0, escapify(n.code))

    elif isinstance(n, IfExp):
        return IfExp(escapify(n.test), escapify(n.then), escapify(n.else_))

    elif isinstance(n, Return):
        return Return(escapify(n.value))

    elif isinstance(n, Class):
        return Class(n.name, n.bases, n.doc, escapify(n.code))
        
    elif isinstance(n, AssAttr):
        return n

    elif isinstance(n, Getattr):
        return n

    elif isinstance(n, If):
        return If([(n.tests[0][0], escapify(n.tests[0][1]))], escapify(n.else_))

    elif isinstance(n, While):
        return While(n.test, escapify(n.body), escapify(n.else_))

ast = compiler.parseFile("/Users/rb/GoogleDrive/School/Dropbox/CSCI4555/project-escapeAnalysis/mytests/test16.py")

print "Orig: "+str(ast)
print "Escp: "+str(escapify(ast))
