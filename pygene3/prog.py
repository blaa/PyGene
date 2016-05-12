"""
Implements genetic programming organisms.
"""

from random import random, randrange, choice
from math import sqrt

from .organism import BaseOrganism

from .xmlio import PGXmlMixin


class TypeDoesNotExist(Exception):
    """Parameters does not allow to construct a tree."""
    pass

class BaseNode:
    """
    Base class for genetic programming nodes
    """
    def calc(self, **vars):
        """
        evaluates this node, plugging vars into
        the nodes
        """
        raise Exception("method 'calc' not implemented")

class FuncNode(BaseNode):
    """
    Node which holds a function and its argument nodes
    """
    def __init__(self, org, depth, name=None, children=None, type_=None):
        """
        creates this func node
        """
        self.org = org

        if org.type and type_:
            options = [x for x in org.funcsList if x[-1][0] == type_]
        else:
            options = org.funcsList

        if not options:
            raise TypeDoesNotExist

        if name == None:
            # randomly choose a func
            name, func, nargs, typed = choice(options)
        else:
            # lookup func in organism
            func, nargs, typed = org.funcsDict[name]

        # and fill in the args, from given, or randomly
        if not children:
            if typed:
                children = [org.genNode(depth+1, typed[1+i]) for i in range(nargs)]
            else:
                children = [org.genNode(depth+1) for i in range(nargs)]

        self.type = org.type and typed[0] or None
        self.argtype = org.type and typed[1:] or []
        self.name = name
        self.func = func
        self.nargs = nargs
        self.children = children

        # Additional type check
        self.check_types()

    def calc_nodes(self):
        "Return number of nodes in equation"
        cnt = [0]
        def dfs(node):
            cnt[0] += 1
            if isinstance(node, FuncNode):
                for child in node.children:
                    dfs(child)

        dfs(self)
        return cnt[0]

    def calc(self, **vars):
        """
        evaluates this node, plugging vars into
        the nodes
        """
        args = []
        for child in self.children:
            #print "FuncNode.calc: child %s dump:" % (
            #    child.__class__,
            #    )
            #child.dump()
            arg = child.calc(**vars)
            #print "child returned %s" % repr(arg)
            args.append(arg)

        #print "FuncNode.calc: name=%s func=%s vars=%s args=%s" % (
        #    self.name,
        #    self.func,
        #    vars,
        #    args
        #    )
        if self.argtype:
            for i, pair in enumerate(zip(self.argtype, self.children)):
                argtype, child = pair
                if argtype != child.type:
                    msg = (
                        "\n"
                        "Genetical programming type error:\n"
                        "  Function '%s' called with arguments: %s\n"
                        "  Expected %s found %s (%s) for function argument %d\n"
                        "  Tree:"
                    )
                    print(msg % (self.name, args, argtype, child.name, child.type, i + 1))
                    self.org.tree.dump(1)
                    print()
                    raise TypeError

        t = self.func(*args)
        #print self.name, args, t

        if self.type and (type(t) != self.type):
            msg = (
                "\n"
                "Genetical programming type error:\n"
                "  Function '%s' returned %s (%r) instead of type %r\n"
            )
            print(msg % (self.name, t, type(t), self.type))
            self.org.tree.dump(1)
            print()
            raise TypeError

        return t

    def dump(self, level=0):
        indents = "  " * level
        #print indents + "func:" + self.name
        print("%s%s" % (indents, self.name))
        for child in self.children:
            child.dump(level+1)

    def check_types(self):
        "Check if types of this function match its arguments"
        if not self.type:
            return

        for childtype, child in zip(self.argtype, self.children):
            if child.type != childtype:
                msg = (
                    "\n"
                    "Genetical programming type error:\n"
                    "  Function '%s' has children not matching it's types\n"
                    "  types: %r\n"
                    "  children: %r\n"
                    "  child types: %r\n"
                )
                print(msg % (self.name,
                             self.argtype,
                             self.children,
                             [c.type for c in self.children]))
                self.org.tree.dump(1)
                print()
                raise TypeError

    def copy(self, doSplit=False):
        """
        Copies this node and recursively its children, returning
        the copy

        if doSplit is true, then
        cuts off a piece of the tree, to support
        the recombination phase of mating with another program

        returns a quadruple:
             - copy - a copy of this node
             - fragment - fragment to be given to mate
             - lst - list within copy tree to which fragment
               from mate should be written
             - idx - index within the lst at which the fragment
               should be written

        if doSplit is false, then the last 3 tuple items will be None
        """
        if not doSplit:
            # easy case - split has already occurred elsewhere
            # within the tree, so just clone the kids without
            # splitting
            clonedChildren = \
                [child.copy() for child in self.children]

            # now ready to instantiate clone
            copy = FuncNode(self.org, 0, self.name, clonedChildren, type_=self.type)
            return copy

        # choose a child of this node that we might split
        childIdx = randrange(0, self.nargs)
        childToSplit = self.children[childIdx]

        # if child is a terminal, we *must* split here.
        # if child is not terminal, randomly choose whether
        # to split here
        if (random() < 0.33
            or isinstance(childToSplit, TerminalNode)):

            # split at this node, and just copy the kids
            clonedChildren = [
                child.copy() for child in self.children
            ]

            # now ready to instantiate clone
            copy = FuncNode(self.org, 0, self.name, clonedChildren, type_=self.type)
            return copy, childToSplit, clonedChildren, childIdx
        else:
            # delegate the split down to selected child
            clonedChildren = []
            for i in range(self.nargs):
                child = self.children[i]
                if (i == childIdx):
                    # chosen child
                    (clonedChild, fragment, lst, idx) = child.copy(True)
                else:
                    # just clone without splitting
                    clonedChild = child.copy()
                clonedChildren.append(clonedChild)

            # now ready to instantiate clone
            copy = FuncNode(self.org, 0, self.name, clonedChildren, type_=self.type)
            return copy, fragment, lst, idx

    def mutate(self, depth):
        """
        randomly mutates either this tree, or a child
        """
        # 2 in 3 chance of mutating a child of this node
        if random() > 0.33:
            child = choice(self.children)
            if not isinstance(child, TerminalNode):
                child.mutate(depth+1)
                return

        # mutate this node - replace one of its children
        mutIdx = randrange(0, self.nargs)
        new_child = self.org.genNode(depth+1, type_=self.children[mutIdx].type)
        self.children[mutIdx] = new_child
        self.check_types()

        #print "mutate: depth=%s" % depth


