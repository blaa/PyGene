#! /usr/bin/env python

from distutils.core import setup

import pygene

setup(name="pygene",
      version=pygene.version,
      description="Simple Genetic Algorithms Library",
      author="David McNab",
      author_email="david@freenet.org.nz",
      url="http://www.freenet.org.nz/python/pygene",
      packages=['pygene'],
     )

