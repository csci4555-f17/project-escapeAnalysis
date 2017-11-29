import compiler
from compiler.ast import *

def free_vars(n, bounded):
    if isinstance(n, Const):
        return (set([]), bounded)

    elif isinstance(n, Name) and (n.name == "True" or n.name == "False"):
        return (set([]), bounded)

    elif isinstance(n, Name):
        return (set([n.name]), bounded)

    elif isinstance(n, Add):
        return (free_vars(n.left, bounded)[0] | free_vars(n.right, bounded)[0], \
        bounded)

    elif isinstance(n, CallFunc):
        fv_args = [free_vars(e, bounded)[0] for e in n.args]
        free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
        return (free_vars(n.node, bounded)[0] | free_in_args, bounded)

    elif isinstance(n, Lambda):
        return (free_vars(n.code, bounded)[0] - set(n.argnames), bounded)

    elif isinstance(n, Module):
        val = free_vars(n.node, bounded)
        return (val[0], val[1] | bounded)

    elif isinstance(n, Stmt):
        ast = []
        bound = []
        for s in n.nodes:
            val = free_vars(s, bounded)
            ast.append(val[0])
            bound.append(val[1])
        free_in_args = reduce(lambda a, b: a | b, ast, set([]))
        bound_in_args = reduce(lambda a, b: a | b, bound, set([]))
        return (free_in_args, bound_in_args)

    elif isinstance(n, Printnl):
        fv_args = [free_vars(e, bounded)[0] for e in n.nodes]
        free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
        return (free_in_args, bounded)

    elif isinstance(n, Assign):
        left = free_vars(n.nodes[0], bounded)[1]
        right = free_vars(n.expr, bounded)[0]
        return (right, left)

    elif isinstance(n, AssName):
        return (set([]), bounded | set([n.name]))

    elif isinstance(n, Discard):
        val = free_vars(n.expr, bounded)
        return (val[0], val[1] | bounded)

    elif isinstance(n, UnarySub):
        val = free_vars(n.expr, bounded)
        return (val[0], val[1] | bounded)

    elif isinstance(n, Compare):
        fv_args = [free_vars(e[1], bounded)[0] for e in n.ops]
        free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
        return (free_vars(n.expr, bounded)[0] | free_in_args, bounded)

    elif isinstance(n, Function):
        code = free_vars(n.code, bounded)
        setify = map(lambda x:set([x]), n.argnames)
        reduction = reduce(lambda a,b: a | b, setify) if len(setify) > 0 else set([])
        return (code[0] - code[1] - reduction - set([n.name]), bounded | code[1] | reduction | set([n.name]))

    elif isinstance(n, Return):
        val = free_vars(n.value, bounded)
        return (val[0], val[1] | bounded)

    elif isinstance(n, Or) or isinstance(n, And) or isinstance(n, List):
        ast = []
        bound = []
        for n in n.nodes:
            val = free_vars(n, bounded)
            ast.append(val[0])
            bound.append(val[1])
        free_in_args = reduce(lambda a, b: a | b, ast, set([]))
        bound_in_args = reduce(lambda a, b: a | b, bound, set([]))
        return (free_in_args, bound_in_args | bounded)

    elif isinstance(n, Not):
        val = free_vars(n.expr, bounded)
        return (val[0], val[1] | bounded)

    elif isinstance(n, Dict):
        ast = []
        bound = []
        for n in n.items:
            val = free_vars(n[0], bounded)
            val2 = free_vars(n[1], bounded)
            ast.append(val[0])
            bound.append(val[1])
            ast.append(val2[0])
            bound.append(val2[1])
        free_in_args = reduce(lambda a, b: a | b, ast, set([]))
        bound_in_args = reduce(lambda a, b: a | b, bound, set([]))
        return (free_in_args, bound_in_args | bounded)

    elif isinstance(n, Subscript):
        name = free_vars(n.expr, bounded)
        subs = free_vars(n.subs[0], bounded)
        return (name[0] | subs[0], name[1] | subs[1] | bounded)

    elif isinstance(n, IfExp):
        if_ = free_vars(n.test, bounded)
        then= free_vars(n.then, bounded)
        else_ = free_vars(n.else_, bounded)
        return (if_[0] | then[0] | else_[0], if_[1] | then[1] | else_[1] | bounded)
        
    else:
        print "free_var experienced an unknown node called: "+str(n)
        return None
