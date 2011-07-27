"""
Implements a collection of gene classes

Genes support the following python operators:
    - + - calculates the phenotype resulting from the
      combination of a pair of genes

These genes work via classical Mendelian genetics
"""

import sys, new
from random import randrange, random, uniform
from math import sqrt

from xmlio import PGXmlMixin

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
    
    def __init__(self, value=None):
    
        # if value is not provided, it will be
        # randomly generated
        if value == None:
            value = self.randomValue()
    
        self.value = value
    
    def copy(self):
        """
        returns clone of this gene
        """
        return self.__class__(self.value)
    
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
    
    
    def copy(self):
        """
        Produce an exact copy of this gene
    
        Shouldn't need to be overridden
        """
        return self.__class__(self.value)
    
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
    
    def __add__(self, other):
        """
        Combines two genes in a gene pair, to produce an effect
    
        This is used to determine the gene's phenotype
    
        This class computes the arithmetic mean
        of the two genes' values, so is akin to incomplete
        dominance.
    
        Override if desired
        """
        return (self.value + other.value) / 2
        #return abs(complex(self.value.real, other.value.imag))
    
    
    def mutate(self):
        """
        Mutate this gene's value by a random amount
        within the range +/- self.mutAmt
    
        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value += complex(
            random()*self.mutAmtReal*2 - self.mutAmtReal,
            random()*self.mutAmtImag*2 - self.mutAmtImag
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
    
        real = random() * range + min
        imag = random() * range + min
    
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
    
    def __add__(self, other):
        """
        Combines two genes in a gene pair, to produce an effect
    
        This is used to determine the gene's phenotype
    
        This class computes the arithmetic mean
        of the two genes' values, so is akin to incomplete
        dominance.
    
        Override if desired
        """
        return (self.value + other.value) / 2
    
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
        min = self.randMin
        range = self.randMax - min
    
        return random() * range + min
    

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
    

class IntGene(BaseGene):
    """
    Implements a gene whose values are ints,
    constrained within the randMin,randMax range
    """
    # minimum possible value for gene
    # override in subclasses as needed
    randMin = -sys.maxint
    
    # maximum possible value for gene
    # override in subclasses as needed
    randMax = sys.maxint + 1
    
    # maximum amount by which gene can mutate
    mutAmt = 1
    
    def mutate(self):
        """
        perform gene mutation
    
        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value += randrange(-self.mutAmt, self.mutAmt + 1)
    
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
        return randrange(self.randMin, self.randMax+1)
    
    def __add__(self, other):
        """
        produces the phenotype resulting from combining
        this gene with another gene in the pair
        
        returns an int value, based on a formula of higher
        numbers dominating
        """
        return max(self.value, other.value)
    


class CharGene(BaseGene):
    """
    Gene that holds a single ASCII character,
    as a 1-byte string
    """
    # minimum possible value for gene
    # override in subclasses as needed
    randMin = chr(0)
    
    # maximum possible value for gene
    # override in subclasses as needed
    randMax = chr(255)
    
    def __repr__(self):
        """
        Returns safely printable value
        """
        return str(self.value)
    
    def mutate(self):
        """
        perform gene mutation
    
        perform mutation IN-PLACE, ie don't return mutated copy
        """
        self.value = chr(ord(self.value) + randrange(-self.mutAmt, self.mutAmt + 1))
    
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
        return chr(randrange(ord(self.randMin), ord(self.randMax)+1))
    
    def __add__(self, other):
        """
        produces the phenotype resulting from combining
        this gene with another gene in the pair
        
        returns an int value, based on a formula of higher
        numbers dominating
        """
        return max(self.value, other.value)
    

class AsciiCharGene(CharGene):
    """
    Specialisation of CharGene that can only
    hold chars in the legal ASCII range
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
        if random() < 0.5:
            return 1
        else:
            return 0
    


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
    


def FloatGeneFactory(name, **kw):
    """
    Returns a new class object, being a subclass
    of FloatGene, with class attributes
    set from keywords
    """
    return new.classobj(name, (FloatGene,), kw)


def IntGeneFactory(name, **kw):
    """
    Returns a new class object, being a subclass
    of IntGene, with class attributes
    set from keywords
    """
    return new.classobj(name, (IntGene,), kw)


def CharGeneFactory(name, **kw):
    """
    Returns a new class object, being a subclass
    of CharGene, with class attributes
    set from keywords
    """
    return new.classobj(name, (CharGene,), kw)


def AsciiCharGeneFactory(name, **kw):
    """
    Returns a new class object, being a subclass
    of AsciiCharGene, with class attributes
    set from keywords
    """
    return new.classobj(name, (AsciiCharGene,), kw)

def PrintableCharGeneFactory(name, **kw):
    """
    Returns a new class object, being a subclass
    of PrintableGene, with class attributes
    set from keywords
    """
    return new.classobj(name, (AsciiCharGene,), kw)

def DiscreteGeneFactory(name, **kw):
    """
    Returns a new class object, being a subclass
    of DiscreteGene, with class attributes
    set from keywords
    """
    return new.classobj(name, (DiscreteGene,), kw)

# utility functions

def rndPair(geneclass):
    """
    Returns a gene pair, comprising two random
    instances of the given gene class
    """
    return (geneclass(), geneclass())



