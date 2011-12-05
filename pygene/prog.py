#@+leo-ver=4
#@+node:@file pygene/prog.py
"""
Implements genetic programming organisms
"""

#@+others
#@+node:imports
from random import random, randrange, choice
from math import sqrt

from organism import BaseOrganism

from xmlio import PGXmlMixin

#@-node:imports
#@+node:class BaseNode
class BaseNode:
    """
    Base class for genetic programming nodes
    """
    #@    @+others
    #@+node:calc
    def calc(self, **vars):
        """
        evaluates this node, plugging vars into
        the nodes
        """
        raise Exception("method 'calc' not implemented")
    
    #@-node:calc
    #@-others

#@-node:class BaseNode
#@+node:class FuncNode
class FuncNode(BaseNode):
    """
    node which holds a function and its argument nodes
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, org, depth, name=None, children=None):
        """
        creates this func node
        """
        self.org = org
    
        if name == None:
            # randomly choose a func
            name, func, nargs = choice(org.funcsList)
        else:
            # lookup func in organism
            func, nargs = org.funcsDict[name]
        
        # and fill in the args, from given, or randomly
        if not children:
            children = [org.genNode(depth+1) for i in xrange(nargs)]
    
        self.name = name
        self.func = func
        self.nargs = nargs
        self.children = children
        
    #@-node:__init__
    #@+node:calc
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
    
        return self.func(*args)
    
    #@-node:calc
    #@+node:dump
    def dump(self, level=0):
        
        indents = "  " * level
        #print indents + "func:" + self.name
        print "%s%s" % (indents, self.name)
        for child in self.children:
            child.dump(level+1)
    
    #@-node:dump
    #@+node:copy
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
            fragment = None
            lst = None
            idx = None
    
            # now ready to instantiate clone
            copy = FuncNode(self.org, 0, self.name, clonedChildren)
            return copy
    
        # choose a child of this node that we might split
        childIdx = randrange(0, self.nargs)
        childToSplit = self.children[childIdx]
    
        # if child is a terminal, we *must* split here.
        # if child is not terminal, randomly choose whether
        # to split here
        if random() < 0.33 \
                or isinstance(childToSplit, TerminalNode):
    
            # split at this node, and just copy the kids
            clonedChildren = \
                [child.copy() for child in self.children]
    
            # now ready to instantiate clone
            copy = FuncNode(self.org, 0, self.name, clonedChildren)
    
            return copy, childToSplit, self.children, childIdx
        
        else:
            # delegate the split down to selected child
            clonedChildren = []
            for i in xrange(self.nargs):
                child = self.children[i]
                if (i == childIdx):
                    # chosen child
                    (clonedChild,fragment,lst,idx) = child.copy(True)
                else:
                    # just clone without splitting
                    clonedChild = child.copy()
                clonedChildren.append(clonedChild)
    
            # now ready to instantiate clone
            copy = FuncNode(self.org, 0, self.name, clonedChildren)
    
            return copy, fragment, lst, idx
    
    #@-node:copy
    #@+node:mutate
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
        self.children[mutIdx] = self.org.genNode(depth+1)
    
        #print "mutate: depth=%s" % depth
    
    #@-node:mutate
    #@-others

#@-node:class FuncNode
#@+node:class TerminalNode
class TerminalNode(BaseNode):
    """
    Holds a terminal value
    """
    #@    @+others
    #@-others

#@-node:class TerminalNode
#@+node:class ConstNode
class ConstNode(TerminalNode):
    """
    Holds a constant value
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, org, value=None):
        """
        """
        self.org = org
    
        if value == None:
            value = choice(org.consts)
    
        self.value = value
    
        
    #@nonl
    #@-node:__init__
    #@+node:calc
    def calc(self, **vars):
        """
        evaluates this node, returns value
        """
        # easy
        return self.value
    
    #@-node:calc
    #@+node:dump
    def dump(self, level=0):
        
        indents = "  " * level
        #print "%sconst: {%s}" % (indents, self.value)
        print "%s{%s}" % (indents, self.value)
    
    #@-node:dump
    #@+node:copy
    def copy(self):
        """
        clone this node
        """
        return ConstNode(self.org, self.value)
    
    #@-node:copy
    #@-others


