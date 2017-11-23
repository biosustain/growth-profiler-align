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
from glob import glob
from multiprocessing import cpu_count

import click
import click_log
from pandas import read_csv
from six import iteritems
from tqdm import tqdm

from gp_align.analysis import analyze_run
from gp_align.conversion import convert_run


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
              help="The plate type where 1 = 96 black wells, 2 = 96 white "
                   "wells, and 3 = 24 wells.")
@click.option("--scanner", type=click.IntRange(min=1, max=2),
              default=1, show_default=True,
              help="The scanner used 1 = left, 2 = right.")
@click.option("--time-unit", default="h", type=click.Choice(["D", "h", "m"]),
              show_default=True,
              help="The unit of time can be either day = D, hour = h, "
                   "or minute = m.")
@click.option("--processes", "-p", type=int, default=cpu_count(),
              show_default=True, help="Select the number of processes to use.")
@click.argument("pattern", type=str)
def analyze(pattern, scanner, plate_type, orientation, out, time_unit,
            processes):
    """
    Analyze a series of images.

    The provided pattern is interpreted just like a shell glob.
    """
    filenames = glob(pattern)
    if len(filenames) == 0:
        LOGGER.critical("No files match the given glob pattern.")
        return 1
    data = analyze_run(filenames, scanner, plate_type, orientation=orientation,
                       unit=time_unit, num_proc=processes)

    for name, df in iteritems(data):
        df.to_csv(out + "_" + name + ".G.tsv", sep="\t", index=False)


@cli.command()
@click.help_option("--help", "-h")
@click.argument("parameters", nargs=3)
@click.argument("pattern", type=str)
def convert(pattern, parameters):
    """
    Convert tabular G values to equivalent tables of OD values.

    Provided with three parameters for fitting an exponential function, convert
    all the given files to OD values.
    """
    filenames = glob(pattern)
    if len(filenames) == 0:
        LOGGER.critical("No files match the given glob pattern.")
        return 1
    parameters = tuple(map(float, parameters))
    for path in tqdm(filenames):
        if not path.endswith(".G.tsv"):
            LOGGER.error("'%s' does not end with '.G.tsv'.", path)
            continue
        try:
            df = read_csv(path, sep="\t")
        except OSError as err:
            LOGGER.error(str(err))
            continue
        df = convert_run(df, *parameters)
        df.to_csv(path[:-5] + "OD.tsv", sep="\t", index=False)
