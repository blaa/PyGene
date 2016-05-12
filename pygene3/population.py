"""
pygene/population.py - Represents a population of organisms
"""

import random
from random import randrange, choice
from math import sqrt

from .organism import Organism, BaseOrganism

from .xmlio import PGXmlMixin

class Population(PGXmlMixin):
    """
    Represents a population of organisms

    You might want to subclass this

    Overridable class variables:

        - species - Organism class or subclass, being the 'species'
          of organism comprising this population

        - initPopulation - size of population to randomly create
          if no organisms are passed in to constructor

        - childCull - cull to this many children after each generation

        - childCount - number of children to create after each generation

        - incest - max number of best parents to mix amongst the
          kids for next generation, default 10

        - numNewOrganisms - number of random new orgs to add each
          generation, default 0

        - initPopulation - initial population size, default 10

        - mutants - default 0.1 - if mutateAfterMating is False,
          then this sets the percentage of mutated versions of
          children to add to the child population; children to mutate
          are selected based on fitness

    Supports the following python operators:

        - + - produces a new population instances, whose members are
          an aggregate of the members of the values being added

        - [] - int subscript - returns the ith fittest member

    """
    # cull to this many children after each generation
    childCull = 20

    # number of children to create after each generation
    childCount = 100

    # max number of best parents to mix amongst the kids for
    # next generation
    incest = 10

    # parameters governing addition of random new organisms
    numNewOrganisms = 0 # number of new orgs to add each generation

    # set to initial population size
    initPopulation = 10

    # set to species of organism
    species = Organism

    # mutate this proportion of organisms
    mutants = 0.1

    # set this to true to mutate all progeny
    mutateAfterMating = True

    def __init__(self, *items, **kw):
        """
        Create a population with zero or more members

        Arguments:
            - any number of arguments and/or sequences of args,
              where each arg is an instance of this population's
              species. If no arguments are given, organisms are
              randomly created and added automatically, according
              to self.initPopulation and self.species

        Keywords:
            - init - size of initial population to randomly create.
              Ignored if 1 or more constructor arguments are given.
              if not given, value comes from self.initPopulation
            - species - species of organism to create and add. If not
              given, value comes from self.species
        """
        self.organisms = []

        if 'species' in kw:
            species = self.species = kw['species']
        else:
            species = self.species

        if 'init' in kw:
            init = self.initPopulation = kw['init']
        else:
            init = self.initPopulation

        if not items:
            for i in range(init):
                self.add(species())

    def add(self, *args):
        """
        Add an organism, or a population of organisms,
        to this population

        You can also pass lists or tuples of organisms and/or
        populations, to any level of nesting
        """
        for arg in args:
            if isinstance(arg, tuple) or isinstance(arg, list):
                # got a list of things, add them one by one
                self.add(*arg)

            if isinstance(arg, BaseOrganism):
                # add single organism
                self.organisms.append(arg)

            elif isinstance(arg, Population):
                # absorb entire population
                self.organisms.extend(arg)
            else:
                raise TypeError(
                    "can only add Organism or Population objects")

        self.sorted = False

    def __add__(self, other):
        """
        Produce a whole new population consisting of an aggregate
        of this population and the other population's members
        """
        return Population(self, other)

    def getRandom(self, items=None):
        """
        randomly select one of the given items
        (or one of this population's members, if items
        not given).

        Favours fitter members
        """
        if items == None:
            items = self.organisms

        nitems = len(items)
        n2items = nitems * nitems

        # pick one parent randomly, favouring fittest
        idx = int(sqrt(randrange(n2items)))
        return items[nitems - idx - 1]

    def gen(self, nfittest=None, nchildren=None):
        """
        Executes a generation of the population.

        This consists of:
            - producing 'nchildren' children, parented by members
              randomly selected with preference for the fittest
            - culling the children to the fittest 'nfittest' members
            - killing off the parents, and replacing them with the
              children

        Read the source code to study the method of probabilistic
        selection.
        """
        if not nfittest:
            nfittest = self.childCull
        if not nchildren:
            nchildren = self.childCount

        children = []

        # add in some new random organisms, if required
        if self.numNewOrganisms:
            #print "adding %d new organisms" % self.numNewOrganisms
            for i in range(self.numNewOrganisms):
                self.add(self.species())


        # we use square root to skew the selection probability to
        # the fittest

        # get in order, if not already
        self.sort()
        nadults = len(self)

        n2adults = nadults * nadults

        # statistical survey
        #stats = {}
        #for j in xrange(nchildren):
        #    stats[j] = 0

        # wild orgy, have lots of children
        nchildren = 1 if nchildren == 1 else nchildren // 2
        for i in range(nchildren):
            # pick one parent randomly, favouring fittest
            idx1 = idx2 = int(sqrt(randrange(n2adults)))
            parent1 = self[-idx1]

            # pick another parent, distinct from the first parent
            while idx2 == idx1:
                idx2 = int(sqrt(randrange(n2adults)))
            parent2 = self[-idx2]

            #print "picking items %s, %s of %s" % (
            #    nadults - idx1 - 1,
            #    nadults - idx2 - 1,
            #    nadults)

            #stats[nadults - idx1 - 1] += 1
            #stats[nadults - idx2 - 1] += 1

            # get it on, and store the child
            child1, child2 = parent1 + parent2

            # mutate kids if required
            if self.mutateAfterMating:
                child1 = child1.mutate()
                child2 = child2.mutate()

            children.extend([child1, child2])

        # if incestuous, add in best adults
        if self.incest:
            children.extend(self[:self.incest])

        for child in children:
            child.prepare_fitness()

        children.sort()

        # and add in some mutants, a proportion of the children
        # with a bias toward the fittest
        if not self.mutateAfterMating:
            nchildren = len(children)
            n2children = nchildren * nchildren
            mutants = []
            numMutants = int(nchildren * self.mutants)

            # children[0] - fittest
            # children[-1] - worse fitness
            if 0:
                for i in range(numMutants):
                    # pick one parent randomly, favouring fittest
                    idx = int(sqrt(randrange(n2children)))

                    child = children[-idx]
                    mutant = child.mutate()
                    mutant.prepare_fitness()
                    mutants.append(mutant)
            else:
                for i in range(numMutants):
                    mutant = children[i].mutate()
                    mutant.prepare_fitness()
                    mutants.append(mutant)

            children.extend(mutants)
            children.sort()
        #print "added %s mutants" % numMutants
        # sort the children by fitness
        # take the best 'nfittest', make them the new population
        self.organisms[:] = children[:nfittest]

        self.sorted = True

        #return stats
    def __repr__(self):
        """
        crude human-readable dump of population's members
        """
        return str(self.organisms)

    def __getitem__(self, n):
        """
        Return the nth member of this population,
        which we guarantee to be sorted in order from
        fittest first
        """
        self.sort()
        return self.organisms[n]

    def __len__(self):
        """
        return the number of organisms in this population
        """
        return len(self.organisms)

    def fitness(self):
        """
        returns the average fitness value for the population
        """
        fitnesses = [org.get_fitness() for org in self.organisms]

        return sum(fitnesses)/len(fitnesses)

    def best(self):
        """
        returns the fittest member of the population
        """
        self.sort()
        return self[0]

    def sort(self):
        """
        Sorts this population in order of fitness, with
        the fittest first.

        We keep track of whether this population is in order
        of fitness, so we don't perform unnecessary and
        costly sorting
        """
        if not self.sorted:
            for organism in self.organisms:
                organism.prepare_fitness()
            self.organisms.sort()
            self.sorted = True

    # methods for loading/saving to/from xml

    def xmlDumpSelf(self, doc, parent):
        """
        Writes out the contents of this population
        into the xml tree
        """
        # create population element
        pop = doc.createElement("population")
        parent.appendChild(pop)

        # set population class details
        pop.setAttribute("class", self.__class__.__name__)
        pop.setAttribute("module", self.__class__.__module__)

        # set population params as xml tag attributes
        pop.setAttribute("childCull", str(self.childCull))
        pop.setAttribute("childCount", str(self.childCount))

        # dump out organisms
        for org in self.organisms:
            org.xmlDumpSelf(doc, pop)
