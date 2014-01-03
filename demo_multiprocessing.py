#! /usr/bin/env python
"""
Parallel fitness calculation using the Python multiprocessing library.

Based on demo_string.py, but using a pool of 4 worker processes to do the fitness calculation.

Note: the fitness calculation for this GA problem is not very computationally expensive,
so the worker processes don't look very busy. However, if you add some extra CPU-intensive calculations
to the calculate_fitness() function, you'll notice the difference.

"""

from pygene.gene import FloatGene, FloatGeneMax, rndPair
from pygene.gamete import Gamete
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from multiprocessing import Pool

# Fitness function - global and unbound, for multiprocessing to be able to Pickle it
def calculate_fitness(guess, numgenes):
	diffs = 0
	for i in xrange(numgenes):
		x0 = teststrNums[i]
		x1 = ord(guess[i])
		diffs += (x1 - x0) ** 2
	return diffs

# this is the string that our organisms
# are trying to evolve into
teststr = "hackthis"

# convert the string into a list of floats, where
# each float is the ascii value of the corresponding
# char

teststrNums = [float(ord(c)) for c in teststr]

# derive a gene which holds a character, and can
# mutate into another character

class HackerGene(FloatGeneMax):
    
    mutProb = 0.1
    mutAmt = 0.2
    
    randMin = 0x0
    randMax = 0xff

    def __repr__(self):

        return str(chr(int(self.value)))

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
        chars = []
        for i in xrange(self.numgenes):

            #x = self[str(i)]
            #print "x=%s" % repr(x)
    
            c = chr(int(self[str(i)]))
            chars.append(c)

        return str(''.join(chars))

    # submit fitness calculation to worker process
    def prepare_fitness(self):
    	self.result = pool.apply_async(calculate_fitness, [str(self), self.numgenes])

    # block until result is ready, and retrieve it
    def fitness(self):
        return self.result.get()

class StringHackerPopulation(Population):

    initPopulation = 10
    species = StringHacker
    
    # cull to this many children after each generation
    childCull = 10
    
    # number of children to create after each generation
    childCount = 50
    
    mutants = 0.25

# start with a population of 10 random organisms
ph = StringHackerPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    while True:
        b = ph.best()
        print "generation %s: %s best=%s average=%s)" % (
            i, repr(b), b.get_fitness(), ph.fitness())
        if b.get_fitness() <= 0:
            print "cracked!"
            break
        i += 1
        ph.gen()


if __name__ == '__main__':
	# create a pool of 4 worker processes (has to be declared below 'if __name....')
	pool = Pool(processes=4)

	# execute main loop
	main()
