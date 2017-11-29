x = [False,True]
xor = True if x[0] and (True if not x[1] else False) else True if x[1] and (True if not x[0] else False) else False
print xor
