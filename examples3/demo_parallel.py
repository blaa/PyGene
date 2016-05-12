#! /usr/bin/env python3
"""
Parallel fitness calculation demo based on demo_string_char.py.
Instead of threads this could be written using Celery.

Execution time of 11 generations with 10 threads: 2.9s
With 1 thread: 12.1s
(Keep in mind that fitness here simulates processing with sleep)
"""

from pygene3.gene import PrintableCharGene
from pygene3.gamete import Gamete
from pygene3.organism import Organism, MendelOrganism
from pygene3.population import Population

from time import sleep
import threading
import queue

# The same as in demo_string_char
teststr = "hackthis"
teststrlen = len(teststr)
geneNames = []
for i in range(len(teststr)):
    geneNames.append("%s" % i)

class HackerGene(PrintableCharGene):
    mutProb = 0.1
    mutAmt = 2

genome = {}
for i in range(len(teststr)):
    genome[str(i)] = HackerGene


##
# Worker thread / threads
##

threads_cnt = 15

# Global task queue
queue = queue.Queue()

# Worker thread
class Worker(threading.Thread):

    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue

    def fitness(self, string):
        diffs = 0
        guess = string
        # Simulate a lot of processing
        sleep(0.01)
        for i in range(len(teststr)):
            x0 = ord(teststr[i])
            x1 = ord(string[i])
            diffs += (2 * (x1 - x0)) ** 2
        return diffs

    def run(self):
        while True:
            task = self.queue.get()
            string, result_dict = task
            fitness = self.fitness(string)
            result_dict['fitness'] = fitness
            self.queue.task_done()

# Start threads
threads = []
for i in range(threads_cnt):
    worker = Worker(queue)
    worker.setDaemon(True)
    worker.start()
    threads.append(worker)


class StringHacker(MendelOrganism):
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a string
        """
        chars = []
        for k in range(self.numgenes):
            c = self[str(k)]
            chars.append(c)
        return ''.join(chars)

    def prepare_fitness(self):
        """
        Here we request fitness calculation.  Prepare place for result
        and put our string into a queue.  A running worker-thread will
        pick it up from the queue and calculate.
        """
        self.result_dict = {}
        queue.put((str(self), self.result_dict))

    def fitness(self):
        # Wait until all organisms in this population have it's fitness calculated
        # Could wait only for it's fitness but it's more complicated...
        queue.join()
        return self.result_dict['fitness']

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
        print("generation %s: %s best=%s average=%s)" % (
            i, str(b), b.get_fitness(), ph.fitness()))
        if b.get_fitness() <= 0:
            print("cracked!")
            break
        i += 1
        ph.gen()


if __name__ == '__main__':
    main()
