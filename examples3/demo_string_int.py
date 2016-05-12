#! /usr/bin/env python3
"""
another demo that cracks a secret string

This one uses the discrete int gene
"""

from pygene3.gene import FloatGene, IntGene, rndPair
from pygene3.gamete import Gamete
from pygene3.organism import Organism 
from pygene3.population import Population

# this is the string that our organisms
# are trying to evolve into
teststr = "hackthis"

# convert the string into a list of ints, where
# each int is the ascii value of the corresponding
# char

teststrNums = [ord(c) for c in teststr]

# derive a gene which holds a character, and can
# mutate into another character

class HackerGene(IntGene):
    
    mutProb = 0.1
    mutAmt = 10
    
    randMin = 0
    randMax = 255

# generate a genome, one gene for each char in the string
genome = {}
for i in range(len(teststr)):
    genome[str(i)] = HackerGene

# an organism that evolves towards the required string

class StringHacker(Organism):
    
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a string
        """
        chars = []
        for k in range(self.numgenes):

            n = self[str(k)]
            #print "n=%s" % repr(n)
            c = str(chr(n))

            chars.append(c)

        return ''.join(chars)

    def fitness(self):
        """
        calculate fitness, as the sum of the squares
        of the distance of each char gene from the
        corresponding char of the target string
        """
        diffs = 0.0
        guess = str(self)
        for i in range(self.numgenes):
            x0 = teststrNums[i]
            x1 = ord(guess[i])
            diffs += (x1 - x0) ** 2
        return diffs

class StringHackerPopulation(Population):
 
    # Population species
    species = StringHacker

    # start with a population of 10 random organisms
    initPopulation = 10
    
    # cull to this many children after each generation
    childCull = 10
    
    # number of children to create after each generation
    childCount = 50
    

def main():
    # Create initial population
    world = StringHackerPopulation()

    # Iterate over generations
    i = 0
    while True:
        b = world.best()
        print("generation %s: %s best=%s average=%s)" % (
            i, repr(b), b.get_fitness(), world.fitness()))
        if b.get_fitness() <= 0:
            print("cracked!")
            break
        i += 1
        world.gen()


if __name__ == '__main__':
    main()
