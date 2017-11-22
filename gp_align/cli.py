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

"""The analysis and conversion command line interface."""

from __future__ import absolute_import

import logging
import os
from glob import glob
from multiprocessing import cpu_count

import click
import click_log
from six import iteritems

from gp_align.analyze import analyze_run


LOGGER = logging.getLogger()
click_log.basic_config(LOGGER)


@click.group()
@click.help_option("--help", "-h")
@click_log.simple_verbosity_option(
    LOGGER, default="INFO", show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]))
def cli():
    """
    Growth profiler raw image analysis.

    Based on calibration images this tool extracts G values from a
    series of images and can later convert them to OD values.
    """
    pass


@cli.command()
@click.help_option("--help", "-h")
@click.option("--out", "-o", default="result", show_default=True,
              help="The base output filename. (Will have appended tray "
                   "suffixes.)")
@click.option("--orientation", type=click.Choice(["top-right", "bottom-left"]),
              default="top-right", show_default=True,
              help="The corner position of plate well A1.")
@click.option("--plate-type", type=click.IntRange(min=1, max=3),
              default=1, show_default=True,
              help="The plate type where 1 = 96 wells, 2 = 96 deep wells, "
                   "and 3 = 24 wells.")
@click.option("--scanner", type=click.IntRange(min=1, max=2),
              default=1, show_default=True,
              help="The scanner used 1 = left, 2 = right.")
@click.option("--processes", "-p", type=int, default=cpu_count(),
              show_default=True, help="Select the number of processes to use.")
@click.argument("pattern", type=str)
def analyze(pattern, scanner, plate_type, orientation, out, processes):
    """
    Analyze a series of images.

    The provided pattern is interpreted just like a shell glob.
    """
    filenames = glob(pattern)
    if len(filenames) == 0:
        LOGGER.critical("No files match the given glob pattern.")
        return 1
    data = analyze_run(filenames, scanner, plate_type, orientation=orientation,
                       num_proc=processes)

    for name, df in iteritems(data):
        df.to_csv(out + "_" + name + ".G.tsv", sep="\t", index=False)


@cli.command()
@click.help_option("--help", "-h")
@click.argument("parameters", nargs=3)
@click.argument("files", nargs=-1)
def convert():
    """
    Convert tabular G values to equivalent tables of OD values.

    Provided with three parameters for fitting the logistic function, convert
    all the given files to OD values.
    """
    pass


def convert_g_values(args):
    import numpy as np
    import pandas as pd

    def convert_G_to_OD(val, A, B, C):
        return np.exp((val - C) / A) - B

    parameters = args.parameters
    inputs = args.files

    parameters = list(map(float, parameters))
    print(parameters)

    filenames = []
    for f in inputs:
        if "*" in f:
            filenames.extend(glob.glob(f))
        else:
            filenames.append(f)

    for filename in filenames:
        if not os.path.isfile(filename):
            raise ValueError(filename, "does not exist")
        if not filename.endswith(".G.tsv"):
            raise ValueError(filename, "does not end with .G.tsv")

    for filename in filenames:
        df = pd.read_csv(filename, sep="\t", index_col=0)

        converted_df = convert_G_to_OD(df, *parameters)
        converted_df.index = converted_df.index / 60

        outname = filename[:-5] + "OD.v2.tsv"
        converted_df.to_csv(outname, sep="\t")
