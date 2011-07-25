#! /usr/bin/env python

"""
experiment in using fractals to fit a set of values

may or may not work
"""

import math

from pygene.gene import FloatGene, ComplexGene
from pygene.gene import IntGene, OrBitGene, rndPair
from pygene.organism import Organism
from pygene.population import Population

# data set to model

targetData = [432, 444, 520, 419, 450, 540, 625]
targetDataLen = len(targetData)

# gene classes for fractals

class OrgGene(ComplexGene):
    """
    gene to use for initial value
    """
    mutProb = 0.03
    mutAmt = 0.5

    randMin = -2.0
    randMax = 2.0

class DeltaGene(ComplexGene):
    """
    gene to use for motion
    """
    mutProb = 0.03
    mutAmt = 1.0

    rndMin = -0.4
    rndMax = 0.4


class IterationsGene(IntGene):
    """
    gene that controls number of mandelbrot iterations
    """
    mutProb = 0.001
    randMin = 2
    randMax = 10

# utility func - standard deviation

def sdev(dataset):
    
    n = float(len(dataset))
    mean = sum(dataset) / n
    devs = [(x - mean) ** 2 for x in dataset]
    sd = math.sqrt(sum(devs) / n)
    return mean, sd
    
# organism class

class FracOrganism(Organism):
    """
    organism class
    """
    genome = {
        'init':OrgGene,
        'delta':DeltaGene,
        'iterations':IterationsGene,
        }

    maxIterations = 100

    def fitness(self):
        """
        fitness is the standard deviation of the ratio of
        each generated value to each target value
        """
        guessData = self.getDataSet()
        badness = 0.0
        ratios = [100000.0 * guessData[i] / targetData[i] \
            for i in xrange(targetDataLen)]
        try:
            sd, mean = sdev(ratios)
            var = sd / mean
            badness = var, sd, mean
        except:
            #raise
            badness = 10000.0, None, None
        return badness
        
    def getDataSet(self):
        """
        computes the data set resulting from genes
        """
        guessData = []
        org = self['init']
        delta = self['delta']
        niterations = self['iterations']
        for i in xrange(targetDataLen):
            #guessData.append(self.mand(org, niterations))
            guessData.append(self.mand(org))
            org += delta
        return guessData
    
    def mand_old(self, org, niterations):
        """
        performs the mandelbrot calculation on point org for
        niterations generations,
        returns final magnitude
        """
        c = complex(0,0)
        
        for i in xrange(niterations):
            c = c * c + org
        
        return abs(c)

    def mand(self, org):
        """
        returns the number of iterations needed for abs(org)
        to exceed 1.0
        """
        i = 0
        c = complex(0,0)
        while i < self.maxIterations:
            if abs(c) > 1.0:
                break
            c = c * c + org
            i += 1
        return i
            
def newOrganism(self=None):

    return FracOrganism(
        init=OrgGene,
        delta=DeltaGene,
        iterations=IterationsGene,
        )

class FracPopulation(Population):

    species = FracOrganism
    initPopulation = 100

    # cull to this many children after each generation
    childCull = 6

    # number of children to create after each generation
    childCount = 30

    # enable addition of random new organisms
    newOrganism = newOrganism
    numNewOrganisms = 5

    # keep best 5 parents    
    incest = 5


# create an initial random population

pop = FracPopulation()


# now a func to run the population
def main():
    try:
        while True:
            # execute a generation
            pop.gen()

            # and dump it out
            #print [("%.2f %.2f" % (o['x1'], o['x2'])) for o in pop.organisms]
            best = pop.organisms[0]
            print "fitness=%s" % (best.fitness(),)

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()


