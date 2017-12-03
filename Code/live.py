class Live():
    def __init__(self,x86Statement):
        self.x86Statement = x86Statement
        self.liveSet = set()
        self.listOfLiveSet = []
            #parse takes x86 statement where statement is a list of tokens and continually builds the interference graph
    def parse(self,tokenList):
        #Do nothing to the set for call input. Move eax into liveset & G
        if tokenList[0] == 'call':
            #Add to graph and liveset eax
            self.liveSet = self.liveSet.union(set(['%eax']))
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
            #self.liveSet = self.liveSet.difference(set([tokenList[2]]))
            if tokenList[2] not in ['%esp','%ebp']:
                self.liveSet = self.liveSet.union(set([tokenList[2]]))
            if tokenList[1][0] != '$':
                self.liveSet = self.liveSet.union(set([tokenList[1]]))

            #        #Live variable on pushed on stack
        elif tokenList[0] == 'pushl' and tokenList[1] not in ['%ebp','%esp'] and tokenList[1][0] != '$':
            self.liveSet = self.liveSet.union(set([tokenList[1]]))
        elif tokenList[0] == 'negl':
            self.liveSet = self.liveSet.union(set(['%eax']))


        self.listOfLiveSet.append(self.liveSet)

    def driver(self):
        for i in range(len(self.x86Statement)-1,0,-1):
            #print self.x86Statement[i]
            self.parse(self.x86Statement[i])
        l = list()
        l.extend(self.listOfLiveSet)
        return l
