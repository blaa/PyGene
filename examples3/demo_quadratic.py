#! /usr/bin/env python3

"""
Very simple demo in which organisms try to minimise
the output value of a function
"""

from pygene3.gene import FloatGene, FloatGeneMax
from pygene3.organism import Organism, MendelOrganism
from pygene3.population import Population

# parameters for quadratic equation
# has roots 3 and 5
a = 2
b = -16
c = 30

if 0:
    # this alternate set has only 1 root, x=4
    a = 2.0
    b = 3.0
    c = -44.0

class XGene(FloatGene):
    """
    Gene which represents the numbers used in our organism
    """
    # genes get randomly generated within this range
    randMin = -100.0
    randMax = 100.0
    
    # probability of mutation
    mutProb = 0.1
    
    # degree of mutation
    mutAmt = 0.1

def quad(x):
    return a * x ** 2 + b * x + c

class QuadraticSolver(Organism):
    """
    Implements the organism which tries
    to solve a quadratic equation
    """
    genome = {'x1':XGene, 'x2':XGene}
    
    def fitness(self):
        """
        Implements the 'fitness function' for this species.
        Organisms try to evolve to minimise this function's value
        """
        x1 = self['x1']
        x2 = self['x2']
        
        # this formula punishes for roots being wrong, also for
        # roots being the same
        badness_x1 = abs(quad(x1)) # punish for incorrect first root
        badness_x2 = abs(quad(x2)) # punish for incorrect second root
        badness_equalroots = 1.0 / (abs(x1 - x2)) # punish for equal roots
        return badness_x1 + badness_x2 + badness_equalroots

    def __repr__(self):
        return "<fitness=%f x1=%s x2=%s>" % (
            self.fitness(), self['x1'], self['x2'])


class QPopulation(Population):

    species = QuadraticSolver
    initPopulation = 2
    
    # cull to this many children after each generation
    childCull = 5

    # number of children to create after each generation
    childCount = 50


# create a new population, with randomly created members

pop = QPopulation()


# now a func to run the population
def main():
    try:
        generations = 0
        while True:
            # execute a generation
            pop.gen()
            generations += 1

            # and dump it out
            #print [("%.2f %.2f" % (o['x1'], o['x2'])) for o in pop.organisms]
            best = pop.organisms[0]
            print("fitness=%f x1=%f x2=%f" % (best.get_fitness(), best['x1'], best['x2']))
            if best.get_fitness() < 0.6:
                break

    except KeyboardInterrupt:
        pass
    print("Executed", generations, "generations")


if __name__ == '__main__':
    main()


