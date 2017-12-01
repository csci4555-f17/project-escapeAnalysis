from pyCompiler import pyCompiler
from explicate import *
import sys
import compiler
from compiler.ast import *
from uniquify import *
#import parser
WHITE = "\x1B[0m"
RED = "\x1B[31m"
MAGENTA = "\x1B[35m"
YELLOW = "\x1B[33m"
GREEN = "\x1B[32m"
CYAN = "\x1B[36m"

def main():
    try:
        argv1_str = str(sys.argv[1])
    except:
        print("Why you no give me argv 1 >:(")
        print("Example call to pyyc:")
        print("./pyyc tests/test1.py")
        sys.exit()

    #Get standard AST from file
    ast = compiler.parseFile(argv1_str)
    print ast
    #DEBUG
    #print MAGENTA+"Default: "+str(ast)+WHITE

    uniquifiedAST = uniquify(ast)

    #Flatten AST
    token = pyCompiler(uniquifiedAST)
    flatAST = token.driver()

    #DEBUG
    #print GREEN+"Flatten: "+str(flatAST)+WHITE





main()
