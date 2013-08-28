#! /usr/bin/env python

"""
Demo of genetic programming with a typed language

This gp setup seeks to breed an organism which
implements if(x > 0, y, -y)

Takes an average of about X generations
to breed a matching program
"""

import math
from random import random, uniform
from pygene.prog import ProgOrganism, typed
from pygene.population import Population

@typed(float, float, float)
def add(x,y):
    #print "add: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x+y
    except:
        #raise
        return x

@typed(float, float, float)
def sub(x,y):
    #print "sub: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x-y
    except:
        #raise
        return x

@typed(float, float, float)
def mul(x,y):
    #print "mul: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x*y
    except:
        #raise
        return x
        
@typed(bool, bool, float, float)
def iif(x, y, z):
    #print "tan: x=%s" % repr(x)
    try:
        return math.tan(float(x))
    except:
        #raise
        return x
        
@typed(bool, float, float)
def greater(x,y):
    try:
        return x>y
    except:
        #raise
        return x

@typed(bool, float, float)
def lesser(x,y):
    try:
        return x<y
    except:
        #raise
        return x

# define the class comprising the program organism
class MyTypedProg(ProgOrganism):
    """
    """
    funcs = {
        #'+': add,
        '-': sub,
        #'*': mul,
        'iif':iif,
        '>':greater,
        #'<':lesser,
        }
    vars = [('x', float)]
    consts = [0.0, 1.0, True]

    testVals = [{'x':uniform(-10.0, 10.0),
                 'y':uniform(-10.0, 10.0),
                 } \
                     for i in xrange(20)
                ]

    mutProb = 0.4
    
    type = float
    
    def testFunc(self, **vars):
        """
        Just wanting to model iif(x > 0, y, -y)
        """
        if vars['x'] > 0:
            return 1.0
        else:
            return 0.0

    def fitness(self):
        # choose 10 random values
        badness = 0.0
        try:
            for vars in self.testVals:
                badness += (self.calc(**vars) - self.testFunc(**vars)) ** 2
            return badness
        except OverflowError:
            return 1.0e+255 # infinitely bad
        
    # maximum tree depth when generating randomly
    initDepth = 6

# now create the population class
class TypedProgPop(Population):
    
    species = MyTypedProg
    initPopulation = 10
    
    # cull to this many children after each generation
    childCull = 20

    # number of children to create after each generation
    childCount = 20

    mutants = 0.3


pop = TypedProgPop()

def main(nfittest=10, nkids=100):
    
    global pop

    ngens = 0
    i = 0
    while True:
        b = pop.best()
        b.dump()
        print "generation %s: %s best=%s average=%s)" % (
            i, str(b), b.fitness(), pop.fitness())
        if b.fitness() <= 0:
            print "cracked!"
            break
        i += 1
        ngens += 1
        
        if ngens < 100000:
            pop.gen()
        else:
            print "failed after 100 generations, restarting"
            pop = TypedProgPop()
            ngens = 0

if __name__ == '__main__':
    main()
    pass

