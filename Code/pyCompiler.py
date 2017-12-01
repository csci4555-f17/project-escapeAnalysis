import random
import compiler
from compiler.ast import *
from os import remove
import sys
import re
from live import Live
from nodes import *
from explicate import *
from free_vars import *
from heapify import *


WHITE = "\x1B[0m"
RED = "\x1B[31m"
MAGENTA = "\x1B[35m"
YELLOW = "\x1B[33m"
GREEN = "\x1B[32m"
CYAN = "\x1B[36m"

def ColorPrint(expr,color):
    print color+str(expr)+WHITE

class Register():
    def __init__(self, regName):
        self.name = regName
    def __repr__(self):
        return 'Register(%s)' % self.name

class pyCompiler():
    def __init__(self, _ast):
        #ast
        self.ast = _ast
        #Internal counters to keep track of unique variables
        self.variableCounter = 0
        # Stack var counter assigns an integer to a variable in P0 as an ID to \
        # trace its location on the stack
        self.stackVarCounter = 1
        #List for appending flatten exprs
        self.flattenStatements = []
        #Dictionary to map P0 vars to their location on the stack. Mulitple by 4
        self.varMap = {}
        #Dictionary to map function name to their set of free vars
        self.freeMap = {}
        #Dictionary to map function name to their bounded variables. This includes arguments
        self.boundMap = {}
        #Dictionary to map fucntion name to its list of arguments
        self.argMap = {}
        #List for appending x86 statements
        self.x86Statements = []
        #Dict of functionName : listOfStatements for functions
        self.functions = {}
        # string "boolean" to see if we're currently in a function.
        # Set to "False" initially, set to function name if in a function
        self.inFunction = "False"
        # Number of statements in the function.code
        self.numOfFunctionStmts = 0
        #tmp variable name
        self.tmp = "var"
        #indent level
        self.block = ""
        #Lambda counter
        self.lambdaCount = 0
        #jmp counter for P1 compile
        self.jmp = 0
        self.short = 0
        #lambda translation to map variable names to lambdaFunctions
        self.lambdaTranslate = {}

    def indent(self):
        level = len(self.block)
        level += 4
        self.block = " "*level

    def dedent(self):
        level = len(self.block)
        if level <= 0:
            ColorPrint("NOTE: Detending a zero level statement",MAGENTA)
        level -= 4
        self.block = " "*level

    def requestUniqueTmpName(self):
        token = ""
        for i in range(0, 4):
            j = random.randint(0, 25)
            token = token + str(self.letters[j])
        self.tmp = token

    #Helper function to quick insert x86 statements. Takes a list of x86
    def quickInsert(self, stmt):
        for i in range(0, len(stmt)):
            # If we're not in a function.
            if self.inFunction == "False":
                self.x86Statements.append(stmt[i])
            # If we are in a function.
            else:
                self.functions[self.inFunction].append(stmt[i])

    #Helpfer function. Takes a variable name and gets a position offset from
    #ebp if inFunction is true
    def isArg(self, varName):
        if self.inFunction != "False" and (varName in self.argMap[self.inFunction]):
            l = self.argMap[self.inFunction]
            return 4*l.index(varName) + 8
        return 0
    #Helper function giving unique numbers for jump statements
    def requestJumpNumber(self):
        self.jmp += 1
        return self.jmp

    #Helpfer function giving unique numbers for jump statements in short-circuit cases
    def requestShortNumber(self):
        self.short += 1
        return self.short

    #Helper function to shorthand isinstance
    def case(self, expr, Class):
        return isinstance(expr, Class)

    # Helper function returning true for irreducible nodes: variables, const, \
    # functions* (input for now)
    def isIrreducible(self, expr):
        return isinstance(expr, Const) or isinstance(expr, Bool) or \
        isinstance(expr, Name) or isinstance(expr, List)

    #Helper function to add P0 to the varMap dictionary
    def map(self, name):
        # If a P0's var name is in the dictionary, ignore it. If not, add \
        # it to the dictionary with the current count value and incl
        if name not in self.varMap:
            self.varMap[name] = self.stackVarCounter
            self.stackVarCounter = self.stackVarCounter + 1

    def flattenAST(self, expr):
        #Base case
        #Const - return int or str
        #P2 Okay
        if self.case(expr, Const):
            return expr.value
        #Bool
        #P2 Okay
        elif self.case(expr, Bool):
            return expr.expr
        #Name - return str
        #P2 Okay
        elif self.case(expr, Name):
            return expr.name
        #CallFunc : input() - Special case so far - return Name(). Sequence Append
        elif self.case(expr, CallFunc):
            funcName = self.flattenAST(expr.node)
            #Special case input
            if funcName == 'input':
                return Name("input()")
            elif self.case(funcName, Name):
                funcName = self.flattenAST(funcName)

            #Reduce if ness
            argList = []
            if len(expr.args) > 0:
                for i in range(0,len(expr.args)):
                    argVal = expr.args[i]
                    while not self.isIrreducible(argVal):
                        argVal = self.flattenAST(argVal)
                    argVal = self.flattenAST(argVal)

                    argList.append(argVal)

            #Create new tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            # Ross Change
            self.map(tmpVar)
            argv = reduce(lambda x,y: str(x)+","+str(y),argList) if len(expr.args) > 0 else ""
            freeVarArray = reduce(lambda x,y: str(x)+","+str(y), self.freeMap[funcName]) if len(self.freeMap[funcName]) > 0 else ""

            stmt = self.block+tmpVar+"="+str(funcName)+"("+"["+freeVarArray+"],"+str(argv)+")"

            #Append to flattenStatement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)


        #AssName - return str
        #P2 Okay
        elif self.case(expr, AssName):
            return expr.name
        #Module
        #P2 Okay
        elif self.case(expr, Module):
            #Recurse on node, ignore doc
            self.flattenAST(expr.node)
        #Stmt
        #P2 Okay
        elif self.case(expr, Stmt):
            #Flatten each subAST in the Stml list of nodes
            for i in range(0, len(expr.nodes)):
                self.flattenAST(expr.nodes[i])
        #Printnl - appends statement
        #P2 refactored
        elif self.case(expr, Printnl):
            #Ignore dest
            #Flatten each subAST in the Printnl list. Sequence Append
            prntStmt = self.block+"print "
            tokens = ""
            for i in range(0, len(expr.nodes)):
                subStmt = self.flattenAST(expr.nodes[i])
                if self.case(subStmt, Name):
                    subStmt = self.flattenAST(subStmt)
                if tokens == "":
                    tokens = subStmt
                else:
                    tokens = tokens+","+str(subStmt)
            #Append to flattenStatements
            self.flattenStatements.append(prntStmt+str(tokens))
        #Assign - Sequence Append
        #P2 refactored
        elif self.case(expr, Assign) and self.isIrreducible(expr.expr):
            #value being assigned
            val = self.flattenAST(expr.expr)
            if "lambda" in str(val):
                self.freeMap[expr.nodes[0].name] = self.freeMap[val]
                self.argMap[expr.nodes[0].name] = self.argMap[val]
                self.boundMap[expr.nodes[0].name] = self.boundMap[val]
                self.lambdaTranslate[val] = expr.nodes[0].name


            #If assignment is a subscript into a list
            if self.case(expr.nodes[0], Subscript):
                arrayName = self.flattenAST(expr.nodes[0].expr)
                assingingIndex = self.flattenAST(expr.nodes[0].subs[0])
                if self.case(val, Name):
                    val = self.flattenAST(val)
                if self.case(assingingIndex, Name):
                    assingingIndex = self.flattenAST(assingingIndex)
                stmt = self.block+arrayName+"["+str(assingingIndex)+"]"+"="+str(val)
                self.flattenStatements.append(stmt)
                return
            #Multiple assignment for multiple varnames
            for i in range(0, len(expr.nodes)):
                varName = self.flattenAST(expr.nodes[i])
                if self.case(val, Name):
                    val = self.flattenAST(val)
                #Add varName to dict
                self.map(varName)
                stmt = self.block+varName+"="+str(val)
                #Append to flattenStatements
                self.flattenStatements.append(stmt)

        #UnarySub - return Name()
        elif self.case(expr, UnarySub) and self.isIrreducible(expr.expr):
            val = self.flattenAST(expr.expr)
            if self.case(val, Name):
                val = self.flattenAST(val)
            val = "-"+str(val)
            #Create new tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            stmt = self.block+tmpVar+"="+str(val)
            #Add tmp name to dictionary
            self.map(tmpVar)
            #Append to flattenStatement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #Add - return Name()
        elif self.case(expr, Add) and self.isIrreducible(expr.left) and \
        self.isIrreducible(expr.right):
            #lft and rgt are int or var:str that are the operands of add
            lft = self.flattenAST(expr.left)
            rgt = self.flattenAST(expr.right)
            if self.case(lft, Name):
                lft = self.flattenAST(lft)
            if self.case(rgt, Name):
                rgt = self.flattenAST(rgt)
            #Create tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            stmt = self.block+tmpVar+"="+str(lft)+"+"+str(rgt)
            #Add tmp name to dictionary
            self.map(tmpVar)
            #Append statement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)


        #Sub - return Name()
        elif self.case(expr, Sub) and self.isIrreducible(expr.left) and \
        self.isIrreducible(expr.right):
            #lft and rgt are int or var:str that are the operands of add
            lft = self.flattenAST(expr.left)
            rgt = self.flattenAST(expr.right)
            if self.case(lft, Name):
                lft = self.flattenAST(lft)
            if self.case(rgt, Name):
                rgt = self.flattenAST(rgt)
            #Create tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            stmt = self.block+tmpVar+"="+str(lft)+"-"+str(rgt)
            #Add tmp name to dictionary
            self.map(tmpVar)
            #Append statement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #Compare - return Name()
        #P2 refactored
        elif self.case(expr, Compare):
            #reduce all values in the Or statement
            tmpVar = self.tmp+str(self.variableCounter)
            #First two values in statement
            lft = self.flattenAST(expr.expr)
            rgt = self.flattenAST(expr.ops[0][1])
            op = expr.ops[0][0]

            if self.case(lft, Name) or self.case(lft, Const):
                lft = self.flattenAST(lft)
            if self.case(rgt, Name) or self.case(rgt, Const):
                rgt = self.flattenAST(rgt)
            stmt = self.block+tmpVar+"="+str(lft)+" "+op+" "+str(rgt)
            self.map(tmpVar)
            self.flattenStatements.append(stmt)
            self.variableCounter += 1

            if len(expr.ops) <= 1:
                return Name(tmpVar)

            for i in range(1, len(expr.ops)):
                val = self.flattenAST(expr.ops[i][1])
                if self.case(val, Name) or self.case(val, Const):
                    val = self.flattenAST(val)
                op = expr.ops[i][0]
                newTmpVar = self.tmp+str(self.variableCounter)
                stmt = self.block+newTmpVar+"="+tmpVar+" "+op+" "+str(val)
                self.map(newTmpVar)
                self.flattenStatements.append(stmt)
                self.variableCounter += 1
                tmpVar = newTmpVar

            return Name(tmpVar)

        #Or - return Name()
        #P2 refactored
        elif self.case(expr, Or):
            #reduce all values in the Or statement
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter += 1
            self.map(tmpVar)
            #First two values in statement
            lft = self.flattenAST(expr.nodes[0])
            rgt = self.flattenAST(expr.nodes[1])

            if self.case(lft, Name) or self.case(lft, Const):
                lft = self.flattenAST(lft)
            if self.case(rgt, Name) or self.case(rgt, Const):
                rgt = self.flattenAST(rgt)
            stmt = self.block+tmpVar+"="+str(lft)+" or "+str(rgt)

            self.flattenStatements.append(stmt)


            if len(expr.nodes) <= 2:
                return Name(tmpVar)

            for i in range(2, len(expr.nodes)):
                val = self.flattenAST(expr.nodes[i])
                if self.case(val, Name) or self.case(val, Const):
                    val = self.flattenAST(val)

                newTmpVar = self.tmp+str(self.variableCounter)
                stmt = self.block+newTmpVar+"="+tmpVar+" or "+str(val)
                self.map(newTmpVar)
                self.flattenStatements.append(stmt)
                self.variableCounter += 1
                tmpVar = newTmpVar

            return Name(tmpVar)

        #And - return Name()
        #P2 refactored
        elif self.case(expr, And):
            #reduce all values in the Or statement
            tmpVar = self.tmp+str(self.variableCounter)
            self.map(tmpVar)
            self.variableCounter += 1
            #First two values in statement
            lft = self.flattenAST(expr.nodes[0])
            rgt = self.flattenAST(expr.nodes[1])
            if self.case(lft, Name) or self.case(lft, Const):
                lft = self.flattenAST(lft)
            if self.case(rgt, Name) or self.case(rgt, Const):
                rgt = self.flattenAST(rgt)
            stmt = self.block+tmpVar+"="+str(lft)+" and "+str(rgt)

            self.flattenStatements.append(stmt)


            if len(expr.nodes) <= 2:
                return Name(tmpVar)

            for i in range(2, len(expr.nodes)):
                val = self.flattenAST(expr.nodes[i])
                if self.case(val, Name) or self.case(val, Const):
                    val = self.flattenAST(val)

                newTmpVar = self.tmp+str(self.variableCounter)
                stmt = self.block+newTmpVar+"="+tmpVar+" and "+str(val)
                self.map(newTmpVar)
                self.flattenStatements.append(stmt)
                self.variableCounter += 1
                tmpVar = newTmpVar

            return Name(tmpVar)

        #Not - return Name()
        #P2 refactored
        elif self.case(expr, Not) and self.isIrreducible(expr.expr):
            val = expr.expr
            if self.case(val, Name) or self.case(val, Const):
                val = self.flattenAST(val)
            #create tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter += 1
            stmt = self.block+tmpVar+"= not "+str(val)
            #map tmp name
            self.map(tmpVar)
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #List - return Name()
        #P2 refactored
        elif self.case(expr, List):
            # Work here. Step on each element until it is irreducable. \
            # Then construct a list and assign it a tmp name
            # print expr.nodes
            flatList = []
            for i in range(0, len(expr.nodes)):
                val = self.flattenAST(expr.nodes[i])
                if self.case(val, Name):
                    val = self.flattenAST(val)
                flatList.append(val)
            #Tmpvar for list
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter += 1
            stmt = ""
            if len(flatList) != 0:
                stmt = self.block+tmpVar+"=["
                for i in range(0, len(flatList)-1):
                    stmt += str(flatList[i])+str(",")
                stmt += str(flatList[len(flatList)-1])
                stmt += "]"
            else:
                stmt = self+block+str(tmpVar)+"= []"
            self.map(tmpVar)
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #Dict
        #P2 refactored
        elif self.case(expr, Dict):
            #step on all key and value pairs
            d = {}
            for i in range(0, len(expr.items)):
                val = expr.items[i]
                key = self.flattenAST(val[0])
                value = self.flattenAST(val[1])
                if self.case(key, Name):
                    key = self.flattenAST(key)
                if self.case(value, Name):
                    value = self.flattenAST(value)
                d[key] = value
            #tmpVar
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter += 1
            stmt = self.block+tmpVar+"={"
            for key in d:
                stmt += str(key)+":"+str(d[key])+","
            stmt += "}"
            self.map(tmpVar)
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #IfExp
        #P2 refactored
        elif self.case(expr, IfExp):
            condition = self.flattenAST(expr.test)
            then = self.flattenAST(expr.then)
            else_ = self.flattenAST(expr.else_)
            if self.case(condition, Name):
                condition = self.flattenAST(condition)
            if self.case(then, Name):
                then = self.flattenAST(then)
            if self.case(else_, Name):
                else_ = self.flattenAST(else_)
            #tmpVar
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter += 1
            stmt = self.block+tmpVar+"="+str(then)+" if "+str(condition)+" else "+str(else_)
            self.map(tmpVar)
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #Subscript
        #P2 refactored
        elif self.case(expr, Subscript):
            #Reduce index if needed
            index = []
            for i in range(0, len(expr.subs)):
                val = self.flattenAST(expr.subs[i])
                if self.case(val, Name):
                    val = self.flattenAST(val)
                index.append(val)
            arrayName = self.flattenAST(expr.expr)
            if self.case(arrayName, Name):
                arrayName = self.flattenAST(arrayName)
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter += 1
            stmt = self.block+str(tmpVar)+"="+arrayName+"["+str(index[0])+"]"
            self.map(tmpVar)
            self.flattenStatements.append(stmt)

            return Name(tmpVar)

        #Discard
        elif self.case(expr, Discard):
            rtn = self.flattenAST(expr.expr)
            #if self.case(rtn, Name):
            #    rtn = self.flattenAST(rtn)
            #self.flattenStatements.append(self.block+str(rtn))

        #Function FLAT
        elif self.case(expr, Function):
            #Functionally reduce the argument names to a string of formation x,y,z,
            args = reduce(lambda x,y: x+","+y, expr.argnames) if len(expr.argnames)>0 else ""
            #Map function name to its free vars set
            free_bound = free_vars(expr, set([]))

            self.freeMap[expr.name] = listify(free_bound[0])
            self.boundMap[expr.name] = listify(free_bound[1])
            val = list(expr.argnames)
            val.append("free_vars_"+str(expr.name))
            self.argMap[expr.name] = val

            definition = self.block+"def "+str(expr.name)+"("+"free_vars_"+str(expr.name)+","+args+"):"
            self.flattenStatements.append(definition)
            self.indent()

            i = 0
            for fv in self.freeMap[expr.name]:
                expand = self.block+fv+"=free_vars_"+str(expr.name)+"["+str(i)+"]"
                self.flattenStatements.append(expand)
                i += 1
            #recurse on function block statements
            #Reset stack counter to 0 for inner body then set it back originally
            stackHolder = self.stackVarCounter
            self.stackVarCounter = 1
            self.flattenAST(expr.code)
            #restore original stack count value
            self.stackVarCounter = stackHolder
            self.dedent()

        #Return FLAT
        elif self.case(expr, Return):
            rtn = self.flattenAST(expr.value)
            if self.case(rtn, Name):
                rtn = self.flattenAST(rtn)
            stmt = self.block+"return "+str(rtn)
            self.flattenStatements.append(stmt)

        #Lambda FLAT
        elif self.case(expr, Lambda):
            args = reduce(lambda x,y: x+","+y, expr.argnames) if len(expr.argnames)>0 else ""
            #Map function name to its free vars set
            #self.freeMap["lambda_"+str(self.lambdaCount)] = free_vars(expr, set([]))
            lambdaFunctionName = "lambda_"+str(self.lambdaCount)

            free_bound = free_vars(expr, set([]))

            self.freeMap[lambdaFunctionName] = listify(free_bound[0])
            self.boundMap[lambdaFunctionName] = listify(free_bound[1])
            val = list(expr.argnames)
            val.append("free_vars_"+str(lambdaFunctionName))
            self.argMap[lambdaFunctionName] = val

            definition = self.block+"def lambda_"+str(self.lambdaCount)+"("+"free_vars_"+str(lambdaFunctionName)+","+args+"):"
            self.flattenStatements.append(definition)
            #recurse on function block
            self.indent()
            stackHolder = self.stackVarCounter
            self.stackVarCounter = 1

            rtn = self.flattenAST(expr.code)
            rtn = self.flattenAST(rtn) if self.case(rtn, Name) else rtn
            self.flattenStatements.append(self.block+"return "+rtn)

            self.stackVarCounter = stackHolder
            self.dedent()
            tmpVar = "lambda_"+str(self.lambdaCount)
            #self.variableCounter += 1
            self.map("lambda_"+str(self.lambdaCount))
            #stmt = self.block+"lambda_"+str(self.lambdaCount)
            #self.flattenStatements.append(stmt)
            self.lambdaCount += 1
            return Name(tmpVar)

        #Add induct - return AST node
        elif self.case(expr, Add):
            lft = expr.left
            rgt = expr.right
            if not self.isIrreducible(lft):
                lft = self.flattenAST(lft)
                token = Add((lft, rgt))
                return self.flattenAST(token)

            if not self.isIrreducible(rgt):
                rgt = self.flattenAST(rgt)
                token = Add((lft, rgt))
                return self.flattenAST(token)

        #Sub induct - return AST node
        elif self.case(expr, Sub):
            lft = expr.left
            rgt = expr.right
            if not self.isIrreducible(lft):
                lft = self.flattenAST(lft)
                token = Sub((lft, rgt))
                return self.flattenAST(token)

            if not self.isIrreducible(rgt):
                rgt = self.flattenAST(rgt)
                token = Sub((lft, rgt))
                return self.flattenAST(token)

        #Assign induct - return AST node
        elif self.case(expr, Assign):
            val = expr.expr
            if not self.isIrreducible(val):
                val = self.flattenAST(val)
                token = Assign(expr.nodes, val)
                return self.flattenAST(token)

        #UnarySub induct - return AST node
        elif self.case(expr, UnarySub):
            val = expr.expr
            if not self.isIrreducible(val):
                val = self.flattenAST(val)
                token = UnarySub(val)
                return self.flattenAST(token)

        #Not induct - return AST node
        elif self.case(expr, Not):
            val = expr.expr
            if not self.isIrreducible(val):
                val = self.flattenAST(val)
                token = Not(val)
                return self.flattenAST(token)


        #Raise exception
        else:
            ColorPrint("Error: Uncaught node in flatten: "+str(expr),MAGENTA)
            raise Exception()
    #---------------------------------------------------------------------------------------------
    #Wrapper
    def driver(self):
        #Product flatten P0
        #self.requestUniqueTmpName()
        self.flattenAST(self.ast)
        #ColorPrint(self.varMap, MAGENTA)
        f = open("flat.py", "w")
        for i in range(0, len(self.flattenStatements)):
            f.write(str(self.flattenStatements[i])+"\n")
        f.close()

        #Parse flat.py
        #Uncomment line below when using the standard parser again
        ast = compiler.parseFile("flat.py")
        #print ast
        #heapify
        #heapifyAST = heap(ast)
        #print heapifyAST
        #Explicate here for now
        explicateAST = explicate(ast)


        #DEBUG
        #print YELLOW+"Explicated Flatten pyCompiler: "+str(explicateAST)+WHITE
        #print self.varMap
        #print explicateAST
        self.compile(explicateAST)
        #Output asm file
        fileOutName = str(sys.argv[1])[0:-3] + ".s"
        f = open(fileOutName, "w")
        #Write out setup and tear down
        f.write(".globl main\nmain:\npushl %ebp\nmovl %esp, %ebp\n")
        for i in range(0, len(self.x86Statements)):
            f.write(self.x86Statements[i]+"\n")
        f.write("movl $0, %eax\nleave\nret\n")
        # Write the function statements.
        for key in self.functions:
            f.write("\n")
            for stmt in self.functions[key]:
                f.write(stmt+"\n")
        f.close()
        return ast

    #---------------------------------------------------------------------------------------------
    #Explicated Python1 -> x86. all statements are flatten
    def compile(self, expr):
        #Base Cases
        #Const
        #P1 Okay
        if self.case(expr, Const):
            return expr.value
        #Name
        #P1 Okay
        elif self.case(expr, Name):
            return expr.name
        #Bool
        elif self.case(expr, Bool):
            return expr.expr

        #CallFunc - input for now...
        #Needs to be refactored for P1. No longer just 'call input'
        #Needs more work for pushing arguments
        elif self.case(expr, CallFunc):
            #Push arguments on stack
            ColorPrint(expr.args, GREEN)
            argList = expr.args
            for argument in (argList):
                val = self.compile(argument)
                if self.isArg(val):
                    offset = self.isArg(val)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif val in self.varMap:
                    #Get location of variable on stack
                    stackLocation = self.varMap[val] * 4
                    movl_x86 = "movl -"+str(stackLocation)+"(%ebp), %eax"
                    self.quickInsert([movl_x86])
                elif self.case(val, Register):
                    movl = "movl %"+val.name+", %eax"
                    self.quickInsert([movl])
                pushl = "pushl %eax"
                self.quickInsert([pushl])

            print_input_x86 = "call "+str(expr.node.name)
            #Exception for input. Needs to be refactored for P2 for functions that are not input
            self.quickInsert([print_input_x86])
            if expr.node.name == "input":
                shl2_x86 = "shl $2, %eax"
                self.quickInsert([shl2_x86])
            #If input has args, print it out

            return Register("eax")

        #InjectFrom
        #New node from P1
        elif self.case(expr, InjectFrom):
            val = self.compile(expr.arg)
            #Make Tag. Set TAG to be 0 by default as integer const
            TAG = 0x0
            if expr.typ == 'BOOL':
                TAG = 0x1
            elif expr.typ == 'FLOAT':
                TAG = 0x2
            elif expr.typ == 'BIG':
                TAG = 0x3

            #If val not register

            if not self.case(val, Register):
                movl = ""
                if val == 'True':
                    movl = "movl $1, %eax"
                elif val == 'False':
                    movl = "movl $0, %eax"
                else:
                    movl = "movl $"+str(val)+", %eax"
                self.quickInsert([movl])
            #Inject correct tag
            if expr.typ in ['INT', 'BOOL', 'FLOAT']:
                shl_x86 = "shl $2, %eax"
                or_x86 = "or $"+str(TAG)+", %eax"
                self.quickInsert([shl_x86, or_x86])
            elif expr.typ == 'BIG':
                or_x86 = "or $"+str(TAG)+", %eax"
                self.quickInsert([or_x86])

            #return tagged value in eax
            return Register("eax")


        #Module
        #P1 Okay
        elif self.case(expr, Module):
            return self.compile(expr.node)

        #Stmt
        #P1 Okay
        elif self.case(expr, Stmt):
            #Create stack space
            stackVarCounter = self.stackVarCounter-1
            if self.inFunction != "False":
                stackVarCounter = len(self.boundMap[self.inFunction]) - len(self.argMap[self.inFunction])
                stackVarCounter = stackVarCounter * -1 if stackVarCounter < 0 else stackVarCounter
            if not self.stackVarCounter is 0:
                subl_x86 = "subl $" + str(4*(stackVarCounter)) + ", %esp"
                self.quickInsert([subl_x86])
            #For each sub AST, recurse on the sub AST nodes
            for i in range(0, len(expr.nodes)):
                if self.numOfFunctionStmts == 0:
                    self.inFunction = "False"
                self.compile(expr.nodes[i])
                if self.numOfFunctionStmts > 0:
                    self.numOfFunctionStmts = self.numOfFunctionStmts - 1
            #Collapse the stack when program ends
            if self.stackVarCounter != 0:
                addl_x86 = "addl $"+str(4*(stackVarCounter)) + ", %esp"
                self.quickInsert([addl_x86])

        #UnarySub
        #@Refactored for P1 - Removes the tag. The recursion will inject an int tag right after
        elif self.case(expr, UnarySub):
            varName = self.compile(expr.expr)
            #Check if a variable is being negated or a const
            if self.isArg(varName):
                offset = self.isArg(varName)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                shr_x86 = "shr $2, %eax"
                negl_x86 = "negl %eax"
                self.quickInsert([movl, shr_x86, negl_x86])
                return Register("eax")
            elif varName in self.varMap:
                #Get location of variable on stack
                stackLocation = self.varMap[varName] * 4
                movl_x86 = "movl -"+str(stackLocation)+"(%ebp), %eax"
                #Remove tag and negate eax
                shr_x86 = "shr $2, %eax"
                negl_x86 = "negl %eax"
                self.quickInsert([movl_x86, shr_x86, negl_x86])
                return Register("eax")
            elif self.case(varName, Register):
                movl_x86 = "movl %"+str(varName.name)+", %eax"
                shr_x86 = "shr $2, %eax"
                negl = "negl %eax"
                self.quickInsert([movl_x86, shr_x86, negl])
                return Register("eax")


        #Assign
        #Needs to be refactored for P1. Double check if tagging is needed
        #P2 ready
        elif self.case(expr, Assign):
            #If lvalue is a location inside a list, grab the list pointer, step on the index,
            #and assign the stepped rvalue to it.
            if self.case(expr.nodes[0], Subscript):
                subscript = expr.nodes[0]
                listName = self.compile(subscript.expr)
                #offsetName = self.varMap[listName] * 4
                offsetName = 0
                if listName in self.varMap:
                    offsetName = self.varMap[listName] * -4
                elif self.isArg(listName):
                    offsetName = self.isArg(listName) * 4
                #Move list name in edx
                movl1 = "movl "+str(offsetName)+"(%ebp), %edx"
                self.quickInsert([movl1])
                index = self.compile(subscript.subs[0])
                if self.isArg(index):
                    offset = self.isArg(index)
                    movl = "movl "+str(offset)+"(%ebp), %ebx"
                    self.quickInsert([movl])
                elif index in self.varMap:
                    #Move index into ebx
                    offsetIndex = self.varMap[index] * 4
                    movl2 = "movl -"+str(offsetIndex)+"(%ebp), %ebx"
                    self.quickInsert([movl2])
                else:
                    #It's a register, move into ebx
                    movl2 = "movl %"+str(index.name)+", %ebx"
                    self.quickInsert([movl2])
                #Step on rvalue
                val = self.compile(expr.expr)
                if self.isArg(val):
                    offset = self.isArg(val)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif val in self.varMap:
                    assignOffset = self.varMap[val] * 4
                    movl3 = "movl -"+str(assignOffset)+"(%ebp), %eax"
                    self.quickInsert([movl3])
                #Val is already in eax
                #edx[ebx] = eax
                pushl = "pushl %eax\npushl %ebx\npushl %edx"
                call_sub = "call set_subscript"
                self.quickInsert([pushl,call_sub])
                return
            #varName is a raw string. Get its offset on the stack
            varName = self.compile(expr.nodes[0])
            #offset = self.varMap[varName] * 4
            offset = 0
            if varName in self.varMap:
                offset = self.varMap[varName] * -4
            elif self.isArg(varName):
                offset = self.isArg(varName)
            #val is the assigning value. It might be a register or another variable. check
            val = self.compile(expr.expr)
            if self.isArg(val):
                assignOffset = self.isArg(val)
                movl = "movl "+str(assignOffset)+"(%ebp), %eax"
                movl2 = "movl %eax, "+str(offset)+"(%ebp)"
                self.quickInsert([movl1, movl2])
            elif val in self.varMap:
                #If val is the variable being assigned to varName.
                assignOffset = self.varMap[val] * 4
                movl1 = "movl -"+str(assignOffset)+"(%ebp), %eax"
                movl2 = "movl %eax, "+str(offset)+"(%ebp)"
                self.quickInsert([movl1, movl2])
            elif self.case(val, Register):
                movl1 = "movl %"+str(val.name)+", "+str(offset)+"(%ebp)"
                self.quickInsert([movl1])
            else:
                print "Something went wrong "+str(val)+" was trying to be assigned \
                but slipped through."

                #WORK up from here // check stuff below
        #Add
        #@Refactored for P1 - return non tagged value, recursion will add tag
        #P2 ready
        elif self.case(expr, Add):
            lft = self.compile(expr.left)
            #Test the return type of lft
            if self.case(lft, Register):
                regName = lft.name
                #Remove tag and save to ebx
                movl = "movl %"+str(regName)+", %ebx"
                shr_x86 = "shr $2, %ebx"
                self.quickInsert([movl, shr_x86])
            elif self.isArg(lft):
                offset = self.isArg(lft)
                movl = "movl "+str(offset)+"(%ebp), %ebx"
                shr_x86 = "shr $2, %ebx"
                self.quickInsert([movl, shr_x86])
            elif lft in self.varMap:
                #lft is a var. Get its offset
                tmpOffset = self.varMap[lft] * 4
                movl_x86 = "movl -"+str(tmpOffset)+"(%ebp), %ebx"
                shr_x86 = "shr $2, %ebx"
                self.quickInsert([movl_x86, shr_x86])
            rgt = self.compile(expr.right)
            if self.case(rgt, Register):
                regName = rgt.name
                #Remove tag and save to ebx
                movl = "movl %"+str(regName)+", %eax"
                shr_x86 = "shr $2, %eax"
                addl = "addl %eax, %ebx"
                reverse = "movl %ebx, %eax"
                self.quickInsert([movl, shr_x86, addl, reverse])
            elif self.isArg(rgt):
                offset = self.isArg(rgt)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                shr_x86 = "shr $2, %eax"
                addl = "addl %eax, %ebx"
                reverse = "movl %ebx, %eax"
                self.quickInsert([movl, shr_x86, addl, reverse])
            elif rgt in self.varMap:
                #lft is a var. Get its offset
                tmpOffset = self.varMap[rgt] * 4
                movl_x86 = "movl -"+str(tmpOffset)+"(%ebp), %eax"
                shr_x86 = "shr $2, %eax"
                addl = "addl %eax, %ebx"
                reverse = "movl %ebx, %eax"
                self.quickInsert([movl_x86, shr_x86, addl, reverse])

            return Register("eax")


        #AssName
        #P1 Okay
        elif self.case(expr, AssName):
            return expr.name

        #Printnl - prints last thing pushed onto the stack
        #@Refactored for P1
        #P2 ready
        elif self.case(expr, Printnl):
            val = self.compile(expr.nodes[0])
            if self.case(val, Register):
                push = "pushl %"+str(val.name)
                printAny = "call print_any"
                self.quickInsert([push, printAny])
            elif self.isArg(val):
                offset = self.isArg(val)
                pushl = "pushl "+str(offset)+"(%ebp)"
                printAny = "call print_any"
                self.quickInsert([pushl, printAny])
            elif val in self.varMap:
                offset = self.varMap[val] * 4
                pushl = "pushl -"+str(offset)+"(%ebp)"
                printAny = "call print_any"
                self.quickInsert([pushl, printAny])

        #Discard
        #P1 Okay
        elif self.case(expr, Discard):
            self.compile(expr.expr)

