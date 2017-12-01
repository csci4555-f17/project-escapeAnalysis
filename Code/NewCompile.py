import sys
import compiler
from compiler.ast import *
from Flatten import flatten
from explicate import entry
from selectInstructions import compile
from heapify import heap
from Closure import close

from uniquify import uniquify
#import parser
WHITE = "\x1B[0m"
RED = "\x1B[31m"
MAGENTA = "\x1B[35m"
YELLOW = "\x1B[33m"
GREEN = "\x1B[32m"
CYAN = "\x1B[36m"
BLUE = "\x1B[0;34m"
PURPLE = "\x1B[0;35m"

def ColorPrint(expr,color):
    print color+str(expr)+WHITE

def main():
    # try:
    #     argv1_str = str(sys.argv[1])
    # except:
    #     print("Why you no give me argv 1 >:(")
    #     print("Example call to pyyc:")
    #     print("./pyyc tests/test1.py")
    #     sys.exit()

    #New flow ast -> flat(ast) -> heapify(ast) -> -> explicate(ast) -> compile(ast)
    #Get standard AST from file
    #ast = compiler.parseFile(argv1_str)
    name = sys.argv[1]
    ast = compiler.parseFile(name)
    flat = flatten(ast)
    print ast
    ColorPrint(flat, MAGENTA)
    #heap = heapify(flat)
    #compile(flat, "test.py")
    heapAST = heap(flat)
    ColorPrint(heapAST, CYAN)

    (closed, closureMap) = close(heapAST)
    ColorPrint(closed, YELLOW)

    (explicit, stackFrame) = entry(closed)
    #print stackFrame
    ColorPrint(explicit, GREEN)

    compileAST = compile(explicit, name, stackFrame, closureMap)





main()