class TerminalNode(BaseNode):
    """
    Holds a terminal value
    """

class ConstNode(TerminalNode):
    """
    Holds a constant value
    """
    def __init__(self, org, value=None, type_=None):
        """
        """
        self.org = org

        if value == None:
            if type_:
                options = [x for x in org.consts if type(x) == type_]
            else:
                options = org.consts
            if options:
                value = choice(options)
            else:
                raise TypeDoesNotExist

        self.value = value
        self.type = type_ or type(value)
        self.name = str(value)


    def calc(self, **vars):
        """
        evaluates this node, returns value
        """
        # easy
        return self.value

    def dump(self, level=0):
        indents = "  " * level
        #print "%sconst: {%s}" % (indents, self.value)
        print("%s{%s}" % (indents, self.value))

    def copy(self):
        """
        clone this node
        """
        return ConstNode(self.org, self.value, type_=self.type)


class VarNode(TerminalNode):
    """
    Holds a variable
    """
    def __init__(self, org, name=None, type_=None):
        """
        Inits this node as a var placeholder
        """
        self.org = org

        if name == None:
            if org.type and type_:
                options = [x for x in org.vars if org.funcsVars[x] == type_]
            else:
                options = org.vars

            if options:
                name = choice(options)
            else:
                raise TypeDoesNotExist

        self.name = name
        self.type = org.type and org.funcsVars[name] or None

    def calc(self, **vars):
        """
        Calculates val of this node
        """
        val = vars.get(self.name, 0.0)
        #print "VarNode.calc: name=%s val=%s vars=%s" % (
        #    self.name,
        #    val,
        #    vars,
        #    )
        return val

    def dump(self, level=0):

        indents = "  " * level
        #print indents + "var {" + self.name + "}"
        print("%s{%s}" % (indents, self.name))

    def copy(self):
        """
        clone this node
        """
        return VarNode(self.org, self.name, type_=self.type)

class ProgOrganismMetaclass(type):
    """
    A metaclass which analyses class attributes
    of a ProgOrganism subclass, and builds the
    list of functions and terminals
    """
    def __init__(cls, name, bases, data):
        """
        Create the ProgOrganism class object
        """
        # parent constructor
        super(ProgOrganismMetaclass, cls).__init__(name, bases, data)

        # get the funcs, consts and vars class attribs
        funcs = data['funcs']
        consts = data['consts']
        vars = data['vars']

        # process the funcs
        funcsList = []
        funcsDict = {}
        funcsVars = {}
        for name, func in list(funcs.items()):
            try:
                types = func._types
            except:
                types = None
            funcsList.append((name, func, func.__code__.co_argcount, types))
            funcsDict[name] = (func, func.__code__.co_argcount, types)
        if cls.type:
            funcsVars = dict(tuple(vars))
            vars = [x[0] for x in vars]

        cls.vars = vars
        cls.funcsList = funcsList
        cls.funcsDict = funcsDict
        cls.funcsVars = funcsVars

