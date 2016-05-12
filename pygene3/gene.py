"""
Implements a collection of gene classes

Genes support the following python operators:
    - + - calculates the phenotype resulting from the
      combination of a pair of genes

These genes work via classical Mendelian genetics
"""

import sys
from random import random, randint, uniform, choice
from math import sqrt

from .xmlio import PGXmlMixin

class BaseGene(PGXmlMixin):
    """
    Base class from which all the gene classes are derived.

    You cannot use this class directly, because there are
    some methods that must be overridden.
    """
    # each gene should have an object in
    # which its genotype should be stored
    value = None

    # probability of a mutation occurring
    mutProb = 0.01

    # List of acceptable fields for the factory
    fields = ["value", "mutProb"]

    def __init__(self):

        # if value is not provided, it will be
        # randomly generated
        if self.__class__.value == None:
            self.value = self.randomValue()
        else:
            self.value = self.__class__.value


    def copy(self):
        """
        returns clone of this gene
        """
        cls = self.__class__()
        cls.value = self.value
        return cls


    def __add__(self, other):
        """
        Combines two genes in a gene pair, to produce an effect

        This is used to determine the gene's phenotype

        This default method computes the arithmetic mean
        of the two genes.

        Override as needed

        Must be overridden
        """
        raise Exception("Method __add__ must be overridden")

    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.value)

    # def __cmp__(this, other):
    #     return cmp(this.value, other.value)
    #
    def maybeMutate(self):
        if random() < self.mutProb:
            self.mutate()

    def mutate(self):
        """
        Perform a mutation on the gene

        You MUST override this in subclasses
        """
        raise Exception("method 'mutate' not implemented")

    def randomValue(self):
        """
        Generates a plausible random value
        for this gene.

        Must be overridden
        """
        raise Exception("Method 'randomValue' not implemented")

    def xmlDumpSelf(self, doc, parent):
        """
        dump out this gene into parent tag
        """
        genetag = doc.createElement("gene")
        parent.appendChild(genetag)

        self.xmlDumpClass(genetag)

        self.xmlDumpAttribs(genetag)

        # now dump out the value into a text tag
        ttag = doc.createTextNode(str(self.value))

        # and add it to self tag
        genetag.appendChild(ttag)

    def xmlDumpAttribs(self, tag):
        """
        sets attributes of tag
        """
        tag.setAttribute("mutProb", str(self.mutProb))


class ComplexGene(BaseGene):
    """
    A gene whose value is a complex point number
    """
    # amount by which to mutate, will change value
    # by up to +/- this amount
    mutAmtReal = 0.1
    mutAmtImag = 0.1

    # used for random gene creation
    # override in subclasses
    randMin = -1.0
    randMax = 1.0

    # Acceptable fields for factory
    fields = ["value", "mutProb", "mutAmtReal", "mutAmtImag",
              "randMin", "randMax"]

    def __add__(self, other):
        """
        Combines two genes in a gene pair, to produce an effect

        This is used to determine the gene's phenotype

        This class computes the arithmetic mean
        of the two genes' values, so is akin to incomplete
        dominance.

        Override if desired
        """
        return (self.value + other.value) / 2.0
        #return abs(complex(self.value.real, other.value.imag))


    def mutate(self):
        """
        Mutate this gene's value by a random amount
        within the range +/- self.mutAmt

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value += complex(
            uniform(-self.mutAmtReal, self.mutAmtReal),
            uniform(-self.mutAmtImag, self.mutAmtImag)
            )

        # if the gene has wandered outside the alphabet,
        # rein it back in
        real = self.value.real
        imag = self.value.imag

        if real < self.randMin:
            real = self.randMin
        elif real > self.randMax:
            real = self.randMax

        if imag < self.randMin:
            imag = self.randMin
        elif imag > self.randMax:
            imag = self.randMax

        self.value = complex(real, imag)

    def randomValue(self):
        """
        Generates a plausible random value
        for this gene.

        Override as needed
        """
        min = self.randMin
        range = self.randMax - min

        real = uniform(self.randMin, self.randMax)
        imag = uniform(self.randMin, self.randMax)

        return complex(real, imag)


class FloatGene(BaseGene):
    """
    A gene whose value is a floating point number

    Class variables to override:

        - mutAmt - default 0.1 - amount by which to mutate.
          The gene will will move this proportion towards
          its permissible extreme values

        - randMin - default -1.0 - minimum possible value
          for this gene. Mutation will never allow the gene's
          value to be less than this

        - randMax - default 1.0 - maximum possible value
          for this gene. Mutation will never allow the gene's
          value to be greater than this
    """
    # amount by which to mutate, will change value
    # by up to +/- this amount
    mutAmt = 0.1

    # used for random gene creation
    # override in subclasses
    randMin = -1.0
    randMax = 1.0

    # Acceptable fields for factory
    fields = ["value", "mutProb", "mutAmt", "randMin", "randMax"]

    def __add__(self, other):
        """
        Combines two genes in a gene pair, to produce an effect

        This is used to determine the gene's phenotype

        This class computes the arithmetic mean
        of the two genes' values, so is akin to incomplete
        dominance.

        Override if desired
        """
        return (self.value + other.value) / 2.0

    def mutate(self):
        """
        Mutate this gene's value by a random amount
        within the range, which is determined by
        multiplying self.mutAmt by the distance of the
        gene's current value from either endpoint of legal values

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        if random() < 0.5:
            # mutate downwards
            self.value -= uniform(0, self.mutAmt * (self.value-self.randMin))
        else:
            # mutate upwards:
            self.value += uniform(0, self.mutAmt * (self.randMax-self.value))


    def randomValue(self):
        """
        Generates a plausible random value
        for this gene.

        Override as needed
        """
        return uniform(self.randMin, self.randMax)



