"""
Parse genome from config file.
Only int and float genes are supported currently.

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

One section per gene.
'type' is necessary - other fields depends on the selected type
"""

import ConfigParser
from ConfigParser import NoOptionError
# TODO Add other here...
from pygene.gene import ComplexGeneFactory
from pygene.gene import IntGeneFactory, IntGeneExchangeFactory
from pygene.gene import FloatGeneFactory, FloatGeneRandomFactory, FloatGeneMaxFactory
from pygene.gene import FloatGeneExchangeFactory


class LoaderError(Exception):
    pass

# Casts to int and float (TODO: Add other)
def _intcast(section, key, value):
    "Parse string into int or None with correct exceptions"
    if not value: # '' and None are coerced to None
        return None

    try:
        return int(value)
    except ValueError:
        raise LoaderError("Invalid integer value '%s' in position %s / %s." % (
                          value, section, key))

def _floatcast(section, key, value):
    "Parse string into float or None with correct exceptions"
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        raise LoaderError("Invalid floating-point value '%s' in position %s / %s." % (
                          value, section, key))

class ConfigLoader(object):

    def __init__(self, filename=None, require_genes=[], genes=None, config=None):
        """
        Genome loader.
        If genes - a list of names - is passed only named genes will
        be loaded from the config.

        If require_genes are passed after the loading we ensure that
        they exist.

        If filename is given we create config object ourselves and
           load it from the file when .load() method is called
           otherwise we require a config instance which already was
           loaded.  With the 'config' you usually want to pass 'genes'
           option to limit us to only few config sections.
        """

        assert(filename is not None or config is not None)

        # Dictionary of supported types into casts and factories
        self.types = {
            'int': (_intcast, IntGeneFactory),
            'int_exchange': (_intcast, IntGeneExchangeFactory),

            'float': (_floatcast, FloatGeneFactory),
            'float_exchange': (_floatcast, FloatGeneExchangeFactory),
            'float_random': (_floatcast, FloatGeneRandomFactory),
            'float_max': (_floatcast, FloatGeneMaxFactory),

            'complex': (_floatcast, ComplexGeneFactory),
            # 'char': (str, CharGeneFactory),
            # ... TODO: add other
        }

        self.genome = {}

        self.genes_to_load = genes
        self.require_genes = require_genes

        if filename is not None:
            self.config = ConfigParser.RawConfigParser()
            self.config.optionxform = str # Don't lower() names
            self.config.read(filename)
        elif config is not None:
            self.config = config
        else:
            raise LoaderError("Either filename or config object must be passed it")

    def register_type(self, typename, cast, factory):
        """
        User can register his types using this method
        """
        self.types[typename] = (cast, factory)

    def _parse_gene(self, section):
        """
        parse_gene is called by parse_genome to parse
        a single gene from a config.
        config - ConfigParser instance
        section - gene name / config section name
        """
        # This check won't work because of configparser:
        if section in self.genome:
            raise LoaderError("Gene %s was already defined" % section_)

        # Alias?
        try:
            alias = self.config.get(section, 'alias')
            if alias not in self.genome:
                raise LoaderError(("Gene %s is an alias for non-existing gene %s. "
                                   "Order matters!") % alias)
            return self.genome[alias]
        except NoOptionError:
            # Not an alias.
            pass

        try:
            typename = self.config.get(section, 'type')
        except NoOptionError:
            raise LoaderError(("Required field 'type' was not "
                              "found in section/gene '%s'") % section)

        try:
            cast, factory = self.types[typename]
        except KeyError:
            raise LoaderError("Unhandled type in config file: " + typename)

        args = {}
        for key, value in self.config.items(section):
            if key == "type":
                continue
            if key == "mutProb": # Always float
                converted = _floatcast(section, key, value)
            else:
                converted = cast(section, key, value)
            args[key] = converted
        gene = factory(typename + "_" + section, **args)
        return gene

    def load_genome(self):
        """
        Load genome from config file
        """

        sections = self.genes_to_load if self.genes_to_load else self.config.sections()

        for section in sections:
            gene = self._parse_gene(section)
            self.genome[section] = gene

        for gene in self.require_genes:
            if gene not in self.genome:
                raise LoaderError("Required gene '%s' was not found in the config" % gene)
        #for gene in self.genome.itervalues():
        #    print gene.__dict__
        return self.genome
