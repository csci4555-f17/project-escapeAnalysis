from compiler.ast import *
from os import remove
import compiler
import sys
import random
import re

class pyCompiler():
    def __init__(self,_ast):
        #ast
        self.ast = _ast
        #Internal counters to keep track of unique variables
        self.variableCounter = 0
        #Stack var counter assigns an integer to a variable in P0 as an ID to trace its location on the stack
        self.stackVarCounter = 1
        #List for appending flatten exprs
        self.flattenStatements = []
        #Dictionary to map P0 vars to their location on the stack. Mulitple by 4
        self.varMap = {}
        #List for appending x86 statements
        self.x86Statements = []
        #Character list
        self.letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        #tmp variable name
        self.tmp = ""


    def requestUniqueTmpName(self):
        token = ""
        for i in range(0,4):
            j = random.randint(0,25)
            token = token + str(self.letters[j])
        self.tmp = token

    #Helper function to shorthand isinstance
    def case(self,expr,Class):
        return isinstance(expr,Class)

    #Helper function returning true for irreducible nodes: variables, const, functions* (input for now)
    def isIrreducible(self,expr):
        return isinstance(expr,Const) or isinstance(expr,Name)

    #Helper function to add P0 to the varMap dictionary
    def map(self,name):
        #If a P0's var name is in the dictionary, ignore it. If not, add it to the dictionary with the current count value and incl
        if name not in self.varMap:
            self.varMap[name] = self.stackVarCounter
            self.stackVarCounter = self.stackVarCounter + 1

    def flattenAST(self,expr):
        #Base case
        #Const - return int or str
        if self.case(expr,Const):
            return expr.value
        #Name - return str
        elif self.case(expr, Name):
            return expr.name
        #CallFunc : input() - Special case so far - return Name(). Sequence Append
        elif self.case(expr, CallFunc):
            funcName = self.flattenAST(expr.node)
            argv = ""
            if len(expr.args) > 0:
                argv = expr.args[0]

            #Reduce if ness
            if argv != "":
                while(not self.isIrreducible(argv)):
                    argv = self.flattenAST(argv)
                argv = self.flattenAST(argv)

            #If argv was a return Name node or Const
            if argv != "" and self.case(argv,Name):
                argv = self.flattenAST(argv)

            #Create new tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            # Ross Change
            self.map(tmpVar)
            stmt = tmpVar+"="+str(funcName)+"("+str(argv)+")"
            #Append to flattenStatement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)


        #AssName - return str
        elif self.case(expr, AssName):
            return expr.name
        #Module
        elif self.case(expr, Module):
            #Recurse on node, ignore doc
            self.flattenAST(expr.node)
        #Stmt
        elif self.case(expr, Stmt):
            #Flatten each subAST in the Stml list of nodes
            for i in range(0,len(expr.nodes)):
                self.flattenAST(expr.nodes[i])
        #Printnl - appends statement
        elif self.case(expr, Printnl):
            #Ignore dest
            #Flatten each subAST in the Printnl list. Sequence Append
            prntStmt = "print "
            tokens = ""
            for i in range(0,len(expr.nodes)):
                subStmt = self.flattenAST(expr.nodes[i])
                if(self.case(subStmt, Name)):
                    subStmt = self.flattenAST(subStmt)
                if tokens == "":
                    tokens = subStmt
                else:
                    tokens = tokens+","+str(subStmt)
            #Append to flattenStatements
            self.flattenStatements.append(prntStmt+str(tokens))
        #Assign - Sequence Append
        elif self.case(expr, Assign) and self.isIrreducible(expr.expr):
            #value being assigned
            val = self.flattenAST(expr.expr)
            #Multiple assignment for multiple varnames
            for i in range(0,len(expr.nodes)):
                varName = self.flattenAST(expr.nodes[i])
                if self.case(val, Name):
                    val = self.flattenAST(val)
                #Add varName to dict
                self.map(varName)
                stmt = varName+"="+str(val)
                #Append to flattenStatements
                self.flattenStatements.append(stmt)

        #UnarySub - return Name()
        elif self.case(expr, UnarySub) and self.isIrreducible(expr.expr):
            val = self.flattenAST(expr.expr)
            if(self.case(val, Name)):
                val = self.flattenAST(val)
            val = "-"+str(val)
            #Create new tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            stmt = tmpVar+"="+str(val)
            #Add tmp name to dictionary
            self.map(tmpVar)
            #Append to flattenStatement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)




        #Add - return Name()
        elif self.case(expr, Add) and self.isIrreducible(expr.left) and self.isIrreducible(expr.right):
            #lft and rgt are int or var:str that are the operands of add
            lft = self.flattenAST(expr.left)
            rgt = self.flattenAST(expr.right)
            if(self.case(lft,Name)):
                lft = self.flattenAST(lft)
            if(self.case(rgt,Name)):
                rgt = self.flattenAST(rgt)
            #Create tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            stmt = tmpVar+"="+str(lft)+"+"+str(rgt)
            #Add tmp name to dictionary
            self.map(tmpVar)
            #Append statement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)


        #Sub - return Name()
        elif self.case(expr, Sub) and self.isIrreducible(expr.left) and self.isIrreducible(expr.right):
            #lft and rgt are int or var:str that are the operands of add
            lft = self.flattenAST(expr.left)
            rgt = self.flattenAST(expr.right)
            if(self.case(lft,Name)):
                lft = self.flattenAST(lft)
            if(self.case(rgt,Name)):
                rgt = self.flattenAST(rgt)
            #Create tmp variable
            tmpVar = self.tmp+str(self.variableCounter)
            self.variableCounter = self.variableCounter + 1
            stmt = tmpVar+"="+str(lft)+"-"+str(rgt)
            #Add tmp name to dictionary
            self.map(tmpVar)
            #Append statement
            self.flattenStatements.append(stmt)
            return Name(tmpVar)

        #Discard
        elif self.case(expr, Discard):
            rtn = self.flattenAST(expr.expr)
            if(self.case(rtn,Name)):
                rtn = self.flattenAST(rtn)
            self.flattenStatements.append(rtn)

        #Add induct - return AST node
        elif self.case(expr, Add):
            lft = expr.left
            rgt = expr.right
            if(not self.isIrreducible(lft)):
                lft = self.flattenAST(lft)
                token = Add((lft,rgt))
                return self.flattenAST(token)

            if(not self.isIrreducible(rgt)):
                rgt = self.flattenAST(rgt)
                token = Add((lft,rgt))
                return self.flattenAST(token)

        #Sub induct - return AST node
        elif self.case(expr, Sub):
            lft = expr.left
            rgt = expr.right
            if(not self.isIrreducible(lft)):
                lft = self.flattenAST(lft)
                token = Sub((lft,rgt))
                return self.flattenAST(token)

            if(not self.isIrreducible(rgt)):
                rgt = self.flattenAST(rgt)
                token = Sub((lft,rgt))
                return self.flattenAST(token)

        #Assign induct - return AST node
        elif self.case(expr, Assign):
            val = expr.expr
            if(not self.isIrreducible(val)):
                val = self.flattenAST(val)
                token = Assign(expr.nodes,val)
                return self.flattenAST(token)

        #UnarySub induct - return AST node
        elif self.case(expr, UnarySub):
            val = expr.expr
            if(not self.isIrreducible(val)):
                val = self.flattenAST(val)
                token = UnarySub(val)
                return self.flattenAST(token)


        #Raise exception
        else:
            raise Exception('Error: Uncaught node in flattenAST:'+str(expr))
    #---------------------------------------------------------------------------------------------
    #Wrapper
    def driver(self):
        #Product flatten P0
        self.requestUniqueTmpName()
        self.flattenAST(self.ast)
        f = open("flat.py","w")
        for i in range(0,len(self.flattenStatements)):
            f.write(str(self.flattenStatements[i])+"\n")
        f.close()

        #Parse flat.py
        #Uncomment line below when using the standard parser again
        ast = compiler.parseFile("flat.py")
        #ast = parser.driver("flat.py")
        #print ast
        self.compile(ast)
        #Output asm file
        fileOutName = str(sys.argv[1])[0:-3] + ".s"
        f = open(fileOutName,"w")
        #Write out setup and tear down
        f.write(".globl main\nmain:\n    pushl %ebp\n    movl %esp, %ebp\n")
        for i in range(0,len(self.x86Statements)):
            f.write("    "+self.x86Statements[i]+"\n")
        f.write("    movl $0, %eax\n    leave\n    ret\n")
        f.close()

        #Begin live analysis
        #open asm file
        asmFile = open(fileOutName,"r")
        x86Statement = asmFile.readlines() # :[x86 statements]
        asmFile.close()

        #Lex each line and turn it into sublists of tokens
        l = []
        for i in range(0,len(x86Statement)):
            regexStr = re.sub(',','',x86Statement[i])
            l.append(regexStr.split())

        #Create live object
        liveObj = Live(l)
        listOfLiveSet = liveObj.driver()

        #Reverse list of live sets so passing nodes into graph from top to bottom of asm file
        listOfLiveset = listOfLiveSet.reverse()
        #print listOfLiveSet
        #Begin graph / color analysis
        #for each item in listOfLiveSet:
        for x in listOfLiveSet:
            addNode(x)
        #convert dictOfNodes from strings to nodes
        convertStingsToNodes(dictOfNodes)
        #Color the nodes -- add registers to each node
        newStackSize = colorNodes(dictOfNodes) #Need to *4

        #Begin transformation
        self.transform(newStackSize,l)


        #for key in dictOfNodes.keys():
        #    print "Key: "+str(key.name)+" Reg: "+str(key.register)
        #Clean up
        remove("flat.py")

    #---------------------------------------------------------------------------------------------
    #Python0 -> x86. all statements are flatten
    def compile(self,expr):
        #Base Cases
        #Const
        if self.case(expr,Const):
            return expr.value
        #Name
        elif self.case(expr, Name):
            return expr.name
        #CallFunc - input for now...
        elif self.case(expr, CallFunc):
            print_input_x86 = "call input"
            #If input has args, print it out
            if len(expr.args) != 0:
                self.compile(Printnl([expr.args[0]],None))

            self.x86Statements.append(print_input_x86)
            #self.x86Statements.append(movl_x86)
            return Register("eax")

        #Module
        elif self.case(expr, Module):
            return self.compile(expr.node)

        #Stmt
        elif self.case(expr,Stmt):
            #Create stack space
            if not (self.stackVarCounter is 0):
                subl_x86 = "subl $" + str(4*(self.stackVarCounter-1)) + ", %esp"
                self.x86Statements.append(subl_x86)
            #For each sub AST, recurse on the sub AST nodes
            for i in range(0, len(expr.nodes)):
                self.compile(expr.nodes[i])
            #Collapse the stack when program ends
            if self.stackVarCounter != 0:
                addl_x86 = "addl $"+str(4*(self.stackVarCounter-1)) + ", %esp"
                self.x86Statements.append(addl_x86)

        #UnarySub
        elif self.case(expr, UnarySub):
            varName = self.compile(expr.expr)
            #Check if a variable is being negated or a const
            if varName in self.varMap:
                #Get location of variable on stack
                stackLocation = self.varMap[varName] << 2
                #Move variable value into eax
                movl_x86 = "movl -"+str(stackLocation)+"(%ebp), %eax"
                #Negate eax
                negl_x86 = "negl %eax"
                #append
                self.x86Statements.append(movl_x86)
                self.x86Statements.append(negl_x86)
                #return eax to signify a value is in the register
                return Register("eax")
            else:
                #A const is being negated. varName is the const value
                movl_x86 = "movl $"+str(varName)+", %eax"
                negl_x86 = "negl %eax"
                self.x86Statements.append(movl_x86)
                self.x86Statements.append(negl_x86)
                return Register("eax")

        #Assign
        elif self.case(expr, Assign):
            for i in range(0, len(expr.nodes)):
                varName = self.compile(expr.nodes[i])
                offset = self.varMap[varName] << 2
                #get assigning value
                val = self.compile(expr.expr)

                #If val is a variable
                if val in self.varMap:
                    #Assigning var to another variable
                    assignOffset = self.varMap[val] << 2
                    #Move assigning value into eax
                    movl_x86 = "movl -"+str(assignOffset)+"(%ebp), %eax"
                    #Move eax into varName
                    movl_x86_2 = "movl %eax, -"+str(offset)+"(%ebp)"
                    #append
                    self.x86Statements.append(movl_x86)
                    self.x86Statements.append(movl_x86_2)
                #A value was saved into a register. Retrieve that saved value and put into into varName offset
                elif self.case(val, Register):
                    #Move eax into offset
                    movl_x86 = "movl %"+str(val.name)+", -"+str(offset)+"(%ebp)"
                    self.x86Statements.append(movl_x86)
                else:
                    #Assign varName to a const
                    #Move the const into eax then into the offset
                    movl_x86 = "movl $"+str(val)+", %eax"
                    movl_x86_2 = "movl %eax, -"+str(offset)+"(%ebp)"
                    self.x86Statements.append(movl_x86)
                    self.x86Statements.append(movl_x86_2)

        #Add
        elif self.case(expr, Add):
            lft = self.compile(expr.left)

            #Note: Save the value of lft into ebx, so the recursive call on rgt that will most likely save to eax doesn't override lft.

            #Test the return type of lft
            if self.case(lft, Register):
                #Move the content of eax into ebx as tmp storage
                movl_x86 = "movl %"+lft.name+", %ebx"
                self.x86Statements.append(movl_x86)
            elif lft in self.varMap:
                #lft is a var
                #tmpOffset = offset - 4
                tmpOffset = self.varMap[lft] << 2
                movl_x86 = "movl -"+str(tmpOffset)+"(%ebp), %ebx"
                self.x86Statements.append(movl_x86)
            else:
                #Please be a const...
                movl_x86 = "movl $"+str(lft)+", %ebx"
                self.x86Statements.append(movl_x86)

            rgt = self.compile(expr.right)
            #Test content of rgt
            if self.case(rgt, Register):
                #Value was already set to eax, call addl
                addl_x86 = "addl %ebx, %eax"
                self.x86Statements.append(addl_x86)
                #Return register eax
                return Register("eax")
            #rgt is a var
            elif rgt in self.varMap:
                tmpOffset = self.varMap[rgt] << 2
                movl_x86 = "movl -"+str(tmpOffset)+"(%ebp), %eax"
                addl_x86 = "addl %ebx, %eax"
                self.x86Statements.append(movl_x86)
                self.x86Statements.append(addl_x86)
                return Register("eax")
            #rgt is a const...
            else:
                #Are you feeling it now Mr.Krabs?
                addl_x86 = "addl $"+str(rgt)+", %eax"
                movl_x86 = "movl %ebx, %eax"
                self.x86Statements.append(movl_x86)
                self.x86Statements.append(addl_x86)
                return Register("eax")

        #Sub
        elif self.case(expr, Sub):
            lft = self.compile(expr.left)

            #Note: Save the value of lft into ebx, so the recursive call on rgt that will most likely save to eax doesn't override lft.

            #Test the return type of lft
            if self.case(lft, Register):
                #Move the content of eax into ebx as tmp storage
                movl_x86 = "movl %"+lft.name+", %ebx"
                self.x86Statements.append(movl_x86)
            elif lft in self.varMap:
                #lft is a var
                tmpOffset = self.varMap[lft] << 2
                movl_x86 = "movl -"+str(tmpOffset)+"(%ebp), %ebx"
                self.x86Statements.append(movl_x86)
            else:
                #Please be a const...
                movl_x86 = "movl $"+str(lft)+", %ebx"
                self.x86Statements.append(movl_x86)

            rgt = self.compile(expr.right)
                #Test content of rgt
            if self.case(rgt, Register):
                #Value was already set to eax, call addl
                subl_x86 = "subl %ebx, %eax"
                self.x86Statements.append(subl_x86)
                #Return register eax
                return Register("eax")
            #rgt is a var
            elif rgt in self.varMap:
                tmpOffset = self.varMap[rgt] << 2
                movl_x86 = "movl -"+str(tmpOffset)+"(%ebp), %eax"
                subl_x86 = "subl %eax, %ebx"
                movl_x86_2 = "movl %ebx, %eax"
                self.x86Statements.append(movl_x86)
                self.x86Statements.append(subl_x86)
                self.x86Statements.append(movl_x86_2)
                return Register("eax")
                #rgt is a const...
            else:
                #Oh I'm feeling it
                subl_x86 = "subl $"+str(rgt)+", %eax"
                movl_x86 = "movl %ebx, %eax"
                self.x86Statements.append(movl_x86)
                self.x86Statements.append(subl_x86)
                return Register("eax")

        #AssName
        elif self.case(expr, AssName):
            return expr.name

        #Printnl - prints last thing pushed onto the stack
        elif self.case(expr, Printnl):
            for i in range(0, len(expr.nodes)):
                varName = self.compile(expr.nodes[i])
                #Check if a variable is being printed
                if varName in self.varMap:
                    #If so, find its position ID and calculate its offset
                    offset = self.varMap[varName] << 2
                    pushl_x86 = "pushl -"+str(offset)+"(%ebp)"
                    print_int_nl_x86 = "call print_int_nl"
                    #Append x86 statements
                    self.x86Statements.append(pushl_x86)
                    self.x86Statements.append(print_int_nl_x86)
                else:
                    #Probably printing a const
                    pushl_x86 = "pushl $"+str(varName)
                    print_int_nl_x86 = "call print_int_nl"
                    #Append x86 statements
                    self.x86Statements.append(pushl_x86)
                    self.x86Statements.append(print_int_nl_x86)
            return

        #Discard
        elif self.case(expr, Discard):
            self.compile(expr.expr)
        else:
            raise Exception('Error: Uncaught AST node in compile:'+str(expr))