class FloatGeneRandom(FloatGene):
    """
    Variant of FloatGene where mutation always randomises the value
    """
    def mutate(self):
        """
        Randomise the gene

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value = self.randomValue()


class FloatGeneRandRange(FloatGene):
    def __add__(self, other):
        """
        A variation of float gene where during the mixing a random value
        from within range created by the two genes is selected.
        """
        start = min([self.value, other.value])
        end = max([self.value, other.value])
        return uniform(start, end)


class FloatGeneMax(FloatGene):
    """
    phenotype of this gene is the greater of the values
    in the gene pair
    """
    def __add__(self, other):
        """
        produces phenotype of gene pair, as the greater of this
        and the other gene's values
        """
        return max(self.value, other.value)

class FloatGeneExchange(FloatGene):
    """
    phenotype of this gene is the random of the values
    in the gene pair
    """
    def __add__(self, other):
        """
        produces phenotype of gene pair, as the random of this
        and the other gene's values
        """
        return choice([self.value, other.value])


class IntGene(BaseGene):
    """
    Implements a gene whose values are ints,
    constrained within the randMin,randMax range
    """
    # minimum possible value for gene
    # override in subclasses as needed
    randMin = -sys.maxsize

    # maximum possible value for gene
    # override in subclasses as needed
    randMax = sys.maxsize + 1

    # maximum amount by which gene can mutate
    mutAmt = 1

    # Acceptable fields for factory
    fields = ["value", "mutProb", "mutAmt", "randMin", "randMax"]

    def mutate(self):
        """
        perform gene mutation

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value += randint(-self.mutAmt, self.mutAmt)

        # if the gene has wandered outside the alphabet,
        # rein it back in
        if self.value < self.randMin:
            self.value = self.randMin
        elif self.value > self.randMax:
            self.value = self.randMax

    def randomValue(self):
        """
        return a legal random value for this gene
        which is in the range [self.randMin, self.randMax]
        """
        return randint(self.randMin, self.randMax)

    def __add__(self, other):
        """
        produces the phenotype resulting from combining
        this gene with another gene in the pair

        returns an int value, based on a formula of higher
        numbers dominating
        """
        return max(self.value, other.value)


class IntGeneRandom(IntGene):
    """
    Variant of IntGene where mutation always randomises the value
    """
    def mutate(self):
        """
        Randomise the gene

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value = self.randomValue()


class IntGeneExchange(IntGene):
    def __add__(self, other):
        """
        A variation of int gene where during the mixing a
        random gene is selected instead of max.
        """
        return choice([self.value, other.value])


class IntGeneAverage(IntGene):
    def __add__(self, other):
        """
        A variation of int gene where during the mixing a
        average of two genes is selected.
        """
        return (self.value + other.value) / 2


class IntGeneRandRange(IntGene):
    def __add__(self, other):
        """
        A variation of int gene where during the mixing a random value
        from within range created by the two genes is selected.
        """
        start = min([self.value, other.value])
        end = max([self.value, other.value])
        return randint(start, end)


class CharGene(BaseGene):
    """
    Gene that holds a single ASCII character,
    as a 1-byte string
    """
    # minimum possible value for gene
    # override in subclasses as needed
    randMin = '\x00'

    # maximum possible value for gene
    # override in subclasses as needed
    randMax = '\xff'

    def __repr__(self):
        """
        Returns safely printable value
        """
        return self.value

    def mutate(self):
        """
        perform gene mutation

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value = ord(self.value) + randint(-int(self.mutAmt), int(self.mutAmt))

        # if the gene has wandered outside the alphabet,
        # rein it back in
        if self.value < ord(self.randMin):
            self.value = self.randMin
        elif self.value > ord(self.randMax):
            self.value = self.randMax
        else:
            self.value = chr(self.value)

    def randomValue(self):
        """
        return a legal random value for this gene
        which is in the range [self.randMin, self.randMax]
        """
        return chr(randint(ord(self.randMin), ord(self.randMax)))

    def __add__(self, other):
        """
        produces the phenotype resulting from combining
        this gene with another gene in the pair

        returns an int value, based on a formula of higher
        numbers dominating
        """
        return max(self.value, other.value)


class CharGeneExchange(CharGene):
    def __add__(self, other):
        """
        A variation of char gene where during the mixing a
        average of two genes is selected.
        """
        return choice([self.value, other.value])


