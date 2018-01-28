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

from gp_align.analysis import analyze_run, PLATES
from gp_align.conversion import g2od


LOGGER = logging.getLogger(__name__.split(".", 1)[0])
click_log.basic_config(LOGGER)

try:
    NUM_CPU = min(4, cpu_count())
except NotImplementedError:
    LOGGER.warning("Could not detect the number of cores - assuming only one.")
    NUM_CPU = 1


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
              default=1, show_default=True, metavar="[1|2|3]",
              help="The plate type where 1 = 96 black wells, 2 = 96 white "
                   "wells, and 3 = 24 wells.")
@click.option("--scanner", type=click.IntRange(min=1, max=2),
              default=1, show_default=True, metavar="[1|2]",
              help="The scanner used 1 = left, 2 = right.")
@click.option("--trays", default=None, metavar="e.g., 1,5,6",
              help="A comma separated list of tray numbers as listed in the "
                   "README (1-6 for scanner 1 and 7-12 for scanner 2).")
@click.option("--time-unit", default="h", type=click.Choice(["D", "h", "m"]),
              show_default=True,
              help="The unit of time can be either day = D, hour = h, "
                   "or minute = m.")
@click.option("--processes", "-p", type=int, default=NUM_CPU,
              show_default=True, help="Select the number of processes to use.")
@click.argument("pattern", type=str)
def analyze(pattern, scanner, plate_type, orientation, out, trays,
            time_unit, processes):
    """
    Analyze a series of images.

    The provided pattern is interpreted just like a shell glob.
    """
    filenames = glob(pattern)
    if len(filenames) == 0:
        LOGGER.critical("No files match the given glob pattern.")
        return 1
    if trays is None:
        plates = PLATES[scanner]
    else:
        plates = ["tray" + num.strip() for num in trays.split(",")]
        if not frozenset(plates).issubset(PLATES[scanner]):
            raise click.BadParameter(
                "'{}' contains invalid trays for scanner {}. "
                "Please refer to the README.".format(trays, scanner))

    data = analyze_run(filenames, scanner, plate_type, orientation=orientation,
                       plates=plates, unit=time_unit, num_proc=processes)

    for name, df in iteritems(data):
        df.to_csv(out + "_" + name + ".G.tsv", sep="\t")


@cli.command()
@click.help_option("--help", "-h")
@click.option("--out", "-o", default=None, type=str,
              help="The desired output filename. Only permissible when "
                   "processing one file otherwise it is ignored.")
@click.argument("parameters", nargs=3)
@click.argument("pattern", type=str)
def convert(pattern, parameters, out):
    """
    Transform G values to OD values.

    Provided with three parameters for fitting an exponential function,
    transform tabular files of G values given by the glob pattern to OD values.

    """
    filenames = glob(pattern)
    if out is not None and len(filenames) != 1:
        LOGGER.critical(
            "Cannot name the output file when processing more than one file.")
        return 2
    if len(filenames) == 0:
        LOGGER.critical("No files match the given glob pattern.")
        return 1
    parameters = tuple(map(float, parameters))

    # Process the conversion of a single file with custom output name.
    if out is not None and len(filenames) == 1:
        try:
            g_df = read_csv(filenames[0], sep="\t", index_col=0)
        except OSError as err:
            LOGGER.error(str(err))
            return 1
        od_df = g2od(g_df, *parameters)
        od_df.to_csv(out, sep="\t")
        return

    # Process matching files normally.
    for path in tqdm(filenames):
        if not path.endswith(".G.tsv"):
            LOGGER.error("'%s' does not end with '.G.tsv'. Ignored.", path)
            continue
        try:
            g_df = read_csv(path, sep="\t", index_col=0)
        except OSError as err:
            LOGGER.error(str(err))
            continue
        od_df = g2od(g_df, *parameters)
        od_df.to_csv(path[:-5] + "OD.tsv", sep="\t")
