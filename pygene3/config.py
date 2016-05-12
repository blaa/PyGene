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

import configparser
from configparser import NoOptionError

from .gene import ComplexGeneFactory
from .gene import IntGeneFactory, IntGeneExchangeFactory
from .gene import IntGeneAverageFactory, IntGeneRandRangeFactory
from .gene import FloatGeneFactory, FloatGeneRandomFactory, FloatGeneMaxFactory
from .gene import FloatGeneExchangeFactory, FloatGeneRandRangeFactory

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

    def __init__(self, filename, require_genes=[], config_contents=None):
        """
        Genome loader.
        Filename - path to configuration (alternatively you can pass the config
        contents via the config_contents and pass None as the filename).
        If require_genes are passed after the loading we ensure that
        they exist.
        """
        # Dictionary of supported types into casts and factories
        self.types = {
            'int': (_intcast, IntGeneFactory),
            'int_exchange': (_intcast, IntGeneExchangeFactory),
            'int_average': (_intcast, IntGeneAverageFactory),
            'int_randrange': (_intcast, IntGeneRandRangeFactory),

            'float': (_floatcast, FloatGeneFactory),
            'float_average': (_floatcast, FloatGeneFactory), # The same as float.
            'float_randrange': (_floatcast, FloatGeneRandRangeFactory),
            'float_exchange': (_floatcast, FloatGeneExchangeFactory),
            'float_random': (_floatcast, FloatGeneRandomFactory),
            'float_max': (_floatcast, FloatGeneMaxFactory),

            'complex': (_floatcast, ComplexGeneFactory),
            # 'char': (str, CharGeneFactory),
            # ... TODO: add other
        }

        self.genome = {}

        self.require_genes = require_genes

        self.config = configparser.RawConfigParser()
        self.config.optionxform = str # Don't lower() names

        if filename is None and config_contents is not None:
            import io
            self.config.readfp(io.BytesIO(config_contents))
        else:
            self.config.read(filename)

        # Do we have a population definition also?
        self._pre_parse_population()


    def register_type(self, typename, cast, factory):
        """
        User can register his types using this method
        """
        self.types[typename] = (cast, factory)

    def _pre_parse_population(self):
        self.has_population = self.config.has_section('population')
        try:
            genes = self.config.get('population', 'genes')
            genes = [gene.strip()
                     for gene in genes.split()]
            self.genes = genes if genes else None
        except NoOptionError:
            self.genes = None

    def load_population(self, name, species):
        """
        Parse population options and return a population
        """
        from .population import Population

        if not self.has_population:
            raise LoaderError("No population is defined in the config file")
        args = {
            'species': species
        }
        def parse(fun, name):
            if self.config.has_option('population', name):
                try:
                    val = fun('population', name)
                    args[name] = val
                except ValueError:
                    raise LoaderError("Invalid value for population option " + name)

        parse(self.config.getint, 'initPopulation')
        parse(self.config.getint, 'childCull')
        parse(self.config.getint, 'childCount')
        parse(self.config.getint, 'incest')
        parse(self.config.getint, 'numNewOrganisms')
        parse(self.config.getboolean, 'mutateAfterMating')
        parse(self.config.getfloat, 'mutants')

        return type(name, (Population,), args)


    def _parse_gene(self, section):
        """
        parse_gene is called by parse_genome to parse
        a single gene from a config.
        config - ConfigParser instance
        section - gene name / config section name
        """
        genename = section

        if not self.config.has_section(genename):
            raise LoaderError("Gene %s has no section in the config file" % genename)

        # FIXME: This check won't work because of configparser:
        if genename in self.genome:
            raise LoaderError("Gene %s was already defined" % section)

        try:
            clonegene = self.config.get(section, 'clone')
            if not self.config.has_section(clonegene):
                raise LoaderError("Gene %s is cloning a gene %s which is not yet defined" % (genename, clonegene))
            section = clonegene
            genename = clonegene
        except NoOptionError:
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

        if 'randMin' in args and 'randMax' in args:
            if args['randMin'] > args['randMax']:
                raise LoaderError('randMin higher than randMax in section/gene %s' % section)
            if ('value' in args and args['value'] is not None
                and (args['value'] > args['randMax']
                     or args['value'] < args['randMin'])):
                raise LoaderError('value not within randMin, randMax in section/gene %s' % section)

        gene = factory(typename + "_" + genename, **args)
        return gene

    def load_genome(self):
        """
        Load genome from config file
        """

        sections = self.genes if self.genes else self.config.sections()

        for section in sections:
            if section.lower() == 'population':
                continue
            elif self.config.has_option(section, 'alias'):
                alias = self.config.get(section, 'alias')
                if alias not in self.genome:
                    raise LoaderError(("Gene %s is an alias for non-existing gene %s. "
                                       "Order matters!") % (section, alias))
                self.genome[section] = self.genome[alias]
                continue
            else:
                gene = self._parse_gene(section)
                self.genome[section] = gene

        for gene in self.require_genes:
            if gene not in self.genome:
                raise LoaderError("Required gene '%s' was not found in the config" % gene)
        #for gene in self.genome.itervalues():
        #    print gene.__dict__
        return self.genome
