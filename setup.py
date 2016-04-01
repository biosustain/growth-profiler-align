#!/usr/bin/env python

from setuptools import setup

requirements = [
      "numpy",
      "scikit-image",
      "scipy",
      "pandas"
]

setup(name='growth-profiler-align',
      version='0.1',
      description='Utilities for analysing growth profiler raw images',
      author='Kristian Jensen',
      author_email='krisj@biosustain.dtu.dk',
      install_requires=requirements,
      url='http://github.com/biosustain/'
     )