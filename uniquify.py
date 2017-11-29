import compiler
from compiler.ast import *
from explicate import Bool

nameList = [{}]
functionClassNameList = []
nameCounter = 0

def uniquify(n):
    global nameDictionary
    global nameCounter

    if isinstance(n, Const):
        return Const(n.value)

    elif isinstance(n, Module):
        return Module(None, uniquify(n.node))

    elif isinstance(n, Stmt):
        nameList.append({})
        uniquifiedStmt = []
        for i in range(0,len(n.nodes)):
            val = uniquify(n.nodes[i])
            uniquifiedStmt.append(val)
        nameList.pop()
        return Stmt(uniquifiedStmt)

    elif isinstance(n, Bool):
        return Bool(uniquify(n.expr))

    elif isinstance(n, Name):
        inList = False
        for dic in functionClassNameList:
            if (n.name in dic.keys()):
                inList = True
        if n.name in nameList[len(nameList) - 1]:
            return Name(nameList[len(nameList) - 1][n.name])

        elif inList == True:
            for dic in functionClassNameList:
                if (n.name in dic.keys()):
                    return Name(dic[n.name])

        else:
            return Name(n.name)

    elif isinstance(n, Add):
        lft = uniquify(n.left)
        rgt = uniquify(n.right)
        return Add((lft, rgt))

    elif isinstance(n, CallFunc):
        name = uniquify(n.node)
        args = []
        for i in range(0,len(n.args)):
            val = uniquify(n.args[i])
            args.append(val)
        return CallFunc(name,args,None,None)

    elif isinstance(n, Printnl):
        uniquifiedPrintStmt = []
        for i in range(0,len(n.nodes)):
            val = uniquify(n.nodes[i])
            uniquifiedPrintStmt.append(val)
        return Printnl(uniquifiedPrintStmt,None)

    elif isinstance(n, Assign):
        val = uniquify(n.expr)
        nodes = uniquify(n.nodes[0])
        #varName = expr.nodes[0].name
        return Assign([nodes],val)

    elif isinstance(n, AssName):
        if n.name in nameList[len(nameList) - 1]:
            newName = nameList[len(nameList) - 1][n.name]
        else:
            newName = n.name + "_" + str(nameCounter)
            nameList[len(nameList) - 1][n.name] = newName
            nameCounter = nameCounter + 1
        return AssName(newName, "OP_ASSIGN")
    elif isinstance(n, Discard):
        return Discard(uniquify(n.expr))

    elif isinstance(n, UnarySub):
        return UnarySub(uniquify(n.expr))

    elif isinstance(n, Compare):
        return Compare(uniquify(n.expr), [(n.ops[0][0], uniquify(n.ops[0][1]))])

    elif isinstance(n, List):
        nodes = []
        for node in n.nodes:
            uniquifiedNode = uniquify(node)
            nodes.append(uniquifiedNode)
        return List(nodes)

    elif isinstance(n, Function):
        newArgNames = []
        if n.name in nameList[len(nameList) - 1]:
            newName = nameList[len(nameList) - 1][n.name]
            functionClassNameList.append({n.name : newName})
        else:
            newName = n.name + "_" + str(nameCounter)
            nameList[len(nameList) - 1][n.name] = newName
            nameCounter = nameCounter + 1
            functionClassNameList.append({n.name : newName})
        for i in range(0, len(n.argnames)):
            if i in nameList[len(nameList) - 1]:
                newArgNames.append(nameList[len(nameList) - 1][n.argnames[i]])
            else:
                newArgName = str(n.argnames[i]) + "_" + str(nameCounter)
                nameList[len(nameList) - 1][n.argnames[i]] = newArgName
                nameCounter = nameCounter + 1
                newArgNames.append(newArgName)
                functionClassNameList.append({n.argnames[i] : newArgName})
        return Function(None, newName, newArgNames, [], 0, None, uniquify(n.code))

    elif isinstance(n, Lambda):
        newArgNames = []
        for i in range(0, len(n.argnames)):
            if i in nameList[len(nameList) - 1]:
                newArgNames.append(nameList[len(nameList) - 1][n.argnames[i]])
            else:
                newArgName = str(n.argnames[i]) + "_" + str(nameCounter)
                nameList[len(nameList) - 1][n.argnames[i]] = newArgName
                nameCounter = nameCounter + 1
                newArgNames.append(newArgName)
        return Lambda(newArgNames, [], 0, uniquify(n.code))

    elif isinstance(n, IfExp):
        return IfExp(uniquify(n.test), uniquify(n.then), uniquify(n.else_))

    elif isinstance(n, Return):
        return Return(uniquify(n.value))

    elif isinstance(n, Class):
        if n.name in nameList[len(nameList) - 1]:
            newName = nameList[len(nameList) - 1][n.name]
        else:
            newName = n.name + "_" + str(nameCounter)
            nameList[len(nameList) - 1][n.name] = newName
            nameCounter = nameCounter + 1
            functionClassNameList.append({n.name : newName})
        return Class(newName, n.bases, n.doc, uniquify(n.code))
        
    elif isinstance(n, AssAttr):
        return n

    elif isinstance(n, Getattr):
        return n

    elif isinstance(n, If):
        return If([(n.tests[0][0], uniquify(n.tests[0][1]))], uniquify(n.else_))

    elif isinstance(n, While):
        pass

'''
ast = compiler.parseFile("/Users/rb/GoogleDrive/School/Dropbox/CSCI4555/pyyc-foomybar/mytests/test16.py")

print "Orig: "+str(ast)
print "Uniq: "+str(uniquify(ast))
'''