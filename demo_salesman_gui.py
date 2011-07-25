#! /usr/bin/env python

"""
Alternative implementation of travelling salesman problem
that displays solutions in a graphical window, using the
pyFLTK widgets (http://pyfltk.sourceforge.net)
"""

from fltk import *

import psyco

from threading import Lock
from thread import start_new_thread
from time import sleep

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

class TSPCanvas(Fl_Box):
    """
    Implements a custom version of box that draws the
    cities and journey
    """
    def __init__(self, gui, x, y, w, h):
        
        Fl_Box.__init__(self, x, y, w, h)
    
        # style the widget
        self.box(FL_DOWN_BOX)
        self.color(FL_WHITE)
    
        # save needed attribs
        self.gui = gui
        self.pop = gui.pop
    
        # best fitness so far
        self.bestSoFar = 10000000000000000000
    
    def draw(self):
        
        Fl_Box.draw(self)
        
        # now, show the cities and plot their journey
        self.showJourney()
    
    def showJourney(self, *ev):
        """
        Periodically display the best solution
        """
        self.gui.lock.acquire()
    
        # get the best
        best = self.gui.best
    
        fitness = self.gui.fitness
    
        # get the cities in order
        order = best.getCitiesInOrder()
    
        print "best=%s" % fitness
    
        # draw the city names
        fl_color(FL_BLACK)
        for city in order:
            fl_draw(city.name, int(city.x), int(city.y))    
    
        # choose a colour according to whether we're improving, staying the same,
        # or getting worse
        if fitness < self.bestSoFar:
            fl_color(FL_GREEN)
            self.bestSoFar = fitness
        elif fitness == self.bestSoFar:
            # equal best - plot in blue
            fl_color(FL_BLUE)
        else:
            # worse - plot in red
            fl_color(FL_RED)
    
        # now draw the journey
        for i in xrange(len(order)-1):
            city0, city1 = order[i:i+2]
            fl_line(int(city0.x), int(city0.y), int(city1.x), int(city1.y))
    
        # and don't forget the journey back home
        fl_line(int(order[0].x), int(order[0].y), int(order[-1].x), int(order[-1].y))
    
        self.gui.lock.release()
    

class TSPGui:
    """
    displays solutions graphically as we go
    """
    x = 100
    y = 100
    w = width + 10
    h = height + 50
    
    updatePeriod = 0.1
    
    def __init__(self):
        """
        Creates the graphical interface
        """
        # initial empty population
        self.pop = TSPSolutionPopulation()
        self.best = self.pop.best()
        self.updated = True
    
        # lock for drawing
        self.lock = Lock()
    
        # build the gui
        self.win = Fl_Window(
            self.x, self.y,
            self.w, self.h,
            "pygene Travelling Salesman solver")
    
        self.xdraw = 5
        self.ydraw = 5
        self.wdraw = self.w - 10
        self.hdraw = self.h - 90
    
        # bring in our custom canvas
        self.draw_canvas = TSPCanvas(
            self,
            self.xdraw, self.ydraw,
            self.wdraw, self.hdraw,
            )
    
        # add in some fields
        self.fld_numgen = Fl_Output(120, self.h-84, 50, 20, "Generations: ")
        self.fld_numimp = Fl_Output(320, self.h-84, 50, 20, "Improvements: ")
    
        # add a chart widget
        self.chart = Fl_Chart(5, self.h - 60, self.w - 10, 60)
        self.chart.color(FL_WHITE)
        self.chart.type(FL_LINE_CHART)
        self.win.end()
    
        # this flag allows for original generation to be displayed
        self.firsttime = True
        self.fitness = self.pop.best().fitness()
    
        self.ngens = 0
        self.nimp = 0
        self.bestFitness = 9999999999999999999
    
    def run(self):
        """
        Runs the population
        """
        # put up the window
        self.win.show()
    
        # start the background thread
        start_new_thread(self.threadUpdate, ())
    
        # schedule periodical updates
        Fl.add_idle(self.update)
    
        # hit the event loop
        Fl.run()
    
    def update(self, *args):
        """
        checks for updates
        """
        # and let the thread run
        sleep(0.0001)
    
        if self.updated:
    
            self.lock.acquire()
    
            # now draw the current state
            self.draw_canvas.redraw()    
            
            # plot progress on graph
            self.chart.add(self.fitness)
            
            # update status fields
            self.ngens += 1
            self.fld_numgen.value(str(self.ngens))
                
            if self.fitness < self.bestFitness:
                self.nimp += 1
                self.fld_numimp.value(str(self.nimp))
                self.bestFitness = self.fitness
    
            self.updated = False
            
            self.lock.release()
    
    def threadUpdate(self):
        """
        create and display generation
        """
        print "threadUpdate starting"
    
        while True:
    
            self.pop.gen()
    
            #print "generated"
    
            self.lock.acquire()
    
            self.best = self.pop.best()
            self.fitness = self.best.fitness()
            self.updated = True
    
            self.lock.release()
    

def main():

    # build and run the gui    
    gui = TSPGui()

    #psyco.full()

    gui.run()

if __name__ == '__main__':
    main()