#------------------> new P1 AST classes
        #IfExp is done
        elif self.case(expr, IfExp):
            #IfExp takes a tagged value for the condition
            test = self.compile(expr.test)
            #test returns back a reg or a variable
            #Move test register into eax
            if test in self.varMap:
                offset = self.varMap[test] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif self.isArg(test):
                offset = self.isArg(test)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif test in self.varMap:
                movl = "movl %"+str(test.name)+", %eax"
                self.quickInsert([movl])

            #Save value from eax to esi and then call is_true
            movl = "movl %eax, %esi"
            pushl = "pushl %eax"
            call = "call is_true"

            cmpl = "cmpl $0, %eax"
            ifIsFalse = self.requestJumpNumber()
            final = self.requestShortNumber()
            je = "je else"+str(ifIsFalse)
            self.quickInsert([movl, pushl, call, cmpl, je])
            #Then
            then = self.compile(expr.then)
            if self.case(then, Register):
                movl = "movl %"+str(then.name)+", %eax"
                self.quickInsert([movl])
            if self.isArg(then):
                offset = self.isArg(then)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif then in self.varMap:
                offset = self.varMap[then] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])

            #When then clause finish, jump to end
            endIf = "jmp ends"+str(final)
            self.quickInsert([endIf])

            #Else
            else1 = "else"+str(ifIsFalse)+":"
            self.quickInsert([else1])
            #Else clause
            else_output = self.compile(expr.else_)
            if self.case(else_output, Register):
                movl = "movl %"+str(else_output.name)+", %eax"
                self.quickInsert([movl])
            elif self.isArg(else_output):
                offset = self.isArg(else_output)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif else_output in self.varMap:
                offset = self.varMap[else_output] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])

            #End
            end = "ends"+str(final)+":"
            self.quickInsert([end])
            return Register("eax")
        #Compare returns a boolean that's tagged
        #Compare is done
        elif self.case(expr, Compare):
            #eax is the left operand, save it to edi
            lft = self.compile(expr.expr)
            operator = expr.ops[0][0]
            if operator in ['==', '!=']:
                #move lft into eax
                if self.isArg(lft):
                    offset = self.isArg(lft)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif lft in self.varMap:
                    offset = self.varMap[lft] * 4
                    movl = "movl -"+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif self.case(lft, Register):
                    movl = "movl %"+str(lft.name)+", %eax"
                    self.quickInsert([movl])

                #save lft into esi
                final = self.requestShortNumber()
                lftIsBig = self.requestJumpNumber()
                movl = "movl %eax, %esi"
                andl = "andl $0x3, %esi"
                cmpl = "cmpl $2, %esi"
                jg = "jg else"+str(lftIsBig)
                #Move lft back into esi
                movl1 = "movl %eax, %esi"
                self.quickInsert([movl, andl, cmpl, jg, movl1])
                #Begin rgt evaulation
                rgt = self.compile(expr.ops[0][1])
                if self.isArg(rgt):
                    offset = self.isArg(rgt)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif rgt in self.varMap:
                    offset = self.varMap[rgt] * 4
                    movl = "movl -"+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif self.case(rgt, Register):
                    movl = "movl %"+str(rgt.name)+", %eax"
                    self.quickInsert([movl])
                #Move rgt into edi and have lft be in esi
                movl = "movl %eax, %edi"
                #Remove tag on both
                shrl = "shr $2, %esi"
                shrr = "shr $2, %edi"
                cmpl = "cmpl %esi, %edi"
                smallAreNotEqual = self.requestJumpNumber()
                switch = "jne" if operator == '==' else "je"
                jne = switch+" else"+str(smallAreNotEqual)
                #Both are equal, return true value
                movl1 = "movl $1, %eax"
                jmpE = "jmp ends"+str(final)
                elseN = "else"+str(smallAreNotEqual)+":"
                movl2 = "movl $0, %eax"
                jmpE2 = "jmp ends"+str(final)
                else1 = "else"+str(lftIsBig)+":"
                self.quickInsert([movl, shrl, shrr, cmpl, jne, movl1, \
                jmpE, elseN, movl2, jmpE2, else1])
                #movl lft back into esi
                movl = "movl %eax, %esi"
                self.quickInsert([movl])
                rgt = self.compile(expr.ops[0][1])
                if self.isArg(rgt):
                    offset = self.isArg(rgt)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif rgt in self.varMap:
                    offset = self.varMap[rgt] * 4
                    movl = "movl -"+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif self.case(rgt, Register):
                    movl = "movl %"+str(rgt.name)+", %eax"
                    self.quickInsert([movl])
                #move rgt into edi
                movl2 = "movl %eax, %edi"
                #Compare items in dict or list
                pushl= "andl $0xfffffffc, %esi\npushl %esi"
                pushr= "andl $0xfffffffc, %edi\npushl %edi"
                call = "call equal"
                #1 or 0 is in eax. jmp to end
                self.quickInsert([movl2, pushl, pushr, call])
                if operator == "!=":
                    flip = "xor $0x1, %eax"
                    self.quickInsert([flip])
                end = "ends"+str(final)+":"
                self.quickInsert([end])

            elif operator == 'is':
                #eax is the left operand, save it to edi
                lft = self.compile(expr.expr)
                operator = expr.ops[0][0]
                if self.isArg(lft):
                    offset = self.isArg(lft)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif lft in self.varMap:
                    offset = self.varMap[lft] * 4
                    movl = "movl -"+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif self.case(lft, Register):
                    movl = "movl %"+str(lft.name)+", %eax"
                    self.quickInsert([movl])
                #save lft into esi
                final = self.requestShortNumber()
                lftIsBig = self.requestJumpNumber()
                movl = "movl %eax, %esi"
                andl = "andl $0x3, %esi"
                cmpl = "cmpl $2, %esi"
                jg = "jg else"+str(lftIsBig)
                #Move lft back into esi
                movl1 = "movl %eax, %esi"
                self.quickInsert([movl, andl, cmpl, jg, movl1])
                #Begin rgt evaulation
                rgt = self.compile(expr.ops[0][1])
                if self.isArg(rgt):
                    offset = self.isArg(rgt)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif rgt in self.varMap:
                    offset = self.varMap[rgt] * 4
                    movl = "movl -"+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif self.case(rgt, Register):
                    movl = "movl %"+str(rgt.name)+", %eax"
                    self.quickInsert([movl])
                #Move rgt into edi and have lft be in esi
                movl = "movl %eax, %edi"
                #Remove tag on both
                shrl = "shr $2, %esi"
                shrr = "shr $2, %edi"
                cmpl = "cmpl %esi, %edi"
                smallAreNotEqual = self.requestJumpNumber()
                switch = "jne" if operator == 'is' else "je"
                jne = switch+" else"+str(smallAreNotEqual)
                #Both are equal, return true value
                movl1 = "movl $1, %eax"
                jmpE = "jmp ends"+str(final)
                elseN = "else"+str(smallAreNotEqual)+":"
                movl2 = "movl $0, %eax"
                jmpE2 = "jmp ends"+str(final)
                else1 = "else"+str(lftIsBig)+":"
                self.quickInsert([movl, shrl, shrr, cmpl, jne, movl1, jmpE, elseN, \
                movl2, jmpE2, else1])
                #movl lft back into esi
                movl = "movl %eax, %esi"
                self.quickInsert([movl])
                rgt = self.compile(expr.ops[0][1])
                if self.isArg(rgt):
                    offset = self.isArg(rgt)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif rgt in self.varMap:
                    offset = self.varMap[rgt] * 4
                    movl = "movl -"+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                elif self.case(rgt, Register):
                    movl = "movl %"+str(rgt.name)+", %eax"
                    self.quickInsert([movl])
                #move rgt into edi
                movl2 = "movl %eax, %edi"
                pointerCompare = "cmpl %esi, %edi"
                pointerNotEqual = self.requestJumpNumber()
                jne = "jne else"+str(pointerNotEqual)
                #Pointer match, return 1
                movlT = "movl $1, %eax"
                jmpT = "jmp ends"+str(final)
                elseP = "else"+str(pointerNotEqual)+":"
                movlT2 = "movl $0, %eax"
                self.quickInsert([movl2, pointerCompare, jne, movlT, jmpT, elseP, \
                movlT2])
                end  = "ends"+str(final)+":"
                self.quickInsert([end])
            return Register("eax")


        elif self.case(expr, Subscript):
            # Step on expr.subs[0] to get the index.
            value = self.compile(expr.subs[0])
            # If it's already a register:
            if self.case(value, Register):
                if value.name != "eax":
                    # Put it into %eax. (is this needed?)
                    movl_x86 = "movl %" + value.name + ", %eax"
                    # Append x86 statements.
                    self.quickInsert([movl_x86])
            elif self.isArg(value):
                offset = self.isArg(value)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif value in self.varMap:
                offset = self.varMap[value] << 2
                movl_x86 = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl_x86])

            # Assume it's already tagged, so no tagging needed.
            pushl_x86 = "pushl %eax"
            # Append x86 statements.
            self.quickInsert([pushl_x86])

            # This is the pointer to the list.
            varName = self.compile(expr.expr)
            # If it's in the varMap:
            if self.isArg(varName):
                offset = self.isArg(varName)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                pushl = "pushl %eax"
                self.quickInsert([movl,pushl])
            elif varName in self.varMap:
                # Get location of variable on stack.
                stackLocation = self.varMap[varName] << 2
                # Move variable value into %eax.
                movl_x86 = "movl -"+str(stackLocation)+"(%ebp), %eax"
                pushl_x86 = "pushl %eax"
                # Append x86 statements.
                self.quickInsert([movl_x86])
                self.quickInsert([pushl_x86])

            call_get_subscript_x86 = "call get_subscript"
            # Append x86 statements.
            self.quickInsert([call_get_subscript_x86])
            return Register("eax")


        # GetTag is done
        elif self.case(expr, GetTag):
            arg = self.compile(expr.arg)
            if self.case(arg, Register):
                movl = "movl %"+str(arg.name)+", %eax"
                andl = "andl $3, %eax"
                shl2 = "shl $2, %eax"
                self.quickInsert([movl])
                self.quickInsert([andl])
                self.quickInsert([shl2])
            #get tag on variable
            elif self.isArg(arg):
                offset = self.isArg(arg)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                andl = "andl $3, %eax"
                shl2 = "shl $2, %eax"
                self.quickInsert([movl,andl,shl2])
            elif arg in self.varMap:
                offset = self.varMap[arg] << 2
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                andl = "andl $3, %eax"
                shl2 = "shl $2, %eax"
                self.quickInsert([movl])
                self.quickInsert([andl])
                self.quickInsert([shl2])
            return Register("eax")

        # subtract 12 from stack at the beginning, add 12 to stack at end.
        elif self.case(expr, List):
            # Make room for three more variables on the stack.
            subl_x86 = "subl $12, %esp"
            self.quickInsert([subl_x86])

            # Below code creates a list.
            # Below line gets the number of nodes == length of the list.
            lengthOfList = len(expr.nodes)
            # Below two lines adds a tag to the INT.
            movl_x86 = "movl $" + str(lengthOfList) + ", %eax"
            shl_x86 = "shl $2, %eax"
            # Pushes %eax onto the stack to prepare for function call.
            pushl_x86 = "pushl %eax"
            # Calls create_list function.
            call_createList_x86 = "call create_list"
            # Adds a BIG tag to %eax, which is now a pointer to the list.
            # Don't need to shift pointers when adding tag.
            add_BIG_tag_x86 = "or $3, %eax"
            # Moves %eax into next available stack location.
            movl_eax_into_stack1_x86 = "movl %eax, -" + str(4*(self.stackVarCounter)) + "(%ebp)"
            # Appends x86 stataments.
            self.quickInsert([movl_x86])
            self.quickInsert([shl_x86])
            self.quickInsert([pushl_x86])
            self.quickInsert([call_createList_x86])
            self.quickInsert([add_BIG_tag_x86])
            self.quickInsert([movl_eax_into_stack1_x86])
            # Above code creates a list.

            #Below code gets values and puts them at the required index.
            # Loop through each index.
            for index in range(0, lengthOfList):
                # Below code gets and tags the index.
                # Puts the index into %eax.
                movl_1_x86 = "movl $" + str(index) + ", %eax"
                # Tags the index.
                shl_1_x86 = "shl $2, %eax"
                # Puts %eax into the second stack location we made.
                movl_2_x86 = "movl %eax, -" + str(4*(self.stackVarCounter+1)) + "(%ebp)"
                # Above code gets and tags the index.
                # Appends x86 statements.
                self.quickInsert([movl_1_x86])
                self.quickInsert([shl_1_x86])
                self.quickInsert([movl_2_x86])

                # Steps on the node at index, gets the val.
                val = self.compile(expr.nodes[index])
                if self.case(val, Register):
                    movl_4_x86 = "movl %" + val.name + ", -" + str(4*(self.stackVarCounter+2)) + "(%ebp)"
                elif self.isArg(val):
                    offset = self.isArg(val)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    self.quickInsert([movl])
                    movl_4_x86 = "movl %eax, -" + str(4*(self.stackVarCounter+2)) + "(%ebp)"
                else:
                    #val is a variable, get its offset in varMap
                    offset = self.varMap[val] << 2
                    secret_movl = "movl -"+str(offset)+"(%ebp), %eax"
                    #movl_3_x86 = "movl $" + str(val) + ", %eax"
                    # Tags the value. Don't need OR because it's an INT.
                    # Don't tag the values, since it's a var, it already has a tag -Michael
                    #shl_2_x86 = "shl $2, %eax"
                    # Appends x86 statements.
                    self.quickInsert([secret_movl])
                    #self.quickInsert([shl_2_x86)
                    # Puts %eax into the third stack location we made.
                    movl_4_x86 = "movl %eax, -" + str(4*(self.stackVarCounter+2)) + "(%ebp)"
                # Appends x86 statements.
                self.quickInsert([movl_4_x86])
                # Push onto the stack in reverse order.
                pushl_1_x86 = "pushl -" + str(4*(self.stackVarCounter+2)) + "(%ebp)"
                pushl_2_x86 = "pushl -" + str(4*(self.stackVarCounter+1)) + "(%ebp)"
                pushl_3_x86 = "pushl -" + str(4*(self.stackVarCounter)) + "(%ebp)"
                # Calls the function to insert a value at an index.
                call_set_subscript_x86 = "call set_subscript"
                # Appends x86 statements.
                self.quickInsert([pushl_1_x86])
                self.quickInsert([pushl_2_x86])
                self.quickInsert([pushl_3_x86])
                self.quickInsert([call_set_subscript_x86])

            # Put list pointer back into %eax.
            movl_x86 = "movl -" + str(4*(self.stackVarCounter)) + "(%ebp), %eax"
            # Remove the pointer's tag.
            #andl_x86 = "andl $0xfffffffc, %eax"
            # Append x86 statements.
            self.quickInsert([movl_x86])
            #self.quickInsert([andl_x86)

            # Collapse the stack by three variables.
            addl_x86 = "addl $12, %esp"
            self.quickInsert([addl_x86])
            return Register("eax")

        # Waiting on IfExp.
        elif self.case(expr, AddList):
            lft = self.compile(expr.left)

            if self.isArg(lft):
                offset = self.isArg(lft)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif lft in self.varMap:
                offset = self.varMap[lft] << 2
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            #move lft operand to ebx and remove its tag
            removeLftTag = "andl $0xfffffffc, %eax"
            movlLft = "movl %eax, %ebx"
            self.quickInsert([removeLftTag,movlLft])
            rgt = self.compile(expr.right)
            if self.isArg(rgt):
                offset = self.isArg(rgt)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif rgt in self.varMap:
                offset = self.varMap[rgt] << 2
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            removeRgtTag = "andl $0xfffffffc, %eax"
            #Call add
            pushlRgt = "pushl %eax"
            pushlLft = "pushl %ebx"
            callAdd = "call add"
            #Inject big tag
            #orTag = "or $0x3, %eax"

            self.quickInsert([removeRgtTag,pushlRgt,pushlLft,callAdd])
            return Register("eax")

        elif self.case(expr, Dict):
            numberOfItems = (2 * len(expr.items))
            # Make room on the stack.
            subl_x86 = "subl $12, %esp"
            self.quickInsert([subl_x86])
            # Creates the Dict, converts it to a pyobj.
            create_dict_x86 = "call create_dict"
            pushl_x86 = "pushl %eax"
            inject_big_x86 = "or $0x3, %eax"
            # Append x86 statements.
            self.quickInsert([create_dict_x86])
            #self.quickInsert([pushl_x86)
            self.quickInsert([inject_big_x86])
            # Store dict in next stack location.
            movl_x86 = "movl %eax, -" + str(4*(self.stackVarCounter)) + "(%ebp)"
            # Append x86 statements.
            self.quickInsert([movl_x86])

            # Loop through each key : value pair.
            for index in range(0, len(expr.items)):
                # expr.items[index][0] == key
                # expr.items[index][1] == value
                # Step on the key. Hopefully it's a register.
                key = self.compile(expr.items[index][0])
                # If it's a register:
                if self.case(key, Register):
                    #  Move it onto the stack.
                    movl_x86 = "movl %" + key.name + ", -" + str(4*(self.stackVarCounter + 1)) + "(%ebp)"
                    self.quickInsert([movl_x86])
                elif self.isArg(key):
                    offset = self.isArg(key)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    movl_2 = "movl %eax, -" + str(4*(self.stackVarCounter + 1)) + "(%ebp)"
                    self.quickInsert([movl,movl_2])
                elif key in self.varMap:
                    offset = self.varMap[key] << 2
                    movl_1 = "movl -"+str(offset)+"(%ebp), %eax"
                    movl_2 = "movl %eax, -" + str(4*(self.stackVarCounter + 1)) + "(%ebp)"
                    self.quickInsert([movl_1])
                    self.quickInsert([movl_2])
                else:
                    print "still nah"
                    pass

                # Step on the value. Again, hopefully it's a register.
                value = self.compile(expr.items[index][1])
                # If it's a register:
                if self.case(value, Register):
                    #  Move it onto the stack.
                    movl_x86 = "movl %" + value.name + ", -" + str(4*(self.stackVarCounter + 2)) + "(%ebp)"
                    self.quickInsert([movl_x86])
                elif self.isArg(value):
                    offset = self.isArg(value)
                    movl = "movl "+str(offset)+"(%ebp), %eax"
                    movl_2 = "movl %eax, -" + str(4*(self.stackVarCounter + 2)) + "(%ebp)"
                    self.quickInsert([movl, movl_2])
                elif value in self.varMap:
                    offset = self.varMap[value] << 2
                    movl_1 = "movl -" + str(offset) + "(%ebp), %eax"
                    movl_2 = "movl %eax, -" + str(4*(self.stackVarCounter + 2)) + "(%ebp)"
                    self.quickInsert([movl_1])
                    self.quickInsert([movl_2])
                # Hopefully it's always a register.
                else:
                    print "In DICT. Value is not a Register."
                    pass

                # Push onto stack in reverser order: value, key, dict.
                pushl_3_x86 = "pushl -" + str(4*(self.stackVarCounter + 2)) + "(%ebp)"
                pushl_2_x86 = "pushl -" + str(4*(self.stackVarCounter + 1)) + "(%ebp)"
                pushl_1_x86 = "pushl -" + str(4*(self.stackVarCounter)) + "(%ebp)"
                # Appends x86 statements.
                self.quickInsert([pushl_3_x86])
                self.quickInsert([pushl_2_x86])
                self.quickInsert([pushl_1_x86])
                # Calls set_subscript.
                set_subscript_x86 = "call set_subscript"
                # Appends x86 statement.
                self.quickInsert([set_subscript_x86])

            # Put dict pointer back into %eax.
            movl_x86 = "movl -" + str(4*(self.stackVarCounter)) + "(%ebp), %eax"
            self.quickInsert([movl_x86])
            # Collapse the stack.
            addl_x86 = "addl $12, %esp"
            self.quickInsert([addl_x86])

            return Register("eax")
        #Returns the tagged node for short-circuit eval.
        # Or is done
        elif self.case(expr, Or):
            lft = self.compile(expr.nodes[0])
            if self.isArg(lft):
                offset = self.isArg(lft)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif lft in self.varMap:
                offset = self.varMap[lft] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif self.case(lft, Register):
                movl = "movl %"+str(lft.name)+", %eax"
                self.quickInsert([movl])

            final = self.requestShortNumber()
            lftIsNotTrue = self.requestJumpNumber()

            movl = "movl %eax, %esi"
            pushl= "pushl %eax"
            call = "call is_true"
            cmpl = "cmpl $0, %eax"
            #Jump if left is false
            je   = "je else"+str(lftIsNotTrue)
            #If lft is true, move esi back into eax and return
            movl2 = "movl %esi, %eax"
            jmpE = "jmp ends"+str(final)
            else1= "else"+str(lftIsNotTrue)+":"
            self.quickInsert([movl,pushl,call,cmpl,je,movl2,jmpE,else1])
            #Test right
            rgt = self.compile(expr.nodes[1])
            if self.isArg(rgt):
                offset = self.isArg(rgt)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif rgt in self.varMap:
                offset = self.varMap[rgt] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif self.case(rgt, Register):
                movl = "movl %"+str(rgt.name)+", %eax"
                self.quickInsert([movl])

            end  = "ends"+str(final)+":"
            self.quickInsert([end])
            return Register("eax")

        #Return the tagged node for short-circult eval
        #And done
        elif self.case(expr, And):
            lft = self.compile(expr.nodes[0])
            if self.isArg(lft):
                offset = self.isArg(lft)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif lft in self.varMap:
                offset = self.varMap[lft] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif self.case(lft, Register):
                movl = "movl %"+str(lft.name)+", %eax"
                self.quickInsert([movl])

            final = self.requestShortNumber()
            lftIsNotTrue = self.requestJumpNumber()

            movl = "movl %eax, %esi"
            pushl= "pushl %eax"
            call = "call is_true"
            cmpl = "cmpl $0, %eax"
            #Return if left is false
            je   = "jne else"+str(lftIsNotTrue)
            #If lft is true, move esi back into eax and return
            movl2 = "movl %esi, %eax"
            jmpE = "jmp ends"+str(final)
            else1= "else"+str(lftIsNotTrue)+":"
            self.quickInsert([movl,pushl,call,cmpl,je,movl2,jmpE,else1])
            #Test right
            rgt = self.compile(expr.nodes[1])
            if self.isArg(rgt):
                offset = self.isArg(rgt)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif rgt in self.varMap:
                offset = self.varMap[rgt] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif self.case(rgt, Register):
                movl = "movl %"+str(rgt.name)+", %eax"
                self.quickInsert([movl])

            end  = "ends"+str(final)+":"
            self.quickInsert([end])
            return Register("eax")

        #Not Returns raw value. Recursion will add tag
        #Not is done
        elif self.case(expr, Not):
            val = self.compile(expr.expr)
            if self.isArg(val):
                offset = self.isArg(val)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif val in self.varMap:
                offset = self.varMap[val] * 4
                movl_x86 = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl_x86])
            elif self.case(val,Register):
                movl_x86 = "movl %"+str(val.name)+", %eax"
                self.quickInsert([movl_x86])

            #Save val eax into esi
            movl = "movl %eax, %esi"
            pushl= "pushl %eax"
            call = "call is_true"
            #Determine if eax is true
            cmpl = "cmpl $0, %eax"
            valIsFalse = self.requestJumpNumber()
            final = self.requestShortNumber()
            jmp  = "je else"+str(valIsFalse)
            #val is true return 1
            movl1= "movl $0, %eax"
            jmpF = "jmp ends"+str(final)
            elseF= "else"+str(valIsFalse)+":"
            movl2= "movl $1, %eax"
            short= "ends"+str(final)+":"
            self.quickInsert([movl,pushl,call,cmpl,jmp,movl1,jmpF,elseF,movl2,short])
            return Register("eax")



        #Truth Identity helper node for P1.
        #NOTE DO NOT TAG this value ALMOST DONE. Don't use any more
        elif self.case(expr, TruthIdentity):
            val = self.compile(expr.expr)
            #If val is a variable name
            if self.isArg(val):
                offset = self.isArg(val)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif val in self.varMap:
                offset = self.varMap[val] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])

            #Get Tag, move eax to edi, so value is saved
            movl1 = "movl %eax, %esi"
            andl1 = "andl $0x3, %esi"
            #If esi is the tag
            cmpl1 = "cmpl $2, %esi"
            jmpNum = self.requestJumpNumber()
            short = self.requestShortNumber()
            jg1 = "jg else"+str(jmpNum)
            #Is primative.
            #Check if eax has a true value
            shr1 = "shr $2, %eax"
            cmpl2 = "cmpl $0, %eax"
            jmpNum2 = self.requestJumpNumber()
            jmp2 = "je else"+str(jmpNum2)
            #Value is true
            movl3 = "movl $1, %eax"
            jmpShort1 = "jmp ends"+str(short)
            else2 = "else"+str(jmpNum2)+":"
            movl4 = "movl $0, %eax"
            jmpShort = "jmp ends"+str(short)
            elseBig = "else"+str(jmpNum)+":"
            COMMENT = "//WORK HERE FOR BIG TRUENESS"
            shortEnd = "ends"+str(short)+":"

            self.quickInsert([movl1, andl1, cmpl1, jg1, shr1, cmpl2, jmp2, movl3, jmpShort1, else2, \
            movl4, jmpShort, elseBig, COMMENT, shortEnd])

            return Register("eax")

