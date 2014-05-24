#! /usr/bin/env python
"""
demo that cracks a secret string.

the feedback is how 'close' an organism's string
is to the target string, based on the sum of the
squares of the differences in the respective chars

Compare this demo to demo_case.py - similar demo where
ordering/grouping of genes has a meaning.
"""
from pygene.gene import CharGeneExchange
from pygene.organism import Organism
from pygene.population import Population

# this is the string that our organisms
# are trying to evolve into
teststr = "hackthis"

class HackerGene(CharGeneExchange):
    """
    a gene which holds a character, and can mutate into another character
    """
    mutProb = 0.1
    mutAmt = (ord('z') - ord('a')) / 2

    def __repr__(self):
        return self.value

# generate a genome, one gene for each char in the string
# { '0': Gene, '1': Gene2... }
genome = {}
for i in range(len(teststr)):
    genome[str(i)] = HackerGene

# an organism that evolves towards the required string

class StringHacker(Organism):

    # set organism genome
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a string
        """
        chars = [self[str(i)] for i in range(self.numgenes)]
        return str(''.join(chars))

    def fitness(self):
        """
        calculate fitness, as the sum of the squares
        of the distance of each char gene from the
        corresponding char of the target string
        """
        # Get our value as a string
        guess = str(self)

        # Calculate difference
        diffs = 0
        for x0, x1 in zip(teststr, guess):
            diffs += (ord(x1) - ord(x0)) ** 2
        return diffs


class StringHackerPopulation(Population):
    # set population species
    species = StringHacker

    # Number of initial random organisms
    initPopulation = 10

    # cull to this many children after each generation
    childCull = 10

    # number of children to create after each generation
    childCount = 50

    mutants = 0.25


def main():
    from time import time

    # start with a population of random organisms
    world = StringHackerPopulation()

    i = 0
    started = time()
    while True:
        b = world.best()
        print "generation %02d: %s best=%s average=%s)" % (
            i, repr(b), b.get_fitness(), world.fitness())
        if b.get_fitness() <= 0:
            print "cracked in ", i, "generations and ", time() - started, "seconds"
            break
        i += 1
        world.gen()


if __name__ == '__main__':
    main()
