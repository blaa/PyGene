"""
Implements gametes, which are the result of
splitting an organism's genome in two, and are
used in the organism's sexual reproduction

In our model, I don't use any concept of a chromosome.
In biology, during a cell's interphase, there are
no chromosomes as such - the genetic material
is scattered chaotically throughout the cell nucleus.

Chromosomes (from my limited knowledge of biologi)
are mostly just a device used in cell division.
Since division of cells in this model isn't
constrained by the physical structure of the cell,
we shouldn't need a construct of chromosomes.

Gametes support the python '+' operator for sexual
reproduction. Adding two gametes together produces
a whole new Organism.
"""

from .xmlio import PGXmlMixin

class Gamete(PGXmlMixin):
    """
    Contains a set of genes.

    Two gametes can be added together to form a
    new organism
    """
    def __init__(self, orgclass, **genes):
        """
        Creates a new gamete from a set of genes
        """
        self.orgclass = orgclass
        self.genes = dict(genes)

    def __getitem__(self, name):
        """
        Fetch a single gene by name
        """
        return self.genes[name]

    def __add__(self, other):
        """
        Combines this gamete with another
        gamete to form an organism
        """
        return self.conceive(other)

    def conceive(self, other):
        """
        Returns a whole new Organism class
        from the combination of this gamete with another
        """
        if not isinstance(other, Gamete):
            raise Exception("Trying to mate a gamete with a non-gamete")

        return self.orgclass(self, other)
