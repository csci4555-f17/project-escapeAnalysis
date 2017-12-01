# Create a global dictionary of nodes.
dictOfNodes = {}
# Create a global register set.
availableRegisters = set({'esi', 'edi'})
allRegisters = set({'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi'})

# Node class. Each node has a name and a register.
class Node:
    def __init__(self, name, register):
        self.name = name
        self.register = register

# addNode function. Input is each set of the liveliness analysis. Creates graph
# from the liveliness analysis.
def addNode(setOfNodes):
    # Loop through each item in the input (liveliness analysis).
    for x in setOfNodes:
        # Nested loop. For each item in the set, loop through each
        # item in the set.
        for y in setOfNodes:
            # If the items are different (if the two loops are at different
            # locations)
            if not y == x:
                # If x is already a key:
                if x in dictOfNodes.keys():
                    # If y is not a value for the key x:
                    if y not in dictOfNodes[x]:
                        # Add a new value, y, for the key x
                        dictOfNodes[x].append(y)
                            # If x is not a key:
                else:
                    # Add a new key, x, with value y
                    dictOfNodes[x] = [y]

            else:
                if x not in dictOfNodes.keys():
                    #print x, should not be a key
                    dictOfNodes[x] = []

# This function converts the strings in the dictOfNodes dictionary
# to nodes.
def convertStingsToNodes(dictOfNodes):
    # This for loop deletes duplicate empty lists: [] from the values if
    # the value list is not empty otherwise.
    for key in dictOfNodes.keys():
        for value in dictOfNodes[key]:
            if len(value) is 2:
                dictOfNodes[key][0] = value[1]
    # Loop through the keys in dictOfNodes.
    for x in dictOfNodes.keys():
        # Create an empty list at each new key.
        list1 = []
        # Create a node, y, with name x and register None
        y = Node(x, None)
        # Replace the key x with the key y, which is a node, keeping original
        # values.
        dictOfNodes[y] = dictOfNodes.pop(x)

        # Loop through each value for the current key.
        for g in dictOfNodes[y]:
            # Create a node, z, with name g and register None.
            z = Node(g, None)
            # Adds the node z to the list
            list1.append(z)
            # Replace the values of the key y with the list we created above.
        dictOfNodes[y] = list1

# Function that, given a node n with register r, goes through every key and
# value in dictOfNodes and adds the the register r to all nodes with name
# n.name.
def addRegister(node):
    # For each key in dictOfNodes
    for key in dictOfNodes.keys():
        # If the name of the key is equal to the name of the node passed in:
        if key.name is node.name:
            # Add nodes register to key.register.
            key.register = node.register
        # For each value for the current key
        for value in dictOfNodes[key]:
            # If the name of the value is equal to the name of the node
            # passed in:
            if value.name is node.name:
                # Add nodes register to value.register.
                value.register = node.register

# Function that takes a graph (dictionary) of nodes, and "colors" it - using
# registers.
def colorNodes(graph):
    # Set W to all of the keys of the graph.
    W = graph.keys()

    # Create a counter variable just in case there are more variables than
    # registers.
    stackCounter = 0

    # While W is not empty:
    while W:
        # Create a copy of the registers set.
        tmpRegisters = set(availableRegisters)

        # Pick a node, u
        u = W[0]

        # For each of the values for the key u
        for v in dictOfNodes[u]:
            # Below line is for testing purposes.
            # print "key.name", u.name, "| value.name", v.name, "| value.register:", v.register, "in tmpRegisters", tmpRegisters, v.register in tmpRegisters
                    # If the register for the value is in tmpRegisters
            if v.register in tmpRegisters:
                # If there are still available registers:
                if len(tmpRegisters) > 0:
                    # Remove it from tmpRegisters
                    tmpRegisters.remove(v.register)
        # Out of the for loop. If there are available registers:
        #print u.name, len(tmpRegisters)
        if len(tmpRegisters) is not 0:
            # if the key's name is not a register:
            if str(u.name[1:]) not in allRegisters:
                #print u.name[1:]
                # Set the key's register to the next available register.
                u.register = next(iter(tmpRegisters))
                # Remove that register from the available register list.
                tmpRegisters.remove(next(iter(tmpRegisters)))
                # Call the addRegister function for the key with the newly
                # added register.
                addRegister(u)
            # If the key's name is a register:
            else:
                # Set the key's register to the key's name.
                u.register = u.name[1:]
                # Remove that register from the available register list.
                tmpRegisters.remove(next(iter(tmpRegisters)))
                # Call the addRegister function for the key with the newly
                # added register.
                addRegister(u)
        # If there are no available registers:
        else:
            if str(u.name[1:]) in allRegisters:
                # Set the key's register to the key's name.
                u.register = u.name[1:]
                # Call the addRegister function for the key with the newly
                # added register.
                addRegister(u)
            else:
                stackCounter = stackCounter + 1
                # Set the key's register to a stack location.
                u.register = "-"+str(stackCounter*4)+"(%ebp)"
                addRegister(u)
        # Pop a key off of W.
        W.pop(0)
    return stackCounter
