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

