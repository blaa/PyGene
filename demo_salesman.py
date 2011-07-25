#! /usr/bin/env python
"""
Implementation of the travelling salesman problem (TSP)
"""

from random import random
from math import sqrt

from pygene.gene import FloatGene, FloatGeneMax, FloatGeneRandom
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population

width = 500
height = 500

# set the number of cities in our tour
numCities = 30

# tweak these to gen varying levels of performance

geneRandMin = 0.0
geneRandMax = 10.0
geneMutProb = 0.1
geneMutAmt = .5         # only if not using FloatGeneRandom

popInitSize = 10
popChildCull = 20
popChildCount = 100
popIncest = 10           # number of best parents to add to children
popNumMutants = 0.7     # proportion of mutants each generation
popNumRandomOrganisms = 0  # number of random organisms per generation

mutateOneOnly = False

BaseGeneClass = FloatGene
BaseGeneClass = FloatGeneMax
#BaseGeneClass = FloatGeneRandom

OrganismClass = MendelOrganism
#OrganismClass = Organism

mutateAfterMating = True

crossoverRate = 0.05

class CityPriorityGene(BaseGeneClass):
    """
    Each gene in the TSP solver represents the priority
    of travel to the corresponding city
    """
    randMin = geneRandMin
    randMax = geneRandMax
    
    mutProb = geneMutProb
    mutAmt = geneMutAmt

class City:
    """
    represents a city by name and location,
    and calculates distance from another city
    """
    def __init__(self, name, x=None, y=None):
        """
        Create city by name, randomly generating
        its co-ordinates if none given
        """
        self.name = name

        # constrain city coords so they're no closer than 50 pixels
        # to any edge, so the city names show up ok in the gui version        
        if x == None:
            x = random() * (width - 100) + 50
        if y == None:
            y = random() * (height - 100) + 50
            
        self.x = x
        self.y = y
    
    def __sub__(self, other):
        """
        compute distance between this and another city
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)

    def __repr__(self):
        return "<City %s at (%.2f, %.2f)>" % (self.name, self.x, self.y)

if 0:
    cities = [
        City("Sydney"),
        City("Melbourne"),
        City("Brisbane"),
        City("Armidale"),
        City("Woolongong"),
        City("Newcastle"),
        City("Cairns"),
        City("Darwin"),
        City("Perth"),
        City("Townsville"),
        City("Bourke"),
        City("Gosford"),
        City("Coffs Harbour"),
        City("Tamworth"),
        ]

if 1:
    cities = []
    for i in xrange(numCities):
        cities.append(City("%s" % i))

cityNames = [city.name for city in cities]

cityCount = len(cities)

cityDict = {}
for city in cities:
    cityDict[city.name] = city

priInterval = (geneRandMax - geneRandMin) / cityCount
priNormal = []
for i in xrange(cityCount):
    priNormal.append(((i+0.25)*priInterval, (i+0.75)*priInterval))

genome = {}
for name in cityNames:
    genome[name] = CityPriorityGene

class TSPSolution(OrganismClass):
    """
    Organism which represents a solution to
    the TSP
    """
    genome = genome
    
    mutateOneOnly = mutateOneOnly

    crossoverRate = crossoverRate

    numMutants = 0.3

    def fitness(self):
        """
        return the journey distance
        """
        distance = 0.0

        # get the city objects in order of priority
        sortedCities = self.getCitiesInOrder()

        # start at first city, compute distances to last
        for i in xrange(cityCount - 1):
            distance += sortedCities[i] - sortedCities[i+1]
        
        # and add in the return trip
        distance += sortedCities[0] - sortedCities[-1]

        # done
        return distance

    def getCitiesInOrder(self):
        """
        return a list of the cities, sorted in order
        of the respective priority values in this
        organism's genotype
        """
        # create a sortable list of (priority, city) tuples
        # (note that 'self[name]' extracts the city gene's phenotype,
        # being the 'priority' of that city
        sorter = [(self[name], cityDict[name]) for name in cityNames]

        # now sort them, the priority elem will determine order
        sorter.sort()
        
        # now extract the city objects
        sortedCities = [tup[1] for tup in sorter]

        # done
        return sortedCities

    def normalise(self):
        """
        modifies the genes to a reasonably even spacing
        """
        genes = self.genes
        for i in xrange(2):
            sorter = [(genes[name][i], name) for name in cityNames]
            sorter.sort()
            sortedGenes = [tup[1] for tup in sorter]
            
            


class TSPSolutionPopulation(Population):

    initPopulation = popInitSize
    species = TSPSolution
    
    # cull to this many children after each generation
    childCull = popChildCull
    
    # number of children to create after each generation
    childCount = popChildCount
    
    # number of best parents to add in with next gen
    incest = popIncest

    mutants = popNumMutants

    numNewOrganisms = popNumRandomOrganisms

    mutateAfterMating = mutateAfterMating

def main():
    
    # create initial population
    pop = TSPSolutionPopulation()
    
    # now repeatedly calculate generations
    i = 0

    try:
        while True:
            print "gen=%s best=%s avg=%s" % (i, pop.best().get_fitness(), pop.fitness())
            pop.gen()
            i += 1
    except KeyboardInterrupt:
        pass
        
    
    # get the best solution
    solution = pop.best()
    
    # and print out the itinerary
    sortedCities = solution.getCitiesInOrder()
    print "Best solution: total distance %04.2f:" % solution.fitness()
    for city in sortedCities:
        print "  x=%03.2f y=%03.2f %s" % (city.x, city.y, city.name)

if __name__ == '__main__':
    main()


