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
import time

# @typed(Return value type, first input type, second input type)
@typed(float, float, float)
def add(x,y):
    try:
        return x+y
    except:
        #raise
        return x

@typed(float, float, float)
def sub(x,y):
    try:
        return x-y
    except:
        #raise
        return x

@typed(float, float, float)
def mul(x,y):
    try:
        return x*y
    except:
        #raise
        return x

@typed(float, bool, float, float)
def iif(x, y, z):
#    print "IIF:", x, y, z
    if x:
        return y
    else:
        return z

@typed(bool, float, float)
def greater(x,y):
    return x>y

@typed(bool, float, float)
def lesser(x,y):
    return x<y

# define the class comprising the program organism
class MyTypedProg(ProgOrganism):
    """
    """
    funcs = {
        '+': add,
        '-': sub,
        #'*': mul,
        'iif': iif,
        '>': greater,
        #'<': lesser,
        }
    vars = [('x', float), ('y', float)]
    consts = [0.0, 1.0, True]
    type = float

    testVals = [
        {
            'x': uniform(-10.0, 10.0),
            'y': uniform(-10.0, 10.0),
        } for i in xrange(20)
    ]


    mutProb = 0.4

    def testFunc(self, **vars):
        """
        Just wanting to model iif(x > 0, 2.0 * y, -y)
        """
        if vars['x'] > 0:
            return 2.0 * vars['y']
        else:
            return - vars['y']

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
    initDepth = 5


class TypedProgPop(Population):
    u"""Population class for typed programming demo"""

    species = MyTypedProg
    initPopulation = 30

    # cull to this many children after each generation
    childCull = 30

    # number of children to create after each generation
    childCount = 20

    mutants = 0.3

def graph(orig, best):
    "Graph on -10, 10 ranges"
    print "ORIG                                  BEST:"
    for y in range(10, -11, -2):
        for x in range(-10, 11, 3):
            z = orig(x=float(x), y=float(y))
            print "%03.0f " % z,

        print "  ",
        for x in range(-10, 11, 3):
            z = best(x=float(x), y=float(y))
            print "%03.0f " % z,


        print

def main(nfittest=10, nkids=100):
    pop = TypedProgPop()
    origpop = pop
    ngens = 0
    i = 0
    while True:
        b = pop.best()
        print "Generation %s: %s best=%s average=%s)" % (
            ngens, str(b), b.fitness(), pop.fitness())
        b.dump(1)
        graph(b.testFunc, b.calc)
        if b.fitness() <= 0.0:
            print "Cracked!"
            break
        i += 1
        ngens += 1

        if ngens < 30:
            pop.gen()
        else:
            print "Failed after 30 generations, restarting"
            time.sleep(1)
            pop = TypedProgPop()
            ngens = 0

if __name__ == '__main__':
    main()
    pass