class ProgOrganism(BaseOrganism, metaclass=ProgOrganismMetaclass):
    """
    Implements an organism for genetic programming

    Introspects to discover functions and terminals.

    You should add the folling class attribs:
        - funcs - a dictionary of funcs, names are func
          names, values are callable objects
        - vars - a list of variable names
        - consts - a list of constant values
    """

    funcs = {}
    vars = []
    consts = []
    type = None

    # maximum tree depth when generating randomly
    maxDepth = 4

    # probability of a mutation occurring
    mutProb = 0.01

    def __init__(self, root=None):
        """
        Creates this organism
        """

        # Cache fitness
        self.fitness_cache = None

        if root == None:
            root = self.genNode(type_=self.type)

        self.tree = root

    def mate(self, mate):
        """
        Perform recombination of subtree elements
        """

        # get copy of self, plus fragment and location details
        tries = 0
        while True:
            tries += 1

            if tries > 20:
                print("Warning: Failed to swap trees for", tries, "times. Continuing...")
                return self.copy(), mate.copy()

            # Get copied trees
            ourRootCopy, ourFrag, ourList, ourIdx = self.split()
            mateRootCopy, mateFrag, mateList, mateIdx = mate.split()

            # Can we swap them?
            if mateFrag.type != ourFrag.type:
                continue

            # Swap
            ourList[ourIdx] = mateFrag
            mateList[mateIdx] = ourFrag

            # Early sanity check
            mateRootCopy.check_types()
            ourRootCopy.check_types()
            break

        # and return both progeny
        child1 = self.__class__(ourRootCopy)
        child2 = self.__class__(mateRootCopy)

        return (child1, child2)

    def mutate(self):
        """
        Mutates this organism's node tree

        returns the mutant
        """
        mutant = self.copy()
        mutant.tree.mutate(1)
        return mutant

    def split(self):
        """
        support for recombination, returns a tuple
        with four values:
            - root - a copy of the tree, except for the fragment
              to be swapped
            - subtree - the subtree fragment to be swapped
            - lst - a list within the tree, containing the
              fragment
            - idx - index within the list where mate's fragment
              should be written
        """
        # otherwise, delegate the split down the tree
        copy, subtree, lst, idx = self.tree.copy(True)
        return (copy, subtree, lst, idx)

    def calc_nodes(self):
        "Calculate nodes in equation"
        return self.tree.calc_nodes()

    def copy(self):
        """
        returns a deep copy of this organism
        """
        try:
            return self.__class__(self.tree.copy())
        except:
            print("self.__class__ = %s" % self.__class__)
            raise

    def dump(self, node=None, level=1):
        """
        prints out this organism's node tree
        """
        self.tree.dump(1)

    def genNode(self, depth=1, type_=None):
        """
        Randomly generates a node to build in
        to this organism
        """
        cnt = 0
        while True:
            cnt += 1
            try:
                if depth > 1 and (depth >= self.initDepth or flipCoin()):
                    # not root, and either maxed depth, or 50-50 chance
                    if flipCoin():
                        # choose a var
                        v = VarNode(self, type_=type_)
                    else:
                        v = ConstNode(self, type_=type_)
                    return v
                else:
                    # either root, or not maxed, or 50-50 chance
                    f = FuncNode(self, depth, type_=type_)
                    return f
            except TypeDoesNotExist:
                if cnt > 50:
                    print("Warning, probably an infinite loop")
                    print("  your options does not allow for tree construction")
                continue


    def xmlDumpSelf(self, doc, parent):
        """
        Dumps out this object's contents into an xml tree

        Arguments:
            - doc - an xml.dom.minidom.Document object
            - parent - an xml.dom.minidom.Element parent, being
              the node into which this node should be placed
        """
        raise Exception("method xmlDumpSelf not implemented")

    def fitness(self):
        """
        Return the fitness level of this organism, as a float

        Should return a number from 0.0 to infinity, where
        0.0 means 'perfect'

        Organisms should evolve such that 'fitness' converges
        to zero.

        This method must be overridden

        In your override, you should generate a set of values,
        either deterministically or randomly, and pass each
        value to both .testFunc() and .calculate(), comparing
        the results and using this to calculate the fitness
        """
        raise Exception("Method 'fitness' not implemented")

    def testFunc(self, **kw):
        """
        this is the 'reference function' toward which
        organisms are trying to evolve

        You must override this in your organism subclass
        """
        raise Exception("method 'testFunc' not implemented")

    def calc(self, **vars):
        """
        Executes this program organism, using the given
        keyword parameters

        You shouldn't need to override this
        """
        #print "org.calc: vars=%s" % str(vars)

        return self.tree.calc(**vars)

def flipCoin():
    """
    randomly returns True/False
    """
    return choice((True, False))


def typed(*args):
    def typed_decorator(f):
        f._types = args
        return f
    return typed_decorator
