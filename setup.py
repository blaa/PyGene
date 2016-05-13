#! /usr/bin/env python

from distutils.core import setup

import pygene3

setup(name="pygene3",
      version=pygene3.version,
      description="Simple Genetic Algorithms Library",
      author="David McNab, Tomasz Fortuna",
      author_email="bla@thera.be",
      url="https://github.com/blaa/PyGene",
      keywords="learning genetic classification",
      license="GPLv2",
      packages=['pygene3'],
        classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],

)

