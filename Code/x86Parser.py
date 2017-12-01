#Parser to taken in x86 and produces an interference graph
import sys
import re
import compiler

class Live():
    def __init__(self,x86Statement):
        self.x86Statement = x86Statement
        self.liveSet = set()
        self.listOfLiveSet = []

#Register names
#eax, ebx, ecx, edx, esi, edi, eip. Reservered esp, ebp
#Dictionary to map stack variables to letter variables

#parse takes x86 statement where statement is a list of tokens and continually builds the interference graph
    def parse(self,tokenList):
        #Do nothing to the set for call input. Move eax into liveset & G
        if tokenList[0] == 'call':
            #Add to graph and liveset eax
            return
        elif tokenList[0] == 'movl':
            #If moving register, move register into liveset & G
            if tokenList[1] in ['%eax','%ebx','%ecx','%edx','%esi','%edi']:
                #Add to live set the reader
                self.liveSet = self.liveSet.union(set([tokenList[1]]))
                #Add to graph the reader
                #addToGraph(tokenList[1])
                #Remove the writer if in the liveset
                self.liveSet = self.liveSet.difference(set([tokenList[2]]))
            #If moving stack variable, add it into liveset & G
            elif tokenList[1][0] == '-':
                self.liveSet = self.liveSet.union(set([tokenList[1]]))
                #Add to G
                #addToGraph(tokenList[1])
                #Remove writer from liveset
                self.liveSet = self.liveSet.difference(set([tokenList[2]]))
            #If moving a const, remove the writer
            elif tokenList[1][0] == '$':
                self.liveSet = self.liveSet.difference(set([tokenList[2]]))
        #Addl, subtract the writer then add both operands to the live set and G
        elif tokenList[0] == 'addl':
            #Add to the live set if not adding
            self.liveSet = self.liveSet.difference(set([tokenList[2]]))
            if tokenList[2] not in ['%esp','%ebp']:
                self.liveSet = self.liveSet.union(set([tokenList[2]]))
            if tokenList[1][0] != '$':
                self.liveSet = self.liveSet.union(set([tokenList[1]]))
#        #Live variable on pushed on stack
        elif tokenList[0] == 'pushl' and tokenList[1] not in ['%ebp','%esp']:
            self.liveSet = self.liveSet.union(set([tokenList[1]]))
        
        #print "Live: "+str(self.liveSet)
        self.listOfLiveSet.append(self.liveSet)
            
    def driver(self):
        for i in range(len(self.x86Statement)-1,0,-1):
            #print self.x86Statement[i]
            self.parse(self.x86Statement[i])
def main():
    try:
        sys.argv[1]
    except:
        print "x86 liveness checker needs flat.py"
        sys.exit()

    f = open(sys.argv[1],"r")
    x86Statement = f.readlines()
    f.close()

    #Reverse the list. Start at the 5th index from the end of the list of statements, skipping stack collapse, eax return 0, and ret
    l = []
    for i in range(0,len(x86Statement)):
        regexStr = re.sub(',','',x86Statement[i])
        l.append(regexStr.split())

    lojb = Live(l)
    lojb.driver()
    #Note: Give Ross the list of lives set in reverse direction (ready top to bottom)
    for i in range(len(lojb.listOfLiveSet)-1,0,-1):
            print lojb.listOfLiveSet[i]

main()