def flattenAST(self,expr):
    #Base case
    #Const - return int or str
    if self.case(expr,Const):
        return expr.value
    #Name - return str
    elif self.case(expr, Name):
        return expr.name
    #CallFunc : input() - Special case so far - return Name(). Sequence Append
    elif self.case(expr, CallFunc):
        funcName = self.flattenAST(expr.node)
        argv = ""
        if len(expr.args) > 0:
            argv = expr.args[0]

        #Reduce if ness
        if argv != "":
            while(not self.isIrreducible(argv)):
                argv = self.flattenAST(argv)
            argv = self.flattenAST(argv)

        #If argv was a return Name node or Const
        if argv != "" and self.case(argv,Name):
            argv = self.flattenAST(argv)

        #Create new tmp variable
        tmpVar = self.tmp+str(self.variableCounter)
        self.variableCounter = self.variableCounter + 1
        # Ross Change
        self.map(tmpVar)
        stmt = tmpVar+"="+str(funcName)+"("+str(argv)+")"
        #Append to flattenStatement
        self.flattenStatements.append(stmt)
        return Name(tmpVar)


    #AssName - return str
    elif self.case(expr, AssName):
        return expr.name
    #Module
    elif self.case(expr, Module):
        #Recurse on node, ignore doc
        self.flattenAST(expr.node)
    #Stmt
    elif self.case(expr, Stmt):
        #Flatten each subAST in the Stml list of nodes
        for i in range(0,len(expr.nodes)):
            self.flattenAST(expr.nodes[i])
    #Printnl - appends statement
    elif self.case(expr, Printnl):
        #Ignore dest
        #Flatten each subAST in the Printnl list. Sequence Append
        prntStmt = "print "
        tokens = ""
        for i in range(0,len(expr.nodes)):
            subStmt = self.flattenAST(expr.nodes[i])
            if(self.case(subStmt, Name)):
                subStmt = self.flattenAST(subStmt)
            if tokens == "":
                tokens = subStmt
            else:
                tokens = tokens+","+str(subStmt)
        #Append to flattenStatements
        self.flattenStatements.append(prntStmt+str(tokens))
    #Assign - Sequence Append
    elif self.case(expr, Assign) and self.isIrreducible(expr.expr):
        #value being assigned
        val = self.flattenAST(expr.expr)
        #Multiple assignment for multiple varnames
        for i in range(0,len(expr.nodes)):
            varName = self.flattenAST(expr.nodes[i])
            if self.case(val, Name):
                val = self.flattenAST(val)
            #Add varName to dict
            self.map(varName)
            stmt = varName+"="+str(val)
            #Append to flattenStatements
            self.flattenStatements.append(stmt)

    #UnarySub - return Name()
    elif self.case(expr, UnarySub) and self.isIrreducible(expr.expr):
        val = self.flattenAST(expr.expr)
        if(self.case(val, Name)):
            val = self.flattenAST(val)
        val = "-"+str(val)
        #Create new tmp variable
        tmpVar = self.tmp+str(self.variableCounter)
        self.variableCounter = self.variableCounter + 1
        stmt = tmpVar+"="+str(val)
        #Add tmp name to dictionary
        self.map(tmpVar)
        #Append to flattenStatement
        self.flattenStatements.append(stmt)
        return Name(tmpVar)




    #Add - return Name()
    elif self.case(expr, Add) and self.isIrreducible(expr.left) and self.isIrreducible(expr.right):
        #lft and rgt are int or var:str that are the operands of add
        lft = self.flattenAST(expr.left)
        rgt = self.flattenAST(expr.right)
        if(self.case(lft,Name)):
            lft = self.flattenAST(lft)
        if(self.case(rgt,Name)):
            rgt = self.flattenAST(rgt)
        #Create tmp variable
        tmpVar = self.tmp+str(self.variableCounter)
        self.variableCounter = self.variableCounter + 1
        stmt = tmpVar+"="+str(lft)+"+"+str(rgt)
        #Add tmp name to dictionary
        self.map(tmpVar)
        #Append statement
        self.flattenStatements.append(stmt)
        return Name(tmpVar)


    #Sub - return Name()
    elif self.case(expr, Sub) and self.isIrreducible(expr.left) and self.isIrreducible(expr.right):
        #lft and rgt are int or var:str that are the operands of add
        lft = self.flattenAST(expr.left)
        rgt = self.flattenAST(expr.right)
        if(self.case(lft,Name)):
            lft = self.flattenAST(lft)
        if(self.case(rgt,Name)):
            rgt = self.flattenAST(rgt)
        #Create tmp variable
        tmpVar = self.tmp+str(self.variableCounter)
        self.variableCounter = self.variableCounter + 1
        stmt = tmpVar+"="+str(lft)+"-"+str(rgt)
        #Add tmp name to dictionary
        self.map(tmpVar)
        #Append statement
        self.flattenStatements.append(stmt)
        return Name(tmpVar)

    #Discard
    elif self.case(expr, Discard):
        rtn = self.flattenAST(expr.expr)
        if(self.case(rtn,Name)):
            rtn = self.flattenAST(rtn)
        self.flattenStatements.append(rtn)

    #Add induct - return AST node
    elif self.case(expr, Add):
        lft = expr.left
        rgt = expr.right
        if(not self.isIrreducible(lft)):
            lft = self.flattenAST(lft)
            token = Add((lft,rgt))
            return self.flattenAST(token)

        if(not self.isIrreducible(rgt)):
            rgt = self.flattenAST(rgt)
            token = Add((lft,rgt))
            return self.flattenAST(token)

    #Sub induct - return AST node
    elif self.case(expr, Sub):
        lft = expr.left
        rgt = expr.right
        if(not self.isIrreducible(lft)):
            lft = self.flattenAST(lft)
            token = Sub((lft,rgt))
            return self.flattenAST(token)

        if(not self.isIrreducible(rgt)):
            rgt = self.flattenAST(rgt)
            token = Sub((lft,rgt))
            return self.flattenAST(token)

    #Assign induct - return AST node
    elif self.case(expr, Assign):
        val = expr.expr
        if(not self.isIrreducible(val)):
            val = self.flattenAST(val)
            token = Assign(expr.nodes,val)
            return self.flattenAST(token)

    #UnarySub induct - return AST node
    elif self.case(expr, UnarySub):
        val = expr.expr
        if(not self.isIrreducible(val)):
            val = self.flattenAST(val)
            token = UnarySub(val)
            return self.flattenAST(token)


    #Raise exception
    else:
        raise Exception('Error: Uncaught node in flattenAST:'+str(expr))


token = pyCompiler("Module(None, Stmt([Printnl([Add((Const(1), Const(2)))], None)]))")
token.flattenAST(token.ast)
