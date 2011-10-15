#!/usr/bin/env python
"""
another demo that cracks a secret string

This one uses the printable char gene
"""

from pygene.gene import PrintableCharGene
from pygene.gamete import Gamete
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population

# this is the string that our organisms
# are trying to evolve into
teststr = "hackthis"

# derive a gene which holds a character, and can
# mutate into another character
class HackerGene(PrintableCharGene):
    mutProb = 0.1
    mutAmt = 2

# Generate a genome, one gene for each char in the string
genome = {}
for i in xrange(len(teststr)):
    genome[str(i)] = HackerGene 


# An organism that evolves towards the required string
class StringHacker(MendelOrganism):
    
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a string
        """
        chars = []
        for k in xrange(self.numgenes):
            c = self[str(k)]
            chars.append(c)

        return ''.join(chars)

    def fitness(self):
        """
        calculate fitness, as the sum of the squares
        of the distance of each char gene from the
        corresponding char of the target string
        """
        diffs = 0
        guess = str(self)
        for i in xrange(self.numgenes):

            x0 = ord(teststr[i])
            #print "self[%s] = %s" % (i, self[i])
            x1 = ord(self[str(i)])
            diffs += (2 * (x1 - x0)) ** 2

        return diffs

class StringHackerPopulation(Population):
    species = StringHacker

    # start with a population of 10 random organisms
    initPopulation = 10
    
    # cull to this many children after each generation
    childCull = 10
    
    # number of children to create after each generation
    childCount = 40
    

def main(nfittest=10, nkids=100):
    # Create population
    world = StringHackerPopulation()

    # Iterate over generations while displaying best solutions
    i = 0
    while True:
        best = world.best()
        print "generation {0}: {1} best={2} average={3})".format(
            i, str(best), best.get_fitness(), world.fitness())
        if best.get_fitness() <= 0:
            print "cracked!"
            break
        i += 1
        world.gen()

if __name__ == '__main__':
    main()
