#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup the growth profiler image analysis tool."""

from __future__ import absolute_import

from setuptools import setup, find_packages

requirements = [
    "numpy",
    "scikit-image",
    "scipy",
    "pandas",
    "tqdm",
    "click",
    "click-log",
    "six"
]

setup(
    name="gp_align",
    version="0.1.0",
    description='utilities for analysing growth profiler raw images',
    author='Kristian Jensen',
    author_email='krisj@biosustain.dtu.dk',
    url='http://github.com/biosustain/growth-profiler-align',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[],
    entry_points="""
        [console_scripts]
        gpalign=gp_align.cli:cli
    """,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="growth, profiler, align",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ]
)
