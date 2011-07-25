#! /usr/bin/env python
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

teststrlen = len(teststr)

# generate a set of 'gene names', one for each char in the string
geneNames = []
for i in range(len(teststr)):
    geneNames.append("%s" % i)

# derive a gene which holds a character, and can
# mutate into another character

class HackerGene(PrintableCharGene):
    
    mutProb = 0.1
    mutAmt = 2

# generate a genome, one gene for each char in the string
genome = {}
for i in range(len(teststr)):
    genome[str(i)] = HackerGene

# an organism that evolves towards the required string

class StringHacker(MendelOrganism):
    
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a string
        """
        #chars = []
        #for k in self.geneNames:
        #    gene1, gene2 = self.genes[k]
        #    #n = int((gene1.value + gene2.value) / 2)
        #    n = min(gene1.value, gene2.value)
        #    c = str(chr(n))
        #    chars.append(c)
        
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

    initPopulation = 10
    species = StringHacker
    
    # cull to this many children after each generation
    childCull = 10
    
    # number of children to create after each generation
    childCount = 40
    
# start with a population of 10 random organisms
ph = StringHackerPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    while True:
        b = ph.best()
        print "generation %s: %s best=%s average=%s)" % (
            i, str(b), b.fitness(), ph.fitness())
        if b.fitness() <= 0:
            print "cracked!"
            break
        i += 1
        ph.gen()


if __name__ == '__main__':
    main()