#! /usr/bin/env python3

"""
Very simple demo in which organisms try to minimise
the output value of a function
"""

from pygene3.gene import FloatGene, FloatGeneMax
from pygene3.organism import Organism, MendelOrganism
from pygene3.population import Population

class CvGene(FloatGeneMax):
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


class Converger(MendelOrganism):
    """
    Implements the organism which tries
    to converge a function
    """
    genome = {'x':CvGene, 'y':CvGene}
    
    def fitness(self):
        """
        Implements the 'fitness function' for this species.
        Organisms try to evolve to minimise this function's value
        """
        return self['x'] ** 2 + self['y'] ** 2

    def __repr__(self):
        return "<Converger fitness=%f x=%s y=%s>" % (
            self.fitness(), self['x'], self['y'])


# create an empty population

pop = Population(species=Converger, init=2, childCount=50, childCull=20)


# now a func to run the population

def main():
    try:
        while True:
            # execute a generation
            pop.gen()

            # get the fittest member
            best = pop.best()
            
            # and dump it out
            print(best)

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