class AsciiCharGene(CharGene):
    """
    Specialisation of CharGene that can only
    hold chars in the legal ASCII range

    OBSOLETE/REMOVE: Exactly the same as chargene
    """
    # minimum possible value for gene
    # override in subclasses as needed
    randMin = chr(0)

    # maximum possible value for gene
    # override in subclasses as needed
    randMax = chr(255)

    def __repr__(self):
        """
        still need to str() the value, since the range
        includes control chars
        """
        return self.value

class PrintableCharGene(AsciiCharGene):
    """
    Specialisation of AsciiCharGene that can only
    hold printable chars
    """
    # minimum possible value for gene
    # override in subclasses as needed
    randMin = ' '

    # maximum possible value for gene
    # override in subclasses as needed
    randMax = chr(127)

    def __repr__(self):
        """
        don't need to str() the char, since
        it's already printable
        """
        return self.value

class DiscreteGene(BaseGene):
    """
    Gene type with a fixed set of possible values, typically
    strings

    Mutation behaviour is that the gene's value may
    spontaneously change into one of its alleles
    """
    # this is the set of possible values
    # override in subclasses
    alleles = []

    # the dominant allele - leave as None
    # if gene has incomplete dominance
    dominant = None

    # the co-dominant alleles - leave empty
    # if gene has simple dominance
    codominant = []

    # the recessive allele - leave as None if there's a dominant
    recessive = None

    def mutate(self):
        """
        Change the gene's value into any of the possible alleles,
        subject to mutation probability 'self.mutProb'

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value = self.randomValue()

    def randomValue(self):
        """
        returns a random allele
        """
        return choice(self.alleles)

    def __add__(self, other):
        """
        determines the phenotype, subject to dominance properties

        returns a tuple of effects
        """
        # got simple dominance?
        if self.dominant in (self.value, other.value):
            # yes
            return (self.dominant,)

        # got incomplete dominance?
        elif self.codominant:
            phenotype = []
            for val in self.value, other.value:
                if val in self.codominant and val not in phenotype:
                    phenotype.append(val)

            # apply recessive, if one exists and no codominant genes present
            if not phenotype:
                if self.recessive:
                    phenotype.append(self.recessive)

            # done
            return tuple(phenotype)

        # got recessive?
        elif self.recessive:
            return (self.recessive,)

        # nothing else
        return ()

class BitGene(BaseGene):
    """
    Implements a single-bit gene
    """
    def __add__(self, other):
        """
        Produces the 'phenotype' as xor of gene pair values
        """
        raise Exception("__add__ method not implemented")



    def mutate(self):
        """
        mutates this gene, toggling the bit
        probabilistically

        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value ^= 1

    def randomValue(self):
        """
        Returns a legal random (boolean) value
        """
        return choice([0, 1])


class AndBitGene(BitGene):
    """
    Implements a single-bit gene, whose
    phenotype is the AND of each gene in the pair
    """
    def __add__(self, other):
        """
        Produces the 'phenotype' as xor of gene pair values
        """
        return self.value and other.value


class OrBitGene(BitGene):
    """
    Implements a single-bit gene, whose
    phenotype is the OR of each gene in the pair
    """
    def __add__(self, other):
        """
        Produces the 'phenotype' as xor of gene pair values
        """
        return self.value or other.value



class XorBitGene(BitGene):
    """
    Implements a single-bit gene, whose
    phenotype is the exclusive-or of each gene in the pair
    """
    def __add__(self, other):
        """
        Produces the 'phenotype' as xor of gene pair values
        """
        return self.value ^ other.value

##
# Gene factories
# Necessary for config loading.
##

def _new_factory(cls):
    "Creates gene factories"
    def factory(name, **kw):
        "Gene factory"
        for key in kw.keys():
            if key not in cls.fields:
                raise Exception("Tried to create a gene with an invalid field: " + key)
        # return new.classobj(name, (cls,), kw)
        return type(name, (cls,), kw)
    return factory

ComplexGeneFactory  = _new_factory(ComplexGene)
DiscreteGeneFactory = _new_factory(DiscreteGene)

FloatGeneFactory         = _new_factory(FloatGene)
FloatGeneMaxFactory      = _new_factory(FloatGeneMax)
FloatGeneRandomFactory   = _new_factory(FloatGeneRandom)
FloatGeneRandRangeFactory = _new_factory(FloatGeneRandRange)
FloatGeneExchangeFactory = _new_factory(FloatGeneExchange)

IntGeneFactory          = _new_factory(IntGene)
IntGeneExchangeFactory  = _new_factory(IntGeneExchange)
IntGeneAverageFactory   = _new_factory(IntGeneAverage)
IntGeneRandRangeFactory = _new_factory(IntGeneRandRange)

CharGeneFactory          = _new_factory(CharGene)
AsciiCharGeneFactory     = _new_factory(AsciiCharGene)
PrintableCharGeneFactory = _new_factory(PrintableCharGene)


# utility functions

def rndPair(geneclass):
    """
    Returns a gene pair, comprising two random
    instances of the given gene class
    """
    return (geneclass(), geneclass())