#------------------> end of P1 AST classes

#------------------> start of P2 AST classes

        elif self.case(expr, Function):
            self.inFunction = expr.name
            self.numOfFunctionStmts = len(expr.code.nodes)
            # If the function isn't already in the dictionary:
            if expr.name not in self.functions:
                self.functions[self.inFunction] = []
            # If the function is in the dictionary:
            else:
                pass

            name = ""
            if expr.name in self.lambdaTranslate:
                name = self.lambdaTranslate[expr.name]+":"
            else:
                name = expr.name + ":"

            pushl = "pushl %ebp"
            movl = "movl %esp, %ebp"
            self.quickInsert([name, pushl, movl])

            # Function body below.

            #print "expr.argnames: ", expr.argnames

            self.compile(expr.code)

            # Function body above.

            leave = "leave"
            ret = "ret"
            self.quickInsert([leave, ret])

        elif self.case(expr, Return):
            val = self.compile(expr.value)
            if self.isArg(val):
                offset = self.isArg(val)
                movl = "movl "+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif val in self.varMap:
                offset = self.varMap[val] * 4
                movl = "movl -"+str(offset)+"(%ebp), %eax"
                self.quickInsert([movl])
            elif self.case(val, Register):
                movl = "movl %"+val.name+", %eax"
                self.quickInsert([movl])


#------------------> end of P2 AST classes


        #Raise exception
        else:
            ColorPrint("Error: Uncaught node in compile: "+str(expr),GREEN)
            raise Exception()
