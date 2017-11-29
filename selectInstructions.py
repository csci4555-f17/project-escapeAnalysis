import compiler
from compiler.ast import *
from explicate import *

# Global variables.
x86InstructionList = {"main":[]}
stackFrame = {}
closureMap = {}


#Jmp and Short
jmp = -1
short = -1

currentStackFrame = "main"
varMap = {"main":{}}

#Map for function arguments to their stack location
argMap = {"main":{}}

#Map functions to its free vars
freeMap = {"main":[]}

#Request a stack location for a given scope
def requestStackLocationFor(varName):
    if currentStackFrame in varMap:
        if varName in varMap[currentStackFrame]:
            return varMap[currentStackFrame][varName]
        else:
            varMap[currentStackFrame][varName] = -1*len(varMap[currentStackFrame])-1
            return varMap[currentStackFrame][varName]
    else:
        varMap[currentStackFrame] = {varName:-1}
        return -1
#Return positive or negative offset for a variable
def getStackLocationFor(varName):
    if varName in varMap[currentStackFrame]:
        return varMap[currentStackFrame][varName]
    else:
        return 0

#Helper function giving unique numbers for jump statements
def requestJumpNumber():
    global jmp
    jmp += 1
    return jmp

#Helpfer function giving unique numbers for jump statements in short-circuit cases
def requestShortNumber():
    global short
    short += 1
    return short

def case(expr, Class):
    return isinstance(expr, Class)

class Register():
    def __init__(self, regName):
        self.name = regName
    def __repr__(self):
        return 'Register(%s)' % self.name

def quickInsert(stmt):
    for i in range(0,len(stmt)):
        x86InstructionList[currentStackFrame].append(stmt[i])

def IntoReg(register, val):
    if case(val, Register):
        quickInsert(["movl %"+str(val.name)+", %"+register])
    elif getStackLocationFor(val) != 0:
        quickInsert(["movl "+str(getStackLocationFor(val)*4)+"(%ebp), %"+register])
    elif val in argMap[currentStackFrame]:
        quickInsert(["movl "+str(argMap[currentStackFrame][val] * 4)+"(%ebp), %"+register])
    else:
        print "Something went wrong in compile. This variable does not have a location:"+str(val)

def compile(ast, filename, _stackFrame, _closureMap):
    global stackFrame
    global closureMap
    stackFrame = _stackFrame
    closureMap = _closureMap

    quickInsert([".globl main\nmain:\npushl %ebp\nmovl %esp, %ebp"])
    quickInsert(["subl $"+str(4*stackFrame["main"])+", %esp"])
    selectInstructions(ast)
    quickInsert(["addl $"+str(4*stackFrame["main"])+", %esp"])
    quickInsert(["movl $0, %eax\nleave\nret\n"])
    fileOutName = str(filename)[0:-3] + ".s"

    f = open(fileOutName, "w")
    for frame in x86InstructionList:
        for line in x86InstructionList[frame]:
            f.write(line+"\n")
    f.close()