#@-node:class ConstNode
#@+node:class VarNode
class VarNode(TerminalNode):
    """
    Holds a variable
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, org, name=None):
        """
        Inits this node as a var placeholder
        """
        self.org = org
    
        if name == None:
            name = choice(org.vars)
        
        self.name = name
    
    #@-node:__init__
    #@+node:calc
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
    #@-node:calc
    #@+node:dump
    def dump(self, level=0):
        
        indents = "  " * level
        #print indents + "var {" + self.name + "}"
        print "%s{%s}" % (indents, self.name)
    
    #@-node:dump
    #@+node:copy
    def copy(self):
        """
        clone this node
        """
        return VarNode(self.org, self.name)
    
    #@-node:copy
    #@-others

#@-node:class VarNode
#@+node:class ProgOrganismMetaclass
class ProgOrganismMetaclass(type):
    """
    a metaclass which analyses class attribs
    of a ProgOrganism subclass, and builds the
    list of functions and terminals
    """
    #@    @+others
    #@+node:__init__
    def __init__(cls, name, bases, dict):
        """
        Create the ProgOrganism class object
        """
        # parent constructor
        object.__init__(cls, name, bases, dict)
    
        # get the funcs, consts and vars class attribs
        funcs = dict['funcs']
        consts = dict['consts']
        vars = dict['vars']
        
        # process the funcs
        funcsList = []
        funcsDict = {}
        for name, func in funcs.items():
            funcsList.append((name, func, func.func_code.co_argcount))
            funcsDict[name] = (func, func.func_code.co_argcount)
    
        cls.funcsList = funcsList
        cls.funcsDict = funcsDict
    
    #@-node:__init__
    #@-others

#@-node:class ProgOrganismMetaclass
#@+node:class ProgOrganism
class ProgOrganism(BaseOrganism):
    """
    Implements an organism for genetic programming

    Introspects to discover functions and terminals.

    You should add the folling class attribs:
        - funcs - a dictionary of funcs, names are func
          names, values are callable objects
        - vars - a list of variable names
        - consts - a list of constant values
    """
    #@    @+others
    #@+node:attribs
    __metaclass__ = ProgOrganismMetaclass
    
    funcs = {}
    vars = []
    consts = []
    
    # maximum tree depth when generating randomly
    maxDepth = 4
    
    # probability of a mutation occurring
    mutProb = 0.01
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, root=None):
        """
        Creates this organism
        """

        # Cache fitness
        self.fitness_cache = None

        if root == None:
            root = self.genNode()
    
        self.tree = root
    
    #@-node:__init__
    #@+node:mate
    def mate(self, mate):
        """
        Perform recombination of subtree elements
        """
        # get copy of self, plus fragment and location details
        ourRootCopy, ourFrag, ourList, ourIdx = self.split()
    
        # ditto for mate
        mateRootCopy, mateFrag, mateList, mateIdx = mate.split()
    
        # swap the fragments
        ourList[ourIdx] = mateFrag
        mateList[mateIdx] = ourFrag
    
        # and return both progeny
        child1 = self.__class__(ourRootCopy)
        child2 = self.__class__(mateRootCopy)
    
        return (child1, child2)
    
    #@-node:mate
    #@+node:mutate
    def mutate(self):
        """
        Mutates this organism's node tree
    
        returns the mutant
        """
        mutant = self.copy()
        mutant.tree.mutate(1)
        return mutant
    
    #@-node:mutate
    #@+node:split
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
    
    #@-node:split
    #@+node:copy
    def copy(self):
        """
        returns a deep copy of this organism
        """
        try:
            return self.__class__(self.tree)
        except:
            print "self.__class__ = %s" % self.__class__
            raise
    
    
    
    
    
    #@-node:copy
    #@+node:dump
    def dump(self, node=None, level=1):
        """
        prints out this organism's node tree
        """
        print "organism:"
        self.tree.dump(1)
    
    #@-node:dump
    #@+node:genNode
    def genNode(self, depth=1):
        """
        Randomly generates a node to build in
        to this organism
        """
    
        if depth > 1 and (depth >= self.initDepth or flipCoin()):
            # not root, and either maxed depth, or 50-50 chance
            if flipCoin():
                # choose a var
                return VarNode(self)
            else:
                return ConstNode(self)
    
        # either root, or not maxed, or 50-50 chance
        return FuncNode(self, depth)
    
    #@-node:genNode
    #@+node:xmlDumpSelf
    def xmlDumpSelf(self, doc, parent):
        """
        Dumps out this object's contents into an xml tree
        
        Arguments:
            - doc - an xml.dom.minidom.Document object
            - parent - an xml.dom.minidom.Element parent, being
              the node into which this node should be placed
        """
        raise Exception("method xmlDumpSelf not implemented")
    
    #@-node:xmlDumpSelf
    #@+node:fitness
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
    
    #@-node:fitness
    #@+node:testFunc
    def testFunc(self, **kw):
        """
        this is the 'reference function' toward which
        organisms are trying to evolve
    
        You must override this in your organism subclass
        """
        raise Exception("method 'testFunc' not implemented")
    
    #@-node:testFunc
    #@+node:calc
    def calc(self, **vars):
        """
        Executes this program organism, using the given
        keyword parameters
    
        You shouldn't need to override this
        """
        #print "org.calc: vars=%s" % str(vars)
    
        return self.tree.calc(**vars)
    
    #@-node:calc
    #@-others


#@-node:class ProgOrganism
#@+node:funcs
# util funcs

#@+others
#@+node:flipCoin
def flipCoin():
    """
    randomly returns True/False
    """
    return choice((True, False))

#@-node:flipCoin
#@-others

#@-node:funcs
#@-others

#@-node:@file pygene/prog.py
#@-leo
