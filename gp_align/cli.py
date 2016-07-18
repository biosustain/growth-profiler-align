from __future__ import division, absolute_import, print_function

import argparse
import os
import glob
from gp_align.analyse import analyse_run

parser = argparse.ArgumentParser(description="Analyse growth profiler images")
parser.set_defaults(func=lambda args: parser.print_help())

subparsers = parser.add_subparsers()


def analyse_images(args):
    filenames = []
    for f in args.infiles:
        if "*" in f:
            filenames.extend(glob.glob(f))
        else:
            filenames.append(f)

    for filename in filenames:
        if not os.path.isfile(filename):
            raise ValueError(filename, "does not exist")

    outname = args.out

    if args.scanner == 1:
        plate_names = None
    elif args.scanner == 2:
        plate_names = ["tray7", "tray8", "tray9", "tray10", "tray11", "tray12"]

    plate_type = args.plate_type
    orientation = args.orientation

    data = analyse_run(filenames, plate_type, orientation=orientation, plate_names=plate_names)

    for name, df in data.items():
        df.to_csv(outname + "_" + name + ".G.tsv", sep="\t")


analyse_parser = subparsers.add_parser(
    "analyse", help="Analyse a list of growth profiler images and output a tsv file with growth curves"
)
analyse_parser.add_argument("infiles", type=str, nargs="+")
analyse_parser.add_argument("--out", type=str, default="result")
analyse_parser.add_argument("--orientation", type=str, default="top_right", choices=["top_right", "bottom_left"])
analyse_parser.add_argument("--plate_type", type=int, default=1)
analyse_parser.add_argument("--scanner", type=int, default=1, choices=[1, 2])
analyse_parser.set_defaults(func=analyse_images)


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

convert_parser = subparsers.add_parser(
    "convert", help="Convert the output G-value files to OD-values, using a set of calibration parameters."
)
convert_parser.add_argument("parameters", type=str, nargs=3)
convert_parser.add_argument("files", type=str, nargs="+")
convert_parser.set_defaults(func=convert_g_values)