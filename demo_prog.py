#! /usr/bin/env python

"""
Demo of genetic programming

This gp setup seeks to breed an organism which
implements func x^2 + y

Takes an average of about 40 generations
to breed a matching program
"""

import math
from random import random, uniform
from pygene.prog import ProgOrganism
from pygene.population import Population

# a tiny batch of functions
def add(x,y):
    #print "add: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x+y
    except:
        #raise
        return x

def sub(x,y):
    #print "sub: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x-y
    except:
        #raise
        return x

def mul(x,y):
    #print "mul: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x*y
    except:
        #raise
        return x

def div(x,y):
    #print "div: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x / y
    except:
        #raise
        return x

def sqrt(x):
    #print "sqrt: x=%s" % repr(x)
    try:
        return math.sqrt(x)
    except:
        #raise
        return x

def pow(x,y):
    #print "pow: x=%s y=%s" % (repr(x), repr(y))
    try:
        return x ** y
    except:
        #raise
        return x

def log(x):
    #print "log: x=%s" % repr(x)
    try:
        return math.log(float(x))
    except:
        #raise
        return x

def sin(x):
    #print "sin: x=%s" % repr(x)
    try:
        return math.sin(float(x))
    except:
        #raise
        return x
    
def cos(x):
    #print "cos: x=%s" % repr(x)
    try:
        return math.cos(float(x))
    except:
        #raise
        return x
        
def tan(x):
    #print "tan: x=%s" % repr(x)
    try:
        return math.tan(float(x))
    except:
        #raise
        return x

# define the class comprising the program organism
class MyProg(ProgOrganism):
    """
    """
    funcs = {
        '+': add,
#        '-':sub,
        '*': mul,
#        '/':div,
#        '**': pow,
#        'sqrt': sqrt,
#        'log' : log,
#        'sin' : sin,
#        'cos' : cos,
#        'tan' : tan,
        }
    vars = ['x', 'y']
    consts = [0.0, 1.0, 2.0, 10.0]

    testVals = [{'x':uniform(-10.0, 10.0),
                 'y':uniform(-10.0, 10.0),
                 } \
                     for i in xrange(20)
                ]

    mutProb = 0.4

    
    def testFunc(self, **vars):
        """
        Just wanting to model x^2 + y
        """
        return vars['x'] ** 2 + vars['y']

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
class ProgPop(Population):
    
    species = MyProg
    initPopulation = 10
    
    # cull to this many children after each generation
    childCull = 20

    # number of children to create after each generation
    childCount = 20

    mutants = 0.3


pop = ProgPop()

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
        
        if ngens < 100:
            pop.gen()
        else:
            print "failed after 100 generations, restarting"
            pop = ProgPop()
            ngens = 0

if __name__ == '__main__':
    main()
    pass