def selectInstructions(expr):
    global currentStackFrame
    # ------------------ Start of P0 nodes ------------------
    if case(expr, Const):
        return expr.value
    #Name
    elif case(expr, Name):
        return expr.name
    #Bool
    elif case(expr, Bool):
        return expr.expr
    # Module
    elif case(expr, Module):
        return selectInstructions(expr.node)
    #Stmt
    elif case(expr, Stmt):
        map(lambda x: selectInstructions(x), expr.nodes)
    #Printnl
    elif case(expr, Printnl):
        val = selectInstructions(expr.nodes[0])
        IntoReg("eax", val)
        quickInsert(["pushl %eax","call print_any","addl $4, %esp"])
    #InjectFrom
    elif case(expr, InjectFrom):
        val = selectInstructions(expr.arg)
        #Make Tag. Set TAG to be 0 by default as integer const
        TAG = 0x0
        if expr.typ == 'BOOL':
            TAG = 0x1
        elif expr.typ == 'FLOAT':
            TAG = 0x2
        elif expr.typ == 'BIG':
            TAG = 0x3
        #If val not register
        if not case(val, Register):
            movl = ""
            if val == 'True':
                movl = "movl $1, %eax"
            elif val == 'False':
                movl = "movl $0, %eax"
            else:
                movl = "movl $"+str(val)+", %eax"
            quickInsert([movl])
        #Inject correct tag
        if expr.typ in ['INT', 'BOOL', 'FLOAT']:
            shl_x86 = "shl $2, %eax"
            or_x86 = "or $"+str(TAG)+", %eax"
            quickInsert([shl_x86, or_x86])
        elif expr.typ == 'BIG':
            or_x86 = "or $"+str(TAG)+", %eax"
            quickInsert([or_x86])

        #return tagged value in eax
        return Register("eax")
    #Assign
    elif case(expr, Assign):
        #If lvalue is a location inside a list, grab the list pointer, step on the index,
        #and assign the stepped rvalue to it.

        if case(expr.nodes[0], Subscript):
            #Get list
            subscript = expr.nodes[0]
            listName = selectInstructions(subscript.expr)
            IntoReg("edx", listName)

            #Get index
            index = selectInstructions(subscript.subs[0])
            IntoReg("ebx", index)
            #Step on rvalue
            val = selectInstructions(expr.expr)
            IntoReg("eax", val)
            #Future note. This may conflict if calls mutate edx
            quickInsert(["pushl %eax", "pushl %ebx", "pushl %edx", "call set_subscript", "addl $12, %esp"])
            return
        offset = requestStackLocationFor(expr.nodes[0].name)
        val = selectInstructions(expr.expr)
        IntoReg("eax", val)
        quickInsert(["movl %eax, "+str(offset*4)+"(%ebp)"])
        return
    #AssName
    elif case(expr, AssName):
        return expr.name
    #UnarySub
    elif case(expr, UnarySub):
        val = selectInstructions(expr.expr)
        IntoReg("eax", val)
        quickInsert(["shr $2, %eax","negl %eax"])
        return Register("eax")
    #Add
    elif case(expr, Add):
        lft = selectInstructions(expr.left)
        IntoReg("ebx", lft)
        quickInsert(["shr $2, %ebx"])
        rgt = selectInstructions(expr.right)
        IntoReg("eax", rgt)
        quickInsert(["shr $2, %eax", "addl %ebx, %eax"])
        return Register("eax")
    #Discard
    elif case(expr, Discard):
        selectInstructions(expr.expr)

    # ------------------ End of P0 nodes ------------------
    # ------------------ Start of P1 nodes ------------------
    #IfExp
    elif case(expr, IfExp):
        test = selectInstructions(expr.test)
        IntoReg("eax", test)
        # #Save value from eax to esi and then call is_true
        quickInsert(["movl %eax, %esi", "pushl %eax", "call is_true", "addl $4, %esp", \
        "cmpl $0, %eax"])
        testIsFalse = requestJumpNumber()
        final = requestShortNumber()
        quickInsert(["je else"+str(testIsFalse)])

        # Then
        then = selectInstructions(expr.then)
        IntoReg("eax", then)
        quickInsert(["jmp ends"+str(final)])

        # Else
        quickInsert(["else"+str(testIsFalse)+":"])
        else_output = selectInstructions(expr.else_)
        IntoReg("eax", else_output)
        quickInsert(["ends"+str(final)+":"])
        return Register("eax")

    #Or
    elif case(expr, Or):
        lft = selectInstructions(expr.nodes[0])
        IntoReg("eax", lft)
        final = requestShortNumber()
        lftIsNotTrue = requestJumpNumber()
        quickInsert(["movl %eax, %esi", "pushl %eax", "call is_true", "addl $4, %esp", \
        "cmpl $0, %eax", "je else"+str(lftIsNotTrue), "movl %esi, %eax", "jmp ends"+str(final), \
        "else"+str(lftIsNotTrue)+":"])
        # Rgt
        rgt = selectInstructions(expr.nodes[1])
        IntoReg("eax", rgt)
        quickInsert(["ends"+str(final)+":"])

        return Register("eax")

    #And
    elif case(expr, And):
        lft = selectInstructions(expr.nodes[0])
        IntoReg("eax", lft)
        final = requestShortNumber()
        lftIsNotTrue = requestJumpNumber()

        quickInsert(["movl %eax, %esi", "pushl %eax", "call is_true", "addl $4, %esp",\
        "cmpl $0, %eax", "jne else"+str(lftIsNotTrue), "movl %esi, %eax", "jmp ends"+str(final),
        "else"+str(lftIsNotTrue)+":"])
        #rgt
        rgt = selectInstructions(expr.nodes[1])
        IntoReg("eax", rgt)
        quickInsert(["ends"+str(final)+":"])

        return Register("eax")

    #Compare
    elif case(expr, Compare):
        lft = selectInstructions(expr.expr)
        operator = expr.ops[0][0]
        if operator in ['==', '!=']:
            IntoReg("eax", lft)
            final = requestShortNumber()
            lftIsBig = requestJumpNumber()
            quickInsert(["movl %eax, %esi", "andl $0x3, %esi", "cmpl $2, %esi", \
            "jg else"+str(lftIsBig), "movl %eax, %esi"])

            #rgt
            rgt = selectInstructions(expr.ops[0][1])
            IntoReg("eax", rgt)
            quickInsert(["movl %eax, %edi", "shr $2, %esi", "shr $2, %edi", \
            "cmpl %esi, %edi"])
            smallAreNotEqual = requestJumpNumber()
            switch = "jne" if operator == '==' else "je"
            quickInsert([switch+" else"+str(smallAreNotEqual)])
            #Both are equal return true
            quickInsert(["movl $1, %eax", "jmp ends"+str(final), "else"+str(smallAreNotEqual)+":",\
            "movl $0, %eax", "jmp ends"+str(final), "else"+str(lftIsBig)+":"])

            #Movl lft back into esi
            quickInsert(["movl %eax, %esi"])
            rgt = selectInstructions(expr.ops[0][1])
            IntoReg("eax", rgt)
            quickInsert(["movl %eax, %edi", "andl $0xfffffffc, %esi", "pushl %esi", \
            "andl $0xfffffffc, %edi", "pushl %edi", "call equal", "addl $8, %esp"])
            #1 or 0 is in eax. jmp to end
            if operator == '!=':
                quickInsert(["xor $0x1, %eax"])
            quickInsert(["ends"+str(final)+":"])
        elif operator == 'is':
            lft = selectInstructions(expr.expr)
            operator = expr.ops[0][0]
            IntoReg("eax", lft)
            final = requestShortNumber()
            lftIsBig = requestJumpNumber()
            quickInsert(["movl %eax, %esi", "andl $0x3, %esi", "cmpl $2, %esi", \
            "jg else"+str(lftIsBig), "movl %eax, %esi"])
            #rgt
            rgt = selectInstructions(expr.ops[0][1])
            IntoReg("eax", rgt)
            quickInsert(["movl %eax, %edi", "shr $2, %esi", "shr $2, %edi", "cmpl %esi, %edi",])
            smallAreNotEqual = requestJumpNumber()
            switch = "jne" if operator == 'is' else 'je'
            quickInsert([switch+" else"+str(smallAreNotEqual)])
            #Both are equal return true value
            quickInsert(["movl $1, %eax", "jmp ends"+str(final), "else"+str(smallAreNotEqual)+":",\
            "movl $0, %eax", "jmp ends"+str(final), "else"+str(lftIsBig)+":", "movl %eax, %esi"])

            rgt = selectInstructions(expr.ops[0][1])
            IntoReg("eax", rgt)
            quickInsert(["movl %eax, %edi", "cmpl %esi, %edi"])
            pointerNotEqual = requestJumpNumber()
            quickInsert(["jne else"+str(pointerNotEqual), "movl $1, %eax", "jmp ends"+str(final), \
            "else"+str(pointerNotEqual)+":", "movl $0, %eax", "ends"+str(final)])

        return Register("eax")

    #GetTag
    elif case(expr, GetTag):
        arg = selectInstructions(expr.arg)
        IntoReg("eax", arg)
        quickInsert(["andl $3, %eax", "shl $2, %eax"])
        return Register("eax")

    #AddList
    elif case(expr, AddList):
        lft = selectInstructions(expr.left)
        IntoReg("eax", lft)
        # #move lft operand to ebx and remove its tag
        quickInsert(["andl $0xfffffffc, %eax", "movl %eax, %ebx"])
        #rgt
        rgt = selectInstructions(expr.right)
        IntoReg("eax", rgt)
        quickInsert(["andl $0xfffffffc, %eax", "pushl %eax", "pushl %ebx", \
        "call add", "addl $8, %esp", "or $0x3, %eax"])

        return Register("eax")

    #Not
    elif case(expr, Not):
        val = selectInstructions(expr.expr)
        IntoReg("eax", val)
        quickInsert(["movl %eax, %esi", "pushl %eax", "call is_true", "addl $4, %esp",\
        "cmpl $0, %eax"])
        valIsFalse = requestJumpNumber()
        final = requestShortNumber()
        quickInsert(["je else"+str(valIsFalse), "movl $0, %eax", "jmp ends"+str(final),\
         "else"+str(valIsFalse)+":", "movl $1, %eax", "ends"+str(final)+":"])

        return Register("eax")

    #List
    elif case(expr, List):
        # Make room for three more variables on the stack.
        quickInsert(["subl $12, %esp"])
        lengthOfList = len(expr.nodes)
        #Create a list of size length of list
        quickInsert(["movl $"+str(lengthOfList)+", %eax", "shl $2, %eax", "pushl %eax", \
        "call create_list", "addl $4, %esp", "or $3, %eax"])

        localStackFrameSize = len(varMap[currentStackFrame])+3
        quickInsert(["movl %eax, -"+str(4*localStackFrameSize)+"(%ebp)"])

        #Get value of each element and puts in the right index
        for index in range(0, lengthOfList):
            #Create an index and tag it
            quickInsert(["movl $"+str(index)+", %eax", "shl $2, %eax", \
            "movl %eax, -"+str(4*(localStackFrameSize+1))+"(%ebp)"])

            #Step on element
            val = selectInstructions(expr.nodes[index])
            IntoReg("eax", val)
            quickInsert(["movl %eax, -"+str(4*(localStackFrameSize+2))+"(%ebp)"])

            #Push onto the stack in reverse order.
            quickInsert(["pushl -"+str(4*(localStackFrameSize+2))+"(%ebp)", "pushl -"\
            +str(4*(localStackFrameSize+1))+"(%ebp)", "pushl -"+str(4*localStackFrameSize)+"(%ebp)",\
            "call set_subscript", "addl $12, %esp"])

        quickInsert(["movl -"+str(4*localStackFrameSize)+"(%ebp), %eax", "addl $12, %esp"])

        return Register("eax")

    #Dict
    elif case(expr, Dict):
        numberOfItems = (2 * len(expr.items))
        localStackFrameSize = len(varMap[currentStackFrame])+3
        quickInsert(["subl $12, %esp", "call create_dict", "pushl %eax", "addl $4, %esp", \
        "or $3, %eax", "movl %eax, -"+str(4*localStackFrameSize)+"(%ebp)"])

        #For each key:value pair
        for index in range(0, len(expr.items)):
            #key
            key = selectInstructions(expr.items[index][0])
            IntoReg("eax", key)
            quickInsert(["movl %eax, -"+str(4*(localStackFrameSize+1))+"(%ebp)"])

            #val
            val = selectInstructions(expr.items[index][1])
            IntoReg("eax", val)
            quickInsert(["movl %eax, -"+str(4*(localStackFrameSize+2))+"(%ebp)"])

            quickInsert(["pushl -"+str(4*(localStackFrameSize+2))+"(%ebp)", \
            "pushl -"+str(4*(localStackFrameSize+1))+"(%ebp)", "pushl -"+str(4*(localStackFrameSize))+"(%ebp)",\
            "call set_subscript", "addl $12, %esp"])

        #Move dictionary back into eax
        quickInsert(["movl -"+str(4*localStackFrameSize)+"(%ebp), %eax", "addl $12, %esp"])

        return Register("eax")

    #Subscript
    elif case(expr, Subscript):
        val = selectInstructions(expr.subs[0])
        IntoReg("eax", val)
        quickInsert(["pushl %eax"])

        #Pointer to list
        var = selectInstructions(expr.expr)
        IntoReg("eax", var)
        quickInsert(["pushl %eax", "call get_subscript", "addl $8, %esp"])

        return Register("eax")
    # ------------------ End of P1 nodes ------------------
    # ------------------ Start of P2 nodes ------------------
    #FunctionLift
    elif case(expr, FunctionLift):
        tmp = currentStackFrame
        #Change stackframe name to be of the new function
        functionName = expr.expr.nodes[0].name
        currentStackFrame = functionName
        if functionName not in x86InstructionList:
            x86InstructionList[functionName] = []
        if functionName not in varMap:
            varMap[functionName] = {}

        quickInsert([functionName+":", "pushl %ebp", "movl %esp, %ebp",\
        "subl $"+str(4*stackFrame[functionName])+", %esp"])

        selectInstructions(expr.expr.expr)

        quickInsert(["addl $"+str(4*stackFrame[functionName])+", %esp"])
        quickInsert(["leave\nret\n"])

        currentStackFrame = tmp

    #Lambda Note: eax must have the return value
    elif case(expr, Lambda):
        #set up argument displacement
        if currentStackFrame not in argMap:
            argMap[currentStackFrame] = {}
            for i in range(0, len(expr.argnames)):
                argMap[currentStackFrame][expr.argnames[i]] = i+2
        selectInstructions(expr.code)
        return Register("eax")
    #CreateClosure
    elif case(expr, CreateClosure):
        fvs = expr.freeVars
        #Insurance
        freedList = map(lambda x: x.name, fvs)
        freeMap[expr.function] = freedList

        val = selectInstructions(List(fvs))
        IntoReg("eax", val)
        quickInsert(["pushl %eax","pushl $"+expr.function, \
        "call create_closure", "addl $8, %esp"])

        return Register("eax")

    #CallFunc
    elif case(expr, CallFunc):
        #Special case
        if expr.node.function.name == 'input':
            quickInsert(["call input", "shl $2, %eax"])
            return Register("eax")

        #selectInstructions(expr.node)
        #Reverse argument list
        expr.args.reverse()
        count = 0
        for i in range(0, len(expr.args)):
            elem = selectInstructions(expr.args[i])
            IntoReg("eax", elem)
            quickInsert(["pushl %eax"])
            count += 1


        fname = selectInstructions(expr.node)
        IntoReg("eax", fname)
        quickInsert(["call *%eax", "addl $"+str(4*count)+", %esp"])
        return Register("eax")
    #GetFunPtr
    elif case(expr, GetFunPtr):
        fname = selectInstructions(expr.function)
        IntoReg("eax", fname)
        quickInsert(["pushl %eax", "call get_fun_ptr", "addl $4, %esp"])
        return Register("eax")
    #GetFreeVar
    elif case(expr, GetFreeVar):
        fname = selectInstructions(expr.freeVars)
        IntoReg("eax", fname)
        quickInsert(["pushl %eax", "call get_free_vars", "addl $4, %esp"])
        return Register("eax")
    #Return
    elif case(expr, Return):
        val = selectInstructions(expr.value)
        IntoReg("eax", val)

        return Register("eax")
    # ------------------ End of P2 nodes ------------------
    # ------------------ End of P3 nodes ------------------
    #If
    elif case(expr, If):
        test = selectInstructions(expr.tests[0][0])
        IntoReg("eax", test)
        # #Save value from eax to esi and then call is_true
        quickInsert(["movl %eax, %esi", "pushl %eax", "call is_true", "addl $4, %esp", \
        "cmpl $0, %eax"])
        testIsFalse = requestJumpNumber()
        final = requestShortNumber()
        quickInsert(["je else"+str(testIsFalse)])

        # Then
        then = selectInstructions(expr.tests[0][1])
        IntoReg("eax", then)
        quickInsert(["jmp ends"+str(final)])

        # Else
        quickInsert(["else"+str(testIsFalse)+":"])
        else_output = selectInstructions(expr.else_)
        IntoReg("eax", else_output)
        quickInsert(["ends"+str(final)+":"])
        return Register("eax")
    else:
        #pass
        raise Exception("Compile recieved an unknown ast node: "+str(expr))
