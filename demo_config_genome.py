#! /usr/bin/env python

"""
Example build on the demo_quadratic.py - understand that one first!

Program reads it's genome configuration from a config file (quadratic.ini)

Example config file:
[x1]
type = float
randMin = -100.0
randMax = 100.0
mutProb = 0.1
mutAmt = 0.1

[x2]
type = int
randMin = -50
randMax = 50
mutProb = 0.2
mutAmt = 1

[x3]
alias = x2

[x4]
type = float
value = 5.4

One section per gene.
'type' is necessary - other fields depends on the selected type
possible types (for current list see pygene/config.py):
int, int_exchange, float, float_exchange, float_random, float_max, complex
You can create a genes from previously specified ones using 'alias' field.

There might be available a special section 'population' with parameters
for population. It's never treated as a gene.
"""

from pygene.gene import FloatGene, FloatGeneMax
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from pygene.config import ConfigLoader

# parameters for quadratic equation
# has roots 3 and 5
if 1:
    a = 2
    b = -16
    c = 30
else:
    # this alternate set has only 1 root, x=4
    a = 2.0
    b = 3.0
    c = -44.0

def quad(x):
    return a * x ** 2 + b * x + c

loader = ConfigLoader(filename="quadratic.ini", require_genes=['x1', 'x2'])

class QuadraticSolver(Organism):
    """
    Implements the organism which tries
    to solve a quadratic equation
    """
    genome = loader.load_genome()

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


QPopulation = loader.load_population("QPopulation", species=QuadraticSolver)

"""
class QPopulation(Population):

    species = QuadraticSolver
    initPopulation = 20

    # cull to this many children after each generation
    childCull = 20

    # number of children to create after each generation
    childCount = 50

    mutants = 0.5

# create a new population, with randomly created members
"""

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
            print "fitness=%f avg=%f x1=%f x2=%f" % (best.get_fitness(), pop.fitness(),
                                                     best['x1'], best['x2'])
            if best.get_fitness() < 0.6:
                break

    except KeyboardInterrupt:
        pass
    print "Executed", generations, "generations"


if __name__ == '__main__':
    main()


