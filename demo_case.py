#! /usr/bin/env python
"""
demo that tries to show one reason why genetic algorithms are successful.

It tries to crack open a suitcase with a few locks, each with 1-5
digits.  Fitness function can only determine that the lock is open, not
the progress of opening the lock (how much the lock is opened)

Genetic algorithm can keep partial results (e.g. 1 lock open) while
trying other locks.

In general each lock represents a partial solution to the problem
described by organism.
"""

import random
from time import time
import sys

from pygene.gene import IntGene, IntGeneRandom, IntGeneExchange
from pygene.organism import Organism, GenomeSplitOrganism
from pygene.population import Population

# Parameters
locks = 8
digits_in_lock = 3

# Generate codes
codes = []
for lock in range(locks):
    code = [random.randint(0, 9) for i in range(digits_in_lock)]
    codes.append(code)


class DigitCodeGene(IntGeneRandom):
    """
    a gene which holds a single digit, and can mutate into another digit.
    Mutation randomizes gene for IntGeneRandom class.
    """
    mutProb = 0.3
    # mutAmt = 2
    randMin = 0
    randMax = 9

    def __repr__(self):
        return str(self.value)

# generate a genome, one gene for each digit in suitcase
genome = {}
for l in range(locks):
    for d in range(digits_in_lock):
        key = '%d_%d' % (l, d)
        genome[key] = DigitCodeGene

# an organism that evolves towards the required string

class CodeHacker(GenomeSplitOrganism):

    chromosome_intersections = 2
    genome = genome

    def get_code(self, lock):
        "Decode the chromosome (genome) into code for specific lock"
        code = []
        for d in range(digits_in_lock):
            key = '%d_%d' % (lock, d)
            code.append(self[key])
        return code

    def fitness(self):
        "calculate fitness - number of locks opened by genome."
        opened_locks = 0
        for l in range(locks):
            code = self.get_code(l)
            if code == codes[l]:
                opened_locks += 1

        # The lower the better
        # add 0 - 0.5 to force randomization of organisms selection
        fitness = float(locks - opened_locks) #+ random.uniform(0, 0.5)
        return fitness

    def __repr__(self):
        "Display result nicely"
        s='<CodeHacker '
        for l in range(locks):
            code = self.get_code(l)
            code_str = "".join(str(i) for i in code)
            if code == codes[l]:
                s += " %s " % code_str # space - opened lock
            else:
                s += "(%s)" % code_str # () - closed lock
        s = s.strip() + ">"
        return s


class CodeHackerPopulation(Population):
    "Configuration of population"
    species = CodeHacker

    initPopulation = 500

    # Tips: Leave a space for mutants to live.

    # cull to this many children after each generation
    childCull = 600

    # number of children to create after each generation
    childCount = 500

    # Add this many mutated organisms.
    mutants = 1.0

    # Mutate organisms after mating (better results with False)
    mutateAfterMating = False

    numNewOrganisms = 0

    # Add X best parents into new population
    # Good configuration should in general work without an incest.
    # Incest can cover up too much mutation
    incest = 2


def main():

    # Display codes
    print "CODES TO BREAK:",
    for code in codes:
        print "".join(str(digit) for digit in code),
    print

    # Display some statistics
    combinations = 10**(locks * digits_in_lock)
    operations = 10000 * 10**6
    print "Theoretical number of combinations", combinations
    print "Optimistic operations per second:", operations
    print "Direct bruteforce time:", 1.0* combinations / operations / 60.0/60/24, "days"

    # Hack the case.
    started = time()

    # Create population
    ph = CodeHackerPopulation()

    i = 0
    while True:
        b = ph.best()
        print "generation %02d: %s best=%s average=%s)" % (
            i, repr(b), b.get_fitness(), ph.fitness())

        if b.get_fitness() < 1:
            #for org in ph:
            #    print "  ", org

            print "cracked in ", i, "generations and ", time() - started, "seconds"
            break

        sys.stdout.flush()
        i += 1
        ph.gen()


if __name__ == '__main__':
    main()
